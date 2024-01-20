from pydantic import BaseModel
from .dataset_metadata import DatasetMetadata
from pandas import DataFrame
import pandas as pd


class DataSet(BaseModel):
    metadata: DatasetMetadata
    
    @property
    def dataset_path(self) -> str:
        return self.metadata.path

    def get_dataset(self) -> DataFrame:
        """Load the dataset."""
        data: DataFrame = pd.read_csv(self.dataset_path)
        return data
