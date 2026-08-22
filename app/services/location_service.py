from typing import Optional, Tuple

from geoalchemy2.shape import to_shape


def get_coordinates(
    location,
) -> Tuple[Optional[float], Optional[float]]:

    if location is None:
        return None, None

    point = to_shape(location)

    return point.y, point.x