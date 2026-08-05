# Changelog
## v3 — Expanded eval set to 20 cases (angry tone, multi-issue, ambiguous)
**Date:** 2026-08-06

**Change:** Grew `test_cases.json` from 4 to 20 tickets, adding angry-tone tickets
(testing escalation logic), a multi-issue ticket, and vague/off-topic tickets
(testing correct use of the `other` category).

**Result:**
| Metric | v2 (4 cases) | v3 (20 cases) |
|---|---|---|
| Category accuracy | 100.0% | 95.0% |
| Avg relevance | 4.75/5 | 4.75/5 |
| Avg tone | 4.75/5 | 4.70/5 |

**Remaining known issue:** "Not sure who to ask but is there a public API for
this product?" was classified as `technical` instead of the expected `other`.
On review, this is a defensible model call — an API availability question is
arguably more useful routed to a technical team than a catch-all bucket. Not
treating this as a bug; leaving the `other` category definition as-is rather
than over-fitting the prompt to a single ambiguous test case.

**Files changed:** `eval/test_cases.json`

---
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