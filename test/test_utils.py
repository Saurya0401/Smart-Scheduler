import datetime as dt
import unittest

from smartscheduler.utils import Utils
from smartscheduler.exceptions import FatalError


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.config_path = "./test/test_config.ini"
        self.test_time_str = "1234"

    def test_curr_day_and_time(self):
        self.assertEqual(Utils.curr_time(), dt.datetime.now())
        self.assertEqual(Utils.curr_day(), dt.datetime.weekday(dt.datetime.now()))

    def test_time_obj(self):
        test_time_obj = dt.datetime.strptime(self.test_time_str, "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str), test_time_obj)

    def test_time_str(self):
        test_time_str = "12:34"
        self.assertEqual(Utils.time_str("1234"), test_time_str)

    def test_time_sub(self):
        sub_time_obj = dt.datetime.strptime("1204", "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str, 30), sub_time_obj)

    def test_paths(self):
        test_paths_tuple = ("test/test_server/Test.db", "test/test_server/test_subjects.csv")
        self.assertEqual(Utils.paths(self.config_path), test_paths_tuple)
        self.assertRaises(FatalError, Utils.paths, "wrong/config_file/path")

    def test_colours(self):
        test_colours_list = ["#111111", "#222222", "#333333", "#444444", "#555555"]
        self.assertEqual(Utils.colours(self.config_path), test_colours_list)
        self.assertRaises(FatalError, Utils.colours, "wrong/config_file/path")

    def test_fonts(self):
        test_fonts_list = ["Arial", ("Arial", 10), ("Arial", 20), ("Arial", 40)]
        self.assertEqual(Utils.fonts(self.config_path), test_fonts_list)
        self.assertRaises(FatalError, Utils.fonts, "wrong/config_file/path")


if __name__ == '__main__':
    unittest.main()
