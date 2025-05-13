from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.models.short_url import (
    generate_short_code,
    get_pw_url,
    get_pw_url_by_original,
    save_url,
    update_expiration_date,
)
from app.schemas.requests import ShortenRequest
from app.schemas.responses import ShortenResponse

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse)
def create_short_url(payload: ShortenRequest, request: Request):
    try:
        original_url = payload.original_url
    except Exception:
        return ShortenResponse(
            short_url=None,
            expiration_date=None,
            success=False,
            reason="Missing or invalid original_url",
        )
    base_url = str(request.base_url).rstrip("/")
    expiration_date = (datetime.now() + timedelta(days=30)).isoformat()
    if pw_url := get_pw_url_by_original(original_url):
        update_expiration_date(pw_url.short_code, expiration_date)
        return ShortenResponse(
            short_url=f"{base_url}/api/{pw_url.short_code}",
            expiration_date=expiration_date,
            success=True,
            reason=None,
        )
    for _ in range(5):
        short_code = generate_short_code()
        if not get_pw_url(short_code):
            break
    else:
        return ShortenResponse(
            short_url=None,
            expiration_date=None,
            success=False,
            reason="Could not generate unique short code",
        )
    try:
        save_url(short_code, original_url, expiration_date)
    except Exception:
        return ShortenResponse(
            short_url=None, expiration_date=None, success=False, reason="Database error"
        )
    short_url = f"{base_url}/api/{short_code}"
    return ShortenResponse(
        short_url=short_url, expiration_date=expiration_date, success=True, reason=None
    )


@router.get("/{short_code}")
def redirect_short_url(short_code: str):
    pw_url = get_pw_url(short_code)
    if not pw_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    original_url, expiration_date = pw_url.original_url, pw_url.expiration_date
    if datetime.now() > expiration_date:
        raise HTTPException(status_code=410, detail="Short URL expired")
    return RedirectResponse(original_url)
