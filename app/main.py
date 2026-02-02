from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app.sessions import (
    create_session, serialize_session,
    memory_lookup, memory_update
)
from app.honeypot import handle_incoming_scammer_message

app = FastAPI(title="Agentic Honeypot Scam AI")


class AnalyzeIn(BaseModel):
    message: str


class HoneypotStartIn(BaseModel):
    message: str
    analyze_result: Optional[dict] = None


class HoneypotIncomingIn(BaseModel):
    session_id: str
    message: str


def analyze_message(text: str) -> Dict[str, Any]:
    t = (text or "").lower()
    reasons = []
    score = 0.0
    scam_type = "UNKNOWN"

    has_pay = any(k in t for k in [
        "pay", "payment", "upi", "upi id", "upi-id", "collect request",
        "pin", "upi pin", "processing fee", "activate"
    ])
    has_reward = any(k in t for k in ["reward", "points", "redeem", "cashback", "expire", "expiring"])
    has_urgency = any(k in t for k in ["today", "urgent", "immediately", "within", "expire", "fast", "now"])
    has_delivery = any(k in t for k in ["parcel", "courier", "delivery", "shipment", "tracking", "reschedule"])
    has_job = any(k in t for k in ["job", "work from home", "earn", "salary", "registration fee"])
    has_utility = any(k in t for k in ["electricity", "power", "bill", "disconnect", "gas", "water"])
    has_govt = any(k in t for k in ["subsidy", "government", "scheme", "benefit", "processing fee"])

    if has_pay:
        score += 0.3
        reasons.append("keyword:pay")
        scam_type = "UPI_PAYMENT"

    if has_reward:
        score += 0.3
        reasons.append("pattern:reward_scam")
        scam_type = "REWARD_SCAM"

    if has_delivery:
        score += 0.3
        reasons.append("pattern:delivery_scam")
        scam_type = "DELIVERY_SCAM"

    if has_job:
        score += 0.3
        reasons.append("pattern:job_scam")
        scam_type = "JOB_SCAM"

    if has_utility:
        score += 0.3
        reasons.append("pattern:utility_scam")
        scam_type = "UTILITY_SCAM"

    if has_govt:
        score += 0.3
        reasons.append("pattern:govt_benefit_scam")
        scam_type = "GOVT_BENEFIT_SCAM"

    if has_urgency:
        score += 0.2
        reasons.append("pattern:urgency")

    if "otp" in t or "upi pin" in t:
        score += 0.2
        reasons.append("pattern:credential_theft")
        scam_type = "PHISHING"

    if score > 1.0:
        score = 1.0

    is_scam = score >= 0.5

    user_alert = None
    recommended_actions = []
    if is_scam:
        user_alert = "⚠️ Suspicious message detected. Do NOT pay or share OTP/UPI PIN."
        recommended_actions = [
            "Do not click unknown links.",
            "Do not approve UPI collect requests.",
            "Verify through official website/app or customer care.",
            "Report and block the sender."
        ]

    return {
        "is_scam": is_scam,
        "scam_score": float(score),
        "scam_type": scam_type,
        "reasons": reasons,
        "user_alert": user_alert,
        "recommended_actions": recommended_actions
    }


@app.post("/analyze")
def analyze(payload: AnalyzeIn):
    result = analyze_message(payload.message)

    prev = memory_lookup(payload.message)
    memory_match = prev is not None

    rec = memory_update(payload.message, analyze_result=result)

    result["memory_match"] = memory_match
    result["seen_count"] = rec["count"]
    result["first_seen"] = rec["first_seen"]
    result["last_seen"] = rec["last_seen"]
    result["previous_intel"] = rec["intel"]
    return result


@app.post("/honeypot/start")
def honeypot_start(payload: HoneypotStartIn):
    session_id = str(uuid.uuid4())
    create_session(session_id, analyze_result=payload.analyze_result)

    out = handle_incoming_scammer_message(session_id, payload.message)

    return {
        "session_id": session_id,
        "first_reply": out.get("reply"),
        "status": out.get("status"),
        "stop_reason": out.get("stop_reason"),
        "session": serialize_session(session_id),
    }


@app.post("/honeypot/incoming")
def honeypot_incoming(payload: HoneypotIncomingIn):
    out = handle_incoming_scammer_message(payload.session_id, payload.message)
    return {
        "reply": out.get("reply"),
        "status": out.get("status"),
        "stop_reason": out.get("stop_reason"),
        "session": serialize_session(payload.session_id),
    }


@app.get("/honeypot/session/{session_id}")
def honeypot_get_session(session_id: str):
    s = serialize_session(session_id)
    if not s:
        return {"error": "session_not_found"}
    return s
