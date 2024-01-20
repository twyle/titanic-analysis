# Get the data
from utils import extract_dataset, load_data
from experiment import Experiment
from pandas import DataFrame
from schemas import DatasetMetadata
from uuid import uuid4
from os import path
from config.config import app_config
from experiment_config import ExperimentConfig
from experiment_models import models
from experiment_pipelines import create_experiment_pipeline
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# Unzip and store the downloaded dataset with its metadata
archive_name: str = 'archive.zip'
file_name: str = 'Titanic-Dataset.csv'
data_path: str = extract_dataset(archive_name, file_name)
data_path: str = extract_dataset()
data: DataFrame = load_data(data_path)
dataset_metadata: DatasetMetadata = DatasetMetadata(
    source='https://www.kaggle.com/datasets/yasserh/titanic-dataset',
    cols=data.columns.values.tolist(),
    description='A dataset that shows the survivors of the titanic tragedy.',
    path=data_path,
    id=f'Dataset_{str(uuid4())}'
)
dataset_metadata_path: str = path.join(app_config.data_dir, 'titanic_metadata.json')
dataset_metadata.save(dataset_metadata_path)

# Create an experiment for training various models
label_cols: list[str] = ['Survived']
feature_cols: list[str] = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', "PassengerId", "Name", "Ticket", "Cabin"]
columns_to_drop: list[str] = ["PassengerId", "Name", "Ticket", "Cabin"]
numerical_features: list[str] = ["Age", "Fare"]
categorical_features: list[str] = ["Pclass", "Sex", "Embarked"]
experiment_config: ExperimentConfig = ExperimentConfig(
    data_dir=app_config.data_dir,
    models_directory=app_config.models_dir,
    features_dir=app_config.features_dir,
    dataset_metadata=dataset_metadata,
    label_columns=label_cols,
    feature_cols=feature_cols,
    columns_to_drop=columns_to_drop,
    numerical_features=numerical_features,
    categorical_features=categorical_features
)

experiment: Experiment = Experiment(
    experiment_config=experiment_config,
    preprocessor=create_experiment_pipeline(experiment_config),
    models=models
)
experiment.run()
# experiment.get_results()
# experiment.tune_best_models()
# experiment.get_tuned_models()
# print(experiment.get_best_models(start=-3, end=-1)) 