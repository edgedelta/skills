# EdgeDelta Pipeline Validation Rules

## Required Fields

### Top Level
- `version: v3` - MUST be exactly "v3"
- `settings` - Configuration settings object
- `nodes` - Array of pipeline nodes
- `links` - Array of connections between nodes

### Settings
- `tag` - Pipeline identifier (string)

### Nodes
Each node MUST have:
- `name` - Unique node identifier
- `type` - Node type (input/processor/output)

### Links
Each link MUST have:
- `from` - Source node name
- `to` - Destination node name

## Required Nodes

Every pipeline MUST include:
- `ed_self_telemetry_input` - EdgeDelta self-monitoring

## Sequence Rules

1. **Processor Compatibility**: Only sequence-compatible processors allowed (see sequence-processors.md)
2. **Final Flag**: Only the LAST processor should have `final: true`
3. **DeOTEL Position**: If present, `deotel` processor MUST be last
4. **Nested Sequences**: Cannot use `final: true` on processors

## Link Rules

1. All `from` and `to` node names must reference existing nodes
2. No circular dependencies
3. At least one path from inputs to outputs

## YAML Formatting

### Node/Link Lists
- List items start at column 0: `-` (no indentation)
- Example:
  ```yaml
  nodes:
  - name: input1    # '-' at column 0
    type: file_input
  ```

### Node Properties
- 2-space indentation:
  ```yaml
  - name: my_node
    type: sequence
    user_description: Description here
  ```

### Sequence Processors
- `processors:` key at 2-space indent
- Processor list items at 2-space indent
- Processor properties at 4-space indent:
  ```yaml
  processors:
  - type: generic_mask        # 2-space indent
    capture_group_masks:      # 4-space indent
    - capture_group: "..."    # 4-space indent
  ```

## Common Validation Errors

### 1. json_field_path cannot start with "."
❌ `json_field_path: "."`
✓ `json_field_path: "$"`

### 2. Missing required node
❌ No `ed_self_telemetry_input`
✓ Always include telemetry input

### 3. Non-sequence processor in sequence
❌ `type: regex` (not sequence-compatible)
✓ `type: regex_filter` (sequence-compatible)

### 4. Multiple final flags
❌ Two processors with `final: true`
✓ Only last processor has `final: true`

### 5. DeOTEL not last
❌ `deotel` followed by other processors
✓ `deotel` is the last processor

### 6. Unicode in comments
❌ Comments with →, ✓, ✗
✓ Use ASCII characters only

### 7. persisting_cursor_settings
⚠️ May cause API 500 errors - avoid if possible

### 8. Invalid link references
❌ `from: nonexistent_node`
✓ All node names must exist

## Validation Workflow

1. **Syntax Check**: Valid YAML
2. **Schema Check**: Required fields present
3. **Reference Check**: All links valid
4. **Sequence Check**: Processors compatible
5. **Format Check**: YAML indentation correct
6. **API Test**: Deploy to EdgeDelta (optional)

Use `validate_pipeline.py` to check all rules before deployment.
