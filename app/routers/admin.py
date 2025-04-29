from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.audit import AuditLog

# Define response models
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[str]
    timestamp: datetime
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    class Config:
        orm_mode = True

class PaginatedAuditLogs(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    limit: int
    pages: int

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Helper function to check if user is admin
async def is_admin(user: User = Depends(get_current_user)) -> User:
    # This is a placeholder - implement proper admin check based on your user roles
    # For now, we're assuming user with ID 1 is the admin
    if user.id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access admin features"
        )
    return user

@router.get("/audit-logs", response_model=PaginatedAuditLogs)
async def get_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = Query(None, description="Default is current time if start_date is provided"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering"""
    
    # Set default end_date to now if start_date is provided but end_date isn't
    if start_date and not end_date:
        end_date = datetime.now()
        
    # Build query
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
        
    # Order by timestamp descending (newest first)
    query = query.order_by(AuditLog.timestamp.desc())
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    # Get results
    logs = query.all()
    
    # Calculate total pages
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    # Return with pagination info
    return {
        "items": logs,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

@router.get("/check-access")
async def check_admin_access(current_user: User = Depends(is_admin)):
    """Endpoint to check if user has admin access"""
    return {"is_admin": True}