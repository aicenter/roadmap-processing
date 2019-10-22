import math
import utm
import numpy as np

from typing import Tuple
from roadmaptools.init import config


class TransposedUTM:
    def __init__(self):
        self.origin_easting: float = None
        self.origin_northing: float = None
        self.origin_zone_number: int = None
        self.origin_zone_letter: str = None

    @classmethod
    def from_gps(cls, origin_lat: float, origin_lon: float):
        # self.origin_lat = origin_lat
        # self.origin_lon = origin_lon

        res = utm.from_latlon(origin_lat, origin_lon)

        projection = cls()

        projection.origin_easting = res[0]
        projection.origin_northing = res[1]
        projection.origin_zone_number = res[2]
        projection.origin_zone_letter = res[3]

        return projection

    @classmethod
    def from_zone(cls, zone_number: int, zone_letter: str):
        projection = cls()
        projection.origin_zone_number = zone_number
        projection.origin_zone_letter = zone_letter

        return projection

    def wgs84_to_utm(self, lat, lon):
        easting, northing, _, _ = utm.from_latlon(lat, lon, force_zone_number=self.origin_zone_number)
        if config.shift_utm_coordinate_origin_to_utm_center:
            easting -= self.origin_easting
            northing -= self.origin_northing
        return easting, northing

    def utm_to_wgs84(self, easting, northing):
        if config.shift_utm_coordinate_origin_to_utm_center:
            easting += self.origin_easting
            northing += self.origin_northing
        return utm.to_latlon(easting, northing, self.origin_zone_number, self.origin_zone_letter)


# Project to Euclidean plane such that the units are meters.
default_projection = TransposedUTM.from_gps(config.utm_center_lon, config.utm_center_lat)


# default_projection = None


def np_wgs84_to_utm(latlon, projection: TransposedUTM = default_projection):
    easting, northing = np.vectorize(projection.wgs84_to_utm)(latlon[:, 0], latlon[:, 1])
    return np.column_stack([easting, northing])


def np_utm_to_wgs84(latlon, projection: TransposedUTM = default_projection):
    lat, lon = np.vectorize(projection.utm_to_wgs84)(latlon[:, 0], latlon[:, 1])
    return np.column_stack([lat, lon])


def wgs84_to_utm(latitude: float, longitude: float, projection: TransposedUTM = default_projection) -> Tuple[
    float, float]:
    return projection.wgs84_to_utm(latitude, longitude)


def wgs84_to_utm_1E2(latitude: float, longitude: float, projection: TransposedUTM = default_projection) \
        -> Tuple[int, int]:
    """
    Returns utm coordinates in centimeter precision. Coresponds to the Geographtools implementation.
    :param latitude: Latitude WGS84
    :param longitude: Longitude WGS84
    :param projection: UTM projection
    :return: Projected coordinates as a centimeter precision integer.
    """
    return tuple(int(round(coord * 1E2)) for coord in wgs84_to_utm(latitude, longitude, projection))


def utm_to_wgs84(latitude: float, longitude: float, projection: TransposedUTM = default_projection) -> Tuple[
    float, float]:
    return projection.utm_to_wgs84(latitude, longitude)


def get_id_from_utm_coords(x: float, y: float) -> int:
    y_int = int(round(y, 3) * 1000)
    return int(round(x, 3) * 1000) * int(math.pow(10, len(str(y_int)))) + y_int


class CoordinateConvertor:
    projection = default_projection

    @staticmethod
    def convert(latitude: float, longitude: float) -> Tuple[float, float]:
        return wgs84_to_utm(latitude, longitude, CoordinateConvertor.projection)
