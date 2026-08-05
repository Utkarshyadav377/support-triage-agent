from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import triage_ticket
from .db import SessionLocal, TicketEvent
from sqlalchemy import func

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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