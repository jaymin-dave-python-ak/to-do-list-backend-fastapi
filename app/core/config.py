from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic automatically reads these from environment variables
    # or the specified .env file
    DB_URL: str
    TEST_DB_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_ACCESS_KEY: str
    SECRET_REFRESH_KEY:str
    ALGORITHM: str = "HS256"

    # Configuration to link the .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
