import datetime as dt
import unittest

from smartscheduler.utils import Utils


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.config_path = "./test/test_config.ini"
        self.test_time_str = "1234"

    def test_time_obj(self):
        test_time_obj = dt.datetime.strptime(self.test_time_str, "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str), test_time_obj)

    def test_time_sub(self):
        sub_time_obj = dt.datetime.strptime("1204", "%H%M").time()
        self.assertEqual(Utils.time_obj(self.test_time_str, 30), sub_time_obj)

    def test_paths(self):
        test_paths_tuple = ("test/test_server/Test.db", "test/test_server/test_subjects.csv")
        self.assertEqual(Utils.paths(self.config_path), test_paths_tuple)

    def test_colours(self):
        test_colours_list = ["#111111", "#222222", "#333333", "#444444", "#555555"]
        self.assertEqual(Utils.colours(self.config_path), test_colours_list)

    def test_fonts(self):
        test_fonts_list = ["Arial", ("Arial", 10), ("Arial", 20), ("Arial", 40)]
        self.assertEqual(Utils.fonts(self.config_path), test_fonts_list)


if __name__ == '__main__':
    unittest.main()
