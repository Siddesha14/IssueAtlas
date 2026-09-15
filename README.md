# IssueAtlas

IssueAtlas is an evidence-grounded issue intelligence service for software teams. Given a new issue, it predicts a triage label, retrieves similar resolved issues, and abstains when its classification confidence is too low.

The project is designed to demonstrate production-minded ML engineering: reproducible data, baseline models, retrieval evaluation, confidence calibration, API contracts, and tests. It does not use an LLM until a measurable baseline exists.

## First milestone

This repository contains a working baseline built from public-style issue records:

- TF-IDF + logistic regression for issue-type prediction
- cosine-similarity retrieval over resolved issues
- confidence-based abstention
- FastAPI service and automated tests

## Quick start

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn issue_atlas.api:app --reload
```

Open `http://127.0.0.1:8000/docs` and submit a request to `POST /triage`.

```json
{
  "title": "OAuth callback fails after token refresh",
  "body": "Users receive a 401 when the access token is refreshed.",
  "repository": "sample/auth-service"
}
```

Run the tests with:

```powershell
pytest
```

## Roadmap

1. Replace the bundled sample with a versioned, public GitHub-issue dataset.
2. Add temporal train/test splits and metrics for classification and retrieval.
3. Add hybrid retrieval, reranking, and an evidence-grounded LLM brief.
4. Add monitoring for latency, abstention rate, evidence coverage, and cost.

## Responsible use

IssueAtlas is for triaging public or authorized repository data. It should not ingest private repositories or source code without the repository owner's authorization.
