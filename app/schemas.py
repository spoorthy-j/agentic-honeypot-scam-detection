from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MessageIn(BaseModel):
    message: str
    sender_id: Optional[str] = None

class DetectionOut(BaseModel):
    is_scam: bool
    scam_score: float
    reasons: List[str]
    extracted_intelligence: Dict[str, Any]
    memory_match: bool = False

class SessionStartIn(BaseModel):
    persona: str = "confused_customer"

class SessionStartOut(BaseModel):
    session_id: str
    persona: str

class SessionIncomingIn(BaseModel):
    message: str
