from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # e.g., "login", "create_diagnostic", "view_patient"
    entity_type = Column(String, nullable=False)  # e.g., "user", "patient", "diagnostic"
    entity_id = Column(String, nullable=True)  # ID of the affected entity
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    details = Column(Text, nullable=True)  # JSON-encoded additional details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Relationship to user (optional)
    user = relationship("User", back_populates="audit_logs")