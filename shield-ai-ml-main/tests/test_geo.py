"""
Unit tests for geographic utility functions.
"""

import pytest
import math
from utils.geo import (
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
    reduce_gps_precision
)


class TestCoordinate:
    """Tests for the Coordinate class."""
    
    def test_valid_coordinate(self):
        coord = Coordinate(latitude=28.6139, longitude=77.2090)
        assert coord.latitude == 28.6139
        assert coord.longitude == 77.2090
    
    def test_invalid_latitude_high(self):
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinate(latitude=91.0, longitude=0.0)
    
    def test_invalid_latitude_low(self):
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinate(latitude=-91.0, longitude=0.0)
    
    def test_invalid_longitude_high(self):
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinate(latitude=0.0, longitude=181.0)
    
    def test_invalid_longitude_low(self):
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinate(latitude=0.0, longitude=-181.0)
    
    def test_as_tuple(self):
        coord = Coordinate(latitude=28.6139, longitude=77.2090)
        assert coord.as_tuple() == (28.6139, 77.2090)
    
    def test_boundary_values(self):
        # Test boundary values should work
        coord1 = Coordinate(latitude=90.0, longitude=180.0)
        coord2 = Coordinate(latitude=-90.0, longitude=-180.0)
        assert coord1.latitude == 90.0
        assert coord2.latitude == -90.0


class TestHaversineDistance:
    """Tests for haversine distance calculation."""
    
    def test_same_point(self):
        distance = haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
        assert distance == 0.0
    
    def test_known_distance(self):
        # Delhi to Mumbai: approximately 1,150 km
        distance = haversine_distance(28.6139, 77.2090, 19.0760, 72.8777)
        assert 1100000 < distance < 1200000  # 1100-1200 km in meters
    
    def test_short_distance(self):
        # Very close points (about 100 meters)
        distance = haversine_distance(28.6139, 77.2090, 28.6149, 77.2090)
        assert 100 < distance < 150
    
    def test_coordinate_objects(self):
        coord1 = Coordinate(28.6139, 77.2090)
        coord2 = Coordinate(28.6149, 77.2090)
        distance = haversine_distance(
            coord1.latitude, coord1.longitude,
            coord2.latitude, coord2.longitude
        )
        assert distance > 0


class TestPathLength:
    """Tests for path length calculation."""
    
    def test_empty_path(self):
        assert path_length([]) == 0.0
    
    def test_single_point(self):
        assert path_length([(28.6139, 77.2090)]) == 0.0
    
    def test_two_points(self):
        path = [(28.6139, 77.2090), (28.6149, 77.2090)]
        length = path_length(path)
        assert length > 0
    
    def test_multiple_points(self):
        path = [
            (28.6139, 77.2090),
            (28.6149, 77.2090),
            (28.6159, 77.2090),
            (28.6169, 77.2090)
        ]
        length = path_length(path)
        # Should be approximately 3x the two-point distance
        single_segment = haversine_distance(28.6139, 77.2090, 28.6149, 77.2090)
        assert abs(length - 3 * single_segment) < 10  # Within 10m


class TestPointToSegmentDistance:
    """Tests for point to segment distance."""
    
    def test_point_on_segment(self):
        # Point directly on the segment
        distance = point_to_segment_distance(
            (28.6144, 77.2090),  # Point in middle
            (28.6139, 77.2090),  # Segment start
            (28.6149, 77.2090)   # Segment end
        )
        assert distance < 1  # Should be very close to 0
    
    def test_point_perpendicular(self):
        # Point perpendicular to segment
        distance = point_to_segment_distance(
            (28.6144, 77.2100),  # Point off to the side
            (28.6139, 77.2090),
            (28.6149, 77.2090)
        )
        # Should be approximately the longitudinal distance
        expected = haversine_distance(28.6144, 77.2090, 28.6144, 77.2100)
        assert abs(distance - expected) < 50  # Within 50m


