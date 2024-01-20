# titanic-analysis

This is a machine learning pipeline that trains various models, fine tunes the best and deploys the best model for use in predisction with the titanic dataset.

## Overview
This is a machine learning pipeline that was built to come up with a standard way of training, finetuning and deploying the best predictive model using the sklearn framework. This pipeline uses the titanic dataset to create models that predict whether or not a passenger would survive the sinking of the titanic.

## Getting started

To get started, you need:
- Python3 installed in your laptop
- Docker and docker-compose installed in your pipeline
- An active gmail account and gmail credentials

1. Clone the github repository
```sh
git clone https://github.com/twyle/titanic-analysis.git
```
2. Navigate to the cloned repository, create a python3 virtual environment and install the project dependancies:
```sh
cd titanic-analysis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Create the project secrets. Replace these values as neccessary. Replace the secret file with the path to your own gmail credentials from google.
```sh
DATA_DIR=/home/lyle/tutorial/titanic-analysis/analysis/data
MODELS_DIR=/home/lyle/tutorial/titanic-analysis/analysis/models
FEATURES_DIR=/home/lyle/tutorial/titanic-analysis/analysis/features
REDIS_HOST=localhost
REDIS_PORT=6379
CELERY_BROKER_URL=redis://${REDIS_HOST}:${REDIS_PORT}
CELERY_RESULT_BACKEND=redis://${REDIS_HOST}:${REDIS_PORT}
ACCURACY_CHANNEL=models:accuracy
PRECISION_CHANNEL=models:precision
TRAIN_TIME_CHANNEL=models:train_time
TUNED_ACCURACY_CHANNEL=models:tuned:accuracy
TUNED_PRECISION_CHANNEL=models:tuned:precision
TUNED_TRAIN_TIME_CHANNEL=models:tuned:train_time
SECRET_FILE=/home/lyle/tutorial/titanic-analysis/secrets.json
```
4. Start the redis container
```sh
docker-compose up --build
```
5. Start the celery worker
```
celery -A analysis/extension --worker --loglevel=INFO
```
6. Train and finetune the models: This will take a very long time
```python
python analysis/train.py
```
7. Deploy the model endpoint
```python
uvicorn deployment:manage 
```
8. Test the deployed model (This generates dummy data). An endpoint to generate custom data is in the works.
```python
python deployment/manage.py
```

#### How the whole pipeline works

###### 1. Geting the data

The dataset is obtained from kaggle as a zip file. This is unzipped and stored in a custom format, which includes the metadata such as columns

###### 2. Data Analysis

This is not covered in depth in this project

###### 3. Model Training

An experiment is created that is responsible for tarining various classification models. The models trained include:

- Nearest Neighbors
- Linear SVM
- RBF SVM
- Gaussian Process
- Decision Tree
- Random Forest
- Neural Net
- AdaBoost
- Naive Bayes
- QDA

The experiment creates two pipelines, one for preprocessing numeric features and another for categorical features. It the trains the various models.

Once done training, an email is sent to notify. The training is done using a celery task as well as the sending of the email. The accuracy and train time of each model is then added to a redis sorted set.

###### 3. Model Tuning
The best 3 models are then obtained from the sorted set. Their hyperparmeters are obtained and another celery task used to fine tune these  models. The best model is then saved.

###### 3. Model Deployment

FastAPI is used to create a model endpoint. Data is sent as a post request and the model gives back the prediction, which tells whether the person lived or died as well as the user deatils. Postgres is used to store this data for furhter analysis.

