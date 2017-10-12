"""Helpful tools for work with coordinates and angles between them."""
from math import cos, asin, sqrt, sin, degrees, atan2, isnan, pi
from numpy import radians, array

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"


def get_lat_lon(coords):
    """Return coordinates in order latitude, longitude"""
    return coords[1], coords[0]


def get_lon_lat(coords):
    """Return coordinates in order longitude,latitude"""
    return coords[0], coords[1]


def get_distance_between_coords(point1, point2):
    """Point[lat,lon] (not in radians), returns distance in meters. Based on
    https://en.wikipedia.org/wiki/Haversine_formula """
    p = 0.017453292519943295  # pi/180
    q = 0.5 - cos((point2[0] - point1[0]) * p) / 2 + cos(point1[0] * p) * cos(point2[0] * p) * (
        1 - cos((point2[1] - point1[1]) * p)) / 2
    return 2 * 6378137.0 * asin(sqrt(q))  # 2 * earth radius in meters *....


def get_coordinates_in_radians(coordinates_in_degree):
    """Returns coordinates in radians from decimal degrees"""
    return radians(array(coordinates_in_degree))


def get_coordinates_in_degree(coordinates_in_radian):
    """Return coordinates in decimal degrees from radians"""
    return degrees(array(coordinates_in_radian))


def get_coordinates_in_3d(coordinates_in_radians):
    """Returns point in 3D space. Parameter coordinates[lat,lon]"""
    lat_radians = coordinates_in_radians[0]
    lon_radians = coordinates_in_radians[1]
    return array((cos(lat_radians) * cos(lon_radians), cos(lat_radians) * sin(lon_radians), sin(lat_radians)))


def angle_between_vectors_radians(v_a, v_b):
    """Return angle in radians, interval (-pi,pi>"""
    r = atan2(v_a[1], v_a[0]) - atan2(v_b[1], v_b[0])
    # check nan
    if isnan(r):
        r = 0
    # check interval
    if r <= (-pi):
        r = r + (2 * pi)
    if r > pi:
        r = r - (2 * pi)
    return r


def angle_between_points(p1_rad, p2_rad, p3_rad, p4_rad):
    """ Vector A = [p1_rad,p2_rad] and vector B = [p3_rad,p4_rad].
    Angle is measured between P1 - vertext(P2,P3) - P4. Interval +-<0-180>.
    Including spherical correction.

    Return: angle in radians

    Example:

        P4
         \
          \   (alpha)
    P2=P3  \____________
           /            P1
          /   (beta)
         /
        P4'

    Angle alpha = -(beta), in this example approx. alpha=110 degrees and beta=-110 degrees.
    """
    v_a = [p2_rad[0] - p1_rad[0], p2_rad[1] - p1_rad[1]]
    v_b = [p3_rad[0] - p4_rad[0], p3_rad[1] - p4_rad[1]]

    # correction to 2D at given lat
    v_a[1] = v_a[1] * cos(p2_rad[0])
    v_b[1] = v_b[1] * cos(p3_rad[0])

    return angle_between_vectors_radians(v_a, v_b)
