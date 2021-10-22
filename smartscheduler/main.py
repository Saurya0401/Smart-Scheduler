import csv
import datetime as dt
from ast import literal_eval
from copy import deepcopy
from passlib.hash import pbkdf2_sha256
from random import randint

from smartscheduler.database import SmartSchedulerDB
from smartscheduler.exceptions import CommonError, CommonDatabaseError, FatalError
from smartscheduler.utils import Utils


__all__ = ["SmartScheduler", "Subjects", "Class", "Schedule"]


def catch_db_err(db_cmd):
    def wrapper(*args, **kwargs):
        try:
            ret = db_cmd(*args, **kwargs)
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])
        except (CommonError, FatalError):
            raise
        else:
            return ret
    return wrapper


class SmartScheduler:

    def __init__(self):
        try:
            self.db_path, self.subjects_path = Utils.paths()
            self.db = SmartSchedulerDB(self.db_path)
        except CommonDatabaseError:
            raise FatalError("Could not access database.")
        except CommonError as e:
            raise FatalError(e.args[0])
        self.session_id = None
        self.student_id = None
        self.curr_class_link = None

    def __chk_s_id__(self, student_id: str) -> bool:
        if not student_id:
            raise ValueError("Student ID cannot be empty.")
        if len(student_id) != 10:
            raise ValueError("Student ID must have exactly 10 digits.")
        if not student_id.isnumeric():
            raise ValueError("Student ID must contain only numbers.")
        return self.db.fetch_record(student_id, self.db.COL_STU_ID) != ()

    def __chk_pswrd__(self, student_id: str, pswrd: str) -> bool:
        pass_hash = self.db.fetch_record(student_id, self.db.COL_PAS_HASH)[0]
        return pbkdf2_sha256.verify(pswrd, pass_hash)

    def __chk_s_in__(self, student_id: str) -> bool:
        return self.db.fetch_record(student_id, self.db.COL_SESSION_ID)[0] == "0"

    def __create_acc__(self, student_id: str, pswrd: str):
        pass_hash = pbkdf2_sha256.hash(pswrd)
        self.db.new_record(student_id, pass_hash, str(Schedule.empty_schedule()), str({}))

    def __signed_in__(self, student_id: str) -> bool:
        return self.db.fetch_record(student_id, self.db.COL_SESSION_ID)[0] == self.session_id

    def login(self, student_id: str, pswrd: str):
        try:
            if not self.__chk_s_id__(student_id):
                raise ValueError("Student ID not found.")
            if not self.__chk_pswrd__(student_id, pswrd):
                raise ValueError("Incorrect password.")
            if not self.__chk_s_in__(student_id):
                raise CommonError("logout")
        except ValueError as e:
            raise CommonError(e.args[0])
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])
        except CommonError:
            raise
        else:
            self.session_id = "".join([str(randint(1, 9)) for _ in range(32)])
            self.student_id = student_id
            self.db.update_record(self.student_id, self.db.COL_SESSION_ID, self.session_id)

    def logout(self, remote_student_id: str = None):
        try:
            if remote_student_id:
                return self.db.update_record(remote_student_id, self.db.COL_SESSION_ID, "0")
            else:
                if self.__signed_in__(self.student_id):
                    self.db.update_record(self.student_id, self.db.COL_SESSION_ID, "0")
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])
        else:
            self.student_id = None

    def change_pswrd(self, student_id: str, old_pswrd: str, new_pswrd: str, conf_pswrd: str):
        try:
            if not self.__chk_s_id__(student_id):
                raise ValueError("Student ID not found.")
            if not self.__chk_pswrd__(student_id, old_pswrd):
                raise ValueError("Incorrect old password.")
            if not new_pswrd == conf_pswrd:
                raise ValueError("Password confirmation failed, please try again.")
            self.db.update_record(student_id, self.db.COL_PAS_HASH, pbkdf2_sha256.hash(new_pswrd))
        except ValueError as e:
            raise CommonError(e.args[0])
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])

    def sign_up(self, student_id: str, pswrd: str, conf_pswrd: str):
        try:
            if self.__chk_s_id__(student_id):
                raise ValueError("Student ID already registered.")
            if not pswrd == conf_pswrd:
                raise ValueError("Password confirmation failed, please try again.")
            self.__create_acc__(student_id, pswrd)
        except ValueError as e:
            raise CommonError(e.args[0])
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])

    @catch_db_err
    def delete_acc(self):
        if not self.__signed_in__(self.student_id):
            raise CommonError("logout")
        self.db.delete_record(self.student_id)

    @catch_db_err
    def get_schedule(self) -> dict:
        if not self.__signed_in__(self.student_id):
            raise CommonError("logout")
        return literal_eval(self.db.fetch_record(self.student_id, self.db.COL_SCHEDULE)[0])

    @catch_db_err
    def get_reg_subjects(self) -> dict:
        if not self.__signed_in__(self.student_id):
            raise CommonError("logout")
        return literal_eval(self.db.fetch_record(self.student_id, self.db.COL_SUBJECTS)[0])

    def get_class_link(self, reg_code: str) -> str:
        return self.get_reg_subjects()[reg_code]

    @catch_db_err
    def update_reg_subjects(self, new_subs: dict):
        if not self.__signed_in__(self.student_id):
            raise CommonError("logout")
        self.db.update_record(self.student_id, self.db.COL_SUBJECTS, str(new_subs))

    @catch_db_err
    def update_schedule(self, new_sch: dict):
        if not self.__signed_in__(self.student_id):
            raise CommonError("logout")
        self.db.update_record(self.student_id, self.db.COL_SCHEDULE, str(new_sch))

    @catch_db_err
    def get_subjects_info(self) -> dict:
        subs_info: list = self.db.fetch_all_data(self.db.TAB_SUB_INFO)
        return {info[0]: info[1] for info in subs_info}

    @catch_db_err
    def get_subject_name(self, sub_code: str) -> str:
        return self.db.fetch_sub_name(sub_code)[0]

    def update_curr_link(self, reg_code: str):
        self.curr_class_link = self.get_class_link(reg_code)

    def update_sub_list(self):
        try:
            with open(self.subjects_path) as sub_f:
                reader = csv.DictReader(sub_f)
                subs_info = [(sub["sub_code"], sub["sub_name"]) for sub in reader]
            self.db.make_subs_list(subs_info)
        except csv.Error:
            raise FatalError("Subjects info file corrupted.")
        except FileNotFoundError:
            raise FatalError("Subjects info file not found.")
        except CommonDatabaseError as e:
            raise FatalError(e.args[0])


