"""
SHIELD AI - Input Validators
Comprehensive validation utilities for API inputs
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_latitude(value: Any, field_name: str = "latitude") -> float:
    """Validate latitude value (-90 to 90)"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    try:
        lat = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number", field_name)
    
    if not -90 <= lat <= 90:
        raise ValidationError(f"{field_name} must be between -90 and 90", field_name)
    
    return lat


def validate_longitude(value: Any, field_name: str = "longitude") -> float:
    """Validate longitude value (-180 to 180)"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    try:
        lon = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number", field_name)
    
    if not -180 <= lon <= 180:
        raise ValidationError(f"{field_name} must be between -180 and 180", field_name)
    
    return lon


def validate_coordinate(lat: Any, lon: Any) -> Tuple[float, float]:
    """Validate a coordinate pair"""
    validated_lat = validate_latitude(lat)
    validated_lon = validate_longitude(lon)
    return (validated_lat, validated_lon)


def validate_coordinates(coords: Dict) -> Dict:
    """Validate coordinate dictionary with latitude and longitude"""
    if not isinstance(coords, dict):
        raise ValidationError("Coordinates must be a dictionary")
    
    lat = validate_latitude(coords.get('latitude'))
    lon = validate_longitude(coords.get('longitude'))
    
    return {'latitude': lat, 'longitude': lon}


def validate_path(path: List[Tuple[float, float]], min_points: int = 2) -> List[Tuple[float, float]]:
    """Validate a path (list of coordinate tuples)"""
    if not path:
        raise ValidationError("Path cannot be empty")
    
    if len(path) < min_points:
        raise ValidationError(f"Path must have at least {min_points} points")
    
    validated_path = []
    for i, point in enumerate(path):
        if isinstance(point, (list, tuple)) and len(point) >= 2:
            lat, lon = validate_coordinate(point[0], point[1])
            validated_path.append((lat, lon))
        elif isinstance(point, dict):
            lat = validate_latitude(point.get('latitude', point.get('lat')))
            lon = validate_longitude(point.get('longitude', point.get('lon', point.get('lng'))))
            validated_path.append((lat, lon))
        else:
            raise ValidationError(f"Invalid point at index {i}")
    
    return validated_path


def validate_user_id(value: Any, field_name: str = "user_id") -> str:
    """Validate user ID"""
    if value is None or value == "":
        raise ValidationError(f"{field_name} is required and cannot be empty", field_name)
    
    user_id = str(value).strip()
    
    if len(user_id) > 255:
        raise ValidationError(f"{field_name} is too long (max 255 characters)", field_name)
    
    if not user_id:
        raise ValidationError(f"{field_name} cannot be empty or whitespace", field_name)
    
    return user_id


def validate_device_id(value: Any, field_name: str = "device_id") -> str:
    """Validate device ID"""
    if value is None or value == "":
        raise ValidationError(f"{field_name} is required", field_name)
    
    device_id = str(value).strip()
    
    if len(device_id) < 3:
        raise ValidationError(f"{field_name} is too short (min 3 characters)", field_name)
    
    if len(device_id) > 255:
        raise ValidationError(f"{field_name} is too long (max 255 characters)", field_name)
    
    return device_id


def validate_timestamp(value: Any, field_name: str = "timestamp") -> datetime:
    """Validate and parse timestamp"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        # Try ISO format
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        raise ValidationError(f"Invalid {field_name} format", field_name)
    
    raise ValidationError(f"{field_name} must be a datetime or ISO string", field_name)


def validate_risk_level(value: Any, field_name: str = "risk_level") -> str:
    """Validate risk level"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    valid_levels = ['safe', 'low', 'medium', 'high', 'critical']
    level = str(value).lower().strip()
    
    if level not in valid_levels:
        raise ValidationError(
            f"{field_name} must be one of: {', '.join(valid_levels)}", 
            field_name
        )
    
    return level


def validate_risk_score(value: Any, field_name: str = "risk_score") -> float:
    """Validate risk score (0-1)"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    try:
        score = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number", field_name)
    
    if not 0 <= score <= 1:
        raise ValidationError(f"{field_name} must be between 0 and 1", field_name)
    
    return score


