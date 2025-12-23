from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: Annotated[str, Field(validation_alias="TELEGRAM_BOT_TOKEN")]
    POSTGRES_HOST: Annotated[str, Field(validation_alias="POSTGRES_HOST")]
    POSTGRES_DB: Annotated[str, Field(validation_alias="POSTGRES_DB")]
    POSTGRES_PORT: Annotated[str, Field(validation_alias="POSTGRES_PORT")]
    POSTGRES_USER: Annotated[str, Field(validation_alias="POSTGRES_USER")]
    POSTGRES_PASSWORD: Annotated[str, Field(validation_alias="POSTGRES_PASSWORD")]

    APPLICATION_NAME: Annotated[
        str,
        Field(validation_alias="APPLICATION_NAME", default="video-analytics-bot")
    ]

    POOL_SIZE: Annotated[int, Field(validation_alias="POOL_SIZE")]
    MAX_OVERFLOW: Annotated[int, Field(validation_alias="MAX_OVERFLOW")]

    LLM_MODEL: Annotated[str, Field(validation_alias="LLM_MODEL")]
    LLM_BASE_URL: Annotated[str, Field(validation_alias="LLM_BASE_URL")]
    LLM_PROVIDER: Annotated[str, Field(validation_alias="LLM_PROVIDER")]
    LLM_TIMEOUT: Annotated[int, Field(validation_alias="LLM_TIMEOUT")]
    LLM_TEMPERATURE: Annotated[float, Field(validation_alias="LLM_TEMPERATURE")]
    LLM_MAX_TOKENS: Annotated[int, Field(validation_alias="LLM_MAX_TOKENS")]

    PROMPT_INCLUDE_EXAMPLES: Annotated[bool, Field(validation_alias="PROMPT_INCLUDE_EXAMPLES")]
    PROMPT_INCLUDE_VALIDATION_RULES: Annotated[
        bool,
        Field(validation_alias="PROMPT_INCLUDE_VALIDATION_RULES")
    ]
    PROMPT_MAX_LENGTH: Annotated[int, Field(validation_alias="PROMPT_MAX_LENGTH")]

    LOG_LEVEL: Annotated[str, Field(validation_alias="LOG_LEVEL")]
    LOG_LLM_REQUESTS: Annotated[bool, Field(validation_alias="LOG_LLM_REQUESTS")]

    # .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self):
        """Generate an asynchronous PostgreSQL database URL for application connections.

        :returns:
            url: the database connection URL with asyncpg driver
        """
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


    @property
    def llm_config(self) -> dict:
        return {
            "model": self.LLM_MODEL,
            "base_url": self.LLM_BASE_URL,
            "timeout": self.LLM_TIMEOUT,
            "temperature": self.LLM_TEMPERATURE,
            "max_tokens": self.LLM_MAX_TOKENS,
        }

settings = Settings()
