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
    DEF_CONFIG_FILE: str = "./config.ini"

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
    def colours(config_file: str) -> list:
        """
        Retrieve the hex codes and labels of the colours to be used in the GUI.
        :param config_file: the config file path
        :return: a list of colour hex codes and their corresponding use case labels
        """

        c_labels = ["background", "text", "input", "mmu_blue", "mmu_red"]
        colours = _Config.get_config("colours", config_file)
        return ["#" + colours[label] for label in c_labels]

    @staticmethod
    def fonts(config_file: str) -> list:
        """
        Retrieve the default font family and font family and size pairs to be used in the GUI.
        :param config_file: the config file path
        :return: a list containing the retrieved font specifications
        """

        fonts = _Config.get_config("fonts", config_file)
        def_family = fonts["def_family"]
        return [
            def_family,
            (def_family, int(fonts["sz_normal"])),
            (def_family, int(fonts["sz_heading"])),
            (def_family, int(fonts["sz_title"]))
        ]


class _Config(ConfigParser):

    def __init__(self, config_file: str):
        super().__init__()
        self.read(config_file)

    @classmethod
    def get_config(cls, section: str, config_file: str):
        """
        Retrieve specific configuration info from the given config file.

        If there are any errors while retrieving configs, a FatalError is raised.
        :param section: the section of config_file from which configuration details are to be retrieved
        :param config_file: the configuration file path
        :return: a ConfigParser.Section object containing the retrieved configuration details
        """

        try:
            parser = cls(config_file)
            if not parser.has_section(section):
                raise KeyError(f"Configuration for \"{section}\" not found.")
        except ConfigError:
            raise FatalError("Configuration file (config.ini) not found or corrupted.")
        except KeyError as e:
            raise FatalError(e.args[0])
        else:
            return parser[section]


if __name__ == "__main__":
    # for quick testing

    pass
