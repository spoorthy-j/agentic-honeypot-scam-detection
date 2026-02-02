from __future__ import annotations
from typing import Dict, Any
import time
import hashlib

_SESSIONS: Dict[str, Dict[str, Any]] = {}

# ✅ Global memory database (in-memory)
# message_hash -> {count, first_seen, last_seen, last_analyze, intel}
_MEMORY: Dict[str, Dict[str, Any]] = {}


def _normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def message_hash(text: str) -> str:
    norm = _normalize_text(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def memory_lookup(text: str) -> dict | None:
    h = message_hash(text)
    return _MEMORY.get(h)


def memory_update(text: str, analyze_result: dict | None = None, intel: dict | None = None) -> dict:
    h = message_hash(text)
    now = time.time()

    if h not in _MEMORY:
        _MEMORY[h] = {
            "count": 0,
            "first_seen": now,
            "last_seen": now,
            "last_analyze": None,
            "intel": {"upi_ids": [], "phone_numbers": [], "links": [], "domains": []},
        }

    rec = _MEMORY[h]
    rec["count"] += 1
    rec["last_seen"] = now

    if analyze_result is not None:
        rec["last_analyze"] = analyze_result

    if intel is not None:
        for k in ["upi_ids", "phone_numbers", "links", "domains"]:
            existing = set(rec["intel"].get(k, []))
            incoming = set(intel.get(k, []))
            rec["intel"][k] = sorted(list(existing | incoming))

    return rec


def create_session(session_id: str, analyze_result: dict | None = None) -> Dict[str, Any]:
    s = {
        "id": session_id,
        "status": "RUNNING",
        "stop_reason": None,

        "turns": 0,
        "repeat_count": 0,
        "last_intent": "",

        "nudges": 0,
        "last_scammer_time": time.time(),

        "analyze_result": analyze_result,

        "refused_site_flag": False,
        "no_progress_count": 0,

        "intel": {
            "upi_ids": set(),
            "phone_numbers": set(),
            "links": set(),
            "domains": set(),
        },

        "messages": []  # {role, text, ts}
    }
    _SESSIONS[session_id] = s
    return s


def get_session(session_id: str) -> Dict[str, Any] | None:
    return _SESSIONS.get(session_id)


def end_session(session_id: str, reason: str) -> None:
    s = _SESSIONS.get(session_id)
    if not s:
        return
    s["status"] = "ENDED"
    s["stop_reason"] = reason


def add_message(session_id: str, role: str, text: str) -> None:
    s = _SESSIONS.get(session_id)
    if not s:
        return
    s["messages"].append({"role": role, "text": text, "ts": time.time()})


def update_last_scammer_time(session_id: str) -> None:
    s = _SESSIONS.get(session_id)
    if not s:
        return
    s["last_scammer_time"] = time.time()


def serialize_session(session_id: str) -> Dict[str, Any] | None:
    s = _SESSIONS.get(session_id)
    if not s:
        return None

    intel = s["intel"]
    return {
        "id": s["id"],
        "status": s["status"],
        "stop_reason": s["stop_reason"],
        "turns": s["turns"],
        "repeat_count": s["repeat_count"],
        "last_intent": s["last_intent"],
        "nudges": s["nudges"],
        "last_scammer_time": s["last_scammer_time"],
        "analyze_result": s["analyze_result"],
        "intel": {
            "upi_ids": sorted(list(intel["upi_ids"])),
            "phone_numbers": sorted(list(intel["phone_numbers"])),
            "links": sorted(list(intel["links"])),
            "domains": sorted(list(intel["domains"])),
        },
        "messages": s["messages"],
    }
