from pydantic import BaseModel, Field, field_validator


class ShortenRequest(BaseModel):
    original_url: str = Field(..., description="The original URL to be shortened")

    @field_validator("original_url")
    def validate_url(cls, v):
        v = v.strip()
        if len(v) > 2048:
            raise ValueError("URL too long")
        # Basic URL validation
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Invalid URL")
        return v
