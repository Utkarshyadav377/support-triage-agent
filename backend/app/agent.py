import time, json, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


INPUT_COST_PER_1K = 0.0
OUTPUT_COST_PER_1K = 0.0

CATEGORIES = ["billing", "technical", "account", "feature_request", "other"]

SYSTEM_PROMPT = f"""You are a support ticket triage agent. Given a ticket, respond ONLY with JSON:
{{
  "category": one of {CATEGORIES},
  "confidence": float 0-1,
  "draft_reply": a short, professional draft response to the customer,
  "escalate": true if confidence < 0.6 or the issue seems high-risk (legal, security, angry customer), else false
}}

Category definitions:
- billing: charges, refunds, invoices, payment methods, subscription cost
- technical: app crashes, bugs, broken features, performance issues (NOT login/access issues)
- account: login failures, locked/suspended accounts, password resets, account settings, profile changes
- feature_request: suggestions for new functionality that doesn't exist yet
- other: anything that doesn't clearly fit above

Examples:
Ticket: "I can't log in, it says my account is locked" -> category: account (this is access/login, not a bug)
Ticket: "The export button does nothing when I click it" -> category: technical (broken existing feature)

No preamble, no markdown fences, just the JSON object."""

def triage_ticket(ticket_text: str) -> dict:
    start = time.time()
    error = None
    result = {}
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": ticket_text},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        cost = 0.0  
    except Exception as e:
        error = str(e)
        input_tokens = output_tokens = 0
        cost = 0.0
        result = {"category": "other", "confidence": 0.0, "draft_reply": "", "escalate": True}

    latency_ms = int((time.time() - start) * 1000)
    return {
        **result,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "error": error,
    }