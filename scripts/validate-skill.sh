#!/usr/bin/env bash
#
# Validates an EdgeDelta skill directory
#
# Usage: ./scripts/validate-skill.sh skills/skill-name
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}ERROR${NC}: $1"
    ((ERRORS++))
}

warn() {
    echo -e "${YELLOW}WARNING${NC}: $1"
    ((WARNINGS++))
}

success() {
    echo -e "${GREEN}OK${NC}: $1"
}

info() {
    echo -e "INFO: $1"
}

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <skill-directory>"
    echo "Example: $0 skills/metric-cardinality"
    exit 1
fi

SKILL_DIR="$1"
SKILL_FILE="$SKILL_DIR/SKILL.md"

echo "Validating skill: $SKILL_DIR"
echo "========================================"

# Check directory exists
if [ ! -d "$SKILL_DIR" ]; then
    error "Skill directory does not exist: $SKILL_DIR"
    exit 1
fi

# Check SKILL.md exists
if [ ! -f "$SKILL_FILE" ]; then
    error "SKILL.md not found in $SKILL_DIR"
    exit 1
fi
success "SKILL.md exists"

# Read SKILL.md content
CONTENT=$(cat "$SKILL_FILE")

# Check for frontmatter
if ! echo "$CONTENT" | head -1 | grep -q '^---$'; then
    error "Missing frontmatter (file must start with ---)"
else
    success "Frontmatter detected"
fi

# Extract frontmatter
FRONTMATTER=$(echo "$CONTENT" | sed -n '/^---$/,/^---$/p' | sed '1d;$d')

# Check for name field
if echo "$FRONTMATTER" | grep -q '^name:'; then
    NAME=$(echo "$FRONTMATTER" | grep '^name:' | sed 's/name:[[:space:]]*//')

    # Validate name format (lowercase, hyphens only)
    if echo "$NAME" | grep -qE '^[a-z][a-z0-9-]*$'; then
        success "Name follows conventions: $NAME"
    else
        error "Name must be lowercase with hyphens only: $NAME"
    fi

    # Check name matches directory
    DIR_NAME=$(basename "$SKILL_DIR")
    if [ "$NAME" != "$DIR_NAME" ] && [ "$DIR_NAME" != "TEMPLATE" ]; then
        warn "Name '$NAME' does not match directory '$DIR_NAME'"
    fi
else
    error "Missing 'name' field in frontmatter"
fi

# Check for description field
if echo "$FRONTMATTER" | grep -q '^description:'; then
    DESCRIPTION=$(echo "$FRONTMATTER" | grep '^description:' | sed 's/description:[[:space:]]*//')

    if [ -n "$DESCRIPTION" ]; then
        success "Description present"

        # Check description length
        DESC_LEN=${#DESCRIPTION}
        if [ "$DESC_LEN" -gt 200 ]; then
            warn "Description is long ($DESC_LEN chars). Consider shortening to under 200."
        fi

        # Check for third person
        if echo "$DESCRIPTION" | grep -qiE '^(Use|Create|Build|Make|Do|Run)'; then
            warn "Description should be third person ('Analyzes...' not 'Analyze...')"
        fi
    else
        error "Description is empty"
    fi
else
    error "Missing 'description' field in frontmatter"
fi

# Check content length
LINE_COUNT=$(wc -l < "$SKILL_FILE" | tr -d ' ')
if [ "$LINE_COUNT" -gt 500 ]; then
    warn "SKILL.md has $LINE_COUNT lines. Consider using progressive disclosure (recommended: <500 lines)"
else
    success "Content length acceptable: $LINE_COUNT lines"
fi

# Check for common sections
if echo "$CONTENT" | grep -q '^## When to Use'; then
    success "Has 'When to Use' section"
else
    warn "Missing 'When to Use' section (recommended)"
fi

if echo "$CONTENT" | grep -q '^## Instructions\|^## Steps\|^## Workflow'; then
    success "Has instructions section"
else
    warn "Missing instructions section (recommended)"
fi

# Summary
echo ""
echo "========================================"
echo "Validation complete"
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}FAILED${NC}: Fix errors before submitting"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}PASSED with warnings${NC}"
    exit 0
else
    echo -e "${GREEN}PASSED${NC}"
    exit 0
fi
