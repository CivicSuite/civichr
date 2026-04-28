"""Employee handbook summary support."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HandbookSummaryDraft:
    topic: str
    source_title: str
    plain_language_points: tuple[str, ...]
    requires_hr_review: bool


def draft_handbook_summary(
    topic: str, source_title: str, policy_points: list[str]
) -> HandbookSummaryDraft:
    points = tuple(point.strip() for point in policy_points if point.strip()) or (
        "Source policy text required before summary.",
    )
    return HandbookSummaryDraft(
        topic=topic.strip(),
        source_title=source_title.strip(),
        plain_language_points=points,
        requires_hr_review=True,
    )
