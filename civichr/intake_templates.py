"""Grievance and complaint intake template support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntakeTemplate:
    template_type: str
    prompts: tuple[str, ...]
    boundary: str


def draft_intake_template(template_type: str) -> IntakeTemplate:
    return IntakeTemplate(
        template_type=template_type.strip(),
        prompts=(
            "Date received",
            "Employee or representative contact",
            "Relevant policy or agreement section",
            "Requested next HR review step",
        ),
        boundary="Template only; CivicHR v0.1.0 does not track cases or recommend outcomes.",
    )
