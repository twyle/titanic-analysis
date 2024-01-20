from datetime import datetime
from .model_metrics import Metrics
from sklearn.base import BaseEstimator
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from redis import Redis
from sklearn.pipeline import Pipeline
from joblib import dump


class Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    classifier_name: str
    save_path: str
    train_date: datetime
    owner: str
    
    @staticmethod
    def save_model(model: Pipeline, save_path: str) -> str:
        save_path: str = f'{save_path}.pkl'
        return dump(model, save_path)
    
class UntrainedModel(Model):
    model: BaseEstimator

class TrainedModel(Model):
    metrics: Metrics
    train_time: float
    
    def post_model_metrics(self, app_config, redis: Redis) -> None:
        accuracy: str = app_config.accuracy_channel
        precision: str = app_config.precision_channel
        train_time: str = app_config.train_time_channel
        redis.zadd(name=accuracy, mapping={self.save_path: self.metrics.accuracy})
        redis.zadd(name=precision, mapping={self.save_path: self.metrics.precision})
        redis.zadd(name=train_time, mapping={self.save_path: self.train_time})
        
class TunedModel(TrainedModel):  
    def post_model_metrics(self, app_config, redis: Redis) -> None:
        accuracy: str = app_config.tuned_accuracy_channel
        precision: str = app_config.tuned_precision_channel
        train_time: str = app_config.tuned_train_time_channel
        redis.zadd(name=accuracy, mapping={self.save_path: self.metrics.accuracy})
        redis.zadd(name=precision, mapping={self.save_path: self.metrics.precision})
        redis.zadd(name=train_time, mapping={self.save_path: self.train_time})