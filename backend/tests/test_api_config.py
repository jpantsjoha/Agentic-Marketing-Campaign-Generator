"""
FILENAME: test_api_config.py
DESCRIPTION/PURPOSE: API tests for configuration endpoints
"""

from fastapi.testclient import TestClient

class TestConfigAPI:
    def test_set_gemini_key(self, client: TestClient):
        response = client.post("/api/v1/config/gemini-key", json={"gemini_api_key": "TESTKEY"})
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json().get("gemini_key_configured") is True

