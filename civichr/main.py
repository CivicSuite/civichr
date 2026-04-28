"""FastAPI runtime foundation for CivicHR."""

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civichr import __version__
from civichr.classification_lookup import lookup_classification
from civichr.handbook_summary import draft_handbook_summary
from civichr.intake_templates import draft_intake_template
from civichr.job_description import draft_job_description
from civichr.onboarding import build_onboarding_packet
from civichr.policy_lookup import draft_policy_lookup
from civichr.public_ui import render_public_lookup_page
from civichr.sensitive_review import review_hr_topic
from civichr.source_review import review_hr_sources
from civichr.training_requirements import build_training_checklist

app = FastAPI(title="CivicHR", version=__version__, description="Personnel-policy lookup, job-description drafts, onboarding packet checklists, and HR knowledge support for CivicSuite.")

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
    return {"name":"CivicHR","version":__version__,"status":"HR policy foundation","message":"CivicHR package, API foundation, personnel-policy lookup outlines, handbook summaries, job-description drafts, classification lookups, onboarding checklists, training references, intake templates, HR source review, sensitive-topic preflight, and public UI foundation are online; HRIS, payroll, benefits administration, personnel-file storage, employment-law advice, autonomous publication, live LLM calls, and external HR system integrations are not implemented yet.","next_step":"Post-v0.1.1 roadmap: HR approval queues, source connectors, and counsel review handoffs"}
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
    return draft_job_description(request.title, request.department, request.duties).__dict__
@app.post("/api/v1/civichr/onboarding-packet")
def onboarding_packet(request: OnboardingRequest) -> dict[str, object]:
    return build_onboarding_packet(request.role_title, request.department, request.required_forms).__dict__
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
