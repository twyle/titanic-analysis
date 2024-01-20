from config.config import app_config
from os import path
from zipfile import ZipFile
import logging
import pandas as pd
from pandas import DataFrame
from sklearn.pipeline import Pipeline
from joblib import load
from notification import get_gmail_client, create_message, send_message


def extract_dataset(archive_name: str = 'archive.zip', file_name: str = 'Titanic-Dataset.csv') -> None:
    """Extract the downloaded archive file into the data folder."""
    # Ubuntu OS
    downloads_path: str = path.join(path.expanduser('~'), 'Downloads')
    archive_path: str = path.join(downloads_path, archive_name)
    try:
        with ZipFile(archive_path, 'r') as zip_:
            try:
                zip_.extract(file_name, app_config.data_dir)
                logging.info(f'The file {file_name} has been extracted to {path.join(app_config.data_dir, file_name)}.')
            except KeyError:
                print(f'There is no file "{file_name}" in the archive "{archive_path}".')
                logging.error(f'There is no file "{file_name}" in the archive "{archive_path}".')
    except FileNotFoundError:
        print(f'There is no archive "{archive_path}".')
        logging.error(f'There is no archive "{archive_path}".')
    return path.join(app_config.data_dir, file_name)


def load_data(file_path: str = 'Titanic-Dataset.csv') -> DataFrame:
    """Load the Titanic dataset into a dataframe."""
    try:
        data: DataFrame = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f'There is no file such file "{file_path}".')
        logging.error(f'There is no file such file "{file_path}".')
    return data


def load_model(model_path: str) -> Pipeline:
    """Load a saved model."""
    try:
        model: Pipeline = load(model_path)
    except FileNotFoundError:
        logging.error(f'There is no such model "{model_path}".')
    return model


def send_email():
    logging.info('Sending email.')
    secrets_path = app_config.secret_file
    gmail_client = get_gmail_client(secrets_path)
    message = create_message()
    message = send_message(gmail_client, message)
    logging.info('Email Sent.')
    logging.info(message)
