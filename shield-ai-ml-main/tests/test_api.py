"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "model_loaded" in data


class TestTripEndpoints:
    """Tests for trip management endpoints."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_start_trip(self, client):
        response = client.post("/trip/start", json={
            "user_id": "test_user_123",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trip_id" in data
        assert data["status"] == "active"
        assert "initial_risk" in data
        
        # Store trip_id for later tests
        return data["trip_id"]
    
    def test_start_trip_with_destination(self, client):
        response = client.post("/trip/start", json={
            "user_id": "test_user_456",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "destination": {
                "latitude": 28.6304,
                "longitude": 77.2177,
                "name": "Office"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "trip_id" in data
    
    def test_start_trip_invalid_coordinates(self, client):
        response = client.post("/trip/start", json={
            "user_id": "test_user",
            "latitude": 91.0,  # Invalid
            "longitude": 77.2090
        })
        
        assert response.status_code == 400
    
    def test_start_trip_missing_user_id(self, client):
        response = client.post("/trip/start", json={
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_location_update(self, client):
        # First start a trip
        start_response = client.post("/trip/start", json={
            "user_id": "test_user_loc",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        trip_id = start_response.json()["trip_id"]
        
        # Then update location
        response = client.post("/location/update", json={
            "trip_id": trip_id,
            "latitude": 28.6149,
            "longitude": 77.2100,
            "speed": 25.0,
            "accuracy": 10.0
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["trip_id"] == trip_id
        assert "risk_prediction" in data
        assert "risk_level" in data["risk_prediction"]
    
    def test_location_update_invalid_trip(self, client):
        response = client.post("/location/update", json={
            "trip_id": "nonexistent_trip_id",
            "latitude": 28.6149,
            "longitude": 77.2100
        })
        
        assert response.status_code == 404
    
    def test_end_trip(self, client):
        # Start a trip
        start_response = client.post("/trip/start", json={
            "user_id": "test_user_end",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        trip_id = start_response.json()["trip_id"]
        
        # Add some location updates
        for i in range(3):
            client.post("/location/update", json={
                "trip_id": trip_id,
                "latitude": 28.6139 + (i * 0.001),
                "longitude": 77.2090 + (i * 0.001)
            })
        
        # End the trip
        response = client.post("/trip/end", json={
            "trip_id": trip_id,
            "end_reason": "completed"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "completed"
        assert "duration_minutes" in data
        assert "points_recorded" in data
    
    def test_get_trip_status(self, client):
        # Start a trip
        start_response = client.post("/trip/start", json={
            "user_id": "test_user_status",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        trip_id = start_response.json()["trip_id"]
        
        # Get status
        response = client.get(f"/trip/{trip_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["trip_id"] == trip_id
        assert data["status"] == "active"


class TestRiskCalculation:
    """Tests for risk calculation endpoint."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_calculate_risk(self, client):
        response = client.post("/risk/calculate", json={
            "user_id": "test_user_risk",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "risk_level" in data
        assert data["risk_level"] in ["low", "medium", "high"]
        assert "risk_score" in data
        assert 0 <= data["risk_score"] <= 1
        assert "factors" in data
    
    def test_calculate_risk_with_context(self, client):
        response = client.post("/risk/calculate", json={
            "user_id": "test_user_risk2",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "current_path": [
                [28.6130, 77.2080],
                [28.6135, 77.2085],
                [28.6139, 77.2090]
            ]
        })
        
        assert response.status_code == 200


class TestStalkerDetection:
    """Tests for stalker detection endpoint."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_stalker_check(self, client):
        response = client.post("/stalker/check", json={
            "user_id": "test_user_stalker",
            "lookback_days": 7
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "is_suspicious" in data
        assert "risk_level" in data
        assert "suspicious_signatures" in data
    
    def test_record_proximity_event(self, client):
        response = client.post("/proximity/record", params={
            "user_id": "test_user_prox",
            "device_signature": "test_device_signature_123",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "duration_seconds": 30.0
        })
        
        assert response.status_code == 200
        assert response.json()["status"] == "recorded"


class TestUserData:
    """Tests for user data endpoints."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_get_user_baselines(self, client):
        response = client.get("/user/test_user/baselines")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "baselines" in data
        assert "count" in data
        assert isinstance(data["baselines"], list)
    
    def test_get_user_patterns(self, client):
        response = client.get("/user/test_user/patterns")
        
        assert response.status_code == 200


class TestValidationErrors:
    """Tests for validation error handling."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_invalid_latitude(self, client):
        response = client.post("/trip/start", json={
            "user_id": "test",
            "latitude": 100.0,  # Invalid
            "longitude": 77.0
        })
        
        assert response.status_code in [400, 422]
    
    def test_invalid_longitude(self, client):
        response = client.post("/trip/start", json={
            "user_id": "test",
            "latitude": 28.0,
            "longitude": 200.0  # Invalid
        })
        
        assert response.status_code in [400, 422]
    
    def test_empty_user_id(self, client):
        response = client.post("/trip/start", json={
            "user_id": "",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        response = client.post("/location/update", json={
            "latitude": 28.6139
            # Missing trip_id and longitude
        })
        
        assert response.status_code == 422


class TestPerformance:
    """Tests for API performance."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_response_time_health(self, client):
        import time
        
        start = time.time()
        response = client.get("/health")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 1000  # Should respond within 1 second
    
    def test_response_time_risk_calculation(self, client):
        import time
        
        start = time.time()
        response = client.post("/risk/calculate", json={
            "user_id": "perf_test",
            "latitude": 28.6139,
            "longitude": 77.2090
        })
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        # Should meet performance target of 200ms
        # Allow some slack for test environment
        assert elapsed < 500, f"Risk calculation too slow: {elapsed}ms"
    
    def test_concurrent_requests(self, client):
        import concurrent.futures
        import time
        
        def make_request():
            return client.get("/health")
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in futures]
        elapsed = time.time() - start
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
        # Should complete within reasonable time
        assert elapsed < 10  # 20 requests in under 10 seconds


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_404_unknown_endpoint(self, client):
        response = client.get("/unknown/endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        response = client.put("/health")  # PUT not allowed
        assert response.status_code == 405
    
    def test_malformed_json(self, client):
        response = client.post(
            "/trip/start",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
