# Sequence-Compatible Processors

Only these 23 processors can be used inside `sequence` nodes (from sequence_node.go:52-76):

## Transformation & Filtering

- **ottl_transform** - OpenTelemetry Transformation Language for attribute manipulation
- **attribute_filter** - Filter data based on attributes
- **regex_filter** - Filter using regular expressions
- **regex_based_log_parser** - Parse logs with regex patterns
- **stateful_where** - Stateful filtering with conditions

## Masking & Privacy

- **generic_mask** - Mask sensitive data with regex patterns
- **delete_empty_values** - Remove empty attributes/fields

## Sampling & Throttling

- **sample** - Sample data at specified percentage
- **sampling** - Advanced sampling processor
- **throttle** - Rate limit data flow

## Metrics & Signals

- **extract_metric** - Extract metrics from logs/traces
- **log_to_metric** - Convert logs to metrics
- **metric_to_metric** - Transform metrics
- **log_to_signal** - Convert logs to signals
- **log_to_pattern_metric** - Pattern-based metric extraction

## Data Conversion

- **log_to_log** - Transform log data
- **metric_to_log** - Convert metrics to logs
- **trace_to_log** - Convert traces to logs
- **trace_to_trace** - Transform trace data
- **json_unroll** - Unroll JSON arrays into individual events

## Deduplication

- **dedup** - Remove duplicate entries

## OpenTelemetry

- **deotel** - DeOTEL processor (must be LAST in sequence if used)

## External Calls

- **http_request_call** - Make HTTP requests from pipeline

## Usage Notes

- Processors must be listed under `processors:` key in sequence node
- Mark the last processor with `final: true`
- If using `deotel`, it MUST be the last processor
- Nested sequences cannot use `final: true`
