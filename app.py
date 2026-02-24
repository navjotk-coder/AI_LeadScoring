import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
#from transformers import pipeline

app = FastAPI(title="AI Lead Scoring API (Local Model)")

# Load model once at startup
#classifier = pipeline(
 #   "zero-shot-classification",
  #  model="facebook/bart-large-mnli",
   # framework="pt"  # Force PyTorch
#)


class Lead(BaseModel):
    name: str
    email: str
    message: str
    budget: Optional[str] = None


def analyze_lead(message: str, budget: Optional[str]):

    text = message.lower()

    score = 0

    # Urgency keywords
    urgent_words = ["urgent", "immediately", "asap", "today", "ready"]
    if any(word in text for word in urgent_words):
        score += 30

    # Buying intent keywords
    intent_words = ["need", "buy", "purchase", "looking for", "interested"]
    if any(word in text for word in intent_words):
        score += 30

    # Budget check
    if budget:
        if "cr" in budget.lower() or "lakh" in budget.lower():
            score += 30

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

    return {
        "intent_score": score,
        "urgency": urgency,
        "category": category,
        "reason": "Keyword-based intelligent scoring"
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