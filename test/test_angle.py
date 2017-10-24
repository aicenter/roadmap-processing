"Angle unittest"
import unittest
import coords
from math import degrees

__author__ = "Zdenek Bousa"
__email__ = "bousazde@fel.cvut.cz"


class TestAngle(unittest.TestCase):
    def setUp(self):
        # In real life approx. 90 degrees, in 2D it is around +-106 degrees
        self.c1 = coords.get_coordinates_in_radians((50.103158, 14.402033))  # A
        self.c2 = coords.get_coordinates_in_radians((50.102739, 14.400353))  # vertex
        self.c3 = coords.get_coordinates_in_radians((50.102306, 14.400611))  # B
        self.c4 = coords.get_coordinates_in_radians((50.103708, 14.399776))  # B'

    def testRightAngle(self):
        """On unit circle (0,pi)"""
        angle = coords.angle_between_points(self.c1, self.c2, self.c2, self.c4)
        if 89 < degrees(angle) < 91:
            r = True
        else:
            r = False
        self.assertTrue(r, "Result is not approx. +90 degrees")

    def testLeftAngle(self):
        """On unit circle (pi,2pi)"""
        angle = coords.angle_between_points(self.c1, self.c2, self.c2, self.c3)
        if -89 > degrees(angle) > -91:
            r = True
        else:
            r = False
        self.assertTrue(r, "Result is not approx. -90 degrees")


if __name__ == "__main__":
    unittest.main()
