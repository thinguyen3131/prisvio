import math
from collections.abc import Callable
from enum import Enum
from typing import Any

from django.utils.encoding import force_str


def ensure_string(func: Callable) -> Callable:
    def function_wrapper(*args, **kwargs) -> str:
        return_value: Any = func(*args, **kwargs)
        if isinstance(return_value, Enum):
            return force_str(return_value.value)
        return force_str(return_value)

    return function_wrapper


def haversine(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    radius = 6371.0
    distance = radius * c

    return round(distance, 2)
