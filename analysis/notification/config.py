from pydantic_settings import BaseSettings
from typing import Optional


class Config(BaseSettings):
    api_service_name: Optional[str] = 'gmail'
    api_version: Optional[str] = 'v1'
    credentials_file_name: Optional[str] = 'credentials.json' 
    credentials_dir: Optional[str] = '.gmail_credentials'
