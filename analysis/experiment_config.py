from pydantic import BaseModel, Field
from schemas import DatasetMetadata
from datetime import datetime
from json import dump


class ExperimentConfig(BaseModel):
    data_dir: str
    models_directory: str
    features_dir: str
    dataset_metadata: DatasetMetadata
    label_columns: list[str] = Field(default_factory=list)
    feature_cols: list[str] = Field(default_factory=list)
    columns_to_drop: list[str] = Field(default_factory=list)
    numerical_features: list[str] = Field(default_factory=list)
    categorical_features: list[str] = Field(default_factory=list)
    
    def save_experiment_config(self, path: str,
            title: str = '', 
            description: str = '', 
            date: datetime=datetime.now()
        ) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            dump(self.model_dump(), f, indent=4)
        
        
