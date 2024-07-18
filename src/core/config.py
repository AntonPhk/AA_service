from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib

ENVDIR = str(pathlib.Path(__file__).parent.absolute()) + "/../.."


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENVDIR + "/.env")

    SERVICE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_CONTAINER_HOST: str

    @property
    def postgres_url_async(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    REDIS_PORT: str
    REDIS_HOST: str
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_DATABASES: int
    REDIS_CONTAINER_HOST: str

    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    ROLES: str
    PERMISSIONS: str

    SMTP_SERVER: str
    SMTP_PORT: int
    MAIL_USER: str
    MAIL_PASSWORD: str


settings = Settings()