class Subjects:

    def __init__(self, smart_sch: SmartScheduler):
        self.smart_sch = smart_sch
        self.reg_subjects = self.smart_sch.get_reg_subjects()
        self.orig_reg_subjects = deepcopy(self.reg_subjects)
        self.subjects_info = self.smart_sch.get_subjects_info()

    def register_subject(self, reg_info: dict, old_reg_code: str = None):
        reg_code = reg_info["s_code"] + "_" + reg_info["c_type"]
        if reg_code in self.reg_subjects.keys() and old_reg_code is None:
            raise CommonError("Subject already registered.")
        if old_reg_code is not None:
            self.unregister_subject(old_reg_code)
        self.reg_subjects.update({reg_code: reg_info["c_link"]})

    def unregister_subject(self, reg_code: str):
        del self.reg_subjects[reg_code]

    def subject_name(self, reg_code: str):
        sub_code, class_type = reg_code.split("_")
        return self.subjects_info[sub_code] + " " + class_type

    def update_subjects(self):
        self.smart_sch.update_reg_subjects(self.reg_subjects)

    def reg_subs_changed(self) -> bool:
        return self.reg_subjects != self.orig_reg_subjects

    @staticmethod
    def sub_code_and_type(reg_code: str) -> list:
        return reg_code.split("_")


class Class:

    def __init__(self, sub_code: str, class_type: str, day: str, start: str, end: str):
        self.sub_code = sub_code
        self.class_type = class_type
        self.class_day = day
        self.start_time = start
        self.end_time = end

    def __repr__(self) -> str:
        return str(self.class_id)

    @property
    def class_id(self) -> str:
        return "_".join([self.sub_code, self.class_type, self.class_day, self.start_time, self.end_time])

    @property
    def reg_code(self) -> str:
        return self.sub_code + "_" + self.class_type

    @classmethod
    def from_id(cls, class_id):
        class_attrs = class_id.split("_")
        assert len(class_attrs) == 5
        return cls(*class_attrs)


