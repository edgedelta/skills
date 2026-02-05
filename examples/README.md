# Skill Examples

This directory contains example patterns for EdgeDelta skills.

## Example Skill Patterns

### Basic Skill

A simple skill with straightforward instructions:

```markdown
---
name: example-basic
description: Demonstrates basic skill structure. Use when learning skill authoring.
---

# Basic Example

This skill shows the minimal required structure.

## When to Use

- Learning skill authoring
- Testing skill loading

## Instructions

1. Acknowledge the skill was loaded
2. Explain what the skill does
3. Ask if the user needs help

## Notes

- This is a template example
- Not intended for production use
```

### Progressive Disclosure Pattern

For complex skills, keep the main file concise and link to details:

```markdown
---
name: example-complex
description: Demonstrates progressive disclosure. Use for complex multi-step workflows.
---

# Complex Workflow

Overview of the complex process.

## Quick Start

1. Basic step one
2. Basic step two
3. Basic step three

## Detailed Instructions

See [detailed-guide.md](reference/detailed-guide.md) for:
- Advanced configuration
- Edge case handling
- Troubleshooting

## Reference

- [Full API Reference](reference/api-reference.md)
- [Examples](examples/)
```

### Validation Pattern

Skills that validate user input:

```markdown
---
name: example-validator
description: Validates configuration files. Use when checking configs for errors.
---

# Config Validator

Validates configuration against schema.

## Instructions

1. Request the configuration from the user
2. Parse the configuration format (YAML/JSON)
3. Validate against schema
4. Report errors with line numbers
5. Suggest fixes for common issues

## Validation Rules

- Required fields: `name`, `version`
- Valid types: `string`, `number`, `boolean`
- Nested objects must have unique keys

## Error Format

```
ERROR [line:column]: description
SUGGESTION: how to fix
```
```

## EdgeDelta-Specific Patterns

### Pipeline Skill Pattern

```markdown
---
name: pipeline-builder
description: Creates EdgeDelta pipeline configurations. Use when users need to build data pipelines.
---

# Pipeline Builder

Creates validated pipeline configurations.

## Instructions

1. Identify data source type
2. Determine processing requirements
3. Generate pipeline YAML
4. Validate configuration
5. Provide deployment instructions

## Pipeline Structure

```yaml
version: v3
pipelines:
  - name: example
    inputs:
      - type: source_type
    processors:
      - type: processor_type
    outputs:
      - type: output_type
```

## Reference

- [Pipeline Documentation](https://docs.edgedelta.com/pipelines)
```

### OTTL Transformation Pattern

```markdown
---
name: ottl-transformer
description: Builds OTTL transformation expressions. Use when users need data transformations.
---

# OTTL Transformer

Creates OTTL expressions for data transformation.

## Common Patterns

### Extract Field
```ottl
set(attributes["field"], body["nested"]["field"])
```

### Conditional Transform
```ottl
set(attributes["level"], "error") where severity_number >= 17
```

## Reference

- [OTTL Functions](reference/ottl-functions.md)
- [EDX Extensions](reference/edx-functions.md)
```

## Creating New Examples

1. Add example files to this directory
2. Update this README with a description
3. Link from relevant skills
