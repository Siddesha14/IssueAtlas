from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

from issue_atlas.domain import IssueRecord


@dataclass(frozen=True)
class RelatedIssue:
    issue_id: str
    title: str
    label: str
    repository: str
    resolution: str
    similarity: float


@dataclass(frozen=True)
class TriageResult:
    label: str | None
    confidence: float
    should_abstain: bool
    related_issues: list[RelatedIssue]


class IssueTriageService:
    """Small, inspectable baseline for later model and retrieval experiments."""

    def __init__(self, issues: list[IssueRecord], abstain_threshold: float = 0.45) -> None:
        if not 0.0 <= abstain_threshold <= 1.0:
            raise ValueError("abstain_threshold must be between 0 and 1")

        self.issues = issues
        self.abstain_threshold = abstain_threshold
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        training_texts = [issue.text for issue in issues]
        self.issue_vectors = self.vectorizer.fit_transform(training_texts)
        self.classifier = LogisticRegression(max_iter=1_000, class_weight="balanced")
        self.classifier.fit(self.issue_vectors, [issue.label for issue in issues])
        self.resolved_indices = [index for index, issue in enumerate(issues) if issue.state == "closed"]

    def triage(self, title: str, body: str, repository: str = "") -> TriageResult:
        text = f"{title}\n{body}".strip()
        if not text:
            raise ValueError("title or body is required")

        query_vector = self.vectorizer.transform([text])
        probabilities = self.classifier.predict_proba(query_vector)[0]
        best_index = probabilities.argmax()
        confidence = float(probabilities[best_index])
        should_abstain = confidence < self.abstain_threshold
        label = None if should_abstain else str(self.classifier.classes_[best_index])

        related = self._related_issues(query_vector, repository)
        return TriageResult(label, confidence, should_abstain, related)

    def _related_issues(self, query_vector, repository: str) -> list[RelatedIssue]:
        candidates = self.resolved_indices
        if repository:
            same_repository = [
                index for index in candidates if self.issues[index].repository == repository
            ]
            if same_repository:
                candidates = same_repository

        if not candidates:
            return []

        scores = cosine_similarity(query_vector, self.issue_vectors[candidates]).ravel()
        top_positions = scores.argsort()[::-1][:3]
        return [
            RelatedIssue(
                issue_id=self.issues[candidates[position]].issue_id,
                title=self.issues[candidates[position]].title,
                label=self.issues[candidates[position]].label,
                repository=self.issues[candidates[position]].repository,
                resolution=self.issues[candidates[position]].resolution,
                similarity=round(float(scores[position]), 4),
            )
            for position in top_positions
        ]
