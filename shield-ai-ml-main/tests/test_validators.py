"""
Unit tests for input validators.
"""

import pytest
from datetime import datetime

from utils.validators import (
    ValidationError,
    validate_latitude,
    validate_longitude,
    validate_coordinate,
    validate_path,
    validate_user_id,
    validate_trip_id,
    validate_timestamp,
    validate_risk_level,
    validate_feature_vector,
    validate_device_signature,
    validate_speed,
    validate_location_update_request,
    validate_trip_start_request,
    sanitize_string
)


class TestLatitudeValidation:
    """Tests for latitude validation."""
    
    def test_valid_latitude(self):
        assert validate_latitude(28.6139) == 28.6139
        assert validate_latitude(0.0) == 0.0
        assert validate_latitude(-45.0) == -45.0
    
    def test_boundary_values(self):
        assert validate_latitude(90.0) == 90.0
        assert validate_latitude(-90.0) == -90.0
    
    def test_invalid_high(self):
        with pytest.raises(ValidationError, match="Latitude"):
            validate_latitude(91.0)
    
    def test_invalid_low(self):
        with pytest.raises(ValidationError, match="Latitude"):
            validate_latitude(-91.0)
    
    def test_none_value(self):
        with pytest.raises(ValidationError):
            validate_latitude(None)


class TestLongitudeValidation:
    """Tests for longitude validation."""
    
    def test_valid_longitude(self):
        assert validate_longitude(77.2090) == 77.2090
        assert validate_longitude(0.0) == 0.0
        assert validate_longitude(-122.0) == -122.0
    
    def test_boundary_values(self):
        assert validate_longitude(180.0) == 180.0
        assert validate_longitude(-180.0) == -180.0
    
    def test_invalid_high(self):
        with pytest.raises(ValidationError, match="Longitude"):
            validate_longitude(181.0)
    
    def test_invalid_low(self):
        with pytest.raises(ValidationError, match="Longitude"):
            validate_longitude(-181.0)


class TestCoordinateValidation:
    """Tests for coordinate pair validation."""
    
    def test_valid_coordinate(self):
        lat, lon = validate_coordinate(28.6139, 77.2090)
        assert lat == 28.6139
        assert lon == 77.2090
    
    def test_invalid_latitude(self):
        with pytest.raises(ValidationError):
            validate_coordinate(91.0, 77.0)
    
    def test_invalid_longitude(self):
        with pytest.raises(ValidationError):
            validate_coordinate(28.0, 181.0)


