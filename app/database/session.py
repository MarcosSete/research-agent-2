from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings

engine = create_engine(settings.database_url, echo = False)

SessionLocal = sessionmaker(bind = engine, autoflush = False, autocommit = False)

def get_session() -> Session:
    """Cada chamada retorna uma sessão nova — uma 'conversa' com o banco."""
    return SessionLocal()


