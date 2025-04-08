from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
from app.database import get_db
from app.models.user import User
from app.models.diagnostic import Diagnostic
from app.schemas.diagnostic import DiagnosticCreate, Diagnostic as DiagnosticSchema
from app.auth.jwt import get_current_user
import random
import string

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])

def calculate_diagnostic_result(agrin, timp2, mmp9):
    # Dummy logic - all diagnostics are positive for now
    # You can replace this later with your actual diagnostic algorithm
    return "Positive"

def generate_identifier():
    # Generate a unique identifier with timestamp component
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"WS-{timestamp}-{random_suffix}"

@router.post("/", response_model=DiagnosticSchema)
def create_diagnostic(
    diagnostic: DiagnosticCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if identifier already exists
    existing = db.query(Diagnostic).filter(Diagnostic.identifier == diagnostic.identifier).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Identifier already exists. Please use a unique identifier."
        )
    
    # Calculate diagnostic result (currently dummy logic)
    result = calculate_diagnostic_result(
        diagnostic.agrin, 
        diagnostic.timp2, 
        diagnostic.mmp9
    )
    
    db_diagnostic = Diagnostic(
        identifier=diagnostic.identifier,
        agrin=diagnostic.agrin,
        timp2=diagnostic.timp2,
        mmp9=diagnostic.mmp9,
        result=result,
        user_id=current_user.id
    )
    db.add(db_diagnostic)
    db.commit()
    db.refresh(db_diagnostic)
    return db_diagnostic

@router.get("/", response_model=List[DiagnosticSchema])
def read_diagnostics(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diagnostics = db.query(Diagnostic).filter(Diagnostic.user_id == current_user.id).offset(skip).limit(limit).all()
    return diagnostics

@router.delete("/{diagnostic_id}", status_code=204)
def delete_diagnostic(
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the diagnostic by ID
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    
    # Check if diagnostic exists
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    # Check if the diagnostic belongs to the current user
    if diagnostic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
    
    # Delete the diagnostic
    db.delete(diagnostic)
    db.commit()
    
    return None