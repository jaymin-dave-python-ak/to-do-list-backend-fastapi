from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DB_URL, connect_args={"check_same_thread": False})

if engine:
    print("DB Connection Established Succesfully!")

# sessionmaker is a "factory" that creates the session for us
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    with SessionLocal() as db:
        yield db
