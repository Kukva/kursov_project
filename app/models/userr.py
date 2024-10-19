from sqlmodel import Field
from typing import Optional
from .base import Base

class Userr(Base, table=True):
    __tablename__ = 'user'
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False)
    email: str = Field(index=True, nullable=False, unique=True)
    user_type: str = Field(nullable=False)