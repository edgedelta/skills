#!/usr/bin/env python3
"""
EdgeDelta Pipeline Validation Script
Validates pipeline v3 YAML configurations against EdgeDelta rules

Usage:
    python3 validate_pipeline.py <pipeline.yaml>
    python3 validate_pipeline.py <pipeline.yaml> --verbose

Based on EdgeDelta validation rules from:
    edgedelta-main/configv3/config_validation.go
"""

import sys
import yaml
import re
from typing import Dict, List, Tuple
from pathlib import Path

# Add parent directory to path for instrumentation import
sys.path.insert(0, str(Path(__file__).parents[3] / "_shared"))
try:
    from instrumentation import measure_time, print_summary
    INSTRUMENTATION_AVAILABLE = True
except ImportError:
    # Gracefully degrade if instrumentation not available
    from contextlib import contextmanager
    @contextmanager
    def measure_time(operation):
        yield
    def print_summary():
        pass
    INSTRUMENTATION_AVAILABLE = False

# Sequence-compatible processors (from sequence_node.go:52-76)
# NOTE: Also includes nested 'sequence', 'comment', 'aggregate_metric', 'ottl_filter'
# which are valid in production pipelines
SEQUENCE_COMPATIBLE_PROCESSORS = {
    "generic_mask", "extract_metric", "ottl_transform", "sample", "dedup",
    "log_to_pattern_metric", "delete_empty_values", "json_unroll",
    "log_to_metric", "log_to_signal", "metric_to_log", "trace_to_log",
    "log_to_log", "metric_to_metric", "trace_to_trace", "attribute_filter",
    "regex_filter", "stateful_where", "deotel", "http_request_call",
    "sampling", "throttle", "regex_based_log_parser",
    # Additional valid processor types found in production
    "sequence",          # Nested sequences are valid
    "comment",           # Comment blocks are valid
    "aggregate_metric",  # Metric aggregation is valid
    "ottl_filter",       # OTTL filtering is valid
    "lookup",            # Lookup enrichment processor
    "route",             # Routing processor for conditional flows
}

# Required node that must be present
REQUIRED_NODES = {"ed_self_telemetry_input"}

