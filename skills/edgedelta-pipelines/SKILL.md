---
name: edgedelta-pipelines
version: 2.2.0
last_updated: 2026-02-03
description: This skill should be used when users want to create EdgeDelta pipelines, validate pipeline YAML configurations, deploy pipelines to EdgeDelta, or ask about EdgeDelta monitoring and observability. Recognizes phrases like "create a pipeline", "EdgeDelta config", "validate my pipeline", "deploy to EdgeDelta", "what can I monitor", and "help with OTLP/telemetry collection". Provides 7 production-tested templates, validation tools, and direct API deployment.
dependencies:
  - Python 3.11+
  - EdgeDelta API token
  - edgedelta-reference skill (for processor syntax)
---

# EdgeDelta Pipelines Skill

Creates, validates, and deploys EdgeDelta pipeline v3 configurations. Provides production-tested templates, validation tools, environment inspection, and interactive pipeline building.

## When to Use This Skill

Activate this skill when the user:
- Wants to create an EdgeDelta pipeline
- Asks about EdgeDelta configuration or monitoring
- Needs to collect logs, metrics, or traces
- Wants to validate a pipeline YAML
- Asks "what can I monitor" or wants environment inspection
- Mentions pipelines, telemetry, observability with EdgeDelta context

## Core Capabilities

1. **Quick Deploy**: Choose from 7 production-tested templates
2. **Custom Builder**: Interactive pipeline creation with environment inspection
3. **Validation**: Check pipelines against EdgeDelta rules before deployment
4. **Environment Discovery**: Inspect K8s/Linux/Windows for monitoring opportunities
5. **Direct Deployment**: Deploy pipelines via EdgeDelta API

## Quick Reference Searches

For fast lookups without loading full skill context:

```bash
# Find template by use case
grep -n "Use case:" SKILL.md

# Find template architecture
grep -n "Architecture:" SKILL.md

# Find validation rules
grep -n "validation" assets/scripts/validate_pipeline.py

# Find processor examples
grep -rn "type: generic_mask" assets/templates/

# Find API deployment script
ls assets/scripts/deploy_pipeline.py

# See all templates
ls assets/templates/template-*.yaml
```

## Available Workflows

### Workflow 1: Quick Template Deployment

**When**: User wants to quickly deploy a pipeline

**Steps**:
1. Ask for EdgeDelta credentials:
   - Organization ID
   - API Token
   - Check `~/.edgedelta.env or project .env file` first
   - Store in conversation context

2. Present template options:
   - **Template 1**: Log Ingestion with PII Masking
     - Use case: Application logs with compliance requirements
     - Architecture: file_input → sequence (3x generic_mask + extract_metric) → ed_output

   - **Template 2**: OTLP Dual Receiver
     - Use case: OpenTelemetry data collection
     - Architecture: otlp_input (gRPC+HTTP) → sequence (transform + metrics) → ed_output

   - **Template 3**: Mixed Telemetry Processing
     - Use case: Logs AND metrics with different processing
     - Architecture: file+otlp inputs → parallel sequences → ed_output

   - **Template 4**: API Pull with JSON Processing
     - Use case: REST API polling (ServiceNow, CMDB)
     - Architecture: http_pull → sequence (json_unroll + transform) → ed_output

   - **Template 5**: Multi-API with Aggregation
     - Use case: Multiple API sources (Duo Security pattern)
     - Architecture: 3x http_pull → 3x sequences → aggregator → ed_output

   - **Template 6**: Prometheus Metrics Scraper
     - Use case: Scrape Prometheus exporters (node_exporter, custom metrics)
     - Architecture: prometheus_input → sequence (transform) → ed_output
     - Features: Multi-target scraping, relabel_configs, cluster monitoring

   - **Template 7**: Lookup Enrichment
     - Use case: Enrich logs with reference data (user metadata, IP geo, product catalogs)
     - Architecture: compound (input → sequence (parse + lookup + transform) → route → matched/unmatched outputs)
     - Features: CSV/DB lookups, conditional routing, enrichment validation

