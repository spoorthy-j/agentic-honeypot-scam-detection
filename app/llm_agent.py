import os
from openai import OpenAI

PERSONA_SYSTEM = {
    "confused_customer": (
        "You are a confused customer. Reply politely and short. "
        "Never share OTP/passwords. Never pay. Never click links. "
        "Ask for official details (bank name, website, reference)."
    )
}

FALLBACK_REPLY = (
    "I’m confused. Which bank is this from? Please share the official website and a reference number."
)

def generate_honeypot_reply(persona: str, history: list[dict], goal_hint: str = "") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return FALLBACK_REPLY

    # ✅ IMPORTANT: set a hard timeout so API never hangs
    client = OpenAI(api_key=api_key, timeout=8.0)

    convo = []
    for m in history[-10:]:
        role = "user" if m.get("role") == "scammer" else "assistant"
        convo.append({"role": role, "content": m.get("content", "")})

    system_msg = PERSONA_SYSTEM.get(persona, PERSONA_SYSTEM["confused_customer"])
    if goal_hint:
        system_msg = system_msg + " Goal: " + goal_hint

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=[{"role": "system", "content": system_msg}, *convo],
        )
        text = (resp.output_text or "").strip()
        return text if text else FALLBACK_REPLY

    except Exception:
        # ✅ Always return quickly
        return FALLBACK_REPLY
