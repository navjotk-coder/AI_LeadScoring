import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="AI Lead Scoring API (Local Model)")

# Load model once at startup
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    framework="pt"  # Force PyTorch
)


class Lead(BaseModel):
    name: str
    email: str
    message: str
    budget: Optional[str] = None


def analyze_lead(message: str, budget: Optional[str]):

    labels = ["high buying intent", "medium buying intent", "low buying intent"]

    full_text = f"{message}. Budget: {budget}"

    result = classifier(full_text, candidate_labels=labels)

    top_label = result["labels"][0]
    score = float(result["scores"][0])

    intent_score = int(score * 100)

    # Add keyword-based boosting
    urgent_keywords = ["urgent", "immediately", "asap", "ready to buy"]
    high_budget_keywords = ["cr", "lakh", "million"]

    boost = 0

    if any(word in message.lower() for word in urgent_keywords):
        boost += 15

    if budget and any(word in budget.lower() for word in high_budget_keywords):
        boost += 15

    intent_score = min(intent_score + boost, 100)

    if intent_score >= 75:
        urgency = "High"
        category = "HOT"
    elif intent_score >= 50:
        urgency = "Medium"
        category = "WARM"
    else:
        urgency = "Low"
        category = "COLD"

    return {
        "intent_score": intent_score,
        "urgency": urgency,
        "category": category,
        "reason": f"Detected as {top_label} with keyword boost"
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