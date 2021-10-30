import datetime as dt
import unittest
from os import remove
from random import randint

from smartscheduler.main import SmartScheduler, Subjects, Class, Schedule
from smartscheduler.exceptions import CommonError, FatalError


class SmartSchedulerTest(unittest.TestCase):
    """TEST C.1"""

    smart_sch = None

    @classmethod
    def setUpClass(cls):
        cls.smart_sch = SmartScheduler("./test/test_config.ini")

    def setUp(self):
        self.unregistered_id = str(randint(10**9, 10**10 - 1))
        self.invalid_ids = ["", str(randint(10**8, 10**9 - 1)), "abcde12345"]

    def test_c11_sign_up(self):
        """TEST_CASE_ID C.1.1"""
        student_id, pswrd = str(randint(10**9, 10**10 - 1)), "test_password"
        registered_id = student_id
        wrong_pswrd = pswrd.upper()
        self.smart_sch.sign_up(student_id, pswrd, pswrd)
        self.assertEqual(self.smart_sch.__chk_s_id__(student_id), True)
        for i in self.invalid_ids:
            self.assertRaises(CommonError, self.smart_sch.sign_up, i, pswrd, pswrd)
        self.assertRaises(CommonError, self.smart_sch.sign_up, registered_id, pswrd, pswrd)
        self.assertRaises(CommonError, self.smart_sch.sign_up, self.unregistered_id, pswrd, wrong_pswrd)
        return student_id, pswrd

    def test_c12_login(self):
        """TEST_CASE_ID C.1.2"""
        student_id, pswrd = self.test_c11_sign_up()
        duplicate_id = student_id
        wrong_pswrd = pswrd.upper()
        self.smart_sch.login(student_id, pswrd)
        self.assertEqual(self.smart_sch.__logged_in__(student_id), True)
        for i in self.invalid_ids:
            self.assertRaises(CommonError, self.smart_sch.login, i, pswrd)
        self.assertRaises(CommonError, self.smart_sch.login, self.unregistered_id, pswrd)
        self.assertRaises(CommonError, self.smart_sch.login, student_id, wrong_pswrd)
        self.assertRaises(CommonError, self.smart_sch.login, duplicate_id, pswrd)
        return student_id, pswrd

    def test_c13_logout(self):
        """TEST_CASE_ID C.1.3"""
        student_id, pswrd = self.test_c12_login()
        self.smart_sch.logout()
        self.assertEqual(self.smart_sch.__logged_in__(student_id), False)

    def test_c14_change_pswrd(self):
        """TEST_CASE_ID C.1.4"""
        student_id, pswrd = self.test_c11_sign_up()
        wrong_pswrd = pswrd.upper()
        new_pswrd = "new_test_password"
        wrong_new_pswrd = "password_test_new"
        self.smart_sch.change_pswrd(student_id, pswrd, new_pswrd, new_pswrd)
        self.smart_sch.login(student_id, new_pswrd)
        self.assertEqual(self.smart_sch.__logged_in__(student_id), True)
        for i in self.invalid_ids:
            self.assertRaises(CommonError, self.smart_sch.change_pswrd, i, pswrd, new_pswrd, new_pswrd)
        self.assertRaises(CommonError, self.smart_sch.change_pswrd, self.unregistered_id, pswrd, new_pswrd, new_pswrd)
        self.assertRaises(CommonError, self.smart_sch.change_pswrd, student_id, wrong_pswrd, new_pswrd, new_pswrd)
        self.assertRaises(CommonError, self.smart_sch.change_pswrd, student_id, pswrd, new_pswrd, wrong_new_pswrd)

    def test_c15_del_acct(self):
        """TEST_CASE_ID C.1.5"""
        student_id, pswrd = self.test_c11_sign_up()
        self.smart_sch.login(student_id, pswrd)
        self.smart_sch.delete_acc()
        self.assertEqual(self.smart_sch.__chk_s_id__(student_id), False)

    def test_c16_update_sub_list(self):
        """TEST_CASE_ID C.1.6"""
        test_subs = [
            ("EMT1016", "Engineering Mathematics I"),
            ("EEL1166", "Circuit Theory"),
            ("EEL1176", "Field Theory"),
            ("EEE1016", "Electronics I"),
            ("ECE1016", "Computer and Program Design")
        ]
        self.smart_sch.update_sub_list()
        self.assertEqual(self.smart_sch.db.retrieve_all(self.smart_sch.db.TAB_SUB_INFO), test_subs)
        self.assertRaises(FatalError, lambda: SmartScheduler("wrong/subjects_file/path").update_sub_list())

    @classmethod
    def tearDownClass(cls):
        remove(cls.smart_sch.db_path)


