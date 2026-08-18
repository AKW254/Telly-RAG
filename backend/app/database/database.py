
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.engine.url import URL

from app.config.settings import settings

from contextlib import contextmanager

# --------------------------------------------------
# DATABASE URL
# --------------------------------------------------
DATABASE_URL = URL.create(
     drivername="postgresql+psycopg2",
    username=settings.db_user,
    password=settings.db_pass,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

# --------------------------------------------------
# ENGINE
# --------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    echo=settings.db_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


# --------------------------------------------------
# SESSION FACTORY(Create session with Database)
# --------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# --------------------------------------------------
# BASE MODEL(All models inherit from Base)
# --------------------------------------------------

Base = declarative_base()


# --------------------------------------------------
# INIT DB (USED IN main.py)
# --------------------------------------------------

def init_db():
   
    #Initialize database tables.
    import app.models  # ensures all models are registered
    Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# FASTAPI DEPENDENCY
# --------------------------------------------------

def get_db():
    """
    Dependency for injecting DB session into routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# CONTEXT MANAGER (ensuring resources are properly acquired and released (DB sessions, locks, etc.), even if errors occur)
# --------------------------------------------------

@contextmanager
def db_session():
    """
    Use in scripts or services:
    with db_session() as db:
        ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()