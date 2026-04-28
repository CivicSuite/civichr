CivicHR v0.1.0

CivicHR supports HR policy work without becoming an HRIS. It ships personnel-policy lookup outlines, handbook summaries, job-description drafts, classification references, onboarding and training checklists, intake templates, source review, sensitive-topic preflight, FastAPI endpoints, tests, docs, and browser QA evidence.

It does not ship payroll, benefits administration, personnel records management, employment-law advice, autonomous HR decisions, grievance case tracking, personnel-file ingestion, live LLM calls, or external HR/payroll connector runtime.

Run locally:
  python -m pip install -e ".[dev]"
  python -m uvicorn civichr.main:app --host 127.0.0.1 --port 8138

License: Apache 2.0 code, CC BY 4.0 docs.
