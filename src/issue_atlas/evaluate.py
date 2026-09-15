from __future__ import annotations

from sklearn.model_selection import train_test_split

from issue_atlas.data import load_issues
from issue_atlas.domain import IssueRecord
from issue_atlas.service import IssueTriageService


def evaluate() -> None:
    """Measure the baseline on issue records it did not train on."""
    issues = load_issues()
    train_issues, test_issues = train_test_split(
        issues,
        test_size=0.4,
        random_state=42,
        stratify=[issue.label for issue in issues],
    )
    service = IssueTriageService(train_issues)

    accepted = 0
    correct = 0
    for issue in test_issues:
        result = service.triage(issue.title, issue.body, issue.repository)
        if result.should_abstain:
            continue
        accepted += 1
        correct += result.label == issue.label

    total = len(test_issues)
    coverage = accepted / total
    accuracy = correct / accepted if accepted else 0.0

    print(f"Test issues: {total}")
    print(f"Model coverage: {coverage:.1%}")
    print(f"Accuracy when answering: {accuracy:.1%}")


if __name__ == "__main__":
    evaluate()