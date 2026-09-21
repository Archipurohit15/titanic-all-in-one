from math import radians, sin, cos, sqrt, atan2
from django.conf import settings


def calculate_distance_km(lat, lng):
    if lat is None or lng is None:
        return None
    R = 6371
    lat1, lon1 = radians(settings.STORE_LATITUDE), radians(settings.STORE_LONGITUDE)
    lat2, lon2 = radians(float(lat)), radians(float(lng))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))