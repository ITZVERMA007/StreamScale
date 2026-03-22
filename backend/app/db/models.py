from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.db.database import Base
from datetime import datetime
import uuid

class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)

    # Filenames
    original_filename = Column(Text,nullable=False)
    input_object_name = Column(Text,nullable=False)

    # Track file processing status
    status = Column(String,nullable=False,default="PENDING")

    # Stores resolution - 360,720 ....
    resolutions = Column(ARRAY(Text),default=list)

    created_at = Column(DateTime,default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)