import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default SQLite database path inside app/sketch2ui.db
APP_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = APP_DIR / "sketch2ui.db"

raw_db_url = os.getenv("DATABASE_URL")
if raw_db_url and raw_db_url.strip():
    db_url = raw_db_url.strip()
    # Normalize legacy Heroku/Render postgres:// scheme to postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    # Ensure standard forward-slash URI format for SQLite
    db_url = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency yielding a scoped SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes and creates all database tables if they do not exist."""
    import app.models.user  # noqa: F401
    import app.models.project  # noqa: F401
    Base.metadata.create_all(bind=engine)
