from typing import Optional
from datetime import datetime
from sqlmodel import Field
from .base import Base


class Prediction(Base, table=True):
    __tablename__ = 'prediction'
    predict_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key= 'user.id', nullable=False)
    project_name: str = Field(nullable=False)
    request_data: str = Field(nullable=False)
    prediction: int
    pred_rate: float
    analysis: str
    timestamp: datetime = Field(default_factory=datetime.now,
                                nullable=False)
    
    def __repr__(self):
        return (f"Prediction(user_id={self.user_id}, "
                f"request_data={self.request_data}, "
                f"prediction={self.prediction}, "
                f"pred_rate={self.pred_rate}, "
                f"timestamp={self.timestamp})")