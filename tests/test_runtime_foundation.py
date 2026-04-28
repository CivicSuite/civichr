from fastapi.testclient import TestClient

from civichr import __version__
from civichr.main import app

client = TestClient(app)

def test_root_reports_honest_current_state():
    payload = client.get("/").json()
    assert payload["name"] == "CivicHR"
    assert payload["version"] == __version__
    assert payload["status"] == "HR policy foundation"
    assert "HRIS" in payload["message"]
    assert "not implemented yet" in payload["message"]

def test_health_reports_civiccore_pin():
    payload = client.get("/health").json()
    assert payload == {"status":"ok","service":"civichr","version":"0.1.1","civiccore_version":"0.3.0"}

def test_public_ui_contains_version_boundaries_and_dependency():
    text = client.get("/civichr").text
    assert "CivicHR v0.1.1" in text
    assert "No HRIS" in text
    assert "civiccore==0.3.0" in text

def test_api_endpoints_return_deterministic_payloads():
    assert client.post("/api/v1/civichr/policy-lookup", json={"question":"vacation accrual","policy_titles":["Policy 4"]}).status_code == 200
    assert client.post("/api/v1/civichr/job-description", json={"title":"Planner I","department":"Planning","duties":["Review permits"]}).json()["not_a_classification_decision"] is True
    assert client.post("/api/v1/civichr/onboarding-packet", json={"role_title":"Clerk","department":"Admin","required_forms":["I-9"]}).status_code == 200
    assert client.post("/api/v1/civichr/source-review", json={"source_titles":["Handbook"],"approved_by_hr":False}).json()["ready_for_drafting"] is False
    assert client.post("/api/v1/civichr/sensitive-review", json={"topic":"ADA accommodation","context_terms":[]}).json()["safe_for_self_service"] is False
    assert client.post("/api/v1/civichr/handbook-summary", json={"topic":"Leave","source_title":"Handbook","policy_points":["Accrual is monthly."]}).status_code == 200
    assert client.post("/api/v1/civichr/classification-lookup", json={"position_title":"Planner I","classification":"Class 22","salary_schedule_reference":"Schedule A"}).json()["not_a_compensation_decision"] is True
    assert client.post("/api/v1/civichr/training-checklist", json={"role_title":"Clerk","requirements":["Records"]}).status_code == 200
    assert client.post("/api/v1/civichr/intake-template", json={"template_type":"complaint"}).status_code == 200
