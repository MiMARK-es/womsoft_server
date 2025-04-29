import pytest
from fastapi.testclient import TestClient
import json
from app.models.audit import AuditLog
from app.models.user import User
from datetime import datetime, timedelta

class TestAuditLoggingIntegration:
    
    def test_login_generates_audit_log(self, client, db_session, admin_user):
        """Test that successful login creates an audit log entry"""

        login_data = {
            "username": "adminuser",
            "password": "admin123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        # Print debug info if login fails
        if response.status_code != 200:
            print(f"Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Users in DB: {[u.username for u in db_session.query(User).all()]}")
        
        # Assert - login successful
        assert response.status_code == 200
        
        # Check that an audit log was created
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == "login_success",
            AuditLog.entity_type == "user"
        ).order_by(AuditLog.id.desc()).first()
        
        assert audit_log is not None
        assert audit_log.user_id is not None  # Should be test user's ID
    
    def test_failed_login_generates_audit_log(self, client, db_session):
        """Test that failed login creates an audit log entry"""
        # Arrange - invalid credentials
        login_data = {
            "username": "adminuser",
            "password": "wrongpassword"
        }
        
        # Act - perform login with wrong password
        response = client.post(
            "/api/auth/login",
            data=login_data
        )
        
        # Assert - login failed
        assert response.status_code == 401
        
        # Check that an audit log was created for the failed attempt
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == "login_failed",
            AuditLog.entity_type == "user",
            AuditLog.entity_id == "adminuser"
        ).order_by(AuditLog.id.desc()).first()
        
        assert audit_log is not None
        assert audit_log.user_id is None  # No user ID for failed login
        assert "invalid_credentials" in audit_log.details
    
    def test_api_access_generates_audit_log(self, client, token_headers, db_session):
        """Test that API access is logged through middleware"""
        # Act - make a GET request to an API endpoint
        response = client.get(
            "/api/diagnostics/",
            headers=token_headers
        )
        
        # Assert - request successful
        assert response.status_code == 200
        
        # Check that an audit log was created
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.action == "view_diagnostics",
            AuditLog.entity_type == "diagnostic"
        ).order_by(AuditLog.id.desc()).first()
        
        assert audit_log is not None
        # The user_id will be the test user's ID (2, as it's created after admin)
        assert audit_log.user_id == 2
    
    def test_admin_audit_log_access(self, client, db_session, admin_user):
        """Test that admin can access audit logs API"""
        # Arrange - login as admin
        login_data = {
            "username": "adminuser",
            "password": "admin123"
        }
        
        login_response = client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200
        admin_token = login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Add some audit logs
        now = datetime.now()
        test_log = AuditLog(
            user_id=1,
            action="test_action",
            entity_type="test",
            entity_id="123",
            timestamp=now,
            details='{"test": true}'
        )
        db_session.add(test_log)
        db_session.commit()
        
        # Act - access audit logs endpoint
        response = client.get(
            "/api/admin/audit-logs",
            headers=admin_headers
        )
        
        # Assert - admin can access logs
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        
        # Verify our test log is included
        log_actions = [log["action"] for log in data["items"]]
        assert "test_action" in log_actions
        
        # Test filtering
        filter_response = client.get(
            "/api/admin/audit-logs?action=test_action",
            headers=admin_headers
        )
        assert filter_response.status_code == 200
        filtered_data = filter_response.json()
        assert len(filtered_data["items"]) >= 1
        assert all(log["action"] == "test_action" for log in filtered_data["items"])