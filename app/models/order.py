from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class TestOrder(Base):
    __tablename__ = "test_orders"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    lab_tech_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"), nullable=True)
    status = Column(String, default="pending")

    doctor = relationship("User", foreign_keys=[doctor_id])
    lab_tech = relationship("User", foreign_keys=[lab_tech_id])
    diagnostic = relationship("Diagnostic")
