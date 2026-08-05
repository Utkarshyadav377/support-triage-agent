# Changelog

## v2 — Fixed account vs. technical category confusion
**Date:** 2026-08-06

**Problem found via eval harness:** Category accuracy was 75% (3/4) on the initial test set.
The failing case: "I can't log in, it says my account is locked" was classified as
`technical` when it should have been `account`. The system prompt's category
definitions didn't distinguish access/login issues from bugs.

**Fix:** Added explicit category boundary rules and a one-shot example to the system
prompt clarifying that login/lockout issues belong to `account`, not `technical`.

**Result:**
| Metric | Before | After |
|---|---|---|
| Category accuracy | 75.0% | 100.0% |
| Avg relevance | 5.00/5 | 4.75/5 |
| Avg tone | 4.75/5 | 4.75/5 |

**Files changed:** `backend/app/agent.py` (SYSTEM_PROMPT)

---

## v1 — Initial version
- Built triage agent with categorization, draft reply, and escalation logic
- Instrumented latency, token usage, and cost tracking
- Built LLM-as-Judge eval harness with 4 seed test cases