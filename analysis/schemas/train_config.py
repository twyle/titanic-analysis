from pydantic import BaseModel, ConfigDict
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator
from pandas import Series, DataFrame


class TrainConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    preprocessor: ColumnTransformer
    model: BaseEstimator
    train_features: DataFrame
    train_labels: DataFrame
    test_features: DataFrame
    test_labels: DataFrame
    classifier_name: str
    save_path: str