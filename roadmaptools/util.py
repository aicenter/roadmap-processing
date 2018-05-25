from math import radians, cos, sin, asin, sqrt


def filter_dict(input_dict: dict, keys: set):
    """
    Return a copy of input dictionary that contains only the specified keys.

    """
    out_dict = dict()
    for key in keys:
        if key in input_dict.keys():
            out_dict[key] = input_dict[key]

    return out_dict


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km * 1000.0