import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List

from fastapi import Depends, Request
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit import AuditLog

class AuditService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def log_event(
        self,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log an auditable event
        """
        # Get IP and user agent if request is provided
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent")

        # Convert details to JSON string if provided
        details_json = None
        if details:
            # Filter out sensitive info
            if "password" in details:
                details["password"] = "[REDACTED]"
            details_json = json.dumps(details)

        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details_json,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Add to database
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
        
    async def get_logs(
        self,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Get audit logs with optional filtering and pagination
        """
        query = self.db.query(AuditLog)
        
        # Apply filters if provided
        if action:
            query = query.filter(AuditLog.action == action)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        # Order by timestamp descending (newest first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query and return results
        return query.all()

    async def delete_old_logs(self, days: int = 30) -> int:
        """
        Delete audit logs older than the specified number of days
        Returns the number of logs deleted
        """
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Find logs older than the cutoff date
        old_logs = self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).all()
        count = len(old_logs)
        
        # Delete the logs
        if count > 0:
            self.db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).delete()
            self.db.commit()
        
        return count