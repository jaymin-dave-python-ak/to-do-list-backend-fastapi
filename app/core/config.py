from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic automatically reads these from environment variables
    # or the specified .env file
    DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuration to link the .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
