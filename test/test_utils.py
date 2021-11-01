import datetime as dt
import unittest
from os import remove

from smartscheduler.utils import Utils
from smartscheduler.exceptions import FatalError


class UtilsTest(unittest.TestCase):
    """TEST B.1"""

    def setUp(self):
        self.config_path = "./test/test_config.ini"
        self.test_time_str = "1234"

    def test_b11_curr_day_and_time(self):
        """TEST_CASE_ID B.1.1"""
        self.assertEqual(Utils.curr_time(), dt.datetime.now())
        self.assertEqual(Utils.curr_day(), dt.datetime.weekday(dt.datetime.now()))

    def test_b12_time_obj(self):
        """TEST_CASE_ID B.1.2"""
        test_time_obj = dt.datetime.strptime(self.test_time_str, "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str), test_time_obj)

    def test_b13_time_str_conversion(self):
        """TEST_CASE_ID B.1.3"""
        test_time_str = "12:34"
        self.assertEqual(Utils.time_str("1234"), test_time_str)

    def test_b14_time_subtraction(self):
        """TEST_CASE_ID B.1.4"""
        sub_time_obj = dt.datetime.strptime("1204", "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str, 30), sub_time_obj)

    def test_b16_get_colours(self):
        """TEST_CASE_ID B.1.5"""
        test_colours_list = ["#111111", "#222222", "#333333", "#444444", "#555555"]
        self.assertEqual(Utils.colours(self.config_path), test_colours_list)
        self.assertRaises(FatalError, Utils.colours, "wrong/config_file/path")
        empty_config_file = "./test/empty_config.ini"
        with open(empty_config_file, 'w'):
            pass
        self.assertRaises(FatalError, Utils.colours, empty_config_file)
        remove(empty_config_file)

    def test_b17_get_fonts(self):
        """TEST_CASE_ID B.1.6"""
        test_fonts_list = ["Arial", ("Arial", 10), ("Arial", 20), ("Arial", 40)]
        self.assertEqual(Utils.fonts(self.config_path), test_fonts_list)
        self.assertRaises(FatalError, Utils.fonts, "wrong/config_file/path")
        empty_config_file = "./test/empty_config.ini"
        with open(empty_config_file, 'w'):
            pass
        self.assertRaises(FatalError, Utils.fonts, empty_config_file)
        remove(empty_config_file)


if __name__ == '__main__':
    unittest.main()
