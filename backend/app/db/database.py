from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.pool import QueuePool
import os

# Connection to PostgreSQL (Neon in production, local/Docker for development)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# actual connection is made here
# Pool sized for serverless PostgreSQL (Neon, Railway, etc.)
# Smaller pool prevents connection limit exhaustion
engine = create_engine(
    DATABASE_URL,
    poolclass = QueuePool,
    pool_size = 2,           # Reduced for serverless compatibility
    max_overflow = 3,        # Reduced for serverless compatibility
    pool_pre_ping = True,    # Verify connections before use
    pool_recycle = 300,      # Recycle connections every 5 min (Neon closes idle connections)
    pool_timeout = 30,       # Wait up to 30s for available connection
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