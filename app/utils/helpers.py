import math
from typing import Union

# ---------------------------------------------------------------------------
# Geo helper
# ---------------------------------------------------------------------------
def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two lat/lon pairs (Haversine).
    Returns kilometres.
    """
    # convert to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return 6371.0 * c   # Earth radius in km


# ---------------------------------------------------------------------------
# Error formatting
# ---------------------------------------------------------------------------
def format_error_message(err: Union[str, Exception]) -> str:
    """
    Turn an exception or arbitrary error object into a readable string.
    """
    return str(err) if isinstance(err, Exception) else str(err)