3. Ask customization questions based on selected template:
   - Tag name
   - File paths (Template 1, 3)
   - Ports (Template 2, 3)
   - API endpoints (Template 4, 5)
   - Pull intervals (Template 4, 5)
   - Prometheus targets (Template 6)
   - Scrape intervals (Template 6)
   - Lookup CSV path and key fields (Template 7)
   - Enrichment attributes (Template 7)

4. Read the template from `assets/templates/template-{number}-{name}.yaml`

5. Customize the template with user's values

6. Run validation: `python3 assets/scripts/validate_pipeline.py /tmp/customized.yaml`

7. If valid, deploy: `python3 assets/scripts/deploy_pipeline.py /tmp/customized.yaml <org_id> <api_token>`

8. Provide deployment details:
   - Pipeline ID
   - App URL: https://app.edgedelta.com/pipelines/{id}
   - Install command

### Workflow 2: Environment Inspection + Custom Pipeline

**When**: User wants to build based on their environment OR asks "what can I monitor"

**Steps**:
1. Ask for credentials (same as Workflow 1)

2. Run environment inspection:
   ```bash
   python3 assets/scripts/inspect_environment.py --verbose
   ```

3. Present findings:
   - Kubernetes resources detected
   - Log files found
   - Applications running
   - Metrics endpoints available
   - Suggested input configurations

4. Ask user which sources to monitor

5. Ask processing requirements:
   - PII masking needed? (passwords/emails/credit cards)
   - Sampling? (percentage)
   - Metric extraction?
   - Custom transforms?

6. Build configuration spec (JSON):
   ```json
   {
     "tag": "user-specified-name",
     "inputs": [
       {"type": "file_input", "path": "/var/log/app/*.log"}
     ],
     "processing": {
       "pii_masking": ["passwords", "emails"],
       "extract_metrics": true
     },
     "output": "edgedelta"
   }
   ```

7. Generate pipeline:
   ```bash
   python3 assets/scripts/pipeline_builder.py --config /tmp/spec.json --output /tmp/pipeline.yaml
   ```

8. Validate and deploy (same as Workflow 1 steps 6-8)

### Workflow 3: Validate Existing Pipeline

**When**: User provides a YAML file or asks to validate

**Steps**:
1. Read the YAML file

2. Run validation with verbose output:
   ```bash
   python3 assets/scripts/validate_pipeline.py <file.yaml> --verbose
   ```

3. Report results:
   - ✓ Validation passed
   - ✗ Errors found (explain each)
   - ⚠ Warnings (explain each)

4. If errors found, suggest fixes:
   - Reference `assets/references/validation-rules.md`
   - Provide corrected YAML snippets
   - Explain EdgeDelta requirements

5. Offer to auto-fix common issues:
   - Add missing `ed_self_telemetry_input`
   - Fix `json_field_path` starting with "."
   - Remove Unicode characters from comments
   - Add `final: true` to last processor

6. If user wants, apply fixes and re-validate

### Workflow 4: Environment Inspection Only

**When**: User asks "what can I monitor" without wanting to create pipeline yet

**Steps**:
1. Run inspection (no credentials needed):
   ```bash
   python3 assets/scripts/inspect_environment.py --format markdown
   ```

2. Present report with categories:
   - **Kubernetes** (if available)
   - **Log Files** (paths and counts)
   - **Applications** (Docker, Nginx, databases, etc.)
   - **Services** (systemd or Windows services)
   - **Metrics Endpoints** (Prometheus, etc.)

3. For each finding, suggest EdgeDelta input configuration

4. Ask if user wants to proceed with pipeline creation

### Workflow 5: Update Existing Pipeline

**When**: User wants to modify an existing pipeline (add processors, fix bugs, change configuration)

**Steps**:
1. Get the pipeline ID (conf_id) - user provides or retrieve via EdgeDelta MCP tools:
   ```
   mcp__edgedelta__get_pipelines  # List all pipelines
   mcp__edgedelta__get_pipeline_config(conf_id)  # Get current config
   ```

2. Get current pipeline configuration to understand existing structure

3. Create modified YAML with changes:
   - Keep the same `settings.tag` as the existing pipeline
   - Add/modify/remove processors as needed
   - Preserve existing node IDs in metadata when possible

4. Validate the modified YAML:
   ```bash
   python3 assets/scripts/validate_pipeline.py /tmp/updated-pipeline.yaml --verbose
   ```

