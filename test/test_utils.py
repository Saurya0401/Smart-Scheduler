import datetime as dt
import unittest

from smartscheduler.utils import Utils


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.test_time_str = "1234"

    def test_time_obj(self):
        test_time_obj = dt.datetime.strptime(self.test_time_str, "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str), test_time_obj)

    def test_time_sub(self):
        sub_time_obj = dt.datetime.strptime("1204", "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str, 30), sub_time_obj)

    def test_colours(self):
        test_colours_list = ["#f0f0f0", "#000000", "#ffffff", "#0750a4", "#ed1b2f"]
        self.assertEqual(Utils.colours(), test_colours_list)

    def test_fonts(self):
        test_fonts_list = ["Helvetica", ("Helvetica", 10), ("Helvetica", 12), ("Helvetica", 14)]
        self.assertEqual(Utils.fonts(), test_fonts_list)


if __name__ == '__main__':
    unittest.main()
