from pydantic import BaseModel
from typing import List, Optional


class SMSRequest(BaseModel):
    recipient: List[str]
    message: str
    type: Optional[str] = "plain"
    schedule_time: Optional[str] = None