5. Deploy to existing pipeline using `--pipeline-id`:
   ```bash
   python3 assets/scripts/deploy_pipeline.py /tmp/updated-pipeline.yaml --pipeline-id <conf_id> --env-file <path>
   ```

6. Verify deployment via MCP tools:
   ```
   mcp__edgedelta__get_pipeline_history(conf_id)  # Confirm new version is deployed
   ```

**Alternative: Direct API Deployment**
When MCP tools are available, update pipelines directly via API calls:
1. Save config: POST `/orgs/{org_id}/pipelines/{conf_id}/save` with `{"content": yaml_content}`
2. Get version: GET `/orgs/{org_id}/pipelines/{conf_id}/history` → extract `timestamp` from first entry
3. Deploy: POST `/orgs/{org_id}/pipelines/{conf_id}/deploy/{timestamp}`

### Workflow 6: Template Reference / Learning

**When**: User asks about sequences, processors, patterns, or "how do I..."

**Steps**:
1. Identify the question type:
   - Processors available? → `assets/references/sequence-processors.md`
   - Validation rules? → `assets/references/validation-rules.md`
   - Best practices? → `assets/references/best-practices.md`

2. Read relevant reference document

3. Provide explanation with examples from templates

4. Link to EdgeDelta documentation when appropriate:
   - Main docs: https://docs.edgedelta.com/
   - Pipeline v3: https://docs.edgedelta.com/configuration-v3
   - Processors: https://docs.edgedelta.com/processors
   - OTTL: https://docs.edgedelta.com/ottl

5. Offer to create example configuration

## Credential Management

Check for credentials in this order:
1. User provides directly
2. `~/.edgedelta.env or project .env file`
3. Environment variables: `ED_ORG_ID`, `ED_ORG_API_TOKEN`
4. Prompt user with instructions to get from https://app.edgedelta.com

## Technical Details

### Modern Architecture (v3)
All pipelines use **sequence architecture**:
- Input → Sequence (processors) → Output
- NO standalone processors (legacy)
- Only 23 processors are sequence-compatible (see references)

### Required Components
Every pipeline MUST have:
- `version: v3`
- `ed_self_telemetry_input` node
- At least one output (usually `ed_output`)

### YAML Formatting Rules
- Nodes/links list items: `-` at column 0 (NO indentation)
- Node properties: 2-space indentation
- Sequence processors: Listed under `processors:` key
- Processor properties: Proper nesting (see templates)

### Common Patterns

**PII Masking**:
```yaml
- type: generic_mask
  capture_group_masks:
    - capture_group: "(?i)(password|passwd|pwd)[:=]\\S+"
      enabled: true
      mask: "***PASSWORD***"
      name: "password"
```

**Metric Extraction**:
```yaml
- type: extract_metric
  extract_metric_rules:
    - name: "errors_total"
      unit: "1"
      conditions:
        - 'IsMatch(body, "(?i)ERROR")'
      sum:
        aggregation_temporality: delta
        is_monotonic: true
        value: 1
  interval: 1m
  final: true
```

**OTTL Transform**:
```yaml
- type: ottl_transform
  statements: |
    set(attributes["processed"], "true")
    set(attributes["timestamp"], Now())
```

### Known Issues to Avoid

❌ `persisting_cursor_settings` - causes API 500 errors
❌ Unicode in YAML comments (→, ✓, ✗) - API rejects
❌ `json_field_path: "."` - must use `"$"` instead
❌ Multiple `final: true` flags - only last processor
❌ Non-sequence processors in sequences - see compatibility list

## Script Usage

### Validation
```bash
python3 assets/scripts/validate_pipeline.py <pipeline.yaml> [--verbose]
```

### Deployment - Create NEW Pipeline
```bash
# With credentials directly
python3 assets/scripts/deploy_pipeline.py <pipeline.yaml> <org_id> <api_token> [Linux|Windows|Kubernetes]

# With .env file
python3 assets/scripts/deploy_pipeline.py <pipeline.yaml> --env-file <path> [environment]
```

### Deployment - Update EXISTING Pipeline
```bash
# With credentials directly
python3 assets/scripts/deploy_pipeline.py <pipeline.yaml> --pipeline-id <conf_id> <org_id> <api_token>

# With .env file
python3 assets/scripts/deploy_pipeline.py <pipeline.yaml> --pipeline-id <conf_id> --env-file <path>
```

