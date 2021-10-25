import datetime as dt
import unittest
from os import remove
from random import randint

from smartscheduler.main import SmartScheduler, Subjects, Class, Schedule
from smartscheduler.exceptions import CommonError, FatalError


class SmartSchedulerTest(unittest.TestCase):

    def setUp(self):
        self.smart_sch = SmartScheduler("./test/test_config.ini")
        self.unregistered_id = str(randint(10**9, 10**10 - 1))
        self.invalid_ids = ["", str(randint(10**8, 10**9 - 1)), "abcde12345"]

    def test_sign_up(self):
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

    def test_login(self):
        student_id, pswrd = self.test_sign_up()
        duplicate_id = student_id
        wrong_pswrd = pswrd.upper()
        self.smart_sch.login(student_id, pswrd)
        self.assertEqual(self.smart_sch.__logged_in__(student_id), True)
        for i in self.invalid_ids:
            self.assertRaises(CommonError, self.smart_sch.login, i, pswrd)
        self.assertRaises(CommonError, self.smart_sch.login, self.unregistered_id, pswrd)
        self.assertRaises(CommonError, self.smart_sch.login, student_id, wrong_pswrd)
        self.assertRaises(CommonError, self.smart_sch.login, duplicate_id, pswrd)

    def test_logout(self):
        student_id, pswrd = self.test_sign_up()
        self.smart_sch.login(student_id, pswrd)
        self.smart_sch.logout()
        self.assertEqual(self.smart_sch.__logged_in__(student_id), False)

    def test_change_pswrd(self):
        student_id, pswrd = self.test_sign_up()
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

    def test_del_acct(self):
        student_id, pswrd = self.test_sign_up()
        self.smart_sch.login(student_id, pswrd)
        self.smart_sch.delete_acc()
        self.assertEqual(self.smart_sch.__chk_s_id__(student_id), False)

    def test_update_sub_list(self):
        test_subs = [
            ("EMT1016", "Engineering Mathematics I"),
            ("EEL1166", "Circuit Theory"),
            ("EEL1176", "Field Theory"),
            ("EEE1016", "Electronics I"),
            ("ECE1016", "Computer and Program Design")
        ]
        self.smart_sch.update_sub_list()
        self.assertEqual(self.smart_sch.db.retrieve_all(self.smart_sch.db.TAB_SUB_INFO), test_subs)
        self.assertRaises(FatalError, lambda: SmartScheduler("wrong/config_file/path").update_sub_list())

    def tearDown(self):
        remove(self.smart_sch.db_path)


class SubjectsTest(unittest.TestCase):

    def setUp(self):
        self.smart_sch = SmartScheduler("./test/test_config.ini")
        student_id, pswrd = str(randint(10**9, 10**10 - 1)), "test_password"
        self.smart_sch.sign_up(student_id, pswrd, pswrd)
        self.smart_sch.login(student_id, pswrd)
        self.subjects = Subjects(self.smart_sch)

    def test_get_reg_subjects(self):
        self.assertEqual(self.smart_sch.get_reg_subjects(), {})
        self.smart_sch.logout(self.smart_sch.student_id)
        self.assertRaises(CommonError, self.smart_sch.get_reg_subjects)

    def test_register_subject(self):
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

    def test_edit_subject(self):
        old_reg_code = self.test_register_subject()
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

    def test_unregister_subject(self):
        reg_code = self.test_register_subject()
        self.subjects.unregister_subject(reg_code)
        self.assertNotIn(reg_code, self.subjects.reg_subjects)

    def test_update_subjects(self):
        old_reg_subjects = self.subjects.orig_reg_subjects
        self.test_register_subject()
        self.subjects.update_subjects()
        new_reg_subjects = self.smart_sch.get_reg_subjects()
        self.assertNotEqual(old_reg_subjects, new_reg_subjects)
        self.smart_sch.logout(remote_student_id=self.smart_sch.student_id)
        self.assertRaises(CommonError, self.subjects.update_subjects)

    def tearDown(self):
        remove(self.smart_sch.db_path)


class ClassTest(unittest.TestCase):

    def setUp(self):
        self.class_ = Class("EMT1016", "Lecture", "Monday", "0800", "1000")

    def test_class_id(self):
        test_class_id = "EMT1016_Lecture_Monday_0800_1000"
        self.assertEqual(self.class_.class_id, test_class_id)

    def test_reg_code(self):
        test_reg_code = "EMT1016_Lecture"
        self.assertEqual(self.class_.reg_code, test_reg_code)

    def test_from_class_id(self):
        test_class_id = "EMT1016_Lecture_Monday_0800_1000"
        class2_ = Class.from_id(test_class_id)
        self.assertEqual(class2_.class_id, self.class_.class_id)


