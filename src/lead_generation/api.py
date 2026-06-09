"""
FastAPI endpoint for the lead generation platform.
Accepts lead submissions, scores them, and returns qualification results.
"""
from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class LeadSubmission(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    company: str = Field("", max_length=200)
    email: str = Field(..., min_length=5, max_length=200)
    phone: Optional[str] = None
    budget: str = Field(..., description="low | medium | high | enterprise")
    urgency: str = Field(..., description="immediate | this_week | this_month | exploring")
    industry: str = Field("", max_length=100)
    lead_source: str = Field("website", max_length=50)
    message: Optional[str] = Field(None, max_length=1000)


class LeadScore(BaseModel):
    lead_id: str
    name: str
    company: str
    email: str
    total_score: int
    budget_score: int
    urgency_score: int
    industry_score: int
    source_score: int
    qualification: str  # "qualified" | "review" | "unqualified"
    recommended_action: str
    scored_at: datetime


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------

_BUDGET_SCORES = {"enterprise": 35, "high": 30, "medium": 20, "low": 8}
_URGENCY_SCORES = {"immediate": 30, "this_week": 24, "this_month": 14, "exploring": 5}
_SOURCE_SCORES = {"referral": 15, "demo_request": 14, "paid_ads": 10, "organic_search": 10,
                  "website": 8, "cold_outreach": 4, "other": 3}
_INDUSTRY_BOOST = {"saas", "fintech", "healthtech", "ecommerce", "enterprise", "logistics"}


def score_lead(submission: LeadSubmission) -> tuple[int, str, str]:
    """Return (total_score, qualification_tier, recommended_action)."""
    budget_pts = _BUDGET_SCORES.get(submission.budget.lower(), 10)
    urgency_pts = _URGENCY_SCORES.get(submission.urgency.lower(), 5)
    source_pts = _SOURCE_SCORES.get(submission.lead_source.lower(), 5)
    industry_pts = 20 if any(k in submission.industry.lower() for k in _INDUSTRY_BOOST) else 10
    total = min(100, budget_pts + urgency_pts + source_pts + industry_pts)

    if total >= 70:
        return total, "qualified", "assign_to_sales_immediately"
    elif total >= 45:
        return total, "review", "nurture_sequence_enter"
    else:
        return total, "unqualified", "archive_low_priority"


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Lead Generation Platform",
    description="Lead intake, scoring, and qualification API.",
    version="0.1.0",
)

_lead_store: dict[str, dict] = {}


@app.post("/leads", response_model=LeadScore, status_code=201,
          summary="Submit and score a new lead")
async def submit_lead(submission: LeadSubmission) -> LeadScore:
    lead_id = f"LEAD-{str(uuid.uuid4())[:8].upper()}"
    total, qualification, action = score_lead(submission)

    budget_pts = _BUDGET_SCORES.get(submission.budget.lower(), 10)
    urgency_pts = _URGENCY_SCORES.get(submission.urgency.lower(), 5)
    source_pts = _SOURCE_SCORES.get(submission.lead_source.lower(), 5)
    industry_pts = 20 if any(k in submission.industry.lower() for k in _INDUSTRY_BOOST) else 10

    result = LeadScore(
        lead_id=lead_id,
        name=submission.name,
        company=submission.company,
        email=submission.email,
        total_score=total,
        budget_score=budget_pts,
        urgency_score=urgency_pts,
        industry_score=industry_pts,
        source_score=source_pts,
        qualification=qualification,
        recommended_action=action,
        scored_at=datetime.now(timezone.utc),
    )
    _lead_store[lead_id] = result.model_dump(mode="json")
    return result


@app.get("/leads", summary="List all scored leads")
async def list_leads(qualification: Optional[str] = None) -> dict:
    records = list(_lead_store.values())
    if qualification:
        records = [r for r in records if r["qualification"] == qualification]
    return {"total": len(records), "leads": records}


@app.get("/leads/{lead_id}", summary="Get a lead by ID")
async def get_lead(lead_id: str) -> dict:
    if lead_id not in _lead_store:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id!r} not found")
    return _lead_store[lead_id]


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ai-lead-generation-platform"}
