from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiagnosticBase(BaseModel):
    protein1: float
    protein2: float
    protein3: float

class DiagnosticCreate(DiagnosticBase):
    identifier: str

class Diagnostic(DiagnosticBase):
    id: int
    identifier: str
    user_id: int
    result: str
    timestamp: datetime

    class Config:
        orm_mode = True