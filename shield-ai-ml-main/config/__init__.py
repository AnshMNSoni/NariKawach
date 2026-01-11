"""
SHIELD AI - Configuration Package
Application configuration and constants
"""

from .settings import settings, get_settings, reload_settings, Settings
from .constants import (
    RiskLevel,
    AnomalyType,
    AlertPriority,
    InterventionType,
    EmergencyProtocol,
    RISK_THRESHOLDS,
    FEATURE_WEIGHTS,
    STALKING_THRESHOLDS,
    TIME_RISK_MULTIPLIERS,
    LOCATION_RISK_SCORES,
    CROWD_DENSITY_RISK,
    API_CODES,
    MAX_VALUES,
    MIN_VALUES,
    CACHE_TTL,
    RATE_LIMITS
)

__all__ = [
    # Settings
    'settings',
    'get_settings',
    'reload_settings',
    'Settings',
    
    # Enums
    'RiskLevel',
    'AnomalyType',
    'AlertPriority',
    'InterventionType',
    'EmergencyProtocol',
    
    # Constants
    'RISK_THRESHOLDS',
    'FEATURE_WEIGHTS',
    'STALKING_THRESHOLDS',
    'TIME_RISK_MULTIPLIERS',
    'LOCATION_RISK_SCORES',
    'CROWD_DENSITY_RISK',
    'API_CODES',
    'MAX_VALUES',
    'MIN_VALUES',
    'CACHE_TTL',
    'RATE_LIMITS'
]
