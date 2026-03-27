from enum import Enum, StrEnum

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    postgres_host: str
    postgres_port: int

    kratos_public_host: str
    kratos_public_port: int
    kratos_admin_host: str
    kratos_admin_port: int
    kratos_webhook_secret: SecretStr

    log_level: LogLevel = LogLevel.INFO

    @computed_field
    @property
    def postgres_url(self) -> str:
        return f"asyncpg://{self.postgres_user}:{self.postgres_password.get_secret_value()}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @computed_field
    @property
    def kratos_public_url(self) -> str:
        return f"http://{self.kratos_public_host}:{self.kratos_public_port}"

    @computed_field
    @property
    def kratos_admin_url(self) -> str:
        return f"http://{self.kratos_admin_host}:{self.kratos_admin_port}"


settings = Settings()  # type: ignore
