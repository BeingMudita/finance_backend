from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.database import Base, SessionLocal, engine
from app.routers import auth, dashboard, records, users
from app.services.user_service import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (idempotent)
    Base.metadata.create_all(bind=engine)

    # Seed the first admin account from env config if no admin exists yet
    db = SessionLocal()
    try:
        UserService(db).ensure_admin_exists(
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
        )
    finally:
        db.close()

    yield
    # Teardown hooks can go here (e.g. close connection pools)


# Rate limiter – applies globally, can be overridden per route
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)

app = FastAPI(
    title="Finance Dashboard API",
    description=(
        "Role-based financial data management system.\n\n"
        "**Roles**: `viewer` (read-only) | `analyst` (read + write records) | `admin` (full access)\n\n"
        "All protected routes require a Bearer JWT token obtained from `POST /auth/login`."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS – tighten origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom error handlers (AppError, validation errors)
register_exception_handlers(app)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["Health"], summary="Health check")
def health():
    return {"status": "ok", "version": "1.0.0"}