from pydantic_settings import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class RedisSettings(BaseSettings):
    redis_host: str
    redis_port: int

class Config(BaseSettings):
    data_dir: str
    models_dir: str
    features_dir: str
    redis: RedisSettings
    celery_broker_url: str
    celery_result_backend: str
    accuracy_channel: str
    precision_channel: str
    train_time_channel: str
    tuned_accuracy_channel: str
    tuned_precision_channel: str
    tuned_train_time_channel: str
    secret_file: str
    
app_config: Config = Config(redis=RedisSettings())