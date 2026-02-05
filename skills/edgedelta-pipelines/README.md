# EdgeDelta Pipelines Skill

Expert skill for creating, validating, and deploying EdgeDelta pipeline v3 configurations.

## Quick Start

```
Use this skill to create EdgeDelta pipelines
```

Claude will guide you through template selection, customization, validation, and deployment.

## Features

- **7 Production-Tested Templates** - Ready to deploy
- **Environment Inspection** - Discover what you can monitor (K8s/Linux/Windows)
- **Validation** - Check configurations before deployment
- **Direct Deployment** - Deploy via EdgeDelta API
- **Interactive Builder** - Build custom pipelines step-by-step

## Templates

1. **Log Ingestion with PII Masking** - Application logs with compliance
2. **OTLP Dual Receiver** - OpenTelemetry gRPC + HTTP
3. **Mixed Telemetry** - Logs + Metrics with parallel processing
4. **API Pull with JSON** - REST API polling (ServiceNow pattern)
5. **Multi-API Aggregation** - Multiple sources (Duo Security pattern)
6. **Prometheus Metrics Scraper** - Scrape Prometheus exporters
7. **Lookup Enrichment** - Enrich logs with reference data (CSV/DB lookups)

## Workflows

- **Quick Deploy**: Choose template → customize → deploy (< 2 min)
- **Environment Inspection**: Discover monitoring opportunities
- **Custom Builder**: Build from scratch with environment insights
- **Validation**: Check existing pipeline YAMLs
- **Reference**: Learn about processors, patterns, best practices

## Requirements

- EdgeDelta Organization ID
- EdgeDelta API Token (with pipeline permissions)

Get credentials from: https://app.edgedelta.com

## Architecture

All templates use modern **sequence architecture**:
```
Input → Sequence (processors) → Output
```

Only 23 processors are sequence-compatible (see references).

## Files

```
edgedelta-pipelines/
├── SKILL.md                           # Main skill prompt
├── assets/
│   ├── templates/                     # 7 tested templates
│   ├── scripts/                       # Automation tools
│   │   ├── validate_pipeline.py      # Validate YAMLs
│   │   ├── deploy_pipeline.py        # Deploy to EdgeDelta
│   │   ├── inspect_environment.py    # Discover monitoring opportunities
│   │   └── pipeline_builder.py       # Interactive builder
│   ├── references/                    # Technical documentation
│   │   ├── sequence-processors.md    # 23 compatible processors
│   │   ├── validation-rules.md       # All validation rules
│   │   └── best-practices.md         # Patterns and anti-patterns
│   └── examples/                      # Advanced examples
└── README.md                          # This file
```

## Testing Status

All 7 templates successfully tested and deployed to EdgeDelta API:
- Template 1: Log PII Masking
- Template 2: OTLP Dual
- Template 3: Mixed Telemetry
- Template 4: API JSON
- Template 5: Multi-API
- Template 6: Prometheus Scraper
- Template 7: Lookup Enrichment

**Tested on**: 2025-10-18
**Pipeline ID**: 529198b9-2486-4f5c-9d38-3c2503756ce2

## Example Usage

**Quick template deploy**:
```
Create an EdgeDelta pipeline for application logs with PII masking
```

**Environment inspection**:
```
What can I monitor in my Kubernetes cluster?
```

**Validation**:
```
Validate this EdgeDelta pipeline: /path/to/pipeline.yaml
```

**Custom build**:
```
Build a pipeline to collect logs from /var/log/nginx/*.log and extract error metrics
```

## Documentation

- EdgeDelta Docs: https://docs.edgedelta.com/
- Pipeline v3: https://docs.edgedelta.com/configuration-v3
- OTTL Reference: https://docs.edgedelta.com/ottl

## Credits

Created for comprehensive EdgeDelta pipeline management with production-tested templates and full API integration.
