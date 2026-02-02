from __future__ import annotations
import re
from urllib.parse import urlparse

_UPI_RE = re.compile(r"\b[a-z0-9.\-_]{2,}@[a-z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b")
_LINK_RE = re.compile(r"\bhttps?://[^\s<>]+", re.IGNORECASE)

def extract_intel(text: str) -> dict:
    text = text or ""

    upi_ids = set(m.group(0).lower() for m in _UPI_RE.finditer(text))
    phone_numbers = set(m.group(0) for m in _PHONE_RE.finditer(text))
    links = set(m.group(0) for m in _LINK_RE.finditer(text))

    domains = set()
    for link in links:
        try:
            domains.add(urlparse(link).netloc.lower())
        except Exception:
            pass

    return {
        "upi_ids": upi_ids,
        "phone_numbers": phone_numbers,
        "links": links,
        "domains": domains,
    }
