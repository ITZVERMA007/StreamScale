from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.pool import QueuePool
import os

# connection with the postgres container in docker
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# actual connection is made here
engine = create_engine(
    DATABASE_URL,
    poolclass = QueuePool,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping = True,
    pool_recycle = 3600,
    echo = False
    )

# This helps us to write queries for the database
sessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# Base for the database models
Base = declarative_base()

# This is used in the Fastapi routes
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()