class TestPathValidation:
    """Tests for path validation."""
    
    def test_valid_path(self):
        path = [(28.6139, 77.2090), (28.6149, 77.2100)]
        result = validate_path(path)
        assert result == path
    
    def test_empty_path(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_path([])
    
    def test_invalid_point_in_path(self):
        path = [(28.6139, 77.2090), (91.0, 77.0)]  # Second point invalid
        with pytest.raises(ValidationError):
            validate_path(path)
    
    def test_path_with_tuples(self):
        path = [(28.6139, 77.2090), (28.6149, 77.2100)]
        result = validate_path(path)
        assert len(result) == 2


class TestUserIdValidation:
    """Tests for user ID validation."""
    
    def test_valid_user_id(self):
        assert validate_user_id("user_123") == "user_123"
        assert validate_user_id("abc-def-ghi") == "abc-def-ghi"
    
    def test_empty_user_id(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_user_id("")
    
    def test_whitespace_user_id(self):
        with pytest.raises(ValidationError):
            validate_user_id("   ")
    
    def test_very_long_user_id(self):
        with pytest.raises(ValidationError, match="long"):
            validate_user_id("a" * 300)


class TestTripIdValidation:
    """Tests for trip ID validation."""
    
    def test_valid_trip_id(self):
        assert validate_trip_id("trip_abc123") == "trip_abc123"
    
    def test_uuid_format(self):
        uuid_id = "550e8400-e29b-41d4-a716-446655440000"
        assert validate_trip_id(uuid_id) == uuid_id
    
    def test_empty_trip_id(self):
        with pytest.raises(ValidationError):
            validate_trip_id("")


class TestTimestampValidation:
    """Tests for timestamp validation."""
    
    def test_valid_datetime(self):
        now = datetime.utcnow()
        result = validate_timestamp(now)
        assert result == now
    
    def test_iso_string(self):
        iso_str = "2024-01-15T10:30:00"
        result = validate_timestamp(iso_str)
        assert isinstance(result, datetime)
    
    def test_invalid_format(self):
        with pytest.raises(ValidationError):
            validate_timestamp("not-a-date")
    
    def test_none_value(self):
        with pytest.raises(ValidationError):
            validate_timestamp(None)


class TestRiskLevelValidation:
    """Tests for risk level validation."""
    
    def test_valid_levels(self):
        assert validate_risk_level("low") == "low"
        assert validate_risk_level("medium") == "medium"
        assert validate_risk_level("high") == "high"
    
    def test_case_insensitive(self):
        assert validate_risk_level("LOW") == "low"
        assert validate_risk_level("Medium") == "medium"
        assert validate_risk_level("HIGH") == "high"
    
    def test_invalid_level(self):
        with pytest.raises(ValidationError, match="Risk level"):
            validate_risk_level("critical")
    
    def test_empty_level(self):
        with pytest.raises(ValidationError):
            validate_risk_level("")


class TestFeatureVectorValidation:
    """Tests for feature vector validation."""
    
    def test_valid_vector(self):
        vector = {
            'route_similarity': 0.8,
            'time_deviation': 0.2,
            'crime_risk': 0.3,
            'crowd_density': 0.7,
            'lighting_risk': 0.2
        }
        result = validate_feature_vector(vector)
        assert result == vector
    
    def test_missing_field(self):
        vector = {
            'route_similarity': 0.8,
            'time_deviation': 0.2,
            # Missing crime_risk
            'crowd_density': 0.7,
            'lighting_risk': 0.2
        }
        with pytest.raises(ValidationError, match="crime_risk"):
            validate_feature_vector(vector)
    
    def test_value_out_of_range(self):
        vector = {
            'route_similarity': 1.5,  # > 1.0
            'time_deviation': 0.2,
            'crime_risk': 0.3,
            'crowd_density': 0.7,
            'lighting_risk': 0.2
        }
        with pytest.raises(ValidationError, match="0 and 1"):
            validate_feature_vector(vector)
    
    def test_negative_value(self):
        vector = {
            'route_similarity': -0.1,  # < 0
            'time_deviation': 0.2,
            'crime_risk': 0.3,
            'crowd_density': 0.7,
            'lighting_risk': 0.2
        }
        with pytest.raises(ValidationError):
            validate_feature_vector(vector)


class TestDeviceSignatureValidation:
    """Tests for device signature validation."""
    
    def test_valid_signature(self):
        sig = "abc123def456"
        assert validate_device_signature(sig) == sig
    
    def test_empty_signature(self):
        with pytest.raises(ValidationError):
            validate_device_signature("")
    
    def test_too_short(self):
        with pytest.raises(ValidationError, match="short"):
            validate_device_signature("ab")
    
    def test_too_long(self):
        with pytest.raises(ValidationError, match="long"):
            validate_device_signature("a" * 500)


class TestSpeedValidation:
    """Tests for speed validation."""
    
    def test_valid_speed(self):
        assert validate_speed(25.5) == 25.5
        assert validate_speed(0.0) == 0.0
    
    def test_negative_speed(self):
        with pytest.raises(ValidationError, match="negative"):
            validate_speed(-5.0)
    
    def test_unrealistic_speed(self):
        # 500 km/h is unrealistic for personal travel
        with pytest.raises(ValidationError, match="unrealistic"):
            validate_speed(500.0)
    
    def test_walking_speed(self):
        assert validate_speed(5.0) == 5.0  # ~5 km/h walking
    
    def test_driving_speed(self):
        assert validate_speed(80.0) == 80.0  # Highway speed


class TestLocationUpdateValidation:
    """Tests for location update request validation."""
    
    def test_valid_request(self):
        request = {
            'trip_id': 'trip_123',
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        result = validate_location_update_request(request)
        assert result['trip_id'] == 'trip_123'
    
    def test_with_optional_fields(self):
        request = {
            'trip_id': 'trip_123',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'speed': 25.0,
            'accuracy': 10.0
        }
        result = validate_location_update_request(request)
        assert result['speed'] == 25.0
    
    def test_missing_trip_id(self):
        request = {
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        with pytest.raises(ValidationError, match="trip_id"):
            validate_location_update_request(request)
    
    def test_invalid_coordinates(self):
        request = {
            'trip_id': 'trip_123',
            'latitude': 91.0,  # Invalid
            'longitude': 77.2090
        }
        with pytest.raises(ValidationError):
            validate_location_update_request(request)


class TestTripStartValidation:
    """Tests for trip start request validation."""
    
    def test_valid_request(self):
        request = {
            'user_id': 'user_123',
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        result = validate_trip_start_request(request)
        assert result['user_id'] == 'user_123'
    
    def test_with_destination(self):
        request = {
            'user_id': 'user_123',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'destination': {
                'latitude': 28.6304,
                'longitude': 77.2177,
                'name': 'Office'
            }
        }
        result = validate_trip_start_request(request)
        assert result['destination']['name'] == 'Office'
    
    def test_missing_user_id(self):
        request = {
            'latitude': 28.6139,
            'longitude': 77.2090
        }
        with pytest.raises(ValidationError, match="user_id"):
            validate_trip_start_request(request)


class TestSanitizeString:
    """Tests for string sanitization."""
    
    def test_normal_string(self):
        assert sanitize_string("Hello World") == "Hello World"
    
    def test_html_removal(self):
        result = sanitize_string("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
    
    def test_control_char_removal(self):
        result = sanitize_string("Hello\x00World")
        assert "\x00" not in result
    
    def test_null_byte_removal(self):
        result = sanitize_string("test\x00injection")
        assert "\x00" not in result
    
    def test_whitespace_normalization(self):
        result = sanitize_string("Hello   World")
        assert "   " not in result
    
    def test_max_length(self):
        long_string = "a" * 1000
        result = sanitize_string(long_string, max_length=100)
        assert len(result) <= 100
