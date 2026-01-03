from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)