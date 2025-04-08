from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Diagnostic(Base):
    __tablename__ = "diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True)  # Added identifier field
    user_id = Column(Integer, ForeignKey("users.id"))
    agrin = Column(Float)
    timp2 = Column(Float)
    mmp9 = Column(Float)
    result = Column(String, default="Positive")
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")