from collections import defaultdict
from datetime import datetime
from typing import Dict, List

# In-memory IOC store
# Later you can replace this with PostgreSQL
IOC_MEMORY = {
    "upi_ids": defaultdict(int),
    "domains": defaultdict(int),
    "phishing_links": defaultdict(int),
    "phone_numbers": defaultdict(int),
}

IOC_TIMESTAMPS = {
    "upi_ids": {},
    "domains": {},
    "phishing_links": {},
    "phone_numbers": {},
}

# -----------------------------
# Store extracted intelligence
# -----------------------------
def store_iocs(iocs: Dict[str, List[str]]):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for ioc_type, values in iocs.items():
        if ioc_type not in IOC_MEMORY:
            continue

        for v in values:
            IOC_MEMORY[ioc_type][v] += 1

            if v not in IOC_TIMESTAMPS[ioc_type]:
                IOC_TIMESTAMPS[ioc_type][v] = {
                    "first_seen": now,
                    "last_seen": now,
                }
            else:
                IOC_TIMESTAMPS[ioc_type][v]["last_seen"] = now

# -----------------------------
# Match incoming text IOCs
# -----------------------------
def match_any_ioc(iocs: Dict[str, List[str]]) -> Dict[str, List[str]]:
    hits = {
        "upi_ids": [],
        "domains": [],
        "phishing_links": [],
        "phone_numbers": [],
    }

    for ioc_type, values in iocs.items():
        if ioc_type not in IOC_MEMORY:
            continue

        for v in values:
            if v in IOC_MEMORY[ioc_type]:
                hits[ioc_type].append(v)

    return hits

# -----------------------------
# Boolean helper for main.py
# -----------------------------
def memory_match(iocs: Dict[str, List[str]]) -> bool:
    hits = match_any_ioc(iocs)
    return any(len(v) > 0 for v in hits.values())

# -----------------------------
# Get top known IOCs
# -----------------------------
def get_top_iocs(limit: int = 10):
    results = []

    for ioc_type, values in IOC_MEMORY.items():
        for v, count in values.items():
            meta = IOC_TIMESTAMPS[ioc_type].get(v, {})
            results.append({
                "type": ioc_type[:-1],  # remove plural
                "value": v,
                "count": count,
                "first_seen": meta.get("first_seen"),
                "last_seen": meta.get("last_seen"),
            })

    results.sort(key=lambda x: x["count"], reverse=True)
    return results[:limit]
