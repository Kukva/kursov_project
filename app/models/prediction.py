from typing import Optional
from datetime import datetime
from sqlmodel import Field
from .base import Base


class Prediction(Base, table=True):
    predict_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    request_data: str = Field(nullable=False)
    prediction: int
    mark: float
    pred_rate: float
    timestamp: datetime = Field(default_factory=datetime.now,
                                nullable=False)