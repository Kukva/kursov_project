from sqlmodel import Field
from typing import Optional
from .base import Base

class User(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    email: str = Field(index=True, nullable=False, unique=True)
    user_type: str = Field(nullable=False)
    fr_model_type: str = Field(nullable=False)