def validate_speed(value: Any, field_name: str = "speed") -> float:
    """Validate speed (km/h)"""
    if value is None:
        return 0.0
    
    try:
        speed = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number", field_name)
    
    if speed < 0:
        raise ValidationError(f"{field_name} cannot be negative", field_name)
    
    if speed > 300:
        raise ValidationError(f"{field_name} is unrealistically high (max 300 km/h)", field_name)
    
    return speed


def validate_distance(value: Any, field_name: str = "distance") -> float:
    """Validate distance (meters)"""
    if value is None:
        return 0.0
    
    try:
        distance = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number", field_name)
    
    if distance < 0:
        raise ValidationError(f"{field_name} cannot be negative", field_name)
    
    return distance


def validate_email(value: Any, field_name: str = "email") -> str:
    """Validate email address"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    email = str(value).strip().lower()
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError(f"Invalid {field_name} format", field_name)
    
    return email


def validate_phone(value: Any, field_name: str = "phone") -> str:
    """Validate phone number"""
    if value is None:
        raise ValidationError(f"{field_name} is required", field_name)
    
    # Remove spaces, dashes, parentheses
    phone = re.sub(r'[\s\-\(\)]', '', str(value))
    
    # Basic phone validation (10-15 digits, optional + prefix)
    pattern = r'^\+?[0-9]{10,15}$'
    if not re.match(pattern, phone):
        raise ValidationError(f"Invalid {field_name} format", field_name)
    
    return phone


def validate_nearby_devices(devices: Any, field_name: str = "nearby_devices") -> List[Dict]:
    """Validate list of nearby devices"""
    if devices is None:
        return []
    
    if not isinstance(devices, list):
        raise ValidationError(f"{field_name} must be a list", field_name)
    
    validated_devices = []
    for i, device in enumerate(devices):
        if not isinstance(device, dict):
            raise ValidationError(f"Device at index {i} must be a dictionary")
        
        validated_device = {
            'device_id': validate_device_id(device.get('device_id'), f"device[{i}].device_id")
        }
        
        # Optional fields
        if 'distance_meters' in device:
            validated_device['distance_meters'] = validate_distance(
                device['distance_meters'], 
                f"device[{i}].distance_meters"
            )
        
        if 'signal_strength' in device:
            validated_device['signal_strength'] = device['signal_strength']
        
        validated_devices.append(validated_device)
    
    return validated_devices


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize a string by removing dangerous content"""
    if not isinstance(value, str):
        return str(value)[:max_length]
    
    # Remove null bytes
    sanitized = value.replace('\x00', '')
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    
    # Remove control characters (except newlines and tabs)
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Truncate to max length
    return sanitized[:max_length]


def validate_context(context: Dict, required_fields: List[str] = None) -> Dict:
    """Validate context dictionary with optional required fields"""
    if not isinstance(context, dict):
        raise ValidationError("Context must be a dictionary")
    
    if required_fields:
        missing = [f for f in required_fields if f not in context]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")
    
    # Validate known fields if present
    validated = {}
    
    if 'latitude' in context:
        validated['latitude'] = validate_latitude(context['latitude'])
    if 'longitude' in context:
        validated['longitude'] = validate_longitude(context['longitude'])
    if 'speed' in context:
        validated['speed'] = validate_speed(context['speed'])
    if 'user_id' in context:
        validated['user_id'] = validate_user_id(context['user_id'])
    
    # Copy other fields as-is
    for key, value in context.items():
        if key not in validated:
            if isinstance(value, str):
                validated[key] = sanitize_string(value)
            else:
                validated[key] = value
    
    return validated
