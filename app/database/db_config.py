from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config.settings import settings


def get_session():
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        yield session
