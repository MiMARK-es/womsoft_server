from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiagnosticBase(BaseModel):
    agrin: float
    timp2: float
    mmp9: float

class DiagnosticCreate(DiagnosticBase):
    identifier: str  # Added identifier field to be provided by user

class Diagnostic(DiagnosticBase):
    id: int
    identifier: str
    user_id: int
    result: str
    timestamp: datetime

    class Config:
        orm_mode = True