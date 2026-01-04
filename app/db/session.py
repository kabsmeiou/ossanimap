from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .base import Base

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()