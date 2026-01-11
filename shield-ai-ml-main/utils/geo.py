"""
SHIELD AI - Geographic Utilities
Geospatial calculations for location-based features
"""

import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


# Earth's radius in meters
EARTH_RADIUS_METERS = 6371000


@dataclass
class Coordinate:
    """Geographic coordinate with validation"""
    latitude: float
    longitude: float
    
    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")
    
    def as_tuple(self) -> Tuple[float, float]:
        return (self.latitude, self.longitude)
    
    def as_dict(self) -> Dict[str, float]:
        return {'latitude': self.latitude, 'longitude': self.longitude}


def haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1, lon1: First point coordinates (degrees)
        lat2, lon2: Second point coordinates (degrees)
        
    Returns:
        Distance in meters
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_METERS * c


def path_length(path: List[Tuple[float, float]]) -> float:
    """
    Calculate total length of a path.
    
    Args:
        path: List of (latitude, longitude) tuples
        
    Returns:
        Total path length in meters
    """
    if len(path) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(1, len(path)):
        total_distance += haversine_distance(
            path[i-1][0], path[i-1][1],
            path[i][0], path[i][1]
        )
    
    return total_distance


def point_to_segment_distance(
    point: Tuple[float, float],
    segment_start: Tuple[float, float],
    segment_end: Tuple[float, float]
) -> float:
    """
    Calculate minimum distance from a point to a line segment.
    
    Args:
        point: (lat, lon) of the point
        segment_start: (lat, lon) of segment start
        segment_end: (lat, lon) of segment end
        
    Returns:
        Distance in meters
    """
    # Convert to approximate Cartesian coordinates for simplicity
    # This is accurate enough for short distances
    
    px, py = point[0], point[1]
    ax, ay = segment_start[0], segment_start[1]
    bx, by = segment_end[0], segment_end[1]
    
    # Vector from a to b
    abx = bx - ax
    aby = by - ay
    
    # Vector from a to p
    apx = px - ax
    apy = py - ay
    
    # Project p onto line ab
    ab_squared = abx * abx + aby * aby
    
    if ab_squared == 0:
        # Segment is a point
        return haversine_distance(px, py, ax, ay)
    
    t = max(0, min(1, (apx * abx + apy * aby) / ab_squared))
    
    # Closest point on segment
    closest_x = ax + t * abx
    closest_y = ay + t * aby
    
    return haversine_distance(px, py, closest_x, closest_y)


def point_to_path_distance(
    point: Tuple[float, float],
    path: List[Tuple[float, float]]
) -> float:
    """
    Calculate minimum distance from a point to a path.
    
    Args:
        point: (lat, lon) of the point
        path: List of (lat, lon) tuples
        
    Returns:
        Minimum distance in meters
    """
    if len(path) == 0:
        return float('inf')
    
    if len(path) == 1:
        return haversine_distance(point[0], point[1], path[0][0], path[0][1])
    
    min_distance = float('inf')
    
    for i in range(len(path) - 1):
        distance = point_to_segment_distance(point, path[i], path[i + 1])
        min_distance = min(min_distance, distance)
    
    return min_distance


def path_similarity_score(
    path1: List[Tuple[float, float]],
    path2: List[Tuple[float, float]],
    max_distance: float = 500.0
) -> float:
    """
    Calculate similarity between two paths using Fréchet distance.
    
    Args:
        path1: First path
        path2: Second path
        max_distance: Maximum distance for normalization (meters)
        
    Returns:
        Similarity score (0-1, 1 = identical)
    """
    if not path1 or not path2:
        return 0.0
    
    # Calculate Fréchet distance
    frechet = frechet_distance_simplified(path1, path2)
    
    # Normalize to 0-1 score (inverted: lower distance = higher similarity)
    similarity = max(0.0, 1.0 - (frechet / max_distance))
    
    return similarity


