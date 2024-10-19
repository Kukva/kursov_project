from sqlmodel import Field
from typing import Optional
from .base import Base

class PredictItem(Base):
    project_name: str
    category: str
    created_date: str  
    launch_date: str   
    deadline_date: str 
    goal_amount: float
    staff_pick: int
    num_projects_created: int
    num_projects_backed: int
    project_description: str
    creator_description: str
    
    def to_dict(self):
        return self.model_dump()