class PipelineValidator:
    def __init__(self, verbose=False):
        self.errors = []
        self.warnings = []
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[DEBUG] {msg}")

    def error(self, msg):
        self.errors.append(msg)
        print(f"✗ ERROR: {msg}")

    def warning(self, msg):
        self.warnings.append(msg)
        print(f"⚠ WARNING: {msg}")

    def validate(self, config_path: str) -> bool:
        """Main validation entry point"""
        print(f"\n{'='*80}")
        print(f"Validating: {config_path}")
        print(f"{'='*80}\n")

        with measure_time("Total validation"):
            try:
                with measure_time("YAML parsing"):
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
            except Exception as e:
                self.error(f"Failed to parse YAML: {e}")
                return False

            # Run all validations
            with measure_time("Version validation"):
                self.validate_version(config)

            with measure_time("Required fields validation"):
                self.validate_required_fields(config)

            with measure_time("Node validation"):
                self.validate_nodes(config)

            with measure_time("Link validation"):
                self.validate_links(config)

            with measure_time("Sequence validation"):
                self.validate_sequences(config)

            with measure_time("Required nodes check"):
                self.validate_required_nodes(config)

            with measure_time("YAML formatting check"):
                self.validate_yaml_formatting(config_path)

        # Print summary
        print(f"\n{'='*80}")
        print("VALIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")

        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("\n✓✓✓ VALIDATION PASSED - Pipeline is valid! ✓✓✓\n")
            if INSTRUMENTATION_AVAILABLE:
                print_summary()
            return True
        elif len(self.errors) == 0:
            print(f"\n✓ VALIDATION PASSED with {len(self.warnings)} warnings\n")
            if INSTRUMENTATION_AVAILABLE:
                print_summary()
            return True
        else:
            print(f"\n✗ VALIDATION FAILED with {len(self.errors)} errors\n")
            if INSTRUMENTATION_AVAILABLE:
                print_summary()
            return False

    def validate_version(self, config: Dict):
        """Validate pipeline version"""
        version = config.get("version")
        if not version:
            self.error("Missing 'version' field")
        elif version != "v3":
            self.error(f"Invalid version '{version}' - must be 'v3'")
        else:
            self.log(f"Version: {version} ✓")

    def validate_required_fields(self, config: Dict):
        """Validate required top-level fields"""
        required = ["version", "settings", "nodes", "links"]
        for field in required:
            if field not in config:
                self.error(f"Missing required field: '{field}'")
            else:
                self.log(f"Required field '{field}' present ✓")

        # Validate settings.tag
        settings = config.get("settings", {})
        if "tag" not in settings:
            self.error("Missing required field: 'settings.tag'")
        else:
            self.log(f"Pipeline tag: {settings['tag']} ✓")

    def validate_nodes(self, config: Dict):
        """Validate nodes configuration"""
        nodes = config.get("nodes", [])
        if not nodes:
            self.error("No nodes defined in pipeline")
            return

        self.log(f"Found {len(nodes)} nodes")

        node_names = set()
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict):
                self.error(f"Node {idx} is not a dictionary")
                continue

            # Check required node fields
            if "name" not in node:
                self.error(f"Node {idx} missing 'name' field")
                continue
            if "type" not in node:
                self.error(f"Node '{node['name']}' missing 'type' field")
                continue

            name = node["name"]
            node_type = node["type"]

            # Check for duplicate names
            if name in node_names:
                self.error(f"Duplicate node name: '{name}'")
            node_names.add(name)

            self.log(f"Node '{name}' (type: {node_type}) ✓")

        return node_names

    def validate_links(self, config: Dict):
        """Validate links reference existing nodes"""
        nodes = config.get("nodes", [])
        links = config.get("links", [])

        node_names = {node["name"] for node in nodes if "name" in node}

        self.log(f"Found {len(links)} links")

        for idx, link in enumerate(links):
            if not isinstance(link, dict):
                self.error(f"Link {idx} is not a dictionary")
                continue

            if "from" not in link:
                self.error(f"Link {idx} missing 'from' field")
                continue
            if "to" not in link:
                self.error(f"Link {idx} missing 'to' field")
                continue

            from_node = link["from"]
            to_node = link["to"]

            if from_node not in node_names:
                self.error(f"Link references non-existent 'from' node: '{from_node}'")
            if to_node not in node_names:
                self.error(f"Link references non-existent 'to' node: '{to_node}'")

            self.log(f"Link: {from_node} → {to_node} ✓")

    def validate_sequences(self, config: Dict):
        """Validate sequence processors"""
        nodes = config.get("nodes", [])

        for node in nodes:
            if node.get("type") != "sequence":
                continue

            name = node.get("name", "unnamed")
            processors = node.get("processors", [])

            if not processors:
                self.warning(f"Sequence '{name}' has no processors")
                continue

            self.log(f"Validating sequence '{name}' with {len(processors)} processors")

            # Validate each processor
            final_count = 0
            deotel_position = None

            for idx, processor in enumerate(processors):
                if not isinstance(processor, dict):
                    self.error(f"Sequence '{name}' processor {idx} is not a dictionary")
                    continue

                proc_type = processor.get("type")
                if not proc_type:
                    self.error(f"Sequence '{name}' processor {idx} missing 'type'")
                    continue

                # Check if processor is sequence-compatible
                if proc_type not in SEQUENCE_COMPATIBLE_PROCESSORS:
                    self.error(f"Sequence '{name}' contains non-sequence-compatible processor: '{proc_type}'")

                # Check for final flag
                if processor.get("final"):
                    final_count += 1
                    if idx != len(processors) - 1:
                        self.error(f"Sequence '{name}' has 'final: true' on processor {idx}, but it's not the last processor")

                # Track DeOTEL position
                if proc_type == "deotel":
                    deotel_position = idx

                self.log(f"  Processor {idx}: {proc_type} ✓")

            # Validate DeOTEL is last if present
            if deotel_position is not None:
                if deotel_position != len(processors) - 1:
                    self.error(f"Sequence '{name}' has DeOTEL processor at position {deotel_position}, but it must be last")

            # Warn if no final flag
            if final_count == 0:
                self.warning(f"Sequence '{name}' has no processor with 'final: true'")
            elif final_count > 1:
                self.error(f"Sequence '{name}' has multiple processors with 'final: true'")

    def validate_required_nodes(self, config: Dict):
        """Validate required nodes are present"""
        nodes = config.get("nodes", [])
        node_types = {node.get("type") for node in nodes if "type" in node}

        for required_type in REQUIRED_NODES:
            if required_type not in node_types:
                self.error(f"Missing required node type: '{required_type}'")
            else:
                self.log(f"Required node '{required_type}' present ✓")

    def validate_yaml_formatting(self, config_path: str):
        """Check for common YAML formatting issues"""
        try:
            with open(config_path, 'r') as f:
                content = f.read()

            # Check for Unicode characters in comments
            if '→' in content or '✓' in content or '✗' in content:
                self.warning("YAML contains Unicode characters (→, ✓, ✗) which may cause API errors")

            # Check for json_field_path starting with dot
            if re.search(r'json_field_path:\s*["\']\.', content):
                self.error("json_field_path cannot start with '.' - use '$' instead")

            # Check for persisting_cursor_settings (known to cause issues)
            if 'persisting_cursor_settings' in content:
                self.warning("persisting_cursor_settings may cause API 500 errors - consider removing")

        except Exception as e:
            self.warning(f"Could not validate YAML formatting: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_pipeline.py <pipeline.yaml> [--verbose]")
        sys.exit(1)

    config_path = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    validator = PipelineValidator(verbose=verbose)
    success = validator.validate(config_path)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
