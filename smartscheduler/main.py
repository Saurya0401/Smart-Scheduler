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
    """
    A decorator function to catch exceptions while executing database commands and re-raise them accordingly.

    The purpose of this function is to let the GUI manager know that something went wrong while sending a command to
    the database along with the severity of the error that happened.
    :param db_cmd: the function which can potentially raise an exception
    :return: the wrapper around db_cmd
    """

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
    """Contains most of the core logic for the Smart Scheduler application."""

    def __init__(self, config_file: str = None):
        """
        Initialise instance variables and get the database and subjects file path from the configuration file.
        :param config_file: path to non default config file (for testing)
        """

        try:
            self.db_path, self.subjects_path = Utils.paths(config_file or Utils.DEF_CONFIG_FILE)
            self.db = SmartSchedulerDB(self.db_path)
        except CommonDatabaseError:
            raise FatalError("Could not access database.")
        except CommonError as e:
            raise FatalError(e.args[0])
        self.session_id = None
        self.student_id = None
        self.curr_class_link = None
        self.update_sub_list()

    def __chk_s_id__(self, student_id: str) -> bool:
        """
        Check if an account exists in the accounts table in the database.
        :param student_id: the account's student ID
        :return: a boolean to confirm the account's existence
        """

        if not student_id:
            raise ValueError("Student ID cannot be empty.")
        if len(student_id) != 10:
            raise ValueError("Student ID must have exactly 10 digits.")
        if not student_id.isnumeric():
            raise ValueError("Student ID must contain only numbers.")
        return self.db.query_account_info(student_id, self.db.COL_STU_ID) != ()

    def __chk_pswrd__(self, student_id: str, pswrd: str) -> bool:
        """
        Check if entered account password matches password stored in database, by comparing salted password hashes.
        :param student_id: the account's student ID
        :param pswrd: the entered password
        :return: a boolean to confirm if the passwords match
        """

        pass_hash = self.db.query_account_info(student_id, self.db.COL_PSWRD_HASH)[0]
        return pbkdf2_sha256.verify(pswrd, pass_hash)

    def __chk_s_in__(self, student_id: str) -> bool:
        """
        Check if any session is currently logged in, i.e an account's session ID in database is not '0'.
        :param student_id: the account's student ID
        :return: a boolean to confirm if the session ID is '0'
        """

        return self.db.query_account_info(student_id, self.db.COL_SESSION_ID)[0] == "0"

    def __create_acc__(self, student_id: str, pswrd: str):
        """
        Create a new account in the database's accounts table.
        :param student_id: the account's student ID
        :param pswrd: the account's password
        """

        pass_hash = pbkdf2_sha256.hash(pswrd)
        self.db.new_account(student_id, pass_hash, str(Schedule.empty_schedule()), str({}))

    def __logged_in__(self, student_id: str) -> bool:
        """
        Check if current session is logged in, i.e. account's session ID in database equal current session ID.
        :param student_id: the account's student ID
        :return: a boolean to confirm if the current session is logged in
        """

        return self.db.query_account_info(student_id, self.db.COL_SESSION_ID)[0] == self.session_id

    def login(self, student_id: str, pswrd: str):
        """
        Login to an account.

        Intercepts exceptions and raises a CommonError if the account does not exist, or if the entered password is
        wrong, or if another session is logged in, or if there are database errors.
        :param student_id: the account's student ID
        :param pswrd: the account's password
        """

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
            self.db.update_account_info(self.student_id, self.db.COL_SESSION_ID, self.session_id)

    def logout(self, remote_student_id: str = None):
        """
        Logout of an account.

        Normally, the student ID of the account to logout from is stored in the variable self.student_id. However a
        remote student ID can be provided to logout remotely by disconnecting a session from the current session.
        Intercepts database errors and raises a CommonError.
        :param remote_student_id: the account's student ID for logging out remotely
        """

        try:
            if remote_student_id:
                return self.db.update_account_info(remote_student_id, self.db.COL_SESSION_ID, "0")
            else:
                if self.__logged_in__(self.student_id):
                    self.db.update_account_info(self.student_id, self.db.COL_SESSION_ID, "0")
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])
        else:
            self.student_id = None

    def change_pswrd(self, student_id: str, old_pswrd: str, new_pswrd: str, conf_pswrd: str):
        """
        Change an account's password.

        Intercepts exceptions and raises a CommonError if the account does not exist, or if the old password is
        wrong, or if new password confirmation fails, or if there are database errors.
        :param student_id: the account's student ID
        :param old_pswrd: the account's old password
        :param new_pswrd: the account's new password
        :param conf_pswrd: new password confirmation
        """

        try:
            if not self.__chk_s_id__(student_id):
                raise ValueError("Student ID not found.")
            if not self.__chk_pswrd__(student_id, old_pswrd):
                raise ValueError("Incorrect old password.")
            if not new_pswrd == conf_pswrd:
                raise ValueError("Password confirmation failed, please try again.")
            self.db.update_account_info(student_id, self.db.COL_PSWRD_HASH, pbkdf2_sha256.hash(new_pswrd))
        except ValueError as e:
            raise CommonError(e.args[0])
        except CommonDatabaseError as e:
            raise CommonError("[DBErr] " + e.args[0])

    def sign_up(self, student_id: str, pswrd: str, conf_pswrd: str):
        """
        Create an account.

        Intercepts exceptions and raises a CommonError if the account already exists, or if password confirmation
        fails, or if there are database errors.
        :param student_id: a student ID for the account
        :param pswrd: a password for the account
        :param conf_pswrd: confirmation for the password
        """

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
        """
        Delete the account corresponding to self.student_id from the database's accounts table.

        Raises CommonError if current session is not logged in.
        """

        if not self.__logged_in__(self.student_id):
            raise CommonError("logout")
        self.db.delete_account(self.student_id)

    @catch_db_err
    def get_schedule(self) -> dict:
        """
        Retrieve the schedule associated with self.student_id from the database.

        The schedule is retrieved from the database as a string and is converted into a dictionary by literal_eval().
        Raises CommonError if current session is not logged in.
        :return: the schedule as a dictionary
        """

        if not self.__logged_in__(self.student_id):
            raise CommonError("logout")
        return literal_eval(self.db.query_account_info(self.student_id, self.db.COL_SCHEDULE)[0])

    @catch_db_err
    def get_reg_subjects(self) -> dict:
        """
        Retrieve the registered subjects associated with self.student_id from the database.

        The subjects are retrieved from the database as a string and is converted into a dictionary by literal_eval().
        Raises CommonError if current session is not logged in.
        :return: the registered subjects as a dictionary
        """

        if not self.__logged_in__(self.student_id):
            raise CommonError("logout")
        return literal_eval(self.db.query_account_info(self.student_id, self.db.COL_SUBJECTS)[0])

    def get_class_link(self, reg_code: str) -> str:
        """
        Get the class link given the class's registration code.
        :param reg_code: the class's registration code
        :return: the class link as a string
        """

        return self.get_reg_subjects()[reg_code]

    @catch_db_err
    def update_reg_subjects(self, new_subs: dict):
        """
        Update the registered subjects associated with self.student_id from the database.

        The subjects are converted from a dictionary into a string representation before being stored in the database.
        Raises CommonError if current session is not logged in.
        :param new_subs: the updated subjects to store in the database
        """

        if not self.__logged_in__(self.student_id):
            raise CommonError("logout")
        self.db.update_account_info(self.student_id, self.db.COL_SUBJECTS, str(new_subs))

    @catch_db_err
    def update_schedule(self, new_sch: dict):
        """
        Update the schedule associated with self.student_id from the database.

        The schedule is converted from a dictionary into a string representation before being stored in the database.
        Raises CommonError if current session is not logged in.
        :param new_sch: the updated schedule to store in the database
        """

        if not self.__logged_in__(self.student_id):
            raise CommonError("logout")
        self.db.update_account_info(self.student_id, self.db.COL_SCHEDULE, str(new_sch))

    @catch_db_err
    def get_subjects_info(self) -> dict:
        """
        Retrieve the list of subjects available for registration.
        :return: A dictionary where the keys are the subject codes and the values are the corresponding subject names.
        """

        subs_info: list = self.db.retrieve_all(self.db.TAB_SUB_INFO)
        return {info[0]: info[1] for info in subs_info}

    def update_curr_link(self, reg_code: str):
        """
        Store the link of the current class corresponding to reg_code.
        :param reg_code: the registration code of the current class
        """

        self.curr_class_link = self.get_class_link(reg_code)

    def update_sub_list(self):
        """
        Update the list of subjects available for registration.

        The subjects are extracted from the subjects file specified by config.ini and then merged with the list of
        subjects currently stored in the database. Any error occurring during this process will raise a FatalError
        exception which will result in the application immediately terminating.
        """

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
    """Manages the registered subjects of an account."""

    def __init__(self, smart_sch: SmartScheduler):
        """
        Initialise instance variables and get the current registered subjects for the account.

        The account's student ID is provided by self.smart_sch. A deepcopy is also made of the registered subjects to
        later help in checking if any changes were made.
        :param smart_sch: an instance of SmartScheduler that provides the account information
        """

        self.smart_sch = smart_sch
        self.reg_subjects = self.smart_sch.get_reg_subjects()
        self.orig_reg_subjects = deepcopy(self.reg_subjects)
        self.subjects_info = self.smart_sch.get_subjects_info()

    def register_subject(self, reg_info: dict, old_reg_code: str = None):
        """
        Register a new subject, or edit the details of a previously registered subject corresponding to old_reg_code.
        :param reg_info: the information of the subject to be registered
        :param old_reg_code: optional, function acts as subject editor if provided
        """

        reg_code = reg_info["s_code"] + "_" + reg_info["c_type"]
        if reg_code in self.reg_subjects.keys() and old_reg_code is None:
            raise CommonError("Subject already registered.")
        if old_reg_code is not None:
            self.unregister_subject(old_reg_code)
        self.reg_subjects.update({reg_code: reg_info["c_link"]})

    def unregister_subject(self, reg_code: str):
        """
        Unregister a subject.
        :param reg_code: the registration code of the subject to unregister
        """

        del self.reg_subjects[reg_code]

    def subject_name(self, reg_code: str) -> str:
        """
        Return the name of a subject given its registration code.
        :param reg_code: the registration code of a subject
        :return: the name corresponding to the registration code
        """

        sub_code, class_type = reg_code.split("_")
        return self.subjects_info[sub_code] + " " + class_type

    def update_subjects(self):
        """Update the current registered subjects to the database."""

        self.smart_sch.update_reg_subjects(self.reg_subjects)

    def reg_subs_changed(self) -> bool:
        """
        Check if any changes have been made to the existing registered subjects.
        :return: a boolean to confirm if the registered subjects have been modified
        """

        return self.reg_subjects != self.orig_reg_subjects

    @staticmethod
    def sub_code_and_type(reg_code: str) -> list:
        """
        Convenience method to return the subject code and class type by splitting a registration code
        :param reg_code: a subject registration code
        :return: a list containing the subject code and class type
        """

        return reg_code.split("_")


