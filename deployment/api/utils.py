from sklearn.pipeline import Pipeline
from joblib import load
import logging
from pandas import DataFrame, Series
from .schemas import ModelInputSchema, PassengerInputSchema, ModelPrediction, ModelOutputSchema
from .extensions import redis
from .config import app_config

def get_best_model_path() -> str:
    """Get the best model path."""
    best_models: list(tuple(str, float)) = redis.zrange(name=app_config.tuned_accuracy_channel, start=-1, end=-1, withscores=True)
    best_model: str = best_models[0][0]
    best_model_path: str = f'{best_model}.pkl'
    return best_model_path


def load_model() -> Pipeline:
    """Load a saved model.
    
    Each request should fetch the storage location of the best model. Pass 
    the request a redis client.
    """
    model: Pipeline = None
    model_path: str = get_best_model_path()
    try:
        model = load(model_path)
    except FileNotFoundError:
        logging.error('There is no such model "%s".', model_path)
    except Exception as e:
        logging.error('An error occurred when loading the model.')
        logging.error(str(e))
    else:
        logging.info('Succesfully loaded the model.')
    finally:
        return model


ship_classes_map: dict[str, int] = {
    'First': 1,
    'Second': 2,
    'Third': 3
}

def preprocess_data(model_input: ModelInputSchema) -> DataFrame:
    """Preprocess the passenger data for the model."""
    df_data: list[dict[str, str | int | float]] = []
    passengers: list[PassengerInputSchema] = model_input.Passengers
    for passenger in passengers:
        data: dict[str, str | int | float] = {}
        data['PassengerId'] = passenger.PassengerId
        data['Pclass'] = ship_classes_map[passenger.PassengerClass]
        data['Name'] = passenger.Name
        data['Sex'] = passenger.Sex.lower()
        data['Ticket'] = passenger.Ticket
        data['Age'] = passenger.Age
        data['SibSp'] = passenger.SiblingSpouse
        data['Parch'] = passenger.ParentChild
        data['Fare'] = passenger.Fare
        data['Cabin'] = passenger.Cabin
        data['Embarked'] = passenger.Embarked   
        df_data.append(data)
    logging.info('Succesfully preprocessed the input data.')
    return DataFrame(df_data)


result_classes_map: dict[str, int] = {
    1: 'First',
    2: 'Second',
    3: 'Third'
}

def post_process_data(passenger_data: Series)-> dict:
    data = {
        'PassengerId': passenger_data['PassengerId'],
        'PassengerClass': result_classes_map[passenger_data['Pclass']],
        'Name': passenger_data['Name'],
        'Sex': passenger_data['Sex'].capitalize(),
        'Ticket': passenger_data['Ticket'],
        'Age': passenger_data['Age'],
        'SiblingSpouse': passenger_data['SibSp'],
        'ParentChild': passenger_data['Parch'],
        'Fare': passenger_data['Fare'],
        'Cabin': passenger_data['Cabin'],
        'Embarked': passenger_data['Embarked']
    }
    return data


def predict_survival(data: DataFrame, model: Pipeline)-> ModelOutputSchema:
    """Predixt whether the given passenger surivived."""
    survival_map: dict[int, str] = {
        1: 'Survived',
        0: 'Died'
    }
    outcomes: list[int] = model.predict(data).tolist()
    predictions: ModelOutputSchema = ModelOutputSchema(
        Predictions=[
            ModelPrediction(
                PassengerDetails=PassengerInputSchema(**post_process_data(row)),
                Outcome=survival_map[outcomes[index]]
            )
            for index, row in data.iterrows()
        ]
    )
    logging.info('Successfully predicted the survival of the passengers.')
    logging.info(predictions)
    return predictions