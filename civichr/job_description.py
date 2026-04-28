"""Job-description drafting support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobDescriptionDraft:
    title: str
    department: str
    sections: tuple[str, ...]
    required_reviews: tuple[str, ...]
    not_a_classification_decision: bool


def draft_job_description(title: str, department: str, duties: list[str]) -> JobDescriptionDraft:
    """Create a staff-reviewable job-description outline from role context."""

    duty_lines = tuple(f"Duty: {duty.strip()}" for duty in duties if duty.strip()) or ("Duty list requires HR input.",)
    return JobDescriptionDraft(
        title=title.strip(),
        department=department.strip(),
        sections=("Role summary requires HR approval.", *duty_lines, "Equal opportunity language requires HR/counsel review."),
        required_reviews=("HR", "department head", "legal/counsel if employment-law language is present"),
        not_a_classification_decision=True,
    )