class Class:
    """A convenient representation of a class object in the schedule."""

    def __init__(self, sub_code: str, class_type: str, day: str, start: str, end: str):
        self.sub_code = sub_code
        self.class_type = class_type
        self.class_day = day
        self.start_time = start
        self.end_time = end

    def __eq__(self, other):
        return self.class_id == other.class_id

    def __repr__(self) -> str:
        return str(self.class_id)

    @property
    def class_id(self) -> str:
        """
        Return the class id.
        :return: the class's class id
        """
        return "_".join([self.sub_code, self.class_type, self.class_day, self.start_time, self.end_time])

    @property
    def reg_code(self) -> str:
        """
        Return the registration code.
        :return: the class's registration code
        """
        return self.sub_code + "_" + self.class_type

    @classmethod
    def from_id(cls, class_id: str):
        """
        A class method to create a class instance from a class ID.
        :param class_id: a class ID
        :return: a Class object corresponding to class_id
        """

        class_attrs = class_id.split("_")
        return cls(*class_attrs)


class Schedule:
    """Manages the schedule of an account."""

    CLASS_DAYS = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    CLASS_HOURS = ("08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22")
    CLASS_MINS = ("00", "15", "30", "45")

    def __init__(self, smart_sch: SmartScheduler):
        """
        Initialise instance variables, get the current schedule, and filter out classes of unregistered subjects.
        :param smart_sch: an instance of SmartScheduler that provides the account information
        """

        self._smart_sch: SmartScheduler = smart_sch
        self._schedule: dict = self.__parse__(self._smart_sch.get_schedule())
        self._orig_schedule: dict = {}
        self._subjects_info: dict = self._smart_sch.get_subjects_info()
        self._reg_subjects: dict = self._smart_sch.get_reg_subjects()
        self.__filter__()

    def __parse__(self, schedule: dict) -> dict:
        """
        Build a schedule dictionary with Class objects.
        :param schedule: a schedule dictionary with class IDs
        :return: a schedule dictionary with class objects
        """

        return {day: [Class.from_id(class_id) for class_id in schedule[day]] for day in self.CLASS_DAYS.values()}

    def __filter__(self):
        """Update schedule dictionary to remove classes whose subjects have been unregistered."""

        reg_codes = self._reg_subjects.keys()
        for day, classes in self._schedule.items():
            filtered_classes = []
            for class_ in classes:
                if class_.reg_code in reg_codes:
                    filtered_classes.append(class_)
            self._schedule[day] = filtered_classes
        self._orig_schedule = deepcopy(self._schedule)
        self.update_schedule()

    @property
    def dict_schedule(self) -> dict:
        return self._schedule

    @property
    def db_schedule(self) -> dict:
        """
        Return a dictionary with all Class objects replaced with their respective class_IDs for storing in the database.
        :return: a dictionary containing class IDs
        """
        return {day: [class_.class_id for class_ in self._schedule[day]] for day in self.CLASS_DAYS.values()}

    @property
    def day_strs(self) -> tuple:
        return tuple(self.CLASS_DAYS.values())

    def add_class(self, class_: Class, old_class_: Class = None):
        """
        Add a new class, or edit the details of an existing class.
        :param class_: the Class object to add
        :param old_class_: optional, the class object to edit
        """

        if old_class_ is None:
            for reg_class in self._schedule[class_.class_day]:
                if class_.start_time == reg_class.start_time:
                    raise CommonError(f"There is already a {self.get_class_name(class_=reg_class)} class at this time.")
        else:
            self.delete_class(old_class_)
        self._schedule[class_.class_day].append(class_)
        self.sort_classes(class_.class_day)

    def delete_class(self, class_: Class):
        """
        Delete a class.
        :param class_: the Class object to delete
        """

        classes: list = self._schedule[class_.class_day]
        classes.remove(class_)
        self.sort_classes(class_.class_day)

    def get_subject_name(self, sub_code: str):
        """
        Retrieve the name of a subject given its subject code.
        :param sub_code: a subject code
        :return: the name of the subject as a string
        """

        return self._subjects_info[sub_code]

    def sort_classes(self, day: str):
        """
        For a given day, use the built-in list.sort() to sort Classes in ascending order according to their start times.
        :param day: the day whose classes must be sorted
        """

        self._schedule[day].sort(key=lambda class_: int(class_.start_time))

    def get_class_name(self, class_: Class = None, reg_code: str = None) -> str:
        """
        Retrieve the name of a class given the Class object and the subject registration code.
        :param class_: a Class object
        :param reg_code: a subject registration code
        :return: the class's name as a string
        """

        if reg_code:
            sub_code, class_type = Subjects.sub_code_and_type(reg_code)
        else:
            sub_code, class_type = class_.sub_code, class_.class_type
        return self.get_subject_name(sub_code) + " " + class_type

    def get_class_info(self, day: int = None, time: dt.time = None) -> tuple:
        """
        Retrieve information about the current and next class.

        For both the current and next class, a Class object is returned if they exist or None otherwise.
        :param day: optional, for testing
        :param time: optional, for testing
        :return: a tuple containing Class Objects, None or a mixture of both
        """

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
            # todo: fix time subtraction bug
            c_st: dt.time = Utils.time_obj(c_cls.start_time, 15)
            c_et: dt.time = Utils.time_obj(c_cls.end_time)
            n_cls: Class = day_sch[cls_ind + 1] if cls_ind + 1 < len(day_sch) else None
            if c_st <= curr_time <= c_et:
                if n_cls is not None:
                    return c_cls, n_cls
                return c_cls, None
        return None, None

    def schedule_changed(self) -> bool:
        """
        Check if any changes have been made to the existing schedule.
        :return: a boolean to confirm if the schedule has been modified
        """

        return self._schedule != self._orig_schedule

    def update_curr_class_link(self, curr_class: Class):
        """
        If there is currently a class, store its link.
        :param curr_class: a Class object whose corresponding link is to be stored
        """

        if curr_class:
            self._smart_sch.update_curr_link(curr_class.reg_code)

    def update_schedule(self):
        """Update the current schedule to the database."""

        self._smart_sch.update_schedule(self.db_schedule)

    @staticmethod
    def clear_schedule(smart_sch: SmartScheduler):
        """Clear schedule and update it to the database."""

        smart_sch.update_schedule(Schedule.empty_schedule())

    @staticmethod
    def class_duration(class_: Class) -> str:
        """
        Return the duration of a class.
        :param class_: a Class object
        :return: the duration of class_ as a string
        """

        return f"{Utils.time_str(class_.start_time)} - {Utils.time_str(class_.end_time)}"

    @staticmethod
    def empty_schedule() -> dict:
        """
        Return an empty schedule.
        :return: an empty schedule dictionary
        """

        return {day: [] for day in Schedule.CLASS_DAYS.values()}

    @staticmethod
    def int2day(day_idx: int):
        """
        Convert a day from an integer representation to its actual name.
        :param day_idx: the day as an integer
        :return: the day's actual name as a string
        """

        return Schedule.CLASS_DAYS[day_idx]


if __name__ == "__main__":
    # for quick testing

    pass
