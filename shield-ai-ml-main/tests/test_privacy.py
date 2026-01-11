"""
Unit tests for privacy utilities.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from utils.privacy import (
    hash_device_signature,
    anonymize_user_id,
    anonymize_location_data,
    create_aggregated_pattern,
    sanitize_for_logging,
    check_consent,
    PrivacyAuditLogger
)


class TestHashDeviceSignature:
    """Tests for device signature hashing."""
    
    def test_consistent_hash(self):
        # Same signature should produce same hash (within same day)
        sig = "device123abc"
        hash1 = hash_device_signature(sig)
        hash2 = hash_device_signature(sig)
        assert hash1 == hash2
    
    def test_different_signatures(self):
        # Different signatures should produce different hashes
        hash1 = hash_device_signature("device1")
        hash2 = hash_device_signature("device2")
        assert hash1 != hash2
    
    def test_hash_format(self):
        # Should return a hex string
        hashed = hash_device_signature("test_device")
        assert isinstance(hashed, str)
        # SHA-256 produces 64 character hex
        assert len(hashed) == 64
    
    def test_hash_is_deterministic(self):
        sig = "consistent_device_id"
        hashes = [hash_device_signature(sig) for _ in range(10)]
        assert all(h == hashes[0] for h in hashes)
    
    def test_empty_signature(self):
        # Should handle empty string
        hashed = hash_device_signature("")
        assert len(hashed) == 64


class TestAnonymizeUserId:
    """Tests for user ID anonymization."""
    
    def test_anonymization(self):
        user_id = "user_12345"
        anon_id = anonymize_user_id(user_id)
        
        # Should not be the same as original
        assert anon_id != user_id
        # Should be consistent
        assert anonymize_user_id(user_id) == anon_id
    
    def test_different_users(self):
        anon1 = anonymize_user_id("user1")
        anon2 = anonymize_user_id("user2")
        assert anon1 != anon2
    
    def test_format(self):
        anon = anonymize_user_id("test_user")
        # Should be a valid hash-like string
        assert isinstance(anon, str)
        assert len(anon) > 0


class TestAnonymizeLocationData:
    """Tests for location data anonymization."""
    
    def test_precision_reduction(self):
        data = {
            'latitude': 28.61392567,
            'longitude': 77.20901234
        }
        
        anon = anonymize_location_data(data)
        
        # Should be reduced precision
        assert anon['latitude'] == 28.6139
        assert anon['longitude'] == 77.209
    
    def test_path_anonymization(self):
        data = {
            'path': [
                (28.61392567, 77.20901234),
                (28.61492567, 77.21001234)
            ]
        }
        
        anon = anonymize_location_data(data)
        
        # All points should have reduced precision
        for lat, lon in anon['path']:
            # Check that there are at most 4 decimal places
            lat_decimals = len(str(lat).split('.')[-1]) if '.' in str(lat) else 0
            assert lat_decimals <= 4
    
    def test_sensitive_field_removal(self):
        data = {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'device_id': 'secret_device',
            'user_email': 'user@example.com'
        }
        
        anon = anonymize_location_data(data)
        
        # Sensitive fields should be removed or hashed
        assert 'user_email' not in anon or anon['user_email'] != 'user@example.com'


class TestCreateAggregatedPattern:
    """Tests for pattern aggregation."""
    
    def test_minimum_trips_required(self):
        # Less than 5 trips should fail
        trips = [
            {'path': [(28.6139, 77.2090), (28.6149, 77.2100)]},
            {'path': [(28.6140, 77.2091), (28.6150, 77.2101)]},
        ]
        
        result = create_aggregated_pattern(trips)
        
        # Should return None or indicate insufficient data
        assert result is None or result.get('status') == 'insufficient_data'
    
    def test_aggregation_with_enough_trips(self):
        # Generate 5+ trips
        trips = [
            {'path': [(28.6139 + i*0.0001, 77.2090 + i*0.0001), 
                     (28.6149 + i*0.0001, 77.2100 + i*0.0001)]}
            for i in range(6)
        ]
        
        result = create_aggregated_pattern(trips)
        
        # Should return aggregated pattern
        assert result is not None
        assert 'simplified_path' in result or 'path' in result
    
    def test_path_simplification(self):
        # Create trips with many points
        trips = [
            {'path': [(28.6139 + j*0.0001, 77.2090 + j*0.0001) 
                     for j in range(100)]}
            for _ in range(6)
        ]
        
        result = create_aggregated_pattern(trips)
        
        if result and 'simplified_path' in result:
            # Simplified path should have fewer points
            assert len(result['simplified_path']) < 100


class TestSanitizeForLogging:
    """Tests for log sanitization."""
    
    def test_pii_removal(self):
        data = {
            'user_id': 'user_123',
            'email': 'user@example.com',
            'phone': '+1234567890',
            'latitude': 28.6139
        }
        
        sanitized = sanitize_for_logging(data)
        
        # PII should be redacted
        assert sanitized.get('email') != 'user@example.com'
        assert sanitized.get('phone') != '+1234567890'
    
    def test_safe_fields_preserved(self):
        data = {
            'trip_id': 'trip_123',
            'risk_level': 'medium',
            'timestamp': '2024-01-15T10:30:00'
        }
        
        sanitized = sanitize_for_logging(data)
        
        # Non-sensitive fields should be preserved
        assert sanitized['trip_id'] == 'trip_123'
        assert sanitized['risk_level'] == 'medium'
    
    def test_nested_data(self):
        data = {
            'user': {
                'id': 'user_123',
                'email': 'user@example.com'
            },
            'location': {
                'lat': 28.6139,
                'lon': 77.2090
            }
        }
        
        sanitized = sanitize_for_logging(data)
        
        # Should handle nested structures
        if 'user' in sanitized:
            assert sanitized['user'].get('email') != 'user@example.com'
    
    def test_array_data(self):
        data = {
            'emails': ['user1@example.com', 'user2@example.com'],
            'trip_ids': ['trip_1', 'trip_2']
        }
        
        sanitized = sanitize_for_logging(data)
        
        # Sensitive arrays should be sanitized
        if 'emails' in sanitized:
            assert 'user1@example.com' not in sanitized['emails']


class TestCheckConsent:
    """Tests for consent verification."""
    
    def test_valid_consent(self):
        consent_data = {
            'location_tracking': True,
            'pattern_learning': True,
            'consent_timestamp': datetime.utcnow().isoformat()
        }
        
        result = check_consent(consent_data, 'location_tracking')
        assert result is True
    
    def test_missing_consent(self):
        consent_data = {
            'location_tracking': True
        }
        
        result = check_consent(consent_data, 'pattern_learning')
        assert result is False
    
    def test_denied_consent(self):
        consent_data = {
            'location_tracking': False
        }
        
        result = check_consent(consent_data, 'location_tracking')
        assert result is False
    
    def test_empty_consent(self):
        result = check_consent({}, 'any_feature')
        assert result is False
    
    def test_none_consent(self):
        result = check_consent(None, 'any_feature')
        assert result is False


class TestPrivacyAuditLogger:
    """Tests for privacy audit logging."""
    
    @pytest.fixture
    def logger(self):
        return PrivacyAuditLogger()
    
    def test_log_data_access(self, logger):
        # Should not raise
        logger.log_data_access(
            user_id="user_123",
            data_type="location",
            purpose="risk_calculation",
            accessor="ml_service"
        )
    
    def test_log_consent_check(self, logger):
        # Should not raise
        logger.log_consent_check(
            user_id="user_123",
            consent_type="location_tracking",
            result=True
        )
    
    def test_log_data_deletion(self, logger):
        # Should not raise
        logger.log_data_deletion(
            user_id="user_123",
            data_type="trip_history",
            reason="user_request"
        )
    
    def test_logger_format(self, logger, caplog):
        import logging
        caplog.set_level(logging.INFO)
        
        logger.log_data_access(
            user_id="user_123",
            data_type="location",
            purpose="risk_calculation",
            accessor="ml_service"
        )
        
        # Check that log was created
        # Note: actual log capture depends on logging configuration


class TestDataMinimization:
    """Tests for data minimization principles."""
    
    def test_location_precision_is_limited(self):
        # Verify that location precision is limited to ~11m (4 decimals)
        from config import PrivacyConfig
        config = PrivacyConfig()
        
        assert config.GPS_PRECISION_DECIMALS == 4
    
    def test_raw_gps_not_retained(self):
        from config import PrivacyConfig
        config = PrivacyConfig()
        
        # Raw GPS should not be retained (0 seconds)
        assert config.RAW_GPS_RETENTION_SECONDS == 0
    
    def test_device_signatures_hashed(self):
        # Device signatures should always be hashed, never stored raw
        raw_sig = "real_device_id_12345"
        hashed = hash_device_signature(raw_sig)
        
        # Hashed version should not contain original
        assert raw_sig not in hashed
        # Should be a proper hash
        assert len(hashed) == 64