class SubjectsTest(unittest.TestCase):
    """TEST C.2"""

    smart_sch = None
    student_id, pswrd = str(randint(10**9, 10**10 - 1)), "test_password"

    @classmethod
    def setUpClass(cls):
        cls.smart_sch = SmartScheduler("./test/test_config.ini")
        cls.smart_sch.sign_up(cls.student_id, cls.pswrd, cls.pswrd)
        cls.smart_sch.login(cls.student_id, cls.pswrd)

    def setUp(self):
        self.subjects = Subjects(self.smart_sch)

    def test_c21_get_reg_subjects(self):
        """TEST_CASE_ID C.2.1"""
        self.assertEqual(self.smart_sch.get_reg_subjects(), {})
        self.smart_sch.logout(self.smart_sch.student_id)
        self.assertRaises(CommonError, self.smart_sch.get_reg_subjects)
        self.smart_sch.login(self.student_id, self.pswrd)

    def test_c22_register_subject(self):
        """TEST_CASE_ID C.2.2"""
        test_reg_info = {
            "s_code": "EMT1016",
            "c_type": "Lecture",
            "c_link": "link"
        }
        test_reg_code = test_reg_info["s_code"] + "_" + test_reg_info["c_type"]
        self.subjects.register_subject(test_reg_info)
        self.assertIn(test_reg_code, self.subjects.reg_subjects.keys())
        self.assertEqual(self.subjects.reg_subjects[test_reg_code], test_reg_info["c_link"])
        self.assertRaises(CommonError, self.subjects.register_subject, test_reg_info)
        return test_reg_code

    def test_c23_edit_subject(self):
        """TEST_CASE_ID C.2.3"""
        old_reg_code = self.test_c22_register_subject()
        new_reg_info = {
            "s_code": "EMT1016",
            "c_type": "Tutorial",
            "c_link": "new_link"
        }
        new_reg_code = new_reg_info["s_code"] + "_" + new_reg_info["c_type"]
        self.subjects.register_subject(new_reg_info, old_reg_code)
        self.assertNotIn(old_reg_code, self.subjects.reg_subjects.keys())
        self.assertIn(new_reg_code, self.subjects.reg_subjects.keys())
        self.assertEqual(self.subjects.reg_subjects[new_reg_code], new_reg_info["c_link"])

    def test_c24_unregister_subject(self):
        """TEST_CASE_ID C.2.4"""
        reg_code = self.test_c22_register_subject()
        self.subjects.unregister_subject(reg_code)
        self.assertNotIn(reg_code, self.subjects.reg_subjects)

    def test_c25_update_subjects(self):
        """TEST_CASE_ID C.2.5"""
        old_reg_subjects = self.subjects.orig_reg_subjects
        reg_code = self.test_c22_register_subject()
        updated_reg_subjects = {
            reg_code: "link"
        }
        self.subjects.update_subjects()
        new_reg_subjects = self.smart_sch.get_reg_subjects()
        self.assertNotEqual(old_reg_subjects, new_reg_subjects)
        self.assertEqual(new_reg_subjects, updated_reg_subjects)
        self.smart_sch.logout(remote_student_id=self.smart_sch.student_id)
        self.assertRaises(CommonError, self.subjects.update_subjects)

    @classmethod
    def tearDownClass(cls):
        remove(cls.smart_sch.db_path)


class ClassTest(unittest.TestCase):
    """TEST C.3"""

    def setUp(self):
        self.class_ = Class("EMT1016", "Lecture", "Monday", "0800", "1000")

    def test_c31_class_id(self):
        """TEST_CASE_ID C.3.1"""
        test_class_id = "EMT1016_Lecture_Monday_0800_1000"
        self.assertEqual(self.class_.class_id, test_class_id)

    def test_c32_reg_code(self):
        """TEST_CASE_ID C.3.2"""
        test_reg_code = "EMT1016_Lecture"
        self.assertEqual(self.class_.reg_code, test_reg_code)

    def test_c33_from_class_id(self):
        """TEST_CASE_ID C.3.3"""
        test_class_id = "EMT1016_Lecture_Monday_0800_1000"
        class2_ = Class.from_id(test_class_id)
        self.assertEqual(class2_.class_id, self.class_.class_id)


class ScheduleTest(unittest.TestCase):
    """TEST C.4"""

    smart_sch = None
    student_id, pswrd = str(randint(10**9, 10**10 - 1)), "test_password"
    test_class_id = "EMT1016_Lecture_Monday_1000_1200"

    @classmethod
    def setUpClass(cls):
        cls.smart_sch = SmartScheduler("./test/test_config.ini")
        cls.smart_sch.sign_up(cls.student_id, cls.pswrd, cls.pswrd)
        cls.smart_sch.login(cls.student_id, cls.pswrd)

    def setUp(self):
        self.schedule = Schedule(self.smart_sch)

    def test_c041_get_schedule(self):
        """TEST_CASE_ID C.4.1"""
        self.assertEqual(self.smart_sch.get_schedule(), Schedule.empty_schedule())
        self.smart_sch.logout(self.smart_sch.student_id)
        self.assertRaises(CommonError, self.smart_sch.get_schedule)
        self.smart_sch.login(self.student_id, self.pswrd)

    def test_c042_parse_schedule(self):
        """TEST_CASE_ID C.4.2"""
        test_sch = {
            "Monday": [self.test_class_id],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": []
        }
        test_parsed_sch = {
            "Monday": [Class.from_id(self.test_class_id)],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": []
        }
        self.assertEqual(test_parsed_sch, self.schedule.__parse__(test_sch))

    def test_c043_db_schedule(self):
        """TEST_CASE_ID C.4.3"""
        test_dict_sch = {
            "Monday": [self.test_class_id],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": []
        }
        self.schedule.add_class(Class.from_id(self.test_class_id))
        self.assertEqual(self.schedule.db_schedule, test_dict_sch)
        self.schedule.delete_class(Class.from_id(self.test_class_id))

    def test_c044_add_class(self):
        """TEST_CASE_ID C.4.4"""
        test_class = Class.from_id(self.test_class_id)
        self.schedule.add_class(test_class)
        self.assertIn(test_class, self.schedule.dict_schedule[test_class.class_day])
        self.assertRaises(CommonError, self.schedule.add_class, test_class)
        return test_class

    def test_c045_edit_class(self):
        """TEST_CASE_ID C.4.5"""
        test_class = self.test_c044_add_class()
        edited_class = Class.from_id("EMT1026_Tutorial_Monday_0800_1000")
        self.schedule.add_class(edited_class, test_class)
        self.assertNotIn(test_class, self.schedule.dict_schedule[test_class.class_day])
        self.assertIn(edited_class, self.schedule.dict_schedule[edited_class.class_day])

    def test_c046_delete_class(self):
        """TEST_CASE_ID C.4.6"""
        test_class = self.test_c044_add_class()
        self.schedule.delete_class(test_class)
        self.assertNotIn(test_class, self.schedule.dict_schedule[test_class.class_day])

    def test_c047_class_info_only_curr_class(self):
        """TEST_CASE_ID C.4.7"""
        test_class_1 = Class.from_id("EEL1166_Tutorial_Tuesday_0800_1000")
        self.schedule.add_class(test_class_1)
        test_class_info = self.schedule.get_class_info(1, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsInstance(test_class_info[0], Class)
        self.assertIsNone(test_class_info[1])
        self.assertEqual(test_class_info[0].class_id, test_class_1.class_id)

    def test_c048_class_info_only_next_class(self):
        """TEST_CASE_ID C.4.8"""
        test_class_1 = Class.from_id("EEL1166_Lecture_Tuesday_1300_1500")
        self.schedule.add_class(test_class_1)
        test_class_info = self.schedule.get_class_info(1, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsNone(test_class_info[0])
        self.assertIsInstance(test_class_info[1], Class)
        self.assertEqual(test_class_info[1].class_id, test_class_1.class_id)

    def test_c049_class_info_curr_and_next_class(self):
        """TEST_CASE_ID C.4.9"""
        test_class_1 = Class.from_id("EEL1166_Lecture_Tuesday_1300_1500")
        test_class_2 = Class.from_id("EEL1166_Tutorial_Tuesday_0800_1000")
        self.schedule.add_class(test_class_1)
        self.schedule.add_class(test_class_2)
        test_class_info = self.schedule.get_class_info(1, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsInstance(test_class_info[0], Class)
        self.assertIsInstance(test_class_info[1], Class)
        self.assertEqual(test_class_info[0].class_id, test_class_2.class_id)
        self.assertEqual(test_class_info[1].class_id, test_class_1.class_id)

    def test_c410_class_info_no_classes(self):
        """TEST_CASE_ID C.4.10"""
        test_class_info = self.schedule.get_class_info(1, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsNone(test_class_info[0])
        self.assertIsNone(test_class_info[1])

    def test_c411_update_schedule(self):
        """TEST_CASE_ID C.4.11"""
        test_sch = {
            "Monday": [self.test_class_id],
            "Tuesday": [],
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
            "Saturday": [],
            "Sunday": []
        }
        old_schedule = self.schedule._orig_schedule
        self.test_c044_add_class()
        self.schedule.update_schedule()
        new_schedule = self.smart_sch.get_schedule()
        self.assertNotEqual(new_schedule, old_schedule)
        self.assertEqual(new_schedule, test_sch)
        self.smart_sch.logout(remote_student_id=self.smart_sch.student_id)
        self.assertRaises(CommonError, self.schedule.update_schedule)
        self.smart_sch.login(self.student_id, self.pswrd)

    def test_c412_filter_classes(self):
        """TEST_CASE_ID C.4.12"""
        test_sub_info_1 = {"s_code": "EMT1016", "c_type": "Lecture", "c_link": "link"}
        test_reg_code_1 = test_sub_info_1["s_code"] + "_" + test_sub_info_1["c_type"]
        sub = Subjects(self.smart_sch)
        sub.register_subject(test_sub_info_1)
        sub.update_subjects()
        self.test_c411_update_schedule()
        test_class = Class.from_id(self.test_class_id)
        self.schedule._reg_subjects = self.smart_sch.get_reg_subjects()
        self.schedule.__filter__()
        self.assertIn(test_class.class_id, self.smart_sch.get_schedule()[test_class.class_day])
        sub.unregister_subject(test_reg_code_1)
        sub.update_subjects()
        self.schedule._reg_subjects = self.smart_sch.get_reg_subjects()
        self.schedule.__filter__()
        self.assertNotIn(test_class.class_id, self.smart_sch.get_schedule()[test_class.class_day])

    def test_c413_clear_schedule(self):
        """TEST_CASE_ID C.4.13"""
        self.test_c411_update_schedule()
        self.assertNotEqual(self.smart_sch.get_schedule(), Schedule.empty_schedule())
        self.schedule.clear_schedule(self.smart_sch)
        self.assertEqual(self.smart_sch.get_schedule(), Schedule.empty_schedule())

    def test_c414_update_curr_class_link(self):
        """TEST_CASE_ID C.4.14"""
        sub = Subjects(self.smart_sch)
        sub.register_subject({"s_code": "EMT1016", "c_type": "Lecture", "c_link": "test_link"})
        sub.update_subjects()
        test_class_1 = Class.from_id("EMT1016_Lecture_Monday_1200_1400")
        self.schedule._reg_subjects = self.smart_sch.get_reg_subjects()
        self.schedule.add_class(test_class_1)
        test_class_info = self.schedule.get_class_info(0, dt.datetime.strptime("1200", "%H%M").time())
        self.schedule.update_curr_class_link(test_class_info[0])
        self.assertEqual(self.smart_sch.curr_class_link, "test_link")

    @classmethod
    def tearDownClass(cls):
        remove(cls.smart_sch.db_path)


if __name__ == '__main__':
    unittest.main()
