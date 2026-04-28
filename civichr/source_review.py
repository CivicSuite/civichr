"""HR source-readiness checks."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HRSourceReview:
    ready_for_drafting: bool
    source_titles: tuple[str, ...]
    blockers: tuple[str, ...]


def review_hr_sources(source_titles: list[str], approved_by_hr: bool) -> HRSourceReview:
    """Require HR-approved source materials before drafting staff-facing content."""

    titles = tuple(title.strip() for title in source_titles if title.strip())
    blockers: list[str] = []
    if not titles:
        blockers.append("At least one adopted HR policy, template, or handbook source is required.")
    if not approved_by_hr:
        blockers.append("HR must approve source materials before CivicHR drafts from them.")
    return HRSourceReview(ready_for_drafting=not blockers, source_titles=titles, blockers=tuple(blockers))
