#!/usr/bin/env python3
"""
EdgeDelta Pipeline Builder - Interactive Template Generator

This script should be called by Claude as part of the edgedelta-pipelines skill.
Claude will gather requirements from the user and invoke this script to generate
the YAML configuration.

Usage:
    python3 pipeline_builder.py --interactive
    python3 pipeline_builder.py --config <config.json> --output <pipeline.yaml>

Config JSON format:
{
  "tag": "my-pipeline",
  "inputs": [
    {"type": "file_input", "path": "/var/log/app/*.log"},
    {"type": "otlp_input", "port": 4317, "protocol": "grpc"}
  ],
  "processing": {
    "pii_masking": ["passwords", "emails"],
    "sampling": 10,
    "extract_metrics": true
  },
  "output": "edgedelta"
}
"""

import sys
import json
import yaml
from pathlib import Path

class PipelineBuilder:
    def __init__(self):
        self.config = {
            "version": "v3",
            "settings": {
                "tag": "custom-pipeline",
                "log": {"level": "info"},
                "archive_flush_interval": "1m0s",
                "archive_max_byte_limit": "16MB"
            },
            "links": [],
            "nodes": []
        }

    def add_telemetry_input(self):
        """Add required ed_self_telemetry_input"""
        self.config["nodes"].append({
            "name": "ed_self_telemetry_input",
            "type": "ed_self_telemetry_input",
            "enable_health_metrics": True,
            "enable_agent_stats_metrics": True
        })
        self.config["links"].append({
            "from": "ed_self_telemetry_input",
            "to": "edgedelta"
        })

    def add_output(self, output_type="edgedelta"):
        """Add output node"""
        if output_type == "edgedelta":
            self.config["nodes"].append({
                "name": "edgedelta",
                "type": "ed_output"
            })

    def add_file_input(self, name, path):
        """Add file input node"""
        self.config["nodes"].append({
            "name": name,
            "type": "file_input",
            "user_description": f"File logs from {path}",
            "path": path
        })

    def add_otlp_input(self, name, port, protocol="grpc"):
        """Add OTLP input node"""
        self.config["nodes"].append({
            "name": name,
            "type": "otlp_input",
            "user_description": f"OTLP {protocol.upper()} receiver",
            "port": port,
            "protocol": protocol,
            "read_timeout": "1m0s"
        })

    def add_http_pull_input(self, name, endpoint, pull_interval="5m"):
        """Add HTTP pull input node"""
        self.config["nodes"].append({
            "name": name,
            "type": "http_pull_input",
            "user_description": f"API pull from {endpoint}",
            "endpoint": endpoint,
            "method": "GET",
            "pull_interval": pull_interval,
            "headers": [
                {"header": "Accept", "value": "application/json"}
            ]
        })

    def add_sequence(self, name, processors, description="Processing sequence"):
        """Add sequence node with processors"""
        node = {
            "name": name,
            "type": "sequence",
            "user_description": description,
            "processors": processors
        }
        self.config["nodes"].append(node)

    def build_pii_masking_processors(self, mask_types):
        """Build PII masking processors"""
        processors = []

        if "passwords" in mask_types:
            processors.append({
                "type": "generic_mask",
                "capture_group_masks": [{
                    "capture_group": "(?i)(password|passwd|pwd)[:=]\\S+",
                    "enabled": True,
                    "mask": "***PASSWORD***",
                    "name": "password"
                }]
            })

        if "emails" in mask_types:
            processors.append({
                "type": "generic_mask",
                "capture_group_masks": [{
                    "capture_group": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
                    "enabled": True,
                    "mask": "***EMAIL***",
                    "name": "email"
                }]
            })

        if "credit_cards" in mask_types:
            processors.append({
                "type": "generic_mask",
                "capture_group_masks": [{
                    "capture_group": "\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b",
                    "enabled": True,
                    "mask": "***CC***",
                    "name": "credit_card"
                }]
            })

        return processors

    def build_from_spec(self, spec):
        """Build pipeline from specification"""
        # Set tag
        if "tag" in spec:
            self.config["settings"]["tag"] = spec["tag"]

        # Add output first
        self.add_output(spec.get("output", "edgedelta"))

        # Add telemetry
        self.add_telemetry_input()

        # Add inputs
        for idx, input_spec in enumerate(spec.get("inputs", [])):
            input_type = input_spec["type"]
            input_name = f"input_{idx+1}"

            if input_type == "file_input":
                self.add_file_input(input_name, input_spec["path"])
            elif input_type == "otlp_input":
                self.add_otlp_input(
                    input_name,
                    input_spec.get("port", 4317),
                    input_spec.get("protocol", "grpc")
                )
            elif input_type == "http_pull_input":
                self.add_http_pull_input(
                    input_name,
                    input_spec["endpoint"],
                    input_spec.get("pull_interval", "5m")
                )

            # Add sequence for this input if processing is needed
            processing = spec.get("processing", {})
            if processing:
                processors = []

                # PII masking
                if "pii_masking" in processing:
                    processors.extend(self.build_pii_masking_processors(processing["pii_masking"]))

                # Sampling
                if "sampling" in processing:
                    processors.append({
                        "type": "sample",
                        "percentage": processing["sampling"]
                    })

                # Metric extraction
                if processing.get("extract_metrics"):
                    processors.append({
                        "type": "extract_metric",
                        "extract_metric_rules": [{
                            "name": "log_events_total",
                            "description": "Total log events",
                            "unit": "1",
                            "conditions": ['IsMatch(body, ".*")'],
                            "sum": {
                                "aggregation_temporality": "delta",
                                "is_monotonic": True,
                                "value": 1
                            }
                        }],
                        "interval": "1m"
                    })

                # Mark last processor as final
                if processors:
                    processors[-1]["final"] = True

                    # Add sequence
                    seq_name = f"{input_name}_processing"
                    self.add_sequence(seq_name, processors)

                    # Add links
                    self.config["links"].append({"from": input_name, "to": seq_name})
                    self.config["links"].append({"from": seq_name, "to": "edgedelta"})
                else:
                    # Direct link to output
                    self.config["links"].append({"from": input_name, "to": "edgedelta"})
            else:
                # Direct link to output
                self.config["links"].append({"from": input_name, "to": "edgedelta"})

    def to_yaml(self):
        """Convert to YAML string"""
        return yaml.dump(self.config, default_flow_style=False, sort_keys=False)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 pipeline_builder.py --config <config.json> --output <pipeline.yaml>")
        sys.exit(1)

    if "--config" in sys.argv:
        config_idx = sys.argv.index("--config") + 1
        config_path = sys.argv[config_idx]

        output_idx = sys.argv.index("--output") + 1 if "--output" in sys.argv else None
        output_path = sys.argv[output_idx] if output_idx else "pipeline.yaml"

        # Load config
        with open(config_path, 'r') as f:
            spec = json.load(f)

        # Build pipeline
        builder = PipelineBuilder()
        builder.build_from_spec(spec)

        # Write output
        with open(output_path, 'w') as f:
            f.write(builder.to_yaml())

        print(f"✓ Pipeline written to {output_path}")

if __name__ == "__main__":
    main()
