from fastapi import FastAPI
from .utils import load_model, preprocess_data, predict_survival
from sklearn.pipeline import Pipeline
from .config import app_config
from .schemas import ModelInputSchema, ModelOutputSchema
import logging
from pandas import DataFrame

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

def create_app():
    """Create the FastAPI app model."""
    app: FastAPI = FastAPI()

    @app.post('/predict', tags=['Predictions'])
    async def predict(model_input: ModelInputSchema):
        """Predict whether or not a passenger survived."""
        logging.info('Preprocessing the input data.')
        passenger_df: DataFrame = preprocess_data(model_input)
        logging.info('Predicting the survival of the passengers.')
        predictions: ModelOutputSchema = predict_survival(passenger_df, load_model())
        return predictions
    
    return app