# CivicHR Agent Instructions

CivicHR supports municipal HR policy work without becoming an HRIS. Keep v0.1.1 honest: it drafts outlines and checklists from HR-approved source titles, but it does not make employment-law decisions, track cases, ingest personnel files, or connect to HR/payroll systems.

Run before push or release:

```bash
python -m pytest -q
bash scripts/verify-docs.sh
python scripts/check-civiccore-placeholder-imports.py
python -m ruff check .
bash scripts/verify-release.sh
```

CivicHR may depend on `civiccore==0.3.0`. CivicCore must never import CivicHR. Do not import from CivicCore placeholder packages.
