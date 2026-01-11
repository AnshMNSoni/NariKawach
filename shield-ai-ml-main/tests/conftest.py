"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def sample_coordinates():
    """Sample coordinates for testing."""
    return {
        'delhi': (28.6139, 77.2090),
        'mumbai': (19.0760, 72.8777),
        'bangalore': (12.9716, 77.5946),
        'chennai': (13.0827, 80.2707)
    }


@pytest.fixture(scope="session")
def sample_path():
    """Sample path for testing."""
    return [
        (28.6139, 77.2090),
        (28.6149, 77.2100),
        (28.6159, 77.2110),
        (28.6169, 77.2120),
        (28.6179, 77.2130)
    ]


@pytest.fixture
def feature_vector_low_risk():
    """Low risk feature vector."""
    from models.schemas import FeatureVector
    return FeatureVector(
        route_similarity=0.9,
        time_deviation=0.1,
        crime_risk=0.1,
        crowd_density=0.8,
        lighting_risk=0.1
    )


@pytest.fixture
def feature_vector_high_risk():
    """High risk feature vector."""
    from models.schemas import FeatureVector
    return FeatureVector(
        route_similarity=0.1,
        time_deviation=0.9,
        crime_risk=0.9,
        crowd_density=0.1,
        lighting_risk=0.9
    )


@pytest.fixture
def feature_vector_medium_risk():
    """Medium risk feature vector."""
    from models.schemas import FeatureVector
    return FeatureVector(
        route_similarity=0.5,
        time_deviation=0.5,
        crime_risk=0.5,
        crowd_density=0.5,
        lighting_risk=0.5
    )


@pytest.fixture
def trained_model():
    """Create and return a trained model."""
    from model import RiskPredictionModel
    
    model = RiskPredictionModel(model_type='gradient_boosting')
    
    # Generate training data
    np.random.seed(42)
    X = np.random.rand(200, 5)
    
    # Create labels based on risk formula
    risk_score = (
        (1 - X[:, 0]) * 0.25 +  # route_similarity
        X[:, 1] * 0.15 +         # time_deviation  
        X[:, 2] * 0.25 +         # crime_risk
        (1 - X[:, 3]) * 0.20 +   # crowd_density
        X[:, 4] * 0.15           # lighting_risk
    )
    
    y = np.zeros(200, dtype=int)
    y[risk_score > 0.4] = 1
    y[risk_score > 0.7] = 2
    
    model.train_model(X, y)
    return model


@pytest.fixture
def mock_supabase():
    """Mock Supabase service."""
    from services.supabase_client import MockSupabaseClient
    return MockSupabaseClient()


@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing."""
    from datetime import datetime
    return {
        'trip_id': 'test_trip_123',
        'user_id': 'test_user_456',
        'start_time': datetime.utcnow(),
        'start_location': (28.6139, 77.2090),
        'destination': {
            'latitude': 28.6304,
            'longitude': 77.2177,
            'name': 'Work Office'
        },
        'path': [
            (28.6139, 77.2090),
            (28.6150, 77.2100),
            (28.6160, 77.2110)
        ]
    }


@pytest.fixture
def sample_baseline_route():
    """Sample baseline route for testing."""
    return {
        'route_id': 'route_home_work',
        'user_id': 'test_user',
        'path_simplified': [
            (28.6139, 77.2090),
            (28.6149, 77.2100),
            (28.6159, 77.2110),
            (28.6169, 77.2120),
            (28.6179, 77.2130),
            (28.6189, 77.2140),
            (28.6199, 77.2150),
            (28.6209, 77.2160),
            (28.6219, 77.2170),
            (28.6229, 77.2180)
        ],
        'expected_duration_minutes': 30.0,
        'trip_count': 10,
        'time_variance': 5.0,
        'path_variance': 50.0
    }


# Configure pytest markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


# Skip slow tests by default in CI
def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-slow", default=False):
        return
    
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )
