"""Salary schedule and position classification lookup support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationLookup:
    position_title: str
    matched_classification: str
    salary_schedule_reference: str
    not_a_compensation_decision: bool
    required_review: str


def lookup_classification(
    position_title: str, classification: str, salary_schedule_reference: str
) -> ClassificationLookup:
    return ClassificationLookup(
        position_title=position_title.strip(),
        matched_classification=classification.strip(),
        salary_schedule_reference=salary_schedule_reference.strip(),
        not_a_compensation_decision=True,
        required_review="HR must verify classification and compensation references before use.",
    )
