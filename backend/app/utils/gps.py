"""
GPS distance calculation using the Haversine formula.

IMPORTANT LIMITATIONS OF BROWSER-BASED GPS:
1. Browser GPS accuracy varies (5-50m in open areas, 50-300m+ indoors)
2. GPS spoofing apps can fake location on mobile devices
3. This verification is a DETERRENT, not a foolproof security measure
4. Faculty should be aware that determined students could bypass GPS
5. The system logs distances for audit purposes
6. Recommended: Use GPS as an additional layer, not the sole verification

For educational institutions, the primary security is:
- Cryptographically random, short-lived QR tokens
- Database-level duplicate prevention
- Server-side validation of all data
"""
import math


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates
    using the Haversine formula.

    Args:
        lat1, lon1: Latitude/longitude of point 1 (faculty location)
        lat2, lon2: Latitude/longitude of point 2 (student location)

    Returns:
        Distance in meters

    Formula:
        a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
        c = 2 × atan2(√a, √(1−a))
        d = R × c   (where R = 6,371,000 meters)
    """
    R = 6_371_000  # Earth's radius in meters

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return round(distance, 2)


def is_within_radius(
    faculty_lat: float,
    faculty_lon: float,
    student_lat: float,
    student_lon: float,
    radius_meters: int,
) -> tuple[bool, float]:
    """
    Check if a student is within the allowed radius.

    Returns:
        (is_within: bool, distance_meters: float)
    """
    distance = calculate_distance(faculty_lat, faculty_lon, student_lat, student_lon)
    return distance <= radius_meters, distance
