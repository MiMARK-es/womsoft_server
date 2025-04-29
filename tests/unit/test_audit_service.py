import pytest
from app.services.audit_service import AuditService
from app.models.audit import AuditLog
import json
from datetime import datetime, timedelta
from sqlalchemy import desc
import uuid

class TestAuditService:
    
    @pytest.mark.asyncio
    async def test_log_event_creates_audit_record(self, db_session):
        """Test that log_event creates an audit record with correct data"""
        # Arrange
        audit_service = AuditService(db_session)
        test_action = "test_action"
        test_entity_type = "test_entity"
        test_entity_id = "123"
        test_user_id = 1
        test_details = {"key": "value", "test": True}
        
        # Act
        log_entry = await audit_service.log_event(
            action=test_action,
            entity_type=test_entity_type,
            entity_id=test_entity_id,
            user_id=test_user_id,
            details=test_details
        )
        
        # Assert
        assert log_entry.id is not None
        assert log_entry.action == test_action
        assert log_entry.entity_type == test_entity_type
        assert log_entry.entity_id == test_entity_id
        assert log_entry.user_id == test_user_id
        
        # Verify details were serialized correctly
        stored_details = json.loads(log_entry.details)
        assert stored_details["key"] == "value"
        assert stored_details["test"] is True
        
        # Check database persistence
        db_entry = db_session.query(AuditLog).filter(AuditLog.id == log_entry.id).first()
        assert db_entry is not None
        assert db_entry.action == test_action
    
    @pytest.mark.asyncio
    async def test_log_event_with_complex_details(self, db_session):
        """Test that complex nested data structures are correctly serialized"""
        # Arrange
        audit_service = AuditService(db_session)
        complex_details = {
            "nested": {
                "deeper": {
                    "list": [1, 2, 3],
                    "dict": {"a": 1, "b": 2}
                }
            },
            "array": [{"name": "item1"}, {"name": "item2"}],
            "null_value": None,
            "bool_value": True,
            "number": 12345
        }
        
        # Act
        log_entry = await audit_service.log_event(
            action="complex_test",
            entity_type="test",
            entity_id="complex-123",
            user_id=1,
            details=complex_details
        )
        
        # Assert
        stored_details = json.loads(log_entry.details)
        assert stored_details["nested"]["deeper"]["list"] == [1, 2, 3]
        assert stored_details["nested"]["deeper"]["dict"]["a"] == 1
        assert stored_details["array"][1]["name"] == "item2"
        assert stored_details["null_value"] is None
        assert stored_details["bool_value"] is True
        assert stored_details["number"] == 12345
    
    @pytest.mark.asyncio
    async def test_get_logs_pagination(self, db_session):
        """Test retrieving logs with pagination"""
        # Arrange
        audit_service = AuditService(db_session)
        # Create 10 log entries
        for i in range(10):
            await audit_service.log_event(
                action=f"action_{i}",
                entity_type="test",
                entity_id=str(i),
                user_id=1,
                details={"index": i}
            )
        
        # Act - get first page (5 items)
        page1 = await audit_service.get_logs(limit=5, offset=0)
        # Get second page
        page2 = await audit_service.get_logs(limit=5, offset=5)
        
        # Assert
        assert len(page1) == 5
        assert len(page2) == 5
        # Check that items are different between pages
        page1_ids = [log.id for log in page1]
        page2_ids = [log.id for log in page2]
        assert not set(page1_ids).intersection(set(page2_ids))
    
    @pytest.mark.asyncio
    async def test_get_logs_with_filters(self, db_session):
        """Test filtering logs by various criteria"""
        # Arrange
        audit_service = AuditService(db_session)
        # Create logs with different actions and entity types
        await audit_service.log_event(
            action="create", entity_type="user", entity_id="1", user_id=1, details={}
        )
        await audit_service.log_event(
            action="update", entity_type="user", entity_id="1", user_id=1, details={}
        )
        await audit_service.log_event(
            action="delete", entity_type="user", entity_id="1", user_id=2, details={}
        )
        await audit_service.log_event(
            action="create", entity_type="post", entity_id="1", user_id=1, details={}
        )
        
        # Act - filter by action
        create_logs = await audit_service.get_logs(action="create")
        # Filter by entity_type
        user_logs = await audit_service.get_logs(entity_type="user")
        # Filter by user_id
        user1_logs = await audit_service.get_logs(user_id=1)
        # Combined filters
        create_user_logs = await audit_service.get_logs(action="create", entity_type="user")
        
        # Assert
        assert len(create_logs) == 2  # create user + create post
        assert len(user_logs) == 3    # all user operations
        assert len(user1_logs) == 3   # all operations by user 1
        assert len(create_user_logs) == 1  # only create user
    
    @pytest.mark.asyncio
    async def test_get_logs_date_range(self, db_session):
        """Test filtering logs by date range"""
        # Arrange
        audit_service = AuditService(db_session)
        
        # Create logs with different timestamps by directly setting the timestamp
        # Since we can't easily mock datetime.now() in the service
        now = datetime.now()
        
        # Create log from yesterday
        yesterday_log = AuditLog(
            action="old_action",
            entity_type="test",
            entity_id="old",
            user_id=1,
            details=json.dumps({"old": True}),
            timestamp=now - timedelta(days=1)
        )
        db_session.add(yesterday_log)
        
        # Create log from today
        today_log = AuditLog(
            action="new_action",
            entity_type="test",
            entity_id="new",
            user_id=1,
            details=json.dumps({"new": True}),
            timestamp=now
        )
        db_session.add(today_log)
        db_session.commit()
        
        # Act - get logs from last 12 hours
        recent_logs = await audit_service.get_logs(
            start_date=now - timedelta(hours=12),
            end_date=now + timedelta(hours=1)  # Add buffer for test execution time
        )
        
        # Get all logs
        all_logs = await audit_service.get_logs()
        
        # Assert
        assert len(recent_logs) == 1
        assert recent_logs[0].action == "new_action"
        assert len(all_logs) >= 2  # Should include both logs plus any from other tests
    
    @pytest.mark.asyncio
    async def test_delete_logs(self, db_session):
        """Test deleting old audit logs"""
        # Arrange
        audit_service = AuditService(db_session)
        now = datetime.now()
        
        # Create an old log
        old_log = AuditLog(
            action="delete_me",
            entity_type="test",
            entity_id="old",
            user_id=1,
            details=json.dumps({"old": True}),
            timestamp=now - timedelta(days=90)  # 90 days old
        )
        db_session.add(old_log)
        
        # Create a recent log
        recent_log = AuditLog(
            action="keep_me",
            entity_type="test",
            entity_id="recent",
            user_id=1,
            details=json.dumps({"recent": True}),
            timestamp=now
        )
        db_session.add(recent_log)
        db_session.commit()
        
        # Act - delete logs older than 30 days
        deleted_count = await audit_service.delete_old_logs(days=30)
        
        # Get remaining logs
        remaining_logs = await audit_service.get_logs()
        
        # Assert
        assert deleted_count >= 1  # Should have deleted at least the old log
        assert all(log.action != "delete_me" for log in remaining_logs)
        assert any(log.action == "keep_me" for log in remaining_logs)