class ScheduleTest(unittest.TestCase):

    def setUp(self):
        self.smart_sch = SmartScheduler("./test/test_config.ini")
        self.student_id, self.pswrd = str(randint(10**9, 10**10 - 1)), "test_password"
        self.test_class_id = "EMT1016_Lecture_Monday_1000_1200"
        self.smart_sch.sign_up(self.student_id, self.pswrd, self.pswrd)
        self.smart_sch.login(self.student_id, self.pswrd)
        self.schedule = Schedule(self.smart_sch)

    def test_get_schedule(self):
        self.assertEqual(self.smart_sch.get_schedule(), Schedule.empty_schedule())
        self.smart_sch.logout(self.smart_sch.student_id)
        self.assertRaises(CommonError, self.smart_sch.get_schedule)

    def test_db_schedule(self):
        test_dict_sch = self.schedule.empty_schedule()
        self.assertEqual(self.schedule.dict_schedule, test_dict_sch)

    def test_add_class(self, class_id: str = None):
        test_class = Class.from_id(class_id or self.test_class_id)
        self.schedule.add_class(test_class)
        self.assertIn(test_class, self.schedule.dict_schedule[test_class.class_day])
        self.assertRaises(CommonError, self.schedule.add_class, test_class)
        return test_class

    def test_edit_class(self):
        test_class = self.test_add_class()
        edited_class = Class.from_id("EMT1026_Tutorial_Monday_0800_1000")
        self.schedule.add_class(edited_class, test_class)
        self.assertNotIn(test_class, self.schedule.dict_schedule[test_class.class_day])
        self.assertIn(edited_class, self.schedule.dict_schedule[edited_class.class_day])

    def test_delete_class(self):
        test_class = self.test_add_class()
        self.schedule.delete_class(test_class)
        self.assertNotIn(test_class, self.schedule.dict_schedule[test_class.class_day])

    def test_update_schedule(self):
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
        self.test_add_class()
        self.schedule.update_schedule()
        new_schedule = self.smart_sch.get_schedule()
        self.assertNotEqual(new_schedule, old_schedule)
        self.assertEqual(new_schedule, test_sch)
        self.smart_sch.logout(remote_student_id=self.smart_sch.student_id)
        self.assertRaises(CommonError, self.schedule.update_schedule)
        self.smart_sch.login(self.student_id, self.pswrd)

    def test_class_info_only_curr_class(self):
        self.test_add_class()
        test_class_info = self.schedule.get_class_info(0, dt.datetime.strptime("0950", "%H%M").time())
        self.assertIsInstance(test_class_info[0], Class)
        self.assertIsNone(test_class_info[1])
        self.assertEqual(test_class_info[0].class_id, self.test_class_id)

    def test_class_info_only_next_class(self):
        self.test_add_class()
        test_class_info = self.schedule.get_class_info(0, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsNone(test_class_info[0])
        self.assertIsInstance(test_class_info[1], Class)
        self.assertEqual(test_class_info[1].class_id, self.test_class_id)

    def test_class_info_curr_and_next_class(self):
        test_class_2_id = "EEL1166_Tutorial_Monday_0800_1000"
        self.test_add_class()
        self.test_add_class(test_class_2_id)
        test_class_info = self.schedule.get_class_info(0, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsInstance(test_class_info[0], Class)
        self.assertIsInstance(test_class_info[1], Class)
        self.assertEqual(test_class_info[0].class_id, test_class_2_id)
        self.assertEqual(test_class_info[1].class_id, self.test_class_id)

    def test_class_info_no_classes(self):
        test_class_info = self.schedule.get_class_info(0, dt.datetime.strptime("0800", "%H%M").time())
        self.assertIsNone(test_class_info[0])
        self.assertIsNone(test_class_info[1])

    def test_filter_classes(self):
        test_sub_info_1 = {"s_code": "EMT1016", "c_type": "Lecture", "c_link": "link"}
        test_reg_code_1 = test_sub_info_1["s_code"] + "_" + test_sub_info_1["c_type"]
        sub = Subjects(self.smart_sch)
        sub.register_subject(test_sub_info_1)
        sub.update_subjects()
        self.test_update_schedule()
        test_class = Class.from_id(self.test_class_id)
        self.schedule._reg_subjects = self.smart_sch.get_reg_subjects()
        self.schedule.__filter__()
        self.assertIn(test_class.class_id, self.smart_sch.get_schedule()[test_class.class_day])
        sub.unregister_subject(test_reg_code_1)
        sub.update_subjects()
        self.schedule._reg_subjects = self.smart_sch.get_reg_subjects()
        self.schedule.__filter__()
        self.assertNotIn(test_class.class_id, self.smart_sch.get_schedule()[test_class.class_day])

    def test_parse_schedule(self):
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

    def test_clear_schedule(self):
        self.test_update_schedule()
        self.assertNotEqual(self.smart_sch.get_schedule(), Schedule.empty_schedule())
        self.schedule.clear_schedule(self.smart_sch)
        self.assertEqual(self.smart_sch.get_schedule(), Schedule.empty_schedule())

    def test_update_curr_class_link(self):
        sub = Subjects(self.smart_sch)
        sub.register_subject({"s_code": "EMT1016", "c_type": "Lecture", "c_link": "link"})
        sub.update_subjects()
        self.schedule.update_curr_class_link(Class.from_id(self.test_class_id))
        self.assertEqual(self.smart_sch.curr_class_link, "link")

    def tearDown(self):
        remove(self.smart_sch.db_path)


if __name__ == '__main__':
    unittest.main()
