import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class WebhookPayload(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: datetime # Automatically handles ISO-8601 [cite: 47]
    text: Optional[str] = Field(None, max_length=4096)

    @field_validator("from_msisdn", "to_msisdn")
    @classmethod
    def validate_e164(cls, v: str) -> str:
        if not re.match(r"^\+\d+$", v):
            raise ValueError("Must start with + followed by digits only") # [cite: 46]
        return v