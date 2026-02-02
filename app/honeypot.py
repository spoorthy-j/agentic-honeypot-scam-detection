from __future__ import annotations

from app.extractor import extract_intel
from app.sessions import (
    get_session, end_session, add_message, update_last_scammer_time,
    memory_update
)

MAX_TURNS = 8
REPEAT_LIMIT = 3
NO_PROGRESS_LIMIT = 3


def _intent_key(text: str) -> str:
    t = (text or "").lower()
    if "collect request" in t or "collect" in t or "request money" in t:
        return "COLLECT"
    if "upi" in t or "pay" in t or "pin" in t:
        return "PAYMENT"
    if "http" in t or "link" in t or "www" in t:
        return "LINK"
    if "otp" in t:
        return "OTP"
    return "OTHER"


def _update_repeat_state(session: dict, scammer_text: str) -> None:
    intent = _intent_key(scammer_text)
    if intent == session.get("last_intent", ""):
        session["repeat_count"] = session.get("repeat_count", 0) + 1
    else:
        session["last_intent"] = intent
        session["repeat_count"] = 0


def _is_refusal(text: str) -> bool:
    t = (text or "").lower().strip()
    refusal_phrases = [
        "i won't send", "i wont send", "won't send",
        "can't share", "cant share", "not possible",
        "no website", "no link", "not needed",
        "just pay", "stop asking"
    ]
    return any(p in t for p in refusal_phrases)


def _all_intel_collected(session: dict) -> bool:
    intel = session["intel"]
    has_upi = len(intel["upi_ids"]) > 0
    has_phone = len(intel["phone_numbers"]) > 0
    has_link_or_domain = (len(intel["links"]) > 0) or (len(intel["domains"]) > 0)
    return has_upi and has_phone and has_link_or_domain


def _final_exit_message(reason: str) -> str:
    if reason == "all_intel_collected":
        return "Thank you. I received the details. I’ll verify through official channels."
    if reason == "no_intel_progress":
        return "I can’t verify without any details. I’m stopping this for safety."
    if reason == "max_turns":
        return "I can’t proceed right now. I’ll check later."
    if reason == "repeated_intent":
        return "I’m still not clear. Please email from an official domain with a case ID."
    return "I can’t continue this conversation."


def _adaptive_reply(session: dict, scammer_text: str) -> str:
    intel = session["intel"]
    t = (scammer_text or "").lower()

    if _is_refusal(scammer_text) and ("no website" in t or "no link" in t or "not needed" in t):
        session["refused_site_flag"] = True

    refused_site_flag = session.get("refused_site_flag", False)

    need_link = (len(intel["links"]) == 0 and len(intel["domains"]) == 0)
    need_upi = (len(intel["upi_ids"]) == 0)
    need_phone = (len(intel["phone_numbers"]) == 0)

    if _is_refusal(scammer_text):
        if need_phone:
            return "Okay. Then share a phone number/helpline so I can confirm before paying."
        if need_upi:
            return "I can pay only after seeing the exact UPI ID and merchant name. Share that."
        if need_link:
            return "At least send the QR/payment link screenshot or official tracking/reference number."
        return "Tell exact steps: do I press Pay or Receive? Explain clearly."

    if need_link and not refused_site_flag:
        return "Which company/service is this? Share official website/payment link and a reference number."
    if need_upi:
        return "Okay. Share the exact UPI ID and the merchant name shown on your side."
    if need_phone:
        return "My app is failing. Share your support phone number and alternate UPI/link."
    if need_link and refused_site_flag:
        return "If no website, then send QR/payment link screenshot or tracking/reference number."

    return "Before paying, confirm: is this a collect request or a normal payment? Explain steps."


def handle_incoming_scammer_message(session_id: str, scammer_text: str) -> dict:
    s = get_session(session_id)
    if not s:
        return {"error": "session_not_found"}
    if s["status"] == "ENDED":
        return {"status": "ENDED", "reply": None}

    scammer_text = scammer_text or ""
    update_last_scammer_time(session_id)
    add_message(session_id, "scammer", scammer_text)

    before = (
        len(s["intel"]["upi_ids"]),
        len(s["intel"]["phone_numbers"]),
        len(s["intel"]["links"]),
        len(s["intel"]["domains"]),
    )

    extracted = extract_intel(scammer_text)
    for k in extracted:
        s["intel"][k].update(extracted[k])

    # ✅ update memory with intel from this scammer message
    memory_update(scammer_text, intel={
        "upi_ids": list(extracted["upi_ids"]),
        "phone_numbers": list(extracted["phone_numbers"]),
        "links": list(extracted["links"]),
        "domains": list(extracted["domains"]),
    })

    after = (
        len(s["intel"]["upi_ids"]),
        len(s["intel"]["phone_numbers"]),
        len(s["intel"]["links"]),
        len(s["intel"]["domains"]),
    )

    if after == before:
        s["no_progress_count"] += 1
    else:
        s["no_progress_count"] = 0

    _update_repeat_state(s, scammer_text)

    if _all_intel_collected(s):
        end_session(session_id, "all_intel_collected")
        final_msg = _final_exit_message("all_intel_collected")
        add_message(session_id, "honeypot", final_msg)
        return {"status": "ENDED", "stop_reason": "all_intel_collected", "reply": final_msg}

    if s["no_progress_count"] >= NO_PROGRESS_LIMIT:
        end_session(session_id, "no_intel_progress")
        final_msg = _final_exit_message("no_intel_progress")
        add_message(session_id, "honeypot", final_msg)
        return {"status": "ENDED", "stop_reason": "no_intel_progress", "reply": final_msg}

    if s["turns"] >= MAX_TURNS:
        end_session(session_id, "max_turns")
        final_msg = _final_exit_message("max_turns")
        add_message(session_id, "honeypot", final_msg)
        return {"status": "ENDED", "stop_reason": "max_turns", "reply": final_msg}

    if s["repeat_count"] >= REPEAT_LIMIT:
        end_session(session_id, "repeated_intent")
        final_msg = _final_exit_message("repeated_intent")
        add_message(session_id, "honeypot", final_msg)
        return {"status": "ENDED", "stop_reason": "repeated_intent", "reply": final_msg}

    reply = _adaptive_reply(s, scammer_text)
    s["turns"] += 1
    add_message(session_id, "honeypot", reply)
    return {"status": "RUNNING", "reply": reply}
