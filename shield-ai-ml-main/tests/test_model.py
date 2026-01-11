"""
Unit tests for the risk prediction model.
"""

import pytest
import numpy as np
import os
import tempfile

from model import RiskPredictionModel
from models.schemas import FeatureVector, RiskPrediction


class TestFeatureVector:
    """Tests for FeatureVector validation."""
    
    def test_valid_feature_vector(self):
        fv = FeatureVector(
            route_similarity=0.8,
            time_deviation=0.2,
            crime_risk=0.3,
            crowd_density=0.7,
            lighting_risk=0.2
        )
        assert fv.route_similarity == 0.8
        assert fv.time_deviation == 0.2
    
    def test_boundary_values(self):
        # Test minimum values
        fv = FeatureVector(
            route_similarity=0.0,
            time_deviation=0.0,
            crime_risk=0.0,
            crowd_density=0.0,
            lighting_risk=0.0
        )
        assert fv.route_similarity == 0.0
        
        # Test maximum values
        fv = FeatureVector(
            route_similarity=1.0,
            time_deviation=1.0,
            crime_risk=1.0,
            crowd_density=1.0,
            lighting_risk=1.0
        )
        assert fv.lighting_risk == 1.0


class TestRiskPredictionModel:
    """Tests for the RiskPredictionModel class."""
    
    @pytest.fixture
    def model(self):
        """Create a fresh model instance for each test."""
        return RiskPredictionModel(model_type='gradient_boosting')
    
    @pytest.fixture
    def trained_model(self):
        """Create and train a model."""
        model = RiskPredictionModel(model_type='gradient_boosting')
        
        # Generate simple training data
        np.random.seed(42)
        X = np.random.rand(100, 5)
        # Create labels based on sum of risk features
        risk_score = (
            (1 - X[:, 0]) * 0.25 +  # route_similarity inverted
            X[:, 1] * 0.15 +         # time_deviation
            X[:, 2] * 0.25 +         # crime_risk
            (1 - X[:, 3]) * 0.20 +   # crowd_density inverted
            X[:, 4] * 0.15           # lighting_risk
        )
        y = np.zeros(100, dtype=int)
        y[risk_score > 0.4] = 1
        y[risk_score > 0.7] = 2
        
        model.train_model(X, y)
        return model
    
    def test_model_initialization(self, model):
        assert model.model is None
        assert model.model_type == 'gradient_boosting'
    
    def test_model_training(self, model):
        # Simple training data
        X = np.random.rand(50, 5)
        y = np.random.randint(0, 3, 50)
        
        results = model.train_model(X, y)
        
        assert model.model is not None
        assert 'accuracy' in results
        assert 'training_time' in results
        assert 'feature_importance' in results
        assert len(results['feature_importance']) == 5
    
    def test_prediction_low_risk(self, trained_model):
        # Low risk scenario: familiar route, safe area
        fv = FeatureVector(
            route_similarity=0.9,
            time_deviation=0.1,
            crime_risk=0.2,
            crowd_density=0.8,
            lighting_risk=0.1
        )
        
        prediction = trained_model.predict(fv)
        
        assert isinstance(prediction, RiskPrediction)
        assert prediction.risk_level in ['low', 'medium', 'high']
        assert 0 <= prediction.risk_score <= 1
        assert 0 <= prediction.confidence <= 1
        assert prediction.recommended_action is not None
    
    def test_prediction_high_risk(self, trained_model):
        # High risk scenario
        fv = FeatureVector(
            route_similarity=0.1,
            time_deviation=0.9,
            crime_risk=0.9,
            crowd_density=0.1,
            lighting_risk=0.9
        )
        
        prediction = trained_model.predict(fv)
        
        assert prediction.risk_level in ['medium', 'high']
        assert prediction.risk_score > 0.5
    
    def test_rule_based_fallback(self, model):
        # Model not trained - should use fallback
        fv = FeatureVector(
            route_similarity=0.1,
            time_deviation=0.8,
            crime_risk=0.9,
            crowd_density=0.1,
            lighting_risk=0.9
        )
        
        prediction = model.predict(fv)
        
        assert prediction.risk_level == 'high'
        assert prediction.confidence == 0.7  # Rule-based confidence
    
    def test_prediction_factors(self, trained_model):
        fv = FeatureVector(
            route_similarity=0.3,
            time_deviation=0.7,
            crime_risk=0.8,
            crowd_density=0.2,
            lighting_risk=0.6
        )
        
        prediction = trained_model.predict(fv)
        
        # Should have risk factors
        assert prediction.factors is not None
        assert len(prediction.factors) > 0
        
        # Check factor structure
        factor = prediction.factors[0]
        assert hasattr(factor, 'name')
        assert hasattr(factor, 'score')
        assert hasattr(factor, 'weight')
        assert hasattr(factor, 'contribution')
    
    def test_model_save_load(self, trained_model):
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            model_path = f.name
        
        try:
            # Save model
            trained_model.save_model(model_path)
            assert os.path.exists(model_path)
            
            # Load into new model
            new_model = RiskPredictionModel()
            new_model.load_model(model_path)
            
            # Compare predictions
            fv = FeatureVector(
                route_similarity=0.5,
                time_deviation=0.5,
                crime_risk=0.5,
                crowd_density=0.5,
                lighting_risk=0.5
            )
            
            pred1 = trained_model.predict(fv)
            pred2 = new_model.predict(fv)
            
            assert pred1.risk_level == pred2.risk_level
            assert abs(pred1.risk_score - pred2.risk_score) < 0.01
        
        finally:
            os.unlink(model_path)
    
    def test_random_forest_model(self):
        model = RiskPredictionModel(model_type='random_forest')
        
        X = np.random.rand(50, 5)
        y = np.random.randint(0, 3, 50)
        
        results = model.train_model(X, y)
        
        assert model.model is not None
        assert 'accuracy' in results
    
    def test_inference_time(self, trained_model):
        import time
        
        fv = FeatureVector(
            route_similarity=0.5,
            time_deviation=0.5,
            crime_risk=0.5,
            crowd_density=0.5,
            lighting_risk=0.5
        )
        
        # Measure inference time
        start = time.time()
        for _ in range(100):
            trained_model.predict(fv)
        elapsed = (time.time() - start) / 100 * 1000  # ms per prediction
        
        # Should be under 100ms
        assert elapsed < 100, f"Inference too slow: {elapsed:.2f}ms"


