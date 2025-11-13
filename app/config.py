from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "taskboard"

    @field_validator('*')
    @classmethod
    def check_not_empty(cls, v, info):
        if not v:
            raise ValueError(f'{info.field_name.upper()} is required in environment variables or .env file')
        return v

    class Config:
        env_file = ".env"


settings = Settings()