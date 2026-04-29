from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from civichr.main import app, _dispose_workpaper_repository
from civichr.persistence import HRWorkpaperRepository


client = TestClient(app)


def test_repository_persists_job_description_and_onboarding(tmp_path: Path) -> None:
    db_path = tmp_path / "civichr.db"
    db_url = f"sqlite+pysqlite:///{db_path.as_posix()}"

    repository = HRWorkpaperRepository(db_url=db_url)
    job = repository.create_job_description(
        title="Planner I", department="Planning", duties=["Review permits"]
    )
    packet = repository.create_onboarding_packet(
        role_title="Clerk", department="Admin", required_forms=["I-9"]
    )
    repository.engine.dispose()

    reloaded = HRWorkpaperRepository(db_url=db_url)
    stored_job = reloaded.get_job_description(job.draft_id)
    stored_packet = reloaded.get_onboarding_packet(packet.packet_id)
    reloaded.engine.dispose()

    assert stored_job is not None
    assert stored_job.not_a_classification_decision is True
    assert stored_packet is not None
    assert stored_packet.approvals == ("HR", "hiring manager")
    db_path.unlink()


def test_hr_persistence_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civichr-api.db"
    monkeypatch.setenv("CIVICHR_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()

    created_job = client.post(
        "/api/v1/civichr/job-description",
        json={"title": "Planner I", "department": "Planning", "duties": ["Review permits"]},
    )
    draft_id = created_job.json()["draft_id"]
    fetched_job = client.get(f"/api/v1/civichr/job-description/{draft_id}")
    created_packet = client.post(
        "/api/v1/civichr/onboarding-packet",
        json={"role_title": "Clerk", "department": "Admin", "required_forms": ["I-9"]},
    )
    packet_id = created_packet.json()["packet_id"]
    fetched_packet = client.get(f"/api/v1/civichr/onboarding-packet/{packet_id}")

    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICHR_WORKPAPER_DB_URL")

    assert created_job.status_code == 200
    assert draft_id
    assert fetched_job.status_code == 200
    assert fetched_job.json()["not_a_classification_decision"] is True
    assert created_packet.status_code == 200
    assert packet_id
    assert fetched_packet.status_code == 200
    assert "I-9" in fetched_packet.json()["checklist"]
    db_path.unlink()


def test_get_job_without_persistence_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICHR_WORKPAPER_DB_URL", raising=False)
    _dispose_workpaper_repository()

    response = client.get("/api/v1/civichr/job-description/example")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["message"] == "CivicHR workpaper persistence is not configured."
    assert "Set CIVICHR_WORKPAPER_DB_URL" in detail["fix"]


def test_get_onboarding_missing_id_returns_actionable_404(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civichr-missing.db"
    monkeypatch.setenv("CIVICHR_WORKPAPER_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    _dispose_workpaper_repository()

    response = client.get("/api/v1/civichr/onboarding-packet/missing")

    _dispose_workpaper_repository()
    monkeypatch.delenv("CIVICHR_WORKPAPER_DB_URL")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["message"] == "Onboarding packet record not found."
    assert "POST /api/v1/civichr/onboarding-packet" in detail["fix"]
    db_path.unlink()
