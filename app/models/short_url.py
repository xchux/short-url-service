import random
import string
from datetime import datetime

from app.models.base import get_url_hash
from app.peewee_models.urls import Urls as PwUrls


# Helper functions
def generate_short_code(length: int = 6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def save_url(short_code: str, original_url: str, expiration_date: datetime):
    PwUrls.insert(
        short_code=short_code,
        original_url=original_url,
        expiration_date=expiration_date,
    ).execute()


def get_pw_url(short_code: str):
    return PwUrls.select().where(PwUrls.short_code == short_code).get_or_none()


def get_pw_url_by_original(original_url: str):
    url_hash = get_url_hash(original_url)
    return PwUrls.select().where(PwUrls.url_hash == url_hash).get_or_none()


def update_expiration_date(short_code: str, expiration_date: datetime):
    PwUrls.update(expiration_date=expiration_date).where(
        PwUrls.short_code == short_code
    ).execute()
