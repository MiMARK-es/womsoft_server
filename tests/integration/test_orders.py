import pytest

class TestOrders:
    def test_doctor_creates_and_labtech_fulfills_order(self, client, doctor_token_headers, labtech_token_headers):
        # Doctor creates order
        order_data = {"patient_name": "John Doe"}
        resp = client.post("/api/orders/", json=order_data, headers=doctor_token_headers)
        assert resp.status_code == 200
        order_id = resp.json()["id"]

        # Lab technician fulfills order
        diag_data = {
            "identifier": "ORD-1",
            "protein1": 1.0,
            "protein2": 2.0,
            "protein3": 3.0
        }
        resp = client.post(f"/api/orders/{order_id}/fulfill", json=diag_data, headers=labtech_token_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "fulfilled"
        assert body["diagnostic_id"] is not None

