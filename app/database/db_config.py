from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config.settings import Settings


def get_session():
    engine = create_engine(Settings().DATABASE_URL)
    with Session(engine) as session:
        yield session
