from redis import Redis
from config.config import app_config
from celery import Celery
from utils import extract_dataset
from schemas import Model, TrainedModel, TunedModel
import logging
from schemas import Metrics
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score
from time import perf_counter
from sklearn.pipeline import Pipeline
from experiment_param_grids import hyperparameters
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator
from schemas.train_config import TrainConfig
from os import path
from utils import send_email


redis: Redis = Redis(host=app_config.redis.redis_host, port=app_config.redis.redis_port, decode_responses=True)
celery = Celery(__name__)
celery.conf.broker_url = app_config.celery_broker_url
celery.conf.result_backend = app_config.celery_result_backend
celery.conf.event_serializer = 'pickle' # this event_serializer is optional. somehow i missed this when writing this solution and it still worked without.
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'
celery.conf.accept_content = ['application/json', 'application/x-python-serialize']


@celery.task(name='send_training_report_task')
def send_training_report_task(training_result):
    try:
        logging.info('Sending the email')
        send_email()
    except Exception as e:
        logging.error(f'Unable to send email: {str(e)}')
    else:
        logging.info('Email sent')
    return training_result


@celery.task(name="train_model_task")
def train_model_task(train_config: TrainConfig):
    train_results: dict = fit_pipeline(train_config=train_config)
    trained_model: TrainedModel = TrainedModel(
        classifier_name=train_results['model_name'],
        train_date=datetime.now(),
        save_path=path.join(app_config.models_dir, 'trained', train_results['model_name']),
        owner='Lyle Okoth',
        metrics=train_results['metrics'],
        train_time=train_results['train_time']
    )
    trained_model.post_model_metrics(app_config, redis)
    return {
        'Model Name': train_results['model_name'],
        'Train Time': train_results['train_time'],
        'Metrics': train_results['metrics']
    }
    

@celery.task(name='tune_model')
def tune_model(train_config: TrainConfig):
    train_features = train_config.preprocessor.fit_transform(train_config.train_features)
    test_features = train_config.preprocessor.fit_transform(train_config.test_features)
    clf = GridSearchCV(train_config.model, hyperparameters[train_config.classifier_name], cv=10)
    best_model = clf.fit(train_features, train_config.train_labels.values.ravel())
    best_params = best_model.best_estimator_.get_params()
    preds = best_model.predict(test_features)
    accuracy = accuracy_score(preds, train_config.test_labels)
    return {
        'params': best_params,
        'acuracy': accuracy,
        'name': train_config.classifier_name
    }
    
def fit_pipeline(train_config: TrainConfig, model_params: dict = {}, train: bool = True) -> dict:
    logging.info('Training and saving the tuned model')
    untrained_model: BaseEstimator = train_config.model
    pipeline: Pipeline = Pipeline(steps=[
            ('preprocessor', train_config.preprocessor),
            ('classifier', untrained_model)
        ])
    if model_params:
        untrained_model.set_params(**model_params)
    train_start_time: float = perf_counter()
    pipeline.fit(train_config.train_features, train_config.train_labels.values.ravel())
    train_stop_time: float = perf_counter()
    predictions: list[int] = pipeline.predict(train_config.test_features).tolist()
    accuracy: float = accuracy_score(train_config.test_labels, predictions)
    precision: float = precision_score(train_config.test_labels, predictions)
    recall: float = recall_score(train_config.test_labels, predictions)
    f1: float = f1_score(train_config.test_labels, predictions)
    metrics: Metrics = Metrics(
        accuracy=round(accuracy,2),
        precision=round(precision,2),
        recall=round(recall,2),
        f1=round(f1,2)
    )
    model_train_time = train_stop_time - train_start_time
    if train:
        save_path: str = path.join(app_config.models_dir, 'trained', train_config.classifier_name)
    else:
        save_path: str = path.join(app_config.models_dir, 'tuned', train_config.classifier_name)
    Model.save_model(pipeline, save_path)
    return {
        'model_name': train_config.classifier_name,
        'metrics': metrics,
        'train_time': model_train_time
    }
    
    
@celery.task(name='train_tuned_model')
def train_tuned_model(tuned_model_data: dict, train_config: TrainConfig):
    train_results: dict = fit_pipeline(train_config=train_config, model_params=tuned_model_data['params'])
    tuned_model: TunedModel = TunedModel(
        classifier_name=train_results['model_name'],
        train_date=datetime.now(),
        save_path=path.join(app_config.models_dir, 'trained', train_results['model_name']),
        owner='Lyle Okoth',
        metrics=train_results['metrics'],
        train_time=train_results['train_time']
    )
    logging.info('Posting the model metrics.')
    tuned_model.post_model_metrics(app_config, redis)
    return {
        'Model Name': train_results['model_name'],
        'Train Time': train_results['train_time'],
        'Metrics': train_results['metrics']
    }
    