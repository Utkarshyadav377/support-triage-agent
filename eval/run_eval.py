PROMPT_VERSION = "v4"  # bump this every time you change SYSTEM_PROMPT
import json, requests
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../backend/.env")
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

with open("test_cases.json") as f:
    test_cases = json.load(f)

JUDGE_PROMPT = """You are grading an AI support agent's draft reply.
Ticket: {ticket}
Agent's draft reply: {reply}

Score the reply from 1-5 on:
- relevance (does it address the actual issue)
- tone (professional, empathetic)
- completeness (does it move the conversation forward)

Respond ONLY with JSON: {{"relevance": int, "tone": int, "completeness": int, "notes": "one sentence"}}"""

results = []
correct_category = 0

for case in test_cases:
    resp = requests.post("http://localhost:8000/triage", json={"text": case["ticket"]}).json()

    category_match = resp["category"] == case["expected_category"]
    if category_match:
        correct_category += 1

    judge_resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",  
    messages=[{"role": "user", "content": JUDGE_PROMPT.format(
        ticket=case["ticket"], reply=resp["draft_reply"])}],
    temperature=0,
    )
    judge_score = json.loads(judge_resp.choices[0].message.content)

    results.append({
        "ticket": case["ticket"],
        "expected": case["expected_category"],
        "actual": resp["category"],
        "category_match": category_match,
        "judge_score": judge_score,
        "latency_ms": resp["latency_ms"],
    })

accuracy = correct_category / len(test_cases)
avg_relevance = sum(r["judge_score"]["relevance"] for r in results) / len(results)
avg_tone = sum(r["judge_score"]["tone"] for r in results) / len(results)

print(f"Category accuracy: {accuracy:.1%}")
print(f"Avg relevance: {avg_relevance:.2f}/5")
print(f"Avg tone: {avg_tone:.2f}/5")

with open("eval_results.json", "w") as f:
    json.dump(results, f, indent=2)

import csv
from datetime import datetime
from pathlib import Path

log_path = Path("eval_history.csv")
is_new = not log_path.exists()

with open(log_path, "a", newline="") as f:
    writer = csv.writer(f)
    if is_new:
        writer.writerow(["timestamp", "prompt_version", "accuracy", "avg_relevance", "avg_tone", "num_cases"])
    writer.writerow([
        datetime.now().isoformat(timespec="seconds"),
        PROMPT_VERSION,
        round(accuracy, 3),
        round(avg_relevance, 2),
        round(avg_tone, 2),
        len(test_cases),
    ])