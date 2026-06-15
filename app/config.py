import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI:str
    DB_NAME:str
    JWT_SECRET_KEY:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 480

    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding = "utf-8")

settings = Settings()