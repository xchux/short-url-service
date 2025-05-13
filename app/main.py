from fastapi import FastAPI

from app.api.routers.url_router import router as url_router
from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(title="Short URL Service")

app.add_middleware(RateLimitMiddleware)
app.include_router(url_router, prefix="/api", tags=["url"])
