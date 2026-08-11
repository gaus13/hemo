def get_coordinates(location):
    if location is None:
        return None, None

    return location.y, location.x