from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ans_database"
    DB_USER: str = "ans_user"
    DB_PASSWORD: str = "ans_pass123"

    API_TITLE: str = "ANS Operadoras API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API para consulta de dados de operadoras de saúde"

    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