def frechet_distance_simplified(
    path1: List[Tuple[float, float]],
    path2: List[Tuple[float, float]],
    max_points: int = 100
) -> float:
    """
    Simplified Fréchet distance calculation using dynamic programming.
    
    Args:
        path1: First path
        path2: Second path
        max_points: Maximum points to consider (subsamples if needed)
        
    Returns:
        Fréchet distance in meters
    """
    # Subsample if paths are too long
    if len(path1) > max_points:
        indices = [int(i * (len(path1) - 1) / (max_points - 1)) for i in range(max_points)]
        path1 = [path1[i] for i in indices]
    
    if len(path2) > max_points:
        indices = [int(i * (len(path2) - 1) / (max_points - 1)) for i in range(max_points)]
        path2 = [path2[i] for i in indices]
    
    n = len(path1)
    m = len(path2)
    
    if n == 0 or m == 0:
        return float('inf')
    
    # DP table
    dp = [[float('inf')] * m for _ in range(n)]
    
    # Initialize
    dp[0][0] = haversine_distance(
        path1[0][0], path1[0][1],
        path2[0][0], path2[0][1]
    )
    
    # Fill first row
    for j in range(1, m):
        dist = haversine_distance(
            path1[0][0], path1[0][1],
            path2[j][0], path2[j][1]
        )
        dp[0][j] = max(dp[0][j-1], dist)
    
    # Fill first column
    for i in range(1, n):
        dist = haversine_distance(
            path1[i][0], path1[i][1],
            path2[0][0], path2[0][1]
        )
        dp[i][0] = max(dp[i-1][0], dist)
    
    # Fill rest of table
    for i in range(1, n):
        for j in range(1, m):
            dist = haversine_distance(
                path1[i][0], path1[i][1],
                path2[j][0], path2[j][1]
            )
            dp[i][j] = max(
                min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]),
                dist
            )
    
    return dp[n-1][m-1]


def get_bounding_box(
    lat: float,
    lon: float,
    radius_meters: float
) -> Dict[str, float]:
    """
    Get bounding box around a point.
    
    Args:
        lat: Center latitude
        lon: Center longitude
        radius_meters: Radius in meters
        
    Returns:
        Dict with min_lat, max_lat, min_lon, max_lon
    """
    # Approximate degrees per meter
    lat_per_meter = 1 / 111320
    lon_per_meter = 1 / (111320 * math.cos(math.radians(lat)))
    
    delta_lat = radius_meters * lat_per_meter
    delta_lon = radius_meters * lon_per_meter
    
    return {
        'min_lat': lat - delta_lat,
        'max_lat': lat + delta_lat,
        'min_lon': lon - delta_lon,
        'max_lon': lon + delta_lon
    }


def is_point_in_radius(
    center_lat: float,
    center_lon: float,
    point_lat: float,
    point_lon: float,
    radius_meters: float
) -> bool:
    """Check if a point is within radius of center."""
    distance = haversine_distance(center_lat, center_lon, point_lat, point_lon)
    return distance <= radius_meters


def calculate_bearing(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate bearing from point 1 to point 2.
    
    Returns:
        Bearing in degrees (0-360, 0 = North)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
    
    bearing = math.degrees(math.atan2(x, y))
    
    return (bearing + 360) % 360


def reduce_gps_precision(
    lat: float,
    lon: float,
    decimals: int = 4
) -> Tuple[float, float]:
    """
    Reduce GPS precision for privacy.
    4 decimals ≈ 11 meters accuracy.
    
    Args:
        lat: Latitude
        lon: Longitude
        decimals: Number of decimal places
        
    Returns:
        Tuple of (reduced_lat, reduced_lon)
    """
    return (round(lat, decimals), round(lon, decimals))


def interpolate_path(
    path: List[Tuple[float, float]],
    target_points: int
) -> List[Tuple[float, float]]:
    """
    Interpolate a path to have a specific number of points.
    
    Args:
        path: Original path
        target_points: Target number of points
        
    Returns:
        Interpolated path
    """
    if len(path) < 2 or target_points < 2:
        return path
    
    if len(path) == target_points:
        return path
    
    # Calculate total path length
    total_length = path_length(path)
    
    if total_length == 0:
        return [path[0]] * target_points
    
    # Calculate segment distances
    segment_distances = []
    cumulative = 0.0
    for i in range(1, len(path)):
        dist = haversine_distance(
            path[i-1][0], path[i-1][1],
            path[i][0], path[i][1]
        )
        cumulative += dist
        segment_distances.append(cumulative)
    
    # Generate evenly spaced points
    interpolated = [path[0]]
    
    for i in range(1, target_points - 1):
        target_distance = (i / (target_points - 1)) * total_length
        
        # Find segment containing this distance
        for j, cum_dist in enumerate(segment_distances):
            if cum_dist >= target_distance:
                # Interpolate within this segment
                prev_dist = segment_distances[j-1] if j > 0 else 0
                segment_length = cum_dist - prev_dist
                
                if segment_length > 0:
                    t = (target_distance - prev_dist) / segment_length
                else:
                    t = 0
                
                lat = path[j][0] + t * (path[j+1][0] - path[j][0])
                lon = path[j][1] + t * (path[j+1][1] - path[j][1])
                
                interpolated.append((lat, lon))
                break
    
    interpolated.append(path[-1])
    
    return interpolated
