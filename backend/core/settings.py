from typing import List
from pydantic import AnyHttpUrl, AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SiteInfo(BaseSettings):
    SITE_NAME: str = "SMS Sender"
    SITE_DESCRIPTION: str = "A platform for sharing sms"
    SITE_URL: str = ""
    # SITE_URL: str = "http://localhost:3000"
    LOGO: str = f"{SITE_URL}/f_logo.png"  
    API_SITE_URL:str = ""
    FILE_READ_API:str = ""


    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sms Sender"
    API_VERSION: str = "v1"
    ENVIRONMENT: str = "development"

    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    LOG_DIR: str = "logs"
    LOG_FILE: str = "logs/app.log"

    # ALLOWED_ORIGINS: List[AnyHttpUrl] = [
    #     "http://localhost:5173",
    #     "http://localhost:3000",
    #     "https://househunter.tera-in.top",
    #     "https://www.househunter.tera-in.top",
    # ]
    ALLOWED_ORIGINS: List[str] = ["*"]

    ALLOWED_METHODS: List[str] = [
        "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"
    ]

    ALLOWED_HEADERS: List[str] = [
        "*",  # Or be more specific:
        # "Authorization",
        # "Content-Type",
        # "Accept",
        # "Origin",
        # "X-Requested-With",
        # "X-Request-ID",
        # "X-CSRF-Token",
        # "X-Client-Version",
        # "Access-Control-Request-Method",  # Added for preflight
        # "Access-Control-Request-Headers",  # Added for preflight
    ]

    EXPOSE_HEADERS: List[str] = [
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]

    MAX_AGE: int = 3600

    OPENSMS_API_TOKEN: str | None = None

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None

    EMAIL: str | None = None
    EMAIL_PASSWORD: str | None = None
    SMTP_SERVER: str = "localhost"
    SMTP_PORT: int = 587

    DATABASE_URL: str = "sqlite://db.sqlite3"
    REDIS_URL: str | None ="redis://localhost:6379/0"
 

    SITE: SiteInfo = SiteInfo()

    APARTMENT_STATS_RATE_LIMIT: str = "60/minute"
    APARTMENT_CREATE_RATE_LIMIT: str = "10/minute"
    APARTMENT_LIST_RATE_LIMIT: str = "120/minute"
    APARTMENT_SEARCH_RATE_LIMIT: str = "60/minute"
    APARTMENT_MY_LIST_RATE_LIMIT: str = "30/minute"
    APARTMENT_DETAIL_RATE_LIMIT: str = "60/minute"
    APARTMENT_UPDATE_RATE_LIMIT: str = "30/minute"
    APARTMENT_DELETE_RATE_LIMIT: str = "10/minute"
    APARTMENT_PUBLISH_RATE_LIMIT: str = "10/minute"
    APARTMENT_FEATURE_RATE_LIMIT: str = "15/minute"
    APARTMENT_APPROVE_RATE_LIMIT: str = "20/minute"
    APARTMENT_IMAGE_RATE_LIMIT: str = "20/minute"
    APARTMENT_ANALYTICS_RATE_LIMIT: str = "30/minute"
    APARTMENT_BULK_RATE_LIMIT: str = "5/minute"

    MAX_APARTMENTS_PER_USER: int = 10
    MAX_APARTMENT_IMAGES: int = 20
    MIN_APARTMENT_PRICE: float = 100.0
    MAX_APARTMENT_PRICE: float = 10000.0

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore", # CONTROL STRICTNESS TO .ENV , SWTCH TO 'forbid' IF STRICTNESS NEEDED
        case_sensitive=False
    )


settings = Settings()