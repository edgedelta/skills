# EdgeDelta Skills

Official EdgeDelta skills for Claude Code, claude.ai, and the Anthropic API.

This repository follows the [Agent Skills](https://agentskills.io) open standard for AI agent skills.

## Installation

### Claude Code Plugin (Recommended)

```bash
# From marketplace (when published)
/plugin marketplace add edgedelta/skills

# From local path (for development)
/plugin install /path/to/edgedelta-skills
```

### Manual Installation

```bash
# Clone to personal skills directory
git clone https://github.com/edgedelta/skills ~/.claude/skills/edgedelta
```

### Project-level

```bash
# Add as submodule
git submodule add https://github.com/edgedelta/skills .claude/skills/edgedelta
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [`edgedelta-pipelines`](skills/edgedelta-pipelines/) | Create, validate, and deploy EdgeDelta pipeline v3 configurations with 7 production-tested templates |

### edgedelta-pipelines

Expert skill for EdgeDelta pipeline management. Features include:

- **7 Production Templates**: Log ingestion, OTLP receivers, mixed telemetry, API polling, Prometheus scraping, lookup enrichment
- **Pipeline Validation**: Check configurations against EdgeDelta v3 rules before deployment
- **Direct Deployment**: Deploy pipelines via EdgeDelta API
- **Environment Inspection**: Discover monitoring opportunities in K8s/Linux/Windows
- **Interactive Builder**: Build custom pipelines step-by-step

**Trigger phrases**: "create a pipeline", "EdgeDelta config", "validate my pipeline", "deploy to EdgeDelta", "what can I monitor"

## Upcoming Skills

| Skill | Description | Status |
|-------|-------------|--------|
| `metric-cardinality` | Analyze metric cardinality and recommend optimizations | Planned |
| `metric-aggregation` | Configure aggregation pipelines to reduce data volume | Planned |
| `log-to-patterns` | Convert raw logs into patterns for efficient storage | Planned |

### Planned Skill Categories

| Category | Examples | Status |
|----------|----------|--------|
| Pipelines | Creating, validating, deploying pipeline configs | **Available** |
| Dashboards | Building monitoring dashboards | Planned |
| OTTL | OTTL function references and transformations | Planned |
| Metrics | Cardinality analysis, aggregation, optimization | Planned |
| Logs | Log parsing, pattern detection | Planned |
| Integrations | Splunk, Prometheus, cloud provider setup | Planned |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on creating and submitting skills.

## Repository Structure

```
edgedelta-skills/
├── .claude-plugin/
│   └── plugin.json          # Plugin configuration
├── skills/
│   ├── TEMPLATE/            # Template for new skills
│   │   └── SKILL.md
│   └── edgedelta-pipelines/ # Pipeline creation and deployment
│       ├── SKILL.md
│       └── assets/          # Templates, scripts, references
├── spec/
│   └── SKILL_SPEC.md        # Skill authoring guidelines
├── examples/
│   └── README.md            # Example patterns
├── scripts/
│   └── validate-skill.sh    # Validation script
├── CONTRIBUTING.md
├── LICENSE                  # Apache 2.0
└── README.md
```

## Resources

- [Agent Skills Standard](https://agentskills.io)
- [Claude Code Skills Documentation](https://docs.anthropic.com/en/docs/claude-code/skills)
- [EdgeDelta Documentation](https://docs.edgedelta.com)

## License

Apache 2.0 - See [LICENSE](LICENSE)
