from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import datetime
from app.database import get_db
from app.models.user import User
from app.models.diagnostic import Diagnostic
from app.schemas.diagnostic import DiagnosticCreate, Diagnostic as DiagnosticSchema
from app.auth.jwt import get_current_user
from app.services.audit_service import AuditService
import random
import string

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])

def calculate_diagnostic_result(protein1, protein2, protein3):
    # Dummy logic - all diagnostics are positive for now
    # You can replace this later with your actual diagnostic algorithm
    return "Positive"

def generate_identifier():
    # Generate a unique identifier with timestamp component
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"WS-{timestamp}-{random_suffix}"

@router.post("/", response_model=DiagnosticSchema)
async def create_diagnostic(
    request: Request,
    diagnostic: DiagnosticCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends()
):
    # Check if identifier already exists
    existing = db.query(Diagnostic).filter(Diagnostic.identifier == diagnostic.identifier).first()
    if existing:
        # Log duplicate identifier attempt
        await audit_service.log_event(
            action="create_diagnostic_failed",
            entity_type="diagnostic",
            entity_id=diagnostic.identifier,
            user_id=current_user.id,
            details={"reason": "duplicate_identifier"},
            request=request
        )
        raise HTTPException(
            status_code=400,
            detail="Identifier already exists. Please use a unique identifier."
        )
    
    # Calculate diagnostic result (currently dummy logic)
    result = calculate_diagnostic_result(
        diagnostic.protein1, 
        diagnostic.protein2, 
        diagnostic.protein3
    )
    
    db_diagnostic = Diagnostic(
        identifier=diagnostic.identifier,
        protein1=diagnostic.protein1,
        protein2=diagnostic.protein2,
        protein3=diagnostic.protein3,
        result=result,
        user_id=current_user.id
    )
    db.add(db_diagnostic)
    db.commit()
    db.refresh(db_diagnostic)
    
    # Log successful diagnostic creation
    await audit_service.log_event(
        action="create_diagnostic",
        entity_type="diagnostic",
        entity_id=str(db_diagnostic.id),
        user_id=current_user.id,
        details={
            "identifier": diagnostic.identifier,
            "protein1": diagnostic.protein1,
            "protein2": diagnostic.protein2,
            "protein3": diagnostic.protein3,
            "result": result
        },
        request=request
    )
    
    return db_diagnostic

@router.get("/", response_model=List[DiagnosticSchema])
async def read_diagnostics(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends()
):
    diagnostics = db.query(Diagnostic).filter(Diagnostic.user_id == current_user.id).offset(skip).limit(limit).all()
    
    # Log diagnostic data access
    await audit_service.log_event(
        action="view_diagnostics",
        entity_type="diagnostic",
        user_id=current_user.id,
        details={"count": len(diagnostics), "skip": skip, "limit": limit},
        request=request
    )
    
    return diagnostics

@router.delete("/{diagnostic_id}", status_code=204)
async def delete_diagnostic(
    request: Request,
    diagnostic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends()
):
    # Find the diagnostic by ID
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    
    # Check if diagnostic exists
    if not diagnostic:
        await audit_service.log_event(
            action="delete_diagnostic_failed",
            entity_type="diagnostic",
            entity_id=str(diagnostic_id),
            user_id=current_user.id,
            details={"reason": "not_found"},
            request=request
        )
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    # Check if the diagnostic belongs to the current user
    if diagnostic.user_id != current_user.id:
        await audit_service.log_event(
            action="delete_diagnostic_failed",
            entity_type="diagnostic",
            entity_id=str(diagnostic_id),
            user_id=current_user.id,
            details={"reason": "unauthorized", "owner_id": diagnostic.user_id},
            request=request
        )
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
    
    # Log before deletion to capture diagnostic details
    await audit_service.log_event(
        action="delete_diagnostic",
        entity_type="diagnostic",
        entity_id=str(diagnostic_id),
        user_id=current_user.id,
        details={
            "identifier": diagnostic.identifier,
            "protein1": diagnostic.protein1,
            "protein2": diagnostic.protein2,
            "protein3": diagnostic.protein3,
            "result": diagnostic.result
        },
        request=request
    )
    
    # Delete the diagnostic
    db.delete(diagnostic)
    db.commit()
    
    return None