from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class RedisSettings(BaseSettings):
    redis_host: str
    redis_port: int


class Config(BaseSettings):
    """The application configurations."""
    redis: RedisSettings
    tuned_accuracy_channel: str
    classifier_refresh_key: str
    classifier_refresh_period: int
    classifier_path: str = ''

app_config: Config = Config(redis=RedisSettings())
