from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    protein1 = Column(Float)  # Changed from agrin
    protein2 = Column(Float)  # Changed from timp2
    protein3 = Column(Float)  # Changed from mmp9
    result = Column(String, default="Positive")
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")