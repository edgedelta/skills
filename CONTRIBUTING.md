# Contributing to EdgeDelta Skills

Thank you for your interest in contributing to EdgeDelta Skills.

## Creating a New Skill

### 1. Use the Template

Copy the template to create your skill:

```bash
cp -r skills/TEMPLATE skills/your-skill-name
```

### 2. Follow Naming Conventions

- Use lowercase with hyphens: `metric-cardinality`, `log-parser`
- Use gerund or action-oriented names: `processing-logs`, `analyze-metrics`
- Be specific and descriptive

### 3. Write Your SKILL.md

Your skill file must include:

```yaml
---
name: your-skill-name
description: Third-person description of what this skill does and when to use it
---

# Skill Title

[Instructions for the AI agent]
```

**Description Guidelines:**
- Write in third person: "Analyzes metric cardinality..." not "Analyze metric cardinality..."
- Include trigger phrases: "Use when users need to..."
- Be specific about capabilities and limitations

**Content Guidelines:**
- Keep under 500 lines (use progressive disclosure for complex skills)
- Include clear step-by-step instructions
- Provide examples where helpful
- Reference EdgeDelta documentation links

### 4. Validate Your Skill

```bash
./scripts/validate-skill.sh skills/your-skill-name
```

### 5. Test Your Skill

Test with all target models:
- Claude Haiku (fast, lightweight)
- Claude Sonnet (balanced)
- Claude Opus (complex reasoning)

Verify the skill:
- Triggers correctly based on user prompts
- Produces accurate, helpful outputs
- Handles edge cases gracefully

## Skill Structure Requirements

```
skills/your-skill-name/
└── SKILL.md              # Required: Main skill file
```

Optional additional files:
- `examples/` - Example inputs/outputs
- `reference/` - Additional reference material (linked from SKILL.md)

## Pull Request Process

1. Create a feature branch: `git checkout -b skill/your-skill-name`
2. Add your skill following the guidelines above
3. Run validation: `./scripts/validate-skill.sh skills/your-skill-name`
4. Submit PR with:
   - Description of what the skill does
   - Example use cases
   - Testing notes

## Code of Conduct

- Be respectful and constructive
- Focus on quality and accuracy
- Document your contributions clearly

## Questions?

Open an issue for:
- Clarification on guidelines
- Skill ideas or proposals
- Bug reports
