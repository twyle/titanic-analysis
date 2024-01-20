from pydantic import BaseModel


class Metrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
