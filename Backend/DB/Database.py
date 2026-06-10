# database.py
# Sets up the SQLAlchemy connection to MySQL.
# get_db() is a FastAPI dependency — it opens a DB connection
# for a request and closes it when the request finishes.
#
# Usage in a router:
#   def my_route(db: Session = Depends(get_db)):
#       users = db.query(User).all()

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from Backend.core.config import settings

# create_engine builds the connection pool — pool_pre_ping checks
# that the connection is still alive before using it
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,   # logs every SQL query in DEBUG mode
)

# SessionLocal is a factory — call SessionLocal() to get a new DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# All ORM models will inherit from this Base
class Base(DeclarativeBase):
    pass


# ── FastAPI dependency ────────────────────────────────────────
def get_db():
    """
    Yield a database session for the duration of one HTTP request.
    The finally block ensures the connection is always returned to the pool.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()