from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = "datapulse"
    postgres_password: str = "datapulse"
    postgres_db: str = "datapulse"
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    api_base_url: str = "http://localhost:8010"
    data_incoming_dir: str = "data/incoming"
    data_processed_dir: str = "data/processed"
    data_quarantine_dir: str = "data/quarantine"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
