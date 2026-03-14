from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware


from core.limiter import limiter
from core.settings import settings


from api.router import api_router

app = FastAPI(
    # max_request_size=50 * 1024 * 1024,  # 10MB limit instead of default 1MB
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
    expose_headers=settings.EXPOSE_HEADERS,
    max_age=settings.MAX_AGE,
)

app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter

app.include_router(api_router, prefix="/api")


# uvicorn app:app --reload