class TestPathSimilarity:
    """Tests for path similarity scoring."""
    
    def test_identical_paths(self):
        path = [
            (28.6139, 77.2090),
            (28.6149, 77.2100),
            (28.6159, 77.2110)
        ]
        similarity = path_similarity_score(path, path)
        assert similarity > 0.95  # Should be nearly 1.0
    
    def test_completely_different_paths(self):
        path1 = [(28.6139, 77.2090), (28.6149, 77.2100)]
        path2 = [(19.0760, 72.8777), (19.0860, 72.8877)]  # Mumbai
        similarity = path_similarity_score(path1, path2)
        assert similarity < 0.1  # Should be very low
    
    def test_empty_path(self):
        path1 = []
        path2 = [(28.6139, 77.2090)]
        similarity = path_similarity_score(path1, path2)
        assert similarity == 0.0
    
    def test_similar_paths(self):
        # Slightly different paths
        path1 = [
            (28.6139, 77.2090),
            (28.6149, 77.2100),
            (28.6159, 77.2110)
        ]
        path2 = [
            (28.6140, 77.2091),
            (28.6150, 77.2101),
            (28.6160, 77.2111)
        ]
        similarity = path_similarity_score(path1, path2)
        assert 0.8 < similarity < 1.0  # Should be high but not perfect


class TestBoundingBox:
    """Tests for bounding box calculation."""
    
    def test_single_point(self):
        bbox = get_bounding_box(28.6139, 77.2090, 1000)  # 1km radius
        assert bbox["min_lat"] < 28.6139 < bbox["max_lat"]
        assert bbox["min_lon"] < 77.2090 < bbox["max_lon"]
    
    def test_box_size(self):
        # 1km radius should give roughly 2km box
        bbox = get_bounding_box(28.6139, 77.2090, 1000)
        lat_diff = bbox["max_lat"] - bbox["min_lat"]
        # At this latitude, 1 degree ≈ 111km
        assert 0.015 < lat_diff < 0.025  # ~1.7-2.8km


class TestIsPointInRadius:
    """Tests for point in radius check."""
    
    def test_point_inside(self):
        assert is_point_in_radius(
            28.6139, 77.2090,  # Center
            28.6140, 77.2091,  # Point very close
            1000              # 1km radius
        )
    
    def test_point_outside(self):
        assert not is_point_in_radius(
            28.6139, 77.2090,  # Center
            28.6500, 77.2500,  # Point far away
            1000              # 1km radius
        )
    
    def test_point_on_boundary(self):
        # Calculate a point exactly at the boundary
        # This is approximate due to Earth's curvature
        result = is_point_in_radius(28.6139, 77.2090, 28.6139, 77.2090, 0)
        assert result  # Same point should be within 0 radius (edge case)


class TestCalculateBearing:
    """Tests for bearing calculation."""
    
    def test_north(self):
        bearing = calculate_bearing(28.6139, 77.2090, 28.6239, 77.2090)
        assert abs(bearing - 0) < 1 or abs(bearing - 360) < 1  # North is 0 or 360
    
    def test_east(self):
        bearing = calculate_bearing(28.6139, 77.2090, 28.6139, 77.2190)
        assert 85 < bearing < 95  # East is 90
    
    def test_south(self):
        bearing = calculate_bearing(28.6139, 77.2090, 28.6039, 77.2090)
        assert 175 < bearing < 185  # South is 180
    
    def test_west(self):
        bearing = calculate_bearing(28.6139, 77.2090, 28.6139, 77.1990)
        assert 265 < bearing < 275  # West is 270


class TestReduceGpsPrecision:
    """Tests for GPS precision reduction."""
    
    def test_default_precision(self):
        lat, lon = reduce_gps_precision(28.61392567, 77.20901234)
        assert lat == 28.6139
        assert lon == 77.209
    
    def test_custom_precision(self):
        lat, lon = reduce_gps_precision(28.61392567, 77.20901234, decimals=2)
        assert lat == 28.61
        assert lon == 77.21
    
    def test_zero_precision(self):
        lat, lon = reduce_gps_precision(28.61392567, 77.20901234, decimals=0)
        assert lat == 29.0
        assert lon == 77.0


class TestFrechetDistance:
    """Tests for Fréchet distance calculation."""
    
    def test_identical_paths(self):
        path = [(28.6139, 77.2090), (28.6149, 77.2100)]
        distance = frechet_distance_simplified(path, path)
        assert distance == 0.0
    
    def test_different_paths(self):
        path1 = [(28.6139, 77.2090), (28.6149, 77.2100)]
        path2 = [(28.6140, 77.2091), (28.6150, 77.2101)]
        distance = frechet_distance_simplified(path1, path2)
        assert distance > 0
        assert distance < 200  # Should be small for similar paths
    
    def test_very_different_paths(self):
        path1 = [(28.6139, 77.2090), (28.6149, 77.2100)]
        path2 = [(19.0760, 72.8777), (19.0860, 72.8877)]
        distance = frechet_distance_simplified(path1, path2)
        assert distance > 100000  # Should be very large (>100km)
