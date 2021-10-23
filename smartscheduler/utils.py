import datetime as dt
import pyautogui as pa
import pyzbar.pyzbar as pyz
import webbrowser

from configparser import ConfigParser, Error as ConfigError
from smartscheduler.exceptions import CommonError, FatalError


__all__ = ["Utils"]


class Utils:
    """Provides utility services to various components of the Smart Scheduler application."""

    MEET_LINK: str = "https://meet.google.com/"

    @staticmethod
    def launch_browser(new_window: bool = True, url: str = "www.google.com"):
        """
        Open a link in the default web browser.

        Intercepts any errors encountered while opening the browser and raises a CommonError.
        :param new_window: optional, opens link in a new window if true
        :param url: optional, opens the google homepage by default
        """

        try:
            webbrowser.open(url=url, new=1 if new_window else 2)
        except webbrowser.Error as e:
            raise CommonError(e.args[0])

    @staticmethod
    def scan_qr():
        """
        Scan a QR code displayed on the screen.

        The function first takes a screen shot and scans the first QR code it locates. If none are found or there are
        errors while scanning/decoding the QR code, a CommonError is raised.
        :return: the data embedded in the QR code
        """

        capture = pa.screenshot()
        try:
            data = pyz.decode(capture)[0][0]
            data = data.decode("utf-8")
        except IndexError:
            raise CommonError("QR code image incomplete/not located.")
        except UnicodeError:
            raise CommonError("Could not decode URL.")
        except pyz.PyZbarError as e:
            raise CommonError(e.args[0])
        else:
            return data

    @staticmethod
    def open_class_link(link: str):
        Utils.launch_browser(url="https://meet.google.com/" + link)

    @staticmethod
    def time_obj(time_str: str, s_mins: int = None) -> dt.time:
        """
        Converts a time string into a datetime.time object.

        If s_mins is provided, the number of minutes given by it are subtracted from the datetime.time object.
        :param time_str: a time string, must have the format "HHMM"
        :param s_mins: optional, the number of minutes to subtract
        :return: a datetime.time object
        """

        time = dt.datetime.strptime(time_str, "%H%M").time()
        if s_mins is None:
            return time
        diff = dt.datetime.combine(dt.date.today(), time) - dt.datetime.combine(dt.date.today(), dt.time(minute=s_mins))
        return dt.time(hour=diff.seconds // 3600, minute=diff.seconds // 60 % 60)

    @staticmethod
    def time_str(time: str) -> str:
        """
        Converts a time string from "HHMM" to "HH:MM".
        :param time: a time string with the format "HHMM".
        :return: a time string with the format "HH:MM".
        """

        return dt.datetime.strftime(dt.datetime.strptime(time, "%H%M"), "%H:%M")

    @staticmethod
    def curr_day() -> int:
        """
        Return the current day as an integer, where Monday = 0, Tuesday = 1, ... , Sunday = 6.
        :return: an integer corresponding to the current day as per the computer's date and time
        """

        return dt.date.weekday(dt.date.today())

    @staticmethod
    def curr_time() -> dt.datetime:
        return dt.datetime.now()

    @staticmethod
    def paths():
        """
        Retrieve the paths for the database and the subjects file from the config.ini file.
        :return: a tuple containing the retrieved paths
        """

        paths = Config.get_config("paths")
        return paths["database"], paths["subjects"]

    @staticmethod
    def colours():
        """
        Retrieve the hex codes and labels of the colours to be used in the GUI.
        :return: a list of colour hex codes and their corresponding use case labels
        """

        c_labels = ["background", "text", "input", "mmu_blue", "mmu_red"]
        colours = Config.get_config("colours")
        return ["#" + colours[label] for label in c_labels]

    @staticmethod
    def fonts():
        """
        Retrieve the default font family and font family and size pairs to be used in the GUI.
        :return: a list containing the retrieved font specifications
        """

        fonts = Config.get_config("fonts")
        def_family = fonts["def_family"]
        return [
            def_family,
            (def_family, int(fonts["sz_normal"])),
            (def_family, int(fonts["sz_heading"])),
            (def_family, int(fonts["sz_title"]))
        ]


class Config(ConfigParser):

    def __init__(self):
        super().__init__()
        self.read("config.ini")

    @classmethod
    def get_config(cls, section: str):
        """
        Retrieve specific configuration info from the config.ini file.

        If there are any errors while retrieving configs, a FatalError is raised which will terminate the application.
        :param section: the section of config.ini from which configuration details are to be retrieved.
        :return: a ConfigParser.Section object containing the retrieved configuration details.
        """

        try:
            return cls()[section]
        except (KeyError, ConfigError):
            raise FatalError("Configuration file (config.ini) not found or corrupted.")


if __name__ == "__main__":
    # for quick testing

    pass
