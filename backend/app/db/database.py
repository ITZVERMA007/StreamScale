from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os

# connection with the postgres container in docker
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://streamuser:streampassword123@postgres:5432/streamscale_db"
)

# actual connection is made here
engine = create_engine(DATABASE_URL)

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