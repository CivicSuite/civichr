# CivicHR

CivicHR is the CivicSuite internal HR policy support module. Version 0.1.1 ships a local package, FastAPI runtime, deterministic helpers, optional database-backed HR workpapers, tests, release gates, public documentation, and browser-verified sample UI for HR policy support without becoming an HRIS.

## Shipping in v0.1.1

- Personnel-policy lookup outlines against HR-approved source titles.
- Employee handbook plain-language summary drafts.
- Job-description draft scaffolds from role context.
- Optional SQLAlchemy-backed job-description and onboarding-packet workpaper records through `CIVICHR_WORKPAPER_DB_URL`.
- Salary schedule and position-classification reference lookup.
- Onboarding packet and training requirement checklists.
- Grievance/complaint intake templates only.
- HR source-readiness review and sensitive-topic preflight.

## Not shipped yet

- HRIS, payroll, benefits administration, or personnel records management.
- Employment-law advice, eligibility decisions, discipline recommendations, or autonomous HR determinations.
- Grievance/complaint case tracking.
- Personnel-file ingestion, PHI storage, background-check storage, or compensation-sensitive record storage.
- Live LLM calls, cloud AI, or external HR/payroll connector runtime.

## Install and run locally

CivicHR v0.1.1 is pinned to `civiccore==0.3.0`.

```bash
python -m venv .venv
. .venv/Scripts/activate
python -m pip install -e ".[dev]"
python -m uvicorn civichr.main:app --host 127.0.0.1 --port 8138
```

Open `http://127.0.0.1:8138/civichr` for the browser sample and `http://127.0.0.1:8138/docs` for FastAPI docs.

Set `CIVICHR_WORKPAPER_DB_URL` to persist job-description drafts and onboarding packets. Without it, CivicHR remains deterministic and stateless.

## Verification

```bash
python -m pytest -q
bash scripts/verify-docs.sh
python scripts/check-civiccore-placeholder-imports.py
python -m ruff check .
bash scripts/verify-release.sh
```

## Licensing

Code is Apache 2.0. Documentation is CC BY 4.0 unless otherwise noted. CivicHR is designed for local municipal operation and does not require outbound runtime calls in the default profile.
