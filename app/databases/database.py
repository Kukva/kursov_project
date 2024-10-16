from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings
import subprocess

print(get_settings().DATABASE_URL_psycopg)
engine = create_engine(url=get_settings().DATABASE_URL_psycopg,
                       echo=True, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as sess:
        yield sess


def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
