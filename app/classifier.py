def classify_scam_type(text: str) -> str:
    t = text.lower()

    if "kyc" in t or "bank" in t or "account" in t or "blocked" in t:
        return "BANK_KYC"
    if "courier" in t or "parcel" in t or "delivery" in t:
        return "COURIER"
    if "job" in t or "hr" in t or "salary" in t or "interview" in t:
        return "JOB_SCAM"
    if "lottery" in t or "winner" in t or "prize" in t:
        return "LOTTERY"
    if "anydesk" in t or "teamviewer" in t or "remote access" in t:
        return "TECH_SUPPORT"
    if "upi" in t or "pay" in t:
        return "UPI_PAYMENT"
    return "UNKNOWN"
