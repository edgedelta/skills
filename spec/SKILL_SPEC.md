# EdgeDelta Skill Specification

Guidelines for authoring skills in the EdgeDelta Skills repository.

## Overview

Skills are markdown files that provide AI agents with domain-specific knowledge and workflows. Each skill follows the [Agent Skills](https://agentskills.io) standard with EdgeDelta-specific conventions.

## File Structure

### Required

```
skills/skill-name/
└── SKILL.md              # Main skill definition
```

### Optional

```
skills/skill-name/
├── SKILL.md              # Main skill definition
├── examples/             # Example inputs/outputs
│   └── example-1.md
└── reference/            # Additional reference material
    └── detailed-guide.md
```

## SKILL.md Format

### Frontmatter (Required)

```yaml
---
name: skill-name
description: Third-person description with trigger phrases
---
```

**Name Requirements:**
- Lowercase letters and hyphens only
- Use gerund (`processing-logs`) or action form (`analyze-metrics`)
- Be specific: `metric-cardinality-analyzer` not `metrics`

**Description Requirements:**
- Third person: "Analyzes..." not "Analyze..."
- Include trigger phrases: "Use when users need to..."
- Mention key capabilities
- Under 200 characters recommended

### Content Guidelines

**Length:**
- Keep SKILL.md under 500 lines
- Use progressive disclosure for complex topics
- Link to separate files in `reference/` for detailed content

**Structure:**
```markdown
# Skill Name

Brief overview (1-2 sentences)

## When to Use

Bullet list of trigger conditions

## Instructions

Step-by-step workflow for the agent

## Examples

Concrete examples with expected behavior

## Reference

Links to documentation

## Notes

Limitations, edge cases, considerations
```

## EdgeDelta-Specific Patterns

### OTTL References

When skills involve OTTL transformations:
- Link to OTTL function reference
- Provide syntax examples
- Include common patterns

### Pipeline Validation

For pipeline-related skills:
- Include validation steps
- Reference schema requirements
- Provide error handling guidance

### API Interactions

When skills use EdgeDelta APIs:
- Document required endpoints
- Include authentication notes
- Handle rate limiting

## Testing Requirements

Test each skill with:

1. **Haiku**: Verify basic functionality
2. **Sonnet**: Verify balanced performance
3. **Opus**: Verify complex reasoning

### Test Checklist

- [ ] Skill triggers on expected prompts
- [ ] Instructions are clear and actionable
- [ ] Examples produce expected outputs
- [ ] Edge cases are handled
- [ ] Links are valid
- [ ] No hallucinated capabilities

## Validation

Run the validation script before submitting:

```bash
./scripts/validate-skill.sh skills/your-skill-name
```

The script checks:
- SKILL.md exists
- Required frontmatter fields present
- Name follows conventions
- Description is non-empty

## Best Practices

### Do

- Be concise and specific
- Include concrete examples
- Reference official documentation
- Test with multiple models
- Handle errors gracefully

### Don't

- Include sensitive information
- Make assumptions about user environment
- Exceed 500 lines without progressive disclosure
- Use unclear or ambiguous instructions
- Claim capabilities that don't exist

## Version Control

- One skill per directory
- Meaningful commit messages
- Document breaking changes
- Use semantic versioning for major updates

## Resources

- [Agent Skills Standard](https://agentskills.io)
- [Claude Code Skills Docs](https://docs.anthropic.com/en/docs/claude-code/skills)
- [EdgeDelta Documentation](https://docs.edgedelta.com)
