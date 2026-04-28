"""Sensitive HR topic preflight for CivicHR."""

from dataclasses import dataclass

LEGAL_MARKERS = ("fmla", "ada", "termination", "discipline", "harassment", "discrimination")
PERSONNEL_MARKERS = ("ssn", "medical", "background", "salary", "disciplinary", "personnel_file")


@dataclass(frozen=True)
class SensitiveFinding:
    topic: str
    category: str
    required_action: str


@dataclass(frozen=True)
class SensitiveReview:
    safe_for_self_service: bool
    findings: tuple[SensitiveFinding, ...]
    message: str


def review_hr_topic(topic: str, context_terms: list[str] | None = None) -> SensitiveReview:
    """Flag HR topics that require HR/counsel review before staff-facing use."""

    terms = " ".join([topic, *(context_terms or [])]).lower()
    findings: list[SensitiveFinding] = []
    if any(marker in terms for marker in LEGAL_MARKERS):
        findings.append(SensitiveFinding(topic=topic, category="employment-law", required_action="Route to HR/counsel for review."))
    if any(marker in terms for marker in PERSONNEL_MARKERS):
        findings.append(SensitiveFinding(topic=topic, category="personnel-data", required_action="Do not include personnel files or protected data in CivicHR prompts."))
    return SensitiveReview(
        safe_for_self_service=not findings,
        findings=tuple(findings),
        message="HR/counsel review required before use." if findings else "No sensitive marker detected; HR approval is still required before publication.",
    )
