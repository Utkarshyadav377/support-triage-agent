from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import triage_ticket
from .db import SessionLocal, TicketEvent
from sqlalchemy import func
import requests as http_requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

import requests as http_requests

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ERROR_RATE_THRESHOLD = 0.2  # alert if error rate exceeds 20%

def send_slack_alert(message: str):
    if not SLACK_WEBHOOK_URL:
        return
    try:
        http_requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=5)
    except Exception:
        pass  # don't let alerting failures break the main request

class TicketRequest(BaseModel):
    text: str

@app.post("/triage")
def triage(req: TicketRequest):
    result = triage_ticket(req.text)
    db = SessionLocal()
    event = TicketEvent(
        ticket_text=req.text,
        category=result["category"],
        confidence=result["confidence"],
        escalated=result["escalate"],
        draft_reply=result["draft_reply"],
        latency_ms=result["latency_ms"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        cost_usd=result["cost_usd"],
        error=result["error"],
    )
    db.add(event)
    db.commit()

    # Check error rate over the last 20 tickets and alert if it crosses the threshold
    recent_n = 20
    recent_events = db.query(TicketEvent).order_by(TicketEvent.id.desc()).limit(recent_n).all()
    if len(recent_events) >= 5:  # don't alert on tiny sample sizes
        error_count = sum(1 for e in recent_events if e.error is not None)
        error_rate = error_count / len(recent_events)
        if error_rate > ERROR_RATE_THRESHOLD:
            send_slack_alert(f":rotating_light: Error rate at {error_rate:.0%} over last {len(recent_events)} tickets on Support Triage Agent.")

    db.close()
    return result

@app.get("/metrics")
def metrics():
    db = SessionLocal()
    total = db.query(func.count(TicketEvent.id)).scalar() or 0
    avg_latency = db.query(func.avg(TicketEvent.latency_ms)).scalar() or 0
    total_cost = db.query(func.sum(TicketEvent.cost_usd)).scalar() or 0
    error_count = db.query(func.count(TicketEvent.id)).filter(TicketEvent.error.isnot(None)).scalar() or 0
    escalated_count = db.query(func.count(TicketEvent.id)).filter(TicketEvent.escalated == True).scalar() or 0
    recent = db.query(TicketEvent).order_by(TicketEvent.id.desc()).limit(20).all()
    db.close()
    return {
        "total_tickets": total,
        "avg_latency_ms": round(avg_latency, 1),
        "total_cost_usd": round(total_cost, 4),
        "error_rate": round(error_count / total, 3) if total else 0,
        "escalation_rate": round(escalated_count / total, 3) if total else 0,
        "recent": [
            {
                "id": e.id, "category": e.category, "confidence": e.confidence,
                "escalated": e.escalated, "latency_ms": e.latency_ms,
                "cost_usd": e.cost_usd, "created_at": str(e.created_at),
            } for e in recent
        ],
    }