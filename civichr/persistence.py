from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civichr.job_description import draft_job_description
from civichr.onboarding import build_onboarding_packet


metadata = sa.MetaData()

job_description_records = sa.Table(
    "job_description_records",
    metadata,
    sa.Column("draft_id", sa.String(36), primary_key=True),
    sa.Column("title", sa.String(255), nullable=False),
    sa.Column("department", sa.String(255), nullable=False),
    sa.Column("sections", sa.JSON(), nullable=False),
    sa.Column("required_reviews", sa.JSON(), nullable=False),
    sa.Column("not_a_classification_decision", sa.Boolean(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civichr",
)

onboarding_packet_records = sa.Table(
    "onboarding_packet_records",
    metadata,
    sa.Column("packet_id", sa.String(36), primary_key=True),
    sa.Column("role_title", sa.String(255), nullable=False),
    sa.Column("department", sa.String(255), nullable=False),
    sa.Column("checklist", sa.JSON(), nullable=False),
    sa.Column("approvals", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civichr",
)


@dataclass(frozen=True)
class StoredJobDescription:
    draft_id: str
    title: str
    department: str
    sections: tuple[str, ...]
    required_reviews: tuple[str, ...]
    not_a_classification_decision: bool
    created_at: datetime


@dataclass(frozen=True)
class StoredOnboardingPacket:
    packet_id: str
    role_title: str
    department: str
    checklist: tuple[str, ...]
    approvals: tuple[str, ...]
    created_at: datetime


class HRWorkpaperRepository:
    """SQLAlchemy-backed job-description and onboarding packet workpapers."""

    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civichr": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civichr"))
        metadata.create_all(self.engine)

    def create_job_description(
        self, *, title: str, department: str, duties: list[str]
    ) -> StoredJobDescription:
        draft = draft_job_description(title, department, duties)
        stored = StoredJobDescription(
            draft_id=str(uuid4()),
            title=draft.title,
            department=draft.department,
            sections=draft.sections,
            required_reviews=draft.required_reviews,
            not_a_classification_decision=draft.not_a_classification_decision,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                job_description_records.insert().values(
                    draft_id=stored.draft_id,
                    title=stored.title,
                    department=stored.department,
                    sections=list(stored.sections),
                    required_reviews=list(stored.required_reviews),
                    not_a_classification_decision=stored.not_a_classification_decision,
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_job_description(self, draft_id: str) -> StoredJobDescription | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(job_description_records).where(
                    job_description_records.c.draft_id == draft_id
                )
            ).mappings().first()
        if row is None:
            return None
        data = dict(row)
        return StoredJobDescription(
            draft_id=data["draft_id"],
            title=data["title"],
            department=data["department"],
            sections=tuple(data["sections"]),
            required_reviews=tuple(data["required_reviews"]),
            not_a_classification_decision=data["not_a_classification_decision"],
            created_at=data["created_at"],
        )

    def create_onboarding_packet(
        self, *, role_title: str, department: str, required_forms: list[str]
    ) -> StoredOnboardingPacket:
        packet = build_onboarding_packet(role_title, department, required_forms)
        stored = StoredOnboardingPacket(
            packet_id=str(uuid4()),
            role_title=packet.role_title,
            department=packet.department,
            checklist=packet.checklist,
            approvals=packet.approvals,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                onboarding_packet_records.insert().values(
                    packet_id=stored.packet_id,
                    role_title=stored.role_title,
                    department=stored.department,
                    checklist=list(stored.checklist),
                    approvals=list(stored.approvals),
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_onboarding_packet(self, packet_id: str) -> StoredOnboardingPacket | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(onboarding_packet_records).where(
                    onboarding_packet_records.c.packet_id == packet_id
                )
            ).mappings().first()
        if row is None:
            return None
        data = dict(row)
        return StoredOnboardingPacket(
            packet_id=data["packet_id"],
            role_title=data["role_title"],
            department=data["department"],
            checklist=tuple(data["checklist"]),
            approvals=tuple(data["approvals"]),
            created_at=data["created_at"],
        )
