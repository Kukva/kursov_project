from sqlmodel import Field
from typing import Optional
from .base import Base

class PredictItem(Base):
    category_target_encoding: float
    create_launch: int
    launch_deadline: int
    goal: float
    staff_pick: int
    Nums_created: int
    launch_month_encoded: int
    name_len: float
    market_adaptability: float
    launch_weekday_encoded: int
    execution_capabilities: float
    creator_experience: float
    market_size: float
    product_market_fit: float
    Nums_backed: int
    cutting_edge_technology: float
    development_pace: float
    innovation_mentions: float
    visionary_ability: float
    
    def to_dict(self):
        return self.model_dump()