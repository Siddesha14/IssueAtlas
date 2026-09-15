from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from issue_atlas.data import load_issues
from issue_atlas.service import IssueTriageService

app = FastAPI(title="IssueAtlas", version="0.1.0")


class TriageRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(default="", max_length=10_000)
    repository: str = Field(default="", max_length=200)


class RelatedIssueResponse(BaseModel):
    issue_id: str
    title: str
    label: str
    repository: str
    resolution: str
    similarity: float


class TriageResponse(BaseModel):
    label: str | None
    confidence: float
    should_abstain: bool
    related_issues: list[RelatedIssueResponse]


@lru_cache
def get_service() -> IssueTriageService:
    return IssueTriageService(load_issues())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
def triage_issue(request: TriageRequest) -> TriageResponse:
    try:
        result = get_service().triage(request.title, request.body, request.repository)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return TriageResponse(
        label=result.label,
        confidence=result.confidence,
        should_abstain=result.should_abstain,
        related_issues=[RelatedIssueResponse(**item.__dict__) for item in result.related_issues],
    )
