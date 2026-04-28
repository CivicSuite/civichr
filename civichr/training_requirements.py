"""Training requirement checklist support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingChecklist:
    role_title: str
    requirements: tuple[str, ...]
    tracking_boundary: str


def build_training_checklist(role_title: str, requirements: list[str]) -> TrainingChecklist:
    cleaned = tuple(item.strip() for item in requirements if item.strip())
    return TrainingChecklist(
        role_title=role_title.strip(),
        requirements=cleaned or ("Training requirements require HR source review.",),
        tracking_boundary="Checklist only; CivicHR v0.1.1 does not track completion records.",
    )
