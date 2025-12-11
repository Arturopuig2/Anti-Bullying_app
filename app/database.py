from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Usamos SQLite localmente, luego cambiaremos a PostgreSQL en la nube
SQLALCHEMY_DATABASE_URL = "sqlite:///./bullying_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
