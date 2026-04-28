"""Onboarding packet checklist support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OnboardingPacket:
    role_title: str
    department: str
    checklist: tuple[str, ...]
    approvals: tuple[str, ...]


def build_onboarding_packet(role_title: str, department: str, required_forms: list[str]) -> OnboardingPacket:
    """Build an onboarding checklist, not an HRIS workflow."""

    forms = tuple(form.strip() for form in required_forms if form.strip())
    checklist = ("Confirm start date and supervisor.", "Provide city handbook and adopted personnel policy.", *forms, "Schedule role-specific training.")
    return OnboardingPacket(role_title=role_title.strip(), department=department.strip(), checklist=checklist, approvals=("HR", "hiring manager"))
