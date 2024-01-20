from redis import Redis
from .config import app_config


redis: Redis = Redis(host=app_config.redis.redis_host, 
                     port=app_config.redis.redis_port, decode_responses=True)