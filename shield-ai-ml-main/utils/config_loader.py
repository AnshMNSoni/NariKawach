"""
SHIELD AI - Configuration Loader
Loads and manages configuration from various sources
"""

import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

from .logger import setup_logger

logger = setup_logger(__name__)


class ConfigLoader:
    """
    Configuration loader that supports multiple sources:
    - Environment variables
    - YAML files
    - JSON files
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Any] = {}
    
    def load_yaml(self, filename: str) -> Dict:
        """Load configuration from YAML file"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"Loaded config from {filepath}")
            return config
        except Exception as e:
            logger.error(f"Error loading YAML config {filepath}: {e}")
            return {}
    
    def load_json(self, filename: str) -> Dict:
        """Load configuration from JSON file"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config from {filepath}")
            return config
        except Exception as e:
            logger.error(f"Error loading JSON config {filepath}: {e}")
            return {}
    
    def get_env(self, key: str, default: Any = None, cast_type: type = None) -> Any:
        """Get environment variable with optional type casting"""
        value = os.environ.get(key, default)
        
        if value is None:
            return default
        
        if cast_type is None:
            return value
        
        try:
            if cast_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            elif cast_type == list:
                return [v.strip() for v in value.split(',')]
            else:
                return cast_type(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to cast {key} to {cast_type}, using default")
            return default
    
    def load_api_config(self) -> Dict:
        """Load API-specific configuration"""
        # Try YAML first, then JSON
        config = self.load_yaml('api_config.yaml')
        if not config:
            config = self.load_json('api_config.json')
        
        # Override with environment variables
        env_overrides = {
            'host': self.get_env('API_HOST', config.get('host', '0.0.0.0')),
            'port': self.get_env('API_PORT', config.get('port', 8000), int),
            'debug': self.get_env('DEBUG', config.get('debug', False), bool),
            'cors_origins': self.get_env('CORS_ORIGINS', config.get('cors_origins', ['*']), list)
        }
        
        config.update(env_overrides)
        return config
    
    def load_model_config(self) -> Dict:
        """Load ML model configuration"""
        config = self.load_yaml('model_config.yaml')
        if not config:
            config = {}
        
        # Defaults
        defaults = {
            'model_type': 'gradient_boosting',
            'cache_dir': './models/cache',
            'auto_retrain': False,
            'feature_weights': {
                'temporal': 0.20,
                'spatial': 0.25,
                'environmental': 0.20,
                'behavioral': 0.20,
                'social': 0.15
            }
        }
        
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
        
        return config
    
    def load_stalking_config(self) -> Dict:
        """Load stalking detection configuration"""
        return {
            'coincidence_window_minutes': self.get_env('STALKING_WINDOW_MINUTES', 30, int),
            'min_coincidence_count': self.get_env('STALKING_MIN_COUNT', 3, int),
            'proximity_threshold_meters': self.get_env('STALKING_PROXIMITY_METERS', 100, int),
            'time_threshold_minutes': self.get_env('STALKING_TIME_MINUTES', 10, int),
            'stalking_confidence_threshold': self.get_env('STALKING_CONFIDENCE', 0.7, float),
            'device_history_days': self.get_env('STALKING_HISTORY_DAYS', 30, int)
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a cached configuration value"""
        return self._cache.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value in cache"""
        self._cache[key] = value
    
    def load_all(self) -> Dict:
        """Load all configuration"""
        config = {
            'api': self.load_api_config(),
            'model': self.load_model_config(),
            'stalking': self.load_stalking_config()
        }
        self._cache = config
        return config


# Singleton instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_dir: str = "config") -> ConfigLoader:
    """Get or create the config loader singleton"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(config_dir)
    return _config_loader


@lru_cache(maxsize=1)
def load_api_config() -> Dict:
    """Cached API config loader"""
    return get_config_loader().load_api_config()


@lru_cache(maxsize=1)
def load_model_config() -> Dict:
    """Cached model config loader"""
    return get_config_loader().load_model_config()
