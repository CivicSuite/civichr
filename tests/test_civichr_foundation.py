from civichr import __version__
from civichr.classification_lookup import lookup_classification
from civichr.handbook_summary import draft_handbook_summary
from civichr.intake_templates import draft_intake_template
from civichr.job_description import draft_job_description
from civichr.onboarding import build_onboarding_packet
from civichr.policy_lookup import draft_policy_lookup
from civichr.sensitive_review import review_hr_topic
from civichr.source_review import review_hr_sources
from civichr.training_requirements import build_training_checklist


def test_version_is_release_version():
    assert __version__ == "0.1.0"


def test_sensitive_review_flags_employment_law_topics():
    review = review_hr_topic("FMLA leave for part-time employee", ["handbook"])
    assert review.safe_for_self_service is False
    assert review.findings[0].category == "employment-law"


def test_sensitive_review_flags_personnel_data_topics():
    review = review_hr_topic("salary and medical background data")
    assert {finding.category for finding in review.findings} == {"personnel-data"}


def test_policy_lookup_requires_hr_review_and_cites_policy_titles():
    draft = draft_policy_lookup("vacation accrual", ["Personnel Policy 4.2"])
    assert draft.requires_hr_review is True
    assert draft.matched_policy_titles == ("Personnel Policy 4.2",)
    assert "Confirm the current adopted" in draft.answer_outline[0]


def test_job_description_is_not_classification_decision():
    draft = draft_job_description("Planner I", "Planning", ["Review permit applications"])
    assert draft.not_a_classification_decision is True
    assert "HR" in draft.required_reviews
    assert "Duty: Review permit applications" in draft.sections


def test_onboarding_packet_builds_checklist_not_hris_workflow():
    packet = build_onboarding_packet("Clerk", "Administration", ["I-9", "Policy acknowledgment"])
    assert packet.approvals == ("HR", "hiring manager")
    assert "I-9" in packet.checklist


def test_source_review_blocks_unapproved_sources():
    review = review_hr_sources(["Draft handbook"], approved_by_hr=False)
    assert review.ready_for_drafting is False
    assert "HR must approve" in review.blockers[0]


def test_source_review_requires_sources():
    review = review_hr_sources([], approved_by_hr=True)
    assert review.ready_for_drafting is False
    assert "At least one" in review.blockers[0]


def test_handbook_summary_requires_hr_review():
    draft = draft_handbook_summary("Leave", "Handbook", ["Employees accrue leave monthly."])
    assert draft.requires_hr_review is True
    assert "Employees accrue" in draft.plain_language_points[0]

def test_classification_lookup_is_not_compensation_decision():
    result = lookup_classification("Planner I", "Class 22", "Schedule A")
    assert result.not_a_compensation_decision is True
    assert "HR must verify" in result.required_review

def test_training_checklist_does_not_track_completion_records():
    checklist = build_training_checklist("Clerk", ["Cybersecurity", "Records retention"])
    assert "does not track completion" in checklist.tracking_boundary

def test_intake_template_does_not_track_cases_or_recommend_outcomes():
    template = draft_intake_template("grievance")
    assert "does not track cases" in template.boundary
    assert any("Relevant policy" in prompt for prompt in template.prompts)
