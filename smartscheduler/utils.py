import datetime as dt
import pyautogui as pa
import pyzbar.pyzbar as pyz
import webbrowser

from configparser import ConfigParser, Error as ConfigError
from smartscheduler.exceptions import CommonError, FatalError


__all__ = ["Utils"]


class Utils:

    MEET_LINK: str = "https://meet.google.com/"

    @staticmethod
    def launch_browser(new_window: bool = True, url: str = "www.google.com"):
        try:
            webbrowser.open(url=url, new=1 if new_window else 2)
        except webbrowser.Error as e:
            raise CommonError(e.args[0])

    @staticmethod
    def scan_qr():
        capture = pa.screenshot()
        try:
            url = pyz.decode(capture)[0][0]
            url = url.decode("utf-8")
        except IndexError:
            raise CommonError("QR code image incomplete/not located.")
        except UnicodeError:
            raise CommonError("Could not decode URL.")
        except pyz.PyZbarError as e:
            raise CommonError(e.args[0])
        else:
            return url

    @staticmethod
    def open_class_link(link: str):
        Utils.launch_browser(url="https://meet.google.com/" + link)

    @staticmethod
    def time_obj(time_str: str, s_mins: int = None) -> dt.time:
        time = dt.datetime.strptime(time_str, "%H%M").time()
        if s_mins is None:
            return time
        diff = dt.datetime.combine(dt.date.today(), time) - dt.datetime.combine(dt.date.today(), dt.time(minute=s_mins))
        return dt.time(hour=diff.seconds // 3600, minute=diff.seconds // 60 % 60)

    @staticmethod
    def time_str(time: str) -> str:
        return dt.datetime.strftime(dt.datetime.strptime(time, "%H%M"), "%H:%M")

    @staticmethod
    def curr_day() -> int:
        return dt.date.weekday(dt.date.today())

    @staticmethod
    def curr_time() -> dt.datetime:
        return dt.datetime.now()

    @staticmethod
    def paths():
        paths = Config.get_config("paths")
        return paths["database"], paths["subjects"]

    @staticmethod
    def colours():
        c_labels = ["background", "text", "input", "mmu_blue", "mmu_red"]
        colours = Config.get_config("colours")
        return ["#" + colours[label] for label in c_labels]

    @staticmethod
    def fonts():
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
        try:
            return cls()[section]
        except (KeyError, ConfigError):
            raise FatalError("Configuration file (config.ini) not found or corrupted.")


if __name__ == "__main__":
    print(Utils.colours())
