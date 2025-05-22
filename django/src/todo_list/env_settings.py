from typing import Annotated, Literal

from pydantic import AfterValidator, AnyHttpUrl, BaseModel, Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


AnyHttpUrlString = Annotated[AnyHttpUrl, AfterValidator(str)]


class EnvSettings(BaseSettings):
    DJ_SECRET_KEY: str
    """Default value is missed to protect admin from common mistake when production environment
    get compromised default SECRET_KEY value.
    """

    DJ_DEBUG: bool = False
    """Disabled by default to protect admin from credentials leak on production environment
    when env variable get wrong value. That happends because of typos in names of
    environment variables and another common configuration mistakes.
    """

    DJ_ALLOWED_HOSTS: list[str] = ['127.0.0.1', 'localhost']
    DJ_CSRF_TRUSTED_ORIGINS: list[str] = ['http://127.0.0.1', 'http://localhost']
    DJ_STATIC_URL: str = 'assets/'
    DJ_MEDIA_URL: str = 'media/'

    POSTGRES_DSN: PostgresDsn

    TELEBOT_API_URL: AnyHttpUrlString = 'http://telegram-bot:5000//api/notify'
    """Web application URL to send message to reminder bot. E.g. http://telegram-bot:5000/."""

    SITE_ROOT_URL: AnyHttpUrlString
    """Web application URL to access from frontend. E.g. http://127.0.0.1:8000/ ."""

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        # Use case_sensitive=False to workaround pydantic_settings bug leading to traceback on env params parsing.
        case_sensitive=False,
        validate_default=True,
        extra="forbid",
        use_attribute_docstrings=True,
    )
