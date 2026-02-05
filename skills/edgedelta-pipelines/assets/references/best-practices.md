# EdgeDelta Pipeline Best Practices

## Architecture Patterns

### 1. Always Use Sequences
✓ Modern approach - use `sequence` nodes for all processing
✗ Avoid standalone processors (legacy)

### 2. Sequence Architecture
```
Input → Sequence (processors) → Output
```

Example:
```yaml
file_input → sequence (mask + extract) → ed_output
```

### 3. Parallel Processing for Different Data Types
```
logs_input → log_sequence → output
metrics_input → metric_sequence → output
```

### 4. Multi-Source Aggregation
```
api1 → sequence1 ─┐
api2 → sequence2 ─┼→ aggregator_sequence → output
api3 → sequence3 ─┘
```

## Processor Ordering

### Recommended Order:
1. **Filtering** - Remove unwanted data early
2. **Parsing** - Extract fields
3. **Masking** - Remove sensitive data
4. **Enrichment** - Add context
5. **Sampling** - Reduce volume
6. **Metrics** - Extract metrics (usually last)

Example:
```yaml
processors:
  - type: regex_filter        # 1. Filter
  - type: ottl_transform      # 2. Parse/extract
  - type: generic_mask        # 3. Mask PII
  - type: ottl_transform      # 4. Enrich
  - type: sample              # 5. Sample
  - type: extract_metric      # 6. Metrics
    final: true
```

## Performance Optimization

### 1. Filter Early
Remove unnecessary data at the beginning of sequences to reduce processing.

### 2. Batch Operations
For API pulls, use appropriate `pull_interval` to balance freshness vs API load.

### 3. Sampling
Use `sample` processor to reduce data volume while maintaining statistical validity.

### 4. Avoid Excessive Masking
Combine multiple masks into fewer processors when possible.

## Security & Compliance

### 1. Always Mask PII
Use `generic_mask` for:
- Passwords
- Credit cards
- SSNs
- API tokens
- Email addresses

### 2. Mask Before Transmission
Apply masking processors BEFORE sending to outputs.

### 3. Test Masking Patterns
Verify regex patterns catch all variations:
```yaml
# Good - catches multiple formats
capture_group: "(?i)(password|passwd|pwd)[:=]\\S+"

# Bad - too specific
capture_group: "password:"
```

## Naming Conventions

### Nodes
- Use descriptive names: `app_logs`, `error_processing`, `pii_masking`
- Avoid generic names: `input1`, `processor1`
- Use underscores, not hyphens or spaces

### Tags
- Include environment: `prod-app-logs`, `dev-metrics`
- Include purpose: `log-ingestion`, `api-enrichment`
- Use lowercase with hyphens

## Error Handling

### 1. Add Telemetry
Always include `ed_self_telemetry_input` to monitor pipeline health.

### 2. Use Conditions
Add OTTL conditions to handle edge cases:
```yaml
set(attributes["field"], "default") where attributes["field"] == nil
```

### 3. Test with Real Data
Validate pipelines with actual log samples before production deployment.

## Documentation

### 1. Add user_description
```yaml
- name: pii_processor
  type: sequence
  user_description: Mask PII and extract security metrics
```

### 2. Comment Complex Logic
Use YAML comments for complex OTTL statements:
```yaml
# Extract hostname from syslog header
set(cache["hostname"], EDXExtractPatterns(body, "pattern"))
```

### 3. Keep Configuration in Version Control
Store pipeline YAMLs in git for tracking changes.

## Testing Workflow

1. **Local Validation**: Run `validate_pipeline.py`
2. **Dry Run**: Deploy to test org/environment
3. **Sample Data**: Test with representative log samples
4. **Monitor**: Check EdgeDelta UI for errors
5. **Iterate**: Adjust based on actual behavior

## Common Anti-Patterns to Avoid

❌ **Using persisting_cursor_settings** - Causes API errors
❌ **Unicode in comments** - API rejects
❌ **Multiple final flags** - Invalid configuration
❌ **Standalone processors** - Use sequences instead
❌ **Missing telemetry input** - Pipeline won't validate
❌ **Circular links** - Creates infinite loops
❌ **Generic node names** - Hard to debug
❌ **No PII masking** - Compliance risk
❌ **Hardcoded credentials** - Security risk

## Template Selection Guide

Choose the right template for your use case:

- **Template 1**: File logs with PII compliance needs
- **Template 2**: OpenTelemetry/OTLP data collection
- **Template 3**: Mixed logs + metrics
- **Template 4**: REST API polling (CMDB, inventory)
- **Template 5**: Multiple API sources with aggregation
- **Template 6**: Prometheus metrics scraping from exporters
- **Template 7**: Log enrichment with CSV/DB lookups and routing
