"""Simple lead scoring logic for the AI lead generation concept."""

from __future__ import annotations

from dataclasses import dataclass


HIGH_VALUE_TERMS = ("automation", "ai", "crm", "follow-up", "lead", "booking")
URGENT_TIMELINES = ("today", "this week", "30 days", "this month")


@dataclass(frozen=True)
class Lead:
    lead_id: str
    business_name: str
    contact_name: str
    email: str
    service_interest: str
    timeline: str
    notes: str = ""

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Lead":
        return cls(
            lead_id=row.get("lead_id", "").strip(),
            business_name=row.get("business_name", "").strip(),
            contact_name=row.get("contact_name", "").strip(),
            email=row.get("email", "").strip(),
            service_interest=row.get("service_interest", "").strip(),
            timeline=row.get("timeline", "").strip(),
            notes=row.get("notes", "").strip(),
        )


@dataclass(frozen=True)
class LeadScore:
    score: int
    status: str
    reasons: tuple[str, ...]


def score_lead(lead: Lead) -> LeadScore:
    """Score a lead with transparent prototype rules."""
    score = 20
    reasons: list[str] = ["Base score for complete intake review"]

    if lead.business_name and lead.contact_name and lead.email:
        score += 20
        reasons.append("Has business, contact, and email")

    service_text = lead.service_interest.lower()
    matched_terms = [term for term in HIGH_VALUE_TERMS if term in service_text]
    if matched_terms:
        score += 25
        reasons.append(f"Service interest matches: {', '.join(matched_terms)}")

    timeline_text = lead.timeline.lower()
    if any(term in timeline_text for term in URGENT_TIMELINES):
        score += 20
        reasons.append("Timeline suggests near-term interest")

    if len(lead.notes) >= 20:
        score += 10
        reasons.append("Notes include useful context")

    score = min(score, 100)
    status = "qualified" if score >= 70 else "needs_info" if score >= 45 else "not_fit"

    return LeadScore(score=score, status=status, reasons=tuple(reasons))

