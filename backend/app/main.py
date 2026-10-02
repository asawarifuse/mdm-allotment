from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import SessionLocal
from app.routers import (
    auth as auth_router,
    admin as admin_router,
    courses as courses_router,
    preferences as preferences_router,
    faculty as faculty_router,
        allotment as allotment_router,
)
from app.services.bootstrap import ensure_main_admin
from app.utils.logging import configure_logging
from app.utils.rate_limit import limiter

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        ensure_main_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})


app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(courses_router.router)
app.include_router(preferences_router.router)
app.include_router(faculty_router.router)
app.include_router(allotment_router.router)

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}