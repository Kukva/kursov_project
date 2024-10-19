from sqlmodel import Session, create_engine
from models.base import Base
from models.userr import Userr
from models.prediction import Prediction
from .config import get_settings
import subprocess

print(get_settings().DATABASE_URL_psycopg)
engine = create_engine(url=get_settings().DATABASE_URL_psycopg,
                       echo=True, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as sess:
        yield sess


def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)