class Schedule:
    CLASS_DAYS = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    CLASS_HOURS = ("08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22")
    CLASS_MINS = ("00", "15", "30", "45")

    def __init__(self, smart_sch: SmartScheduler):
        self._smart_sch: SmartScheduler = smart_sch
        self._schedule: dict = self.__parse__(self._smart_sch.get_schedule())
        self._orig_schedule: dict = {}
        self._subjects_info: dict = self._smart_sch.get_subjects_info()
        self._reg_subjects: dict = self._smart_sch.get_reg_subjects()
        self.__filter__()

    def __parse__(self, schedule: dict) -> dict:
        return {day: [Class.from_id(class_id) for class_id in schedule[day]] for day in self.CLASS_DAYS.values()}

    def __filter__(self):
        reg_codes = self._reg_subjects.keys()
        for day, classes in self._schedule.items():
            filtered_classes = []
            for class_ in classes:
                if class_.reg_code in reg_codes:
                    filtered_classes.append(class_)
            self._schedule[day] = filtered_classes
        self._orig_schedule = deepcopy(self._schedule)
        # print(f"(filter) {self._schedule == self._orig_schedule}\n{self._schedule}\n{self._orig_schedule}")
        self.update_schedule()

    @property
    def dict_schedule(self) -> dict:
        return self._schedule

    @property
    def db_schedule(self) -> dict:
        return {day: [class_.class_id for class_ in self._schedule[day]] for day in self.CLASS_DAYS.values()}

    @property
    def day_strs(self) -> tuple:
        return tuple(self.CLASS_DAYS.values())

    def add_class(self, class_: Class, old_class_: Class = None):
        if old_class_ is None:
            for reg_class in self._schedule[class_.class_day]:
                if class_.start_time == reg_class.start_time:
                    raise CommonError(f"There is already a {self.get_class_name(class_=reg_class)} class at this time.")
        else:
            self.delete_class(old_class_)
        self._schedule[class_.class_day].append(class_)
        self.sort_classes(class_.class_day)

    def delete_class(self, class_: Class):
        classes: list = self._schedule[class_.class_day]
        classes.remove(class_)
        self.sort_classes(class_.class_day)

    def get_subject_name(self, sub_code: str):
        return self._subjects_info[sub_code]

    def sort_classes(self, day: str):
        self._schedule[day].sort(key=lambda class_: int(class_.start_time))

    def get_class_name(self, class_: Class = None, reg_code: str = None) -> str:
        if reg_code:
            sub_code, class_type = Subjects.sub_code_and_type(reg_code)
        else:
            sub_code, class_type = class_.sub_code, class_.class_type
        return self.get_subject_name(sub_code) + " " + class_type

    def get_class_info(self, day: int = None, time: dt.time = None) -> tuple:
        curr_day: int = day if day is not None else Utils.curr_day()
        curr_time: dt.time = time or Utils.curr_time().time()
        day_sch: list = self._schedule[self.int2day(curr_day)]
        if not day_sch:
            return None, None
        if curr_time < Utils.time_obj(day_sch[0].start_time, s_mins=15):
            return None, day_sch[0]
        if curr_time > Utils.time_obj(day_sch[-1].end_time):
            return None, None
        for cls_ind in range(len(day_sch)):
            c_cls: Class = day_sch[cls_ind]
            c_st: dt.time = Utils.time_obj(str(int(c_cls.start_time) - 50))
            c_et: dt.time = Utils.time_obj(c_cls.end_time)
            n_cls: Class = day_sch[cls_ind + 1] if cls_ind + 1 < len(day_sch) else None
            if c_st <= curr_time <= c_et:
                if n_cls is not None:
                    return c_cls, n_cls
                return c_cls, None
        return None, None

    def schedule_changed(self) -> bool:
        return self._schedule != self._orig_schedule

    def update_curr_class_link(self, curr_class: Class):
        if curr_class:
            self._smart_sch.update_curr_link(curr_class.reg_code)

    def reset_schedule(self):
        self._smart_sch.update_schedule(self.empty_schedule())

    def update_schedule(self):
        self._smart_sch.update_schedule(self.db_schedule)

    @staticmethod
    def class_duration(class_: Class) -> str:
        return f"{Utils.time_str(class_.start_time)} - {Utils.time_str(class_.end_time)}"

    @staticmethod
    def check_time() -> bool:
        return dt.datetime.strftime(Utils.curr_time(), "%H") in Schedule.CLASS_HOURS

    @staticmethod
    def empty_schedule() -> dict:
        return {day: [] for day in Schedule.CLASS_DAYS.values()}

    @staticmethod
    def int2day(day_idx: int):
        return Schedule.CLASS_DAYS[day_idx]


if __name__ == "__main__":

    def test():
        pass

    test()
