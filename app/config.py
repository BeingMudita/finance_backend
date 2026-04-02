from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite:///./finance.db"

    FIRST_ADMIN_EMAIL: str = "admin@example.com"
    FIRST_ADMIN_PASSWORD: str = "Admin@123!"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60


settings = Settings()