**Important**: When updating an existing pipeline, use the `--pipeline-id` flag with the pipeline's `conf_id` (UUID). The tag in the YAML should match the existing pipeline's tag.

### Environment Inspection
```bash
python3 assets/scripts/inspect_environment.py [--verbose] [--format json|markdown]
```

### Pipeline Builder
```bash
python3 assets/scripts/pipeline_builder.py --config <spec.json> --output <pipeline.yaml>
```

## Progressive Disclosure

- **Level 1**: Use templates for common cases (fastest)
- **Level 2**: Customize templates for specific needs
- **Level 3**: Build from scratch with environment inspection
- **Level 4**: Advanced patterns from reference docs

## Success Criteria

- Quick deployments in <2 minutes using templates
- Environment inspection surfaces all monitoring opportunities
- Validation catches all EdgeDelta errors before API submission
- All generated pipelines use modern sequence architecture
- Users understand the "why" behind configurations

## Example Interactions

**User**: "I need to collect application logs and mask sensitive data"
**Assistant**: Uses Workflow 1, suggests Template 1, customizes for user's paths

**User**: "What can I monitor in my Kubernetes cluster?"
**Assistant**: Uses Workflow 4, runs inspect_environment.py, presents K8s findings

**User**: "This pipeline YAML isn't working"
**Assistant**: Uses Workflow 3, validates, explains errors, offers fixes

**User**: "How do I extract metrics from logs?"
**Assistant**: Uses Workflow 5, shows extract_metric examples, references docs

## Cross-Skill Integration

### Using edgedelta-reference Skill

**When**: User asks about specific processors, needs processor syntax, or wants processor specifications

**The `edgedelta-reference` skill provides**:
- Quick Copy snippets for all 23 sequence-compatible processors
- Detailed documentation for generic_mask, extract_metric, ottl_transform, json_unroll
- Processor parameter specifications
- Common pitfalls and validation rules

**How to use**:

**Example 1: User asks about a processor during pipeline building**
```
User: "I need to mask credit cards in the logs"
Assistant: [Activates edgedelta-reference skill]
→ Reads MASTER_INDEX.md for generic_mask
→ Returns Quick Copy snippet with credit card regex
→ Incorporates into pipeline sequence
```

**Example 2: User needs processor specifications**
```
User: "What parameters does extract_metric support?"
Assistant: [Activates edgedelta-reference skill]
→ Reads references/processors/extract_metric.md
→ Provides parameter table and examples
→ Helps user build extract_metric configuration
```

**Example 3: Troubleshooting processor issues**
```
User: "My json_unroll is failing with 'path cannot start with dot'"
Assistant: [Activates edgedelta-reference skill]
→ Reads json_unroll.md Common Pitfalls section
→ Identifies issue and provides fix
→ Updates pipeline configuration
```

**Quick Reference Pattern**:
- For processor syntax → use `edgedelta-reference` MASTER_INDEX.md
- For detailed processor help → use `edgedelta-reference` detailed references
- For complete pipeline deployment → continue with this skill

**Complementary Workflow**:
1. This skill (edgedelta-pipelines): Template selection, environment inspection
2. edgedelta-reference: Processor specifications and syntax lookups
3. edgedelta-ottl: OTTL function reference (for ottl_transform/ottl_filter processors)
4. This skill: Validation and deployment

## When NOT to Use This Skill

- EdgeDelta dashboard operations → use `edgedelta-dashboards` skill
- Processor reference lookups → use `edgedelta-reference` skill
- OTTL function syntax or reference → use `edgedelta-ottl` skill
- OTTL statement validation → use `edgedelta-ottl` skill
- General observability questions without EdgeDelta context
- Log analysis or querying (not pipeline creation)

---

You have comprehensive templates, validation tools, and automation scripts. Guide users confidently through pipeline creation, always validating before deployment, and leveraging the tested templates whenever possible. Use the `edgedelta-reference` skill for detailed processor specifications and syntax lookups. Use the `edgedelta-ottl` skill for OTTL function reference when building ottl_transform or ottl_filter processors.
