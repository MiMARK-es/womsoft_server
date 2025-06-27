from pydantic import BaseModel
from typing import Optional
from .diagnostic import Diagnostic

class OrderCreate(BaseModel):
    patient_name: str

class Order(BaseModel):
    id: int
    patient_name: str
    doctor_id: int
    lab_tech_id: Optional[int]
    diagnostic_id: Optional[int]
    status: str

    class Config:
        orm_mode = True
