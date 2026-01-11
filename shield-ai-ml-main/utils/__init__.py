"""
SHIELD AI - Utilities Package
Common utility functions and helpers
"""

from .logger import setup_logger, get_logger, LoggerMixin
from .geo import (
    Coordinate,
    haversine_distance,
    path_length,
    point_to_segment_distance,
    point_to_path_distance,
    path_similarity_score,
    frechet_distance_simplified,
    get_bounding_box,
    is_point_in_radius,
    calculate_bearing,
    reduce_gps_precision,
    interpolate_path
)
from .validators import (
    ValidationError,
    validate_latitude,
    validate_longitude,
    validate_coordinate,
    validate_coordinates,
    validate_path,
    validate_user_id,
    validate_device_id,
    validate_timestamp,
    validate_risk_level,
    validate_risk_score,
    validate_speed,
    validate_distance,
    validate_email,
    validate_phone,
    validate_nearby_devices,
    validate_context,
    sanitize_string
)
from .config_loader import (
    ConfigLoader,
    get_config_loader,
    load_api_config,
    load_model_config
)

__all__ = [
    # Logger
    'setup_logger',
    'get_logger',
    'LoggerMixin',
    
    # Validators
    'ValidationError',
    'validate_latitude',
    'validate_longitude',
    'validate_coordinate',
    'validate_coordinates',
    'validate_path',
    'validate_user_id',
    'validate_device_id',
    'validate_timestamp',
    'validate_risk_level',
    'validate_risk_score',
    'validate_speed',
    'validate_distance',
    'validate_email',
    'validate_phone',
    'validate_nearby_devices',
    'validate_context',
    'sanitize_string',
    
    # Config
    'ConfigLoader',
    'get_config_loader',
    'load_api_config',
    'load_model_config'
]
