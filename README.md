# Support Triage Agent

An AI agent that reads incoming support tickets, categorizes them, drafts a reply, and escalates low-confidence or high-risk cases — with a production observability dashboard and an LLM-as-Judge eval harness to catch regressions before they ship.

Built to mirror how a real support-AI system should be developed: not just "call an LLM and hope," but instrumented, tested, and iterated on with evidence.

## What it does

- **Triage:** categorizes tickets into billing / technical / account / feature_request / other
- **Draft reply:** generates a professional first-draft response
- **Escalation:** flags low-confidence or high-risk tickets for human review
- **Observability:** every call logs latency, token usage, and cost
- **Eval harness:** LLM-as-Judge scoring on relevance, tone, and completeness, run against a 20-case test set

## Architecture
Ticket (text) → Agent Service (FastAPI + LLM) → Category, Draft Reply, Escalate?
│ logs every call
▼
SQLite: ticket_events table
│
┌──────────────┴──────────────┐
▼ ▼
React Dashboard Eval Harness (CLI)
(live metrics) LLM-as-Judge scoring

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Frontend:** React, TypeScript, Vite, Recharts
- **LLM:** Groq (Llama 3.3 70B), OpenAI-compatible API
- **Eval:** custom LLM-as-Judge harness

## Results — eval-driven iteration

| Version | Change | Accuracy | Notes |
|---|---|---|---|
| v1 | Initial prompt, 4 test cases | 75% | Baseline |
| v2 | Fixed account/technical category confusion | 100% | Added explicit boundary + example |
| v3 | Expanded to 20 test cases (angry tone, multi-issue, ambiguous) | 95% | More trustworthy signal; one known edge case documented, not over-fit |

Full history in [CHANGELOG.md](./CHANGELOG.md).

## Running it locally

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your-key-here" > .env
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Eval harness:**
```bash
cd eval
python3 run_eval.py
```

## What I'd improve with more time

- Ground draft replies with a small RAG step over a mock knowledge base instead of relying on the model's general knowledge
- Replace the fixed confidence threshold with a calibrated model
- Add Slack alerting when error rate crosses a threshold
- Chart eval accuracy over prompt versions directly in the dashboard

## Why this project

Built to practice the full lifecycle of a production AI feature — not just building a demo, but instrumenting it, testing it against real regressions, and treating prompt changes like code changes that need evidence before shipping.