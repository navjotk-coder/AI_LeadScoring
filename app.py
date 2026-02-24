import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Lead Scoring API (Local Model)")

class Lead(BaseModel):
    name: str
    email: str
    message: str
    budget: Optional[str] = None


def analyze_lead(message: str, budget: Optional[str]):

    text = message.lower()
    score = 0
    reasons = []

    # Urgency keywords
    urgent_words = ["urgent", "immediately", "asap", "today", "ready"]
    if any(word in text for word in urgent_words):
        score += 30
        reasons.append("Urgency detected")

    # Buying intent keywords
    intent_words = ["need", "buy", "purchase", "looking for", "interested"]
    if any(word in text for word in intent_words):
        score += 30
        reasons.append("Buying intent detected")

    # Budget check
    if budget:
        budget_text = budget.lower()
        if "cr" in budget_text or "lakh" in budget_text:
            score += 30
            reasons.append("Budget mentioned")

    score = min(score, 100)

    if score >= 70:
        category = "HOT"
        urgency = "High"
    elif score >= 40:
        category = "WARM"
        urgency = "Medium"
    else:
        category = "COLD"
        urgency = "Low"

    if not reasons:
        reasons.append("Low engagement or unclear buying signals")

    return {
        "intent_score": score,
        "urgency": urgency,
        "category": category,
        "reason": ", ".join(reasons)
    }


@app.post("/score-lead")
def score_lead(lead: Lead):

    analysis = analyze_lead(lead.message, lead.budget)

    return {
        "name": lead.name,
        "email": lead.email,
        "analysis": analysis
    }


@app.get("/")
def root():
    return {"message": "Local AI Lead Scoring API is running"}