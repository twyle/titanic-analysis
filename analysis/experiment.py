from experiment_config import ExperimentConfig
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator
from schemas import DataSet, Model
from pandas import DataFrame, Series
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from extensions import train_model_task, send_training_report_task, redis, tune_model, train_tuned_model
from celery.result import AsyncResult
import logging
from celery import chord
from experiment_models import models
from time import sleep
from config.config import app_config
from schemas.train_config import TrainConfig


class Experiment:
    def __init__(self, experiment_config: ExperimentConfig, preprocessor: ColumnTransformer, models: dict[str, BaseEstimator]):
        self.experiment_config = experiment_config
        self.preprocessor = preprocessor
        self.models = models
        self.dataset: DataSet = DataSet(metadata=experiment_config.dataset_metadata)
        self.trained_models: list[Model] = []
        self.train_task_ids: list[str] = []
    
    def get_features(self) -> DataFrame:
        data: DataFrame = self.dataset.get_dataset()
        features: DataFrame = data[self.experiment_config.feature_cols]
        return features

    def get_labels(self) -> Series:
        data: DataFrame = self.dataset.get_dataset()
        labels: Series = data[self.experiment_config.label_columns]
        return labels

    def get_train_test_data(self) -> ((DataFrame, Series), (DataFrame, Series)):
        features = self.get_features()
        labels = self.get_labels()
        train_features, test_features, train_labels, test_labels = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        return (train_features, train_labels), (test_features, test_labels)

    def save_features(self) -> DataFrame:
        pass

    def save_labels(self) -> DataFrame:
        pass

    def train_model(self, model: Model) -> float:
        (train_features, train_labels), (test_features, test_labels) = self.get_train_test_data()
        pipeline: Pipeline = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('classifier', model.model)
        ])
        logging.info('Queing the model "%s" for training.', model.name)
        res: AsyncResult = train_model_task.delay(pipeline, train_features, train_labels, test_features, test_labels, model.name, model.save_path)
        self.train_task_ids.append(res.id)
        return res.id
        

    def run(self) -> None:  
        self._train_results = chord((train_model_task.s(
            self.create_train_config(model=model.model, name=model.classifier_name, save_path=model.save_path)
            ) for model in self.models), send_training_report_task.s())()
      
    def get_results(self) -> list[Model]:
        """Get the training result."""
        logging.info('Getting the training results')
        print(self._train_results.get())
        
    def get_best_models(self, start: int = 0, end: int = -1) -> Model:
        best_models = redis.zrange(name=app_config.accuracy_channel, start=start, end=end, withscores=True)
        return best_models
        
    def tune_best_models(self) -> None:
        logging.info('Tuning the best models.')
        best_models = self.get_best_models(start=-3, end=-1)
        logging.info(best_models)
        self.tuned_model_ids = []
        for model_path, _ in best_models:
            logging.info(model_path)
            model_name: str = model_path.split('/')[-1]
            for model in models:
                if model_name == model.classifier_name:
                    train_config: TrainConfig = self.create_train_config(model.model, model.classifier_name, model.save_path)
                    res = tune_model.apply_async((train_config,), 
                        link=train_tuned_model.s(train_config,)
                    )
                    self.tuned_model_ids.append(res.id)
                    logging.info('%s queued for tuning and retraining.', model_name)
                        
    def get_tuned_models(self):
        best_model_names = [name.split('/')[-1] for name, _ in self.get_best_models(start=-3, end=-1)]
        while self.tuned_model_ids:
            for index, id in enumerate(self.tuned_model_ids):
                res: AsyncResult = AsyncResult(id)
                if res.ready():
                    logging.info('Tuned Model result for %s is ready.', res.result['name'])
                    logging.info(res.result)
                    self.tuned_model_ids.pop(index)
                    best_model_names.remove(res.result['name'])
                names = ', '.join(best_model_names)
                if names:
                    logging.info('Tuned Model result for %s are not ready.', names)
                sleep(3)
                
    def create_train_config(self, model: BaseEstimator, name: str, save_path: str) -> TrainConfig:
        (train_features, train_labels), (test_features, test_labels) = self.get_train_test_data()
        train_config: TrainConfig = TrainConfig(
            preprocessor=self.preprocessor,
            model=model,
            classifier_name=name,
            save_path=save_path,
            train_features=train_features,
            train_labels=train_labels,
            test_features=test_features,
            test_labels=test_labels
        )
        return train_config