import pytest
from fastapi.testclient import TestClient

class TestDiagnosticAPI:
    def test_create_diagnostic_requires_all_fields(self, client, token_headers):
        """
        Test that creating a diagnostic entry requires all fields to have values.
        """
        # 1. Test with missing identifier
        incomplete_data = {
            "protein1": 1.5,
            "protein2": 2.3,
            "protein3": 3.1
        }
        response = client.post(
            "/api/diagnostics/",
            json=incomplete_data,
            headers=token_headers
        )
        assert response.status_code == 422, "Missing identifier should return validation error"
        
        # 2. Test with missing protein1
        incomplete_data = {
            "identifier": "TEST-ID-1",
            "protein2": 2.3,
            "protein3": 3.1
        }
        response = client.post(
            "/api/diagnostics/",
            json=incomplete_data,
            headers=token_headers
        )
        assert response.status_code == 422, "Missing protein1 should return validation error"
        
        # 3. Test with missing protein2
        incomplete_data = {
            "identifier": "TEST-ID-1",
            "protein1": 1.5,
            "protein3": 3.1
        }
        response = client.post(
            "/api/diagnostics/",
            json=incomplete_data,
            headers=token_headers
        )
        assert response.status_code == 422, "Missing protein2 should return validation error"
        
        # 4. Test with missing protein3
        incomplete_data = {
            "identifier": "TEST-ID-1",
            "protein1": 1.5,
            "protein2": 2.3
        }
        response = client.post(
            "/api/diagnostics/",
            json=incomplete_data,
            headers=token_headers
        )
        assert response.status_code == 422, "Missing protein3 should return validation error"
        
        # 5. Test with all fields present (should succeed)
        complete_data = {
            "identifier": "TEST-ID-1",
            "protein1": 1.5,
            "protein2": 2.3,
            "protein3": 3.1
        }
        response = client.post(
            "/api/diagnostics/",
            json=complete_data,
            headers=token_headers
        )
        assert response.status_code == 200, "Complete data should be accepted"
        assert "result" in response.json()
        assert response.json()["result"] == "Positive"

    def test_diagnostic_result_is_always_positive(self, client, token_headers):
        """
        Test that all created diagnostic entries have a 'Positive' result.
        """
        # Create diagnostic entry
        diagnostic_data = {
            "identifier": "TEST-ID-2",
            "protein1": 1.5,
            "protein2": 2.3,
            "protein3": 3.1
        }
        response = client.post(
            "/api/diagnostics/",
            json=diagnostic_data,
            headers=token_headers
        )
        assert response.status_code == 200
        assert response.json()["result"] == "Positive"

        # Get all diagnostic entries
        response = client.get(
            "/api/diagnostics/",
            headers=token_headers
        )
        assert response.status_code == 200
        diagnostics = response.json()
        
        # Verify all entries have a 'Positive' result
        for diagnostic in diagnostics:
            assert diagnostic["result"] == "Positive"