# config.py
# Reads all settings from the .env file.
# Access anywhere: from app.core.config import settings

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str="DATABASE_URL =mysql+pymysql://root:Root%4018@localhost:3306/taskflow_db"

    # JWT
    JWT_SECRET: str ="271444ccec92540b652b4ced82d397af73b6b299c29ba52cd600a94a8eab84d6"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:3000"
    BCRYPT_ROUNDS: int = 12

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = "Backend/.env"


# lru_cache means Settings() is only created once — not on every import
@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()