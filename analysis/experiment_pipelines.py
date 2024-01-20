from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from experiment_config import ExperimentConfig


def create_numeric_pipeline() -> Pipeline:
    num_pipeline: Pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    return num_pipeline

def create_categorical_pipeline() -> Pipeline:
    cat_pipeline: Pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder())
    ])
    return cat_pipeline

def create_experiment_pipeline(experiment_config: ExperimentConfig) -> ColumnTransformer:
    preprocessor: ColumnTransformer = ColumnTransformer(
        transformers=[
            ('drop_columns', 'drop', experiment_config.columns_to_drop),
            ('num', create_numeric_pipeline(), experiment_config.numerical_features),
            ('cat', create_categorical_pipeline(), experiment_config.categorical_features)
        ],
        remainder='passthrough'
    )
    return preprocessor