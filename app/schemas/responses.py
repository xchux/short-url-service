from typing import Optional

from pydantic import BaseModel


class ShortenResponse(BaseModel):
    short_url: Optional[str]
    expiration_date: Optional[str]
    success: bool
    reason: Optional[str]
