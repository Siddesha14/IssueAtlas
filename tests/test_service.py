from issue_atlas.data import load_issues
from issue_atlas.service import IssueTriageService


def test_triage_returns_prediction_and_evidence() -> None:
    service = IssueTriageService(load_issues())

    result = service.triage(
        title="OAuth refresh request is rejected",
        body="Refreshing a valid token produces a 401 response.",
        repository="sample/auth-service",
    )

    assert result.label == "bug"
    assert result.confidence > 0.45
    assert result.related_issues
    assert result.related_issues[0].issue_id == "auth-101"


def test_triage_rejects_empty_issue() -> None:
    service = IssueTriageService(load_issues())

    try:
        service.triage("", "")
    except ValueError as error:
        assert "required" in str(error)
    else:
        raise AssertionError("Expected empty issue to be rejected")
