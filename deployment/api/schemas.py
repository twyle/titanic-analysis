from pydantic import BaseModel, Field


class PassengerInputSchema(BaseModel):
    """The data for a single passenger."""
    PassengerId: str
    PassengerClass: str
    Name: str
    Sex: str
    Ticket: str
    Age: float
    SiblingSpouse: int
    ParentChild: int
    Fare: float
    Cabin: str
    Embarked: str

    
class ModelInputSchema(BaseModel):
    """The data for many passengers."""
    Passengers: list[PassengerInputSchema] = Field(default_factory=list)


class ModelPrediction(BaseModel):
    PassengerDetails: PassengerInputSchema
    Outcome: str


class ModelOutputSchema(BaseModel):
    """The output of the models predictions."""
    Predictions: list[ModelPrediction] = Field(default_factory=list)
    