"""FastAPI runtime foundation for CivicHR."""

import os

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civichr import __version__
from civichr.classification_lookup import lookup_classification
from civichr.handbook_summary import draft_handbook_summary
from civichr.intake_templates import draft_intake_template
from civichr.job_description import draft_job_description
from civichr.onboarding import build_onboarding_packet
from civichr.persistence import HRWorkpaperRepository, StoredJobDescription, StoredOnboardingPacket
from civichr.policy_lookup import draft_policy_lookup
from civichr.public_ui import render_public_lookup_page
from civichr.sensitive_review import review_hr_topic
from civichr.source_review import review_hr_sources
from civichr.training_requirements import build_training_checklist

app = FastAPI(title="CivicHR", version=__version__, description="Personnel-policy lookup, job-description drafts, onboarding packet checklists, and HR knowledge support for CivicSuite.")

_workpaper_repository: HRWorkpaperRepository | None = None
_workpaper_db_url: str | None = None

@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Return an empty favicon response so browser QA has a clean console."""

    return Response(status_code=204)

class PolicyLookupRequest(BaseModel):
    question: str
    policy_titles: list[str]
class JobDescriptionRequest(BaseModel):
    title: str
    department: str
    duties: list[str]
class OnboardingRequest(BaseModel):
    role_title: str
    department: str
    required_forms: list[str]
class SourceReviewRequest(BaseModel):
    source_titles: list[str]
    approved_by_hr: bool = False
class SensitiveReviewRequest(BaseModel):
    topic: str
    context_terms: list[str] = []
class HandbookSummaryRequest(BaseModel):
    topic: str
    source_title: str
    policy_points: list[str]
class ClassificationLookupRequest(BaseModel):
    position_title: str
    classification: str
    salary_schedule_reference: str
class TrainingChecklistRequest(BaseModel):
    role_title: str
    requirements: list[str]
class IntakeTemplateRequest(BaseModel):
    template_type: str

@app.get("/")
def root() -> dict[str, str]:
    return {"name":"CivicHR","version":__version__,"status":"HR policy foundation plus workpaper persistence","message":"CivicHR package, API foundation, personnel-policy lookup outlines, handbook summaries, job-description drafts, classification lookups, onboarding checklists, optional database-backed job/onboarding workpapers, training references, intake templates, HR source review, sensitive-topic preflight, and public UI foundation are online; HRIS, payroll, benefits administration, personnel-file storage, employment-law advice, autonomous publication, live LLM calls, and external HR system integrations are not implemented yet.","next_step":"Post-v0.1.1 roadmap: HR approval queues, source connectors, and counsel review handoffs"}
@app.get("/health")
def health() -> dict[str,str]:
    return {"status":"ok","service":"civichr","version":__version__,"civiccore_version":CIVICCORE_VERSION}
@app.get("/civichr", response_class=HTMLResponse)
def public_civichr_page() -> str:
    return render_public_lookup_page()
@app.post("/api/v1/civichr/policy-lookup")
def policy_lookup(request: PolicyLookupRequest) -> dict[str, object]:
    draft=draft_policy_lookup(request.question, request.policy_titles)
    return {**draft.__dict__, "sensitive_review": {**draft.sensitive_review.__dict__, "findings": [f.__dict__ for f in draft.sensitive_review.findings]}}
@app.post("/api/v1/civichr/job-description")
def job_description(request: JobDescriptionRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        stored = _get_workpaper_repository().create_job_description(
            title=request.title,
            department=request.department,
            duties=request.duties,
        )
        return _stored_job_response(stored)
    payload = draft_job_description(request.title, request.department, request.duties).__dict__
    payload["draft_id"] = None
    return payload

@app.get("/api/v1/civichr/job-description/{draft_id}")
def get_job_description(draft_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(status_code=503, detail={"message":"CivicHR workpaper persistence is not configured.","fix":"Set CIVICHR_WORKPAPER_DB_URL to retrieve persisted job-description drafts."})
    stored = _get_workpaper_repository().get_job_description(draft_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Job-description draft record not found.","fix":"Use a draft_id returned by POST /api/v1/civichr/job-description."})
    return _stored_job_response(stored)
@app.post("/api/v1/civichr/onboarding-packet")
def onboarding_packet(request: OnboardingRequest) -> dict[str, object]:
    if _workpaper_database_url() is not None:
        stored = _get_workpaper_repository().create_onboarding_packet(
            role_title=request.role_title,
            department=request.department,
            required_forms=request.required_forms,
        )
        return _stored_onboarding_response(stored)
    payload = build_onboarding_packet(request.role_title, request.department, request.required_forms).__dict__
    payload["packet_id"] = None
    return payload

@app.get("/api/v1/civichr/onboarding-packet/{packet_id}")
def get_onboarding_packet(packet_id: str) -> dict[str, object]:
    if _workpaper_database_url() is None:
        raise HTTPException(status_code=503, detail={"message":"CivicHR workpaper persistence is not configured.","fix":"Set CIVICHR_WORKPAPER_DB_URL to retrieve persisted onboarding packets."})
    stored = _get_workpaper_repository().get_onboarding_packet(packet_id)
    if stored is None:
        raise HTTPException(status_code=404, detail={"message":"Onboarding packet record not found.","fix":"Use a packet_id returned by POST /api/v1/civichr/onboarding-packet."})
    return _stored_onboarding_response(stored)
@app.post("/api/v1/civichr/source-review")
def source_review(request: SourceReviewRequest) -> dict[str, object]:
    return review_hr_sources(request.source_titles, request.approved_by_hr).__dict__
@app.post("/api/v1/civichr/sensitive-review")
def sensitive_review(request: SensitiveReviewRequest) -> dict[str, object]:
    review=review_hr_topic(request.topic, request.context_terms)
    return {**review.__dict__, "findings": [f.__dict__ for f in review.findings]}

@app.post("/api/v1/civichr/handbook-summary")
def handbook_summary(request: HandbookSummaryRequest) -> dict[str, object]:
    return draft_handbook_summary(request.topic, request.source_title, request.policy_points).__dict__

@app.post("/api/v1/civichr/classification-lookup")
def classification_lookup(request: ClassificationLookupRequest) -> dict[str, object]:
    return lookup_classification(request.position_title, request.classification, request.salary_schedule_reference).__dict__

@app.post("/api/v1/civichr/training-checklist")
def training_checklist(request: TrainingChecklistRequest) -> dict[str, object]:
    return build_training_checklist(request.role_title, request.requirements).__dict__

@app.post("/api/v1/civichr/intake-template")
def intake_template(request: IntakeTemplateRequest) -> dict[str, object]:
    return draft_intake_template(request.template_type).__dict__

def _workpaper_database_url() -> str | None:
    return os.environ.get("CIVICHR_WORKPAPER_DB_URL")

def _get_workpaper_repository() -> HRWorkpaperRepository:
    global _workpaper_db_url, _workpaper_repository
    db_url = _workpaper_database_url()
    if db_url is None:
        raise RuntimeError("CIVICHR_WORKPAPER_DB_URL is not configured.")
    if _workpaper_repository is None or db_url != _workpaper_db_url:
        _dispose_workpaper_repository()
        _workpaper_db_url = db_url
        _workpaper_repository = HRWorkpaperRepository(db_url=db_url)
    return _workpaper_repository

def _dispose_workpaper_repository() -> None:
    global _workpaper_repository
    if _workpaper_repository is not None:
        _workpaper_repository.engine.dispose()
        _workpaper_repository = None

def _stored_job_response(stored: StoredJobDescription) -> dict[str, object]:
    return {
        "draft_id": stored.draft_id,
        "title": stored.title,
        "department": stored.department,
        "sections": list(stored.sections),
        "required_reviews": list(stored.required_reviews),
        "not_a_classification_decision": stored.not_a_classification_decision,
        "created_at": stored.created_at.isoformat(),
    }

def _stored_onboarding_response(stored: StoredOnboardingPacket) -> dict[str, object]:
    return {
        "packet_id": stored.packet_id,
        "role_title": stored.role_title,
        "department": stored.department,
        "checklist": list(stored.checklist),
        "approvals": list(stored.approvals),
        "created_at": stored.created_at.isoformat(),
    }
