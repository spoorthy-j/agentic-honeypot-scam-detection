import re

HARD_KEYWORDS = [
    "bank", "blocked", "kyc", "upi", "otp",
    "immediately", "pay", "account", "verify"
]

SOFT_KEYWORDS = [
    "credit card", "reward", "reward points",
    "expiring", "redeem", "confirm details"
]

UPI_REGEX = r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}"
URL_REGEX = r"https?://\S+"
PHONE_REGEX = r"\b\d{10}\b"

def detect_scam(text: str):
    text_l = text.lower()

    reasons = []
    score = 0.0

    # Hard keywords
    for k in HARD_KEYWORDS:
        if k in text_l:
            reasons.append(f"keyword:{k}")
            score += 0.2

    # Soft keywords (credit card reward type)
    soft_count = 0
    for k in SOFT_KEYWORDS:
        if k in text_l:
            soft_count += 1

    if soft_count >= 2:
        reasons.append("pattern:reward_scam")
        score += 0.4

    # UPI / link / phone
    if re.search(UPI_REGEX, text):
        reasons.append("has_upi")
        score += 0.4

    if re.search(URL_REGEX, text):
        reasons.append("has_link")
        score += 0.4

    if re.search(PHONE_REGEX, text):
        reasons.append("has_phone")
        score += 0.3

    score = min(score, 1.0)
    is_scam = score >= 0.3

    return is_scam, score, reasons
