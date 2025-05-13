import os

import redis
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.peewee_models.blacklist import Blacklist as PwBlacklist
from app.schemas.enums import BlacklistReasonEnum

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

RATE_LIMIT = 10  # requests
RATE_PERIOD = 60  # seconds
BLACKLIST_KEY = "blacklist"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        # Check blacklist
        if redis_client.hexists(BLACKLIST_KEY, ip):
            reason = redis_client.hget(BLACKLIST_KEY, ip)
            return JSONResponse(
                status_code=429,
                content={"success": False, "reason": f"Blacklisted: {reason}"},
            )
        # Rate limiting
        key = f"ratelimit:{ip}"
        current = redis_client.get(key)
        if current is None:
            redis_client.set(key, 1, ex=RATE_PERIOD)
        else:
            current = int(current)
            if current >= RATE_LIMIT:
                # Add to blacklist with reason
                redis_client.hset(BLACKLIST_KEY, ip, "rate_limit")
                PwBlacklist.insert(
                    ip=ip,
                    reason=BlacklistReasonEnum.RATE_LIMIT.value,
                ).execute()
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "reason": "Rate limit exceeded. You are blacklisted.",
                    },
                )
            else:
                redis_client.incr(key)
        response = await call_next(request)
        return response
