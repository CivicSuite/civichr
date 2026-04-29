# Production Depth: HR Workpaper Persistence

## Summary

CivicHR now supports optional SQLAlchemy-backed job-description and onboarding-packet workpaper records through `CIVICHR_WORKPAPER_DB_URL`.

## Shipped

- `HRWorkpaperRepository` with schema-aware SQLAlchemy tables.
- Persisted job-description draft records with `draft_id`.
- Persisted onboarding-packet records with `packet_id`.
- Retrieval endpoints:
  - `GET /api/v1/civichr/job-description/{draft_id}`
  - `GET /api/v1/civichr/onboarding-packet/{packet_id}`
- Actionable `503` guidance when persistence is not configured.
- Regression tests for repository reload, API round trip, missing-record `404`, no-config `503`, and stateless fallback behavior.

## Still Not Shipped

- HRIS.
- Payroll or benefits administration.
- Personnel records management.
- Employment-law advice.
- Personnel-file ingestion.
- Live LLM calls.
