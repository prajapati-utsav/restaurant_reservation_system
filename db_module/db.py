from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from decouple import config

engine = create_engine(
    f"mysql://{config('MYSQL_USER')}:{quote_plus(config('MYSQL_PASSWORD'))}@{config('MYSQL_HOST')}:{config('MYSQL_PORT')}/{config('MYSQL_DATABASE')}",
    echo=True,  # Set to False in production
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(engine)

def get_db():
    """
    Connects to the DB
    """
    try:
        _db = SessionLocal()
        yield _db
    finally:
        _db.close()