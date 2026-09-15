from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IssueRecord:
    issue_id: str
    title: str
    body: str
    label: str
    repository: str
    state: str
    resolution: str = ""

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.body}".strip()

