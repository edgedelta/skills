# Changelog - edgedelta-pipelines

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-02-03

### Added
- **Update Existing Pipeline Support**: New `--pipeline-id` flag in `deploy_pipeline.py` to update existing pipelines instead of creating new ones
- **Workflow 5: Update Existing Pipeline** in SKILL.md documenting the process
- Direct API deployment documentation for when MCP tools are available

### Fixed
- **Critical Bug**: `deploy_pipeline.py` was using wrong field name `lastUpdated` instead of `timestamp` from history API response
- **Validation False Positives**: `validate_pipeline.py` now correctly allows nested `sequence`, `comment`, `aggregate_metric`, and `ottl_filter` processor types that are valid in production
- **Credential Variable**: Added `ED_API_TOKEN` as recognized credential variable (in addition to `ED_ORG_API_TOKEN`)

### Changed
- Version updated to 2.2.0 with new last_updated date
- Workflow numbering updated (Template Reference is now Workflow 6)

## [2.1.0] - 2025-10-19

### Added
- Template 7: Lookup Enrichment pipeline
  - CSV and database lookup support
  - Conditional routing based on enrichment
  - Compound node architecture
  - Validation for enrichment matching
- Template 6: Prometheus Metrics Scraper
  - Multi-target scraping support
  - Relabel configurations
  - Cluster monitoring patterns
- Performance instrumentation in validation scripts
- Versioning in SKILL.md frontmatter
- SECURITY.md documentation

### Features (Current)
- 7 production-tested templates:
  1. Log Ingestion with PII Masking
  2. OTLP Dual Receiver (gRPC + HTTP)
  3. Mixed Telemetry Processing
  4. API Pull with JSON Processing
  5. Multi-API with Aggregation
  6. Prometheus Metrics Scraper ✨ NEW
  7. Lookup Enrichment ✨ NEW

### Scripts
- `validate_pipeline.py` - Comprehensive pipeline validation
- `deploy_pipeline.py` - Direct deployment via EdgeDelta API
- `inspect_environment.py` - Environment scanning for monitoring opportunities
- `pipeline_builder.py` - Interactive pipeline construction

### Documentation
- 3 reference documents (validation-rules, best-practices, sequence-processors)
- Templates summary with use cases
- Cross-skill integration with edgedelta-reference

## [2.0.0] - 2025-10-15

### Added
- Initial release with 5 templates
- YAML validation before deployment
- Direct API deployment support
- Environment inspection capabilities

### Changed
- Migrated to EdgeDelta v3 pipeline format
- Updated processor compatibility list (23 sequence processors)
- Improved error messages in validation

### Breaking Changes
- Dropped support for EdgeDelta v2 pipelines
- Changed credential handling (environment variables required)

## [1.0.0] - Initial

### Added
- First production release
- Basic template support
- Manual deployment workflow
