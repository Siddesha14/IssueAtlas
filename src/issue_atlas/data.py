from __future__ import annotations

import json
from pathlib import Path

from issue_atlas.domain import IssueRecord


def default_dataset_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "sample_issues.jsonl"


def load_issues(path: Path | None = None) -> list[IssueRecord]:
    dataset_path = path or default_dataset_path()
    records: list[IssueRecord] = []

    with dataset_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                records.append(IssueRecord(**item))
            except (TypeError, json.JSONDecodeError) as error:
                raise ValueError(f"Invalid record at {dataset_path}:{line_number}") from error

    if not records:
        raise ValueError(f"No issue records found in {dataset_path}")
    return records
