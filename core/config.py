from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "LIBRARYISSECRETKEY"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./knihovna.db"

settings = Settings()