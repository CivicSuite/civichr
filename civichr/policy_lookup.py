"""Personnel policy lookup support."""

from dataclasses import dataclass

from civichr.sensitive_review import SensitiveReview, review_hr_topic


@dataclass(frozen=True)
class PolicyLookupDraft:
    question: str
    matched_policy_titles: tuple[str, ...]
    answer_outline: tuple[str, ...]
    sensitive_review: SensitiveReview
    requires_hr_review: bool


def draft_policy_lookup(question: str, policy_titles: list[str]) -> PolicyLookupDraft:
    """Draft a policy lookup outline without giving legal advice."""

    review = review_hr_topic(question, policy_titles)
    titles = tuple(title.strip() for title in policy_titles if title.strip())
    outline = (
        "Confirm the current adopted personnel policy section.",
        "Summarize only cited policy text after HR review.",
        "Escalate employment-law or accommodation questions to HR/counsel.",
    )
    return PolicyLookupDraft(question=question.strip(), matched_policy_titles=titles, answer_outline=outline, sensitive_review=review, requires_hr_review=True)