class TestRuleBased:
    """Tests for rule-based prediction fallback."""
    
    @pytest.fixture
    def model(self):
        return RiskPredictionModel()
    
    def test_low_risk_calculation(self, model):
        fv = FeatureVector(
            route_similarity=0.95,  # Very familiar
            time_deviation=0.05,    # On time
            crime_risk=0.1,         # Safe area
            crowd_density=0.9,      # Many people
            lighting_risk=0.05      # Well lit
        )
        
        prediction = model.predict(fv)
        assert prediction.risk_level == 'low'
    
    def test_medium_risk_calculation(self, model):
        fv = FeatureVector(
            route_similarity=0.5,
            time_deviation=0.4,
            crime_risk=0.5,
            crowd_density=0.4,
            lighting_risk=0.5
        )
        
        prediction = model.predict(fv)
        assert prediction.risk_level in ['low', 'medium']
    
    def test_high_risk_calculation(self, model):
        fv = FeatureVector(
            route_similarity=0.05,  # Unknown route
            time_deviation=0.9,     # Very late
            crime_risk=0.95,        # Dangerous area
            crowd_density=0.05,     # Isolated
            lighting_risk=0.95      # Dark
        )
        
        prediction = model.predict(fv)
        assert prediction.risk_level == 'high'
    
    def test_weighted_calculation(self, model):
        # Test that weights are applied correctly
        # High crime should matter more than time deviation
        
        fv1 = FeatureVector(
            route_similarity=0.5,
            time_deviation=0.9,     # High
            crime_risk=0.3,         # Low
            crowd_density=0.5,
            lighting_risk=0.3
        )
        
        fv2 = FeatureVector(
            route_similarity=0.5,
            time_deviation=0.3,     # Low
            crime_risk=0.9,         # High
            crowd_density=0.5,
            lighting_risk=0.3
        )
        
        pred1 = model.predict(fv1)
        pred2 = model.predict(fv2)
        
        # Crime (weight 0.25) > time (weight 0.15), so pred2 should be higher risk
        assert pred2.risk_score >= pred1.risk_score


class TestRecommendedActions:
    """Tests for recommended action generation."""
    
    @pytest.fixture
    def model(self):
        return RiskPredictionModel()
    
    def test_low_risk_action(self, model):
        fv = FeatureVector(
            route_similarity=0.9,
            time_deviation=0.1,
            crime_risk=0.1,
            crowd_density=0.9,
            lighting_risk=0.1
        )
        
        prediction = model.predict(fv)
        assert 'continue' in prediction.recommended_action.lower()
    
    def test_high_risk_action(self, model):
        fv = FeatureVector(
            route_similarity=0.1,
            time_deviation=0.9,
            crime_risk=0.9,
            crowd_density=0.1,
            lighting_risk=0.9
        )
        
        prediction = model.predict(fv)
        assert 'alert' in prediction.recommended_action.lower() or \
               'location' in prediction.recommended_action.lower()
