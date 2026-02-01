from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.common.settings import settings

Base = declarative_base()
engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
