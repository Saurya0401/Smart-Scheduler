import tkinter as tk
from tkinter import ttk, messagebox

from smartscheduler.main import SmartScheduler, Subjects, Class, Schedule
from smartscheduler.exceptions import CommonError, FatalError
from smartscheduler.utils import Utils


class GUtils:
    """Provides graphical utilities for tkinter windows."""

    class ScrollableFrame(tk.Frame):
        def __init__(self, parent, edit_mode: bool):
            super().__init__(parent)
            self.edit_mode = edit_mode
            self.canvas = tk.Canvas(self, height=100 if self.edit_mode else 250, bd=0, highlightthickness=0)
            self.frame = tk.Frame(self.canvas)
            self.vsb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vsb.set)

            self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas.create_window((4, 4), window=self.frame, anchor=tk.NW)
            self.canvas.bind("<Configure>", self.on_canvas_configure)
            self.frame.bind("<Configure>", self.on_frame_configure)

        def on_canvas_configure(self, _):
            if self.edit_mode:
                self.canvas.yview_moveto("1.0")

        def on_frame_configure(self, event):
            self.canvas.configure(width=event.width, scrollregion=self.canvas.bbox(tk.ALL))

    @staticmethod
    def btn_press_anim(btn: tk.Button):
        fg, bg = btn.cget("fg"), btn.cget("bg")
        btn.config(relief=tk.SUNKEN, fg=Colours.TEXT, bg=Colours.BG)
        btn.after(200, lambda: btn.config(relief=tk.FLAT, fg=fg, bg=bg))

    @staticmethod
    def disp_msg(msg: str, msg_t: str, parent: tk.Tk or tk.Toplevel):
        """
        Display a message in a pop up dialog box.

        The look of the dialog box differs based on whether the message is just information, an error, or a warning.
        :param msg: the message to display
        :param msg_t: the nature of the message to display
        :param parent: which window this dialog box should belong to
        """

        if msg_t == "info":
            return messagebox.showinfo("Info", msg, parent=parent)
        elif msg_t == "err":
            return messagebox.showerror("Error", msg, parent=parent)
        elif msg_t == "warn":
            return messagebox.showwarning("Warning", msg, parent=parent)

    @staticmethod
    def disp_conf(title: str, msg: str, parent: tk.Tk or tk.Toplevel) -> bool:
        """
        Display a confirmation dialog box with "Yes" and "No" options.
        :param title: the title of the dialog box
        :param msg: the message to display
        :param parent: which window this dialog box should belong to
        :return: a boolean to represent the user's decision
        """

        return messagebox.askyesno(title, msg, parent=parent)

    @staticmethod
    def hidden_win(parent: tk.Tk = None):
        win = tk.Toplevel(master=parent) if parent else tk.Tk()
        win.withdraw()
        return win

    @staticmethod
    def loading_win(parent: tk.Tk or tk.Toplevel, msg: str = "Loading") -> tk.Toplevel:
        """
        Create and return a tk.TopLevel window that indicates a "loading" action.
        :param parent: which window this TopLevel window should belong
        :param msg: the text to display, default is "Loading"
        :return: a tk.TopLevel window
        """

        win = tk.Toplevel(master=parent)
        win.overrideredirect(True)
        wait_l = tk.Label(master=win, text=f"{msg}, please wait...", **Style.def_txt(font=Font.HEADING))
        wait_l.pack(expand=1, fill=tk.BOTH)
        win.geometry("400x100+%d+%d" % GUtils.win_pos(win, 0.4, 0.4))
        return win

    @staticmethod
    def win_pos(window: tk.Tk or tk.Toplevel, w_mul: float, h_mul: float) -> tuple:
        """
        Return the position of a window on the screen but modified with height and width multipliers.
        :param window: the window whose position must be determined
        :param w_mul: the width multiplier
        :param h_mul: the height multiplier
        :return: a tuple containing the x and y coordinates of the window
        """

        scr_w, scr_h = window.winfo_screenwidth(), window.winfo_screenheight()
        return int(w_mul * scr_w), int(h_mul * scr_h)

    @staticmethod
    def lift_win(window: tk.Tk or tk.Toplevel, pin: bool = False):
        """
        Lift a window to the top layer of the OS's window manager and then optionally pin it in place.
        :param window: the window to be lifted
        :param pin: optional, the window will be pinned to the top layer of the window manager if true
        """

        window.grab_set()
        if pin:
            window.lift()
            window.attributes("-topmost", True)
        else:
            window.focus_set()

    @staticmethod
    def disp_loading(loading_win: tk.Toplevel, gui_cmd, *args, **kwargs):
        """
        Display a loading screen to mask the execution a GUI command.
        :param loading_win: the loading window to display
        :param gui_cmd: the gui command to execute
        :param args: arguments for the gui command
        :param kwargs: keyword arguments for the gui command
        """

        if not loading_win.winfo_viewable():
            loading_win.deiconify()
        loading_win.after(100, lambda: gui_cmd(*args, **kwargs))

    @staticmethod
    def destroy_all(parent: tk.BaseWidget or tk.Tk):
        for widget in parent.winfo_children():
            widget.destroy()
        parent.destroy()


class Colours:
    """The colours used in the GUI, retrieved from config.ini."""

    try:
        BG, TEXT, INPUT, M_BLUE, M_RED = Utils.colours(Utils.DEF_CONFIG_FILE)
    except FatalError as e:
        temp = GUtils.hidden_win()
        GUtils.disp_msg("Unable to retrieve colour hex codes from config.ini."
                        "\nSwitching to default values.", "warn", temp)
        BG, TEXT, INPUT, M_BLUE, M_RED = "#f0f0f0", "#000000", "#ffffff", "#0750a4", "#ed1b2f"
        temp.destroy()


class Font:
    """The font and font sizes used in the GUI, retrieved from config.ini."""

    try:
        DEF_FAMILY, NORMAL, HEADING, TITLE = Utils.fonts(Utils.DEF_CONFIG_FILE)
    except FatalError as e:
        temp = GUtils.hidden_win()
        GUtils.disp_msg("Unable to retrieve font family and size values from config.ini."
                        "\nSwitching to default values.", "warn", temp)
        DEF_FAMILY = "Helvetica"
        NORMAL, HEADING, TITLE = (DEF_FAMILY, 10), (DEF_FAMILY, 12), (DEF_FAMILY, 14)
        temp.destroy()


class Padding:
    """Provides a range of horizontal and vertical padding combinations for tkinter widgets."""

    DEF_X = 5
    DEF_Y = 5

    @staticmethod
    def pad(values: tuple):
        return {"padx": values[0], "pady": values[1]}

    @staticmethod
    def none():
        return Padding.pad((0, 0))

    @staticmethod
    def default(x: tuple = None, y: tuple = None):
        return Padding.pad((x or Padding.DEF_X, y or Padding.DEF_Y))

    @staticmethod
    def col_elem(x: tuple = None):
        return Padding.pad((x or Padding.DEF_X, (0, Padding.DEF_Y)))

    @staticmethod
    def btm_elem(x: tuple = None):
        return Padding.pad((x or Padding.DEF_X, 0))

    @staticmethod
    def col_no_x():
        return Padding.pad((0, (0, Padding.DEF_Y)))

    @staticmethod
    def no_right(y: tuple = None):
        return Padding.pad(((Padding.DEF_X, 0), y or Padding.DEF_Y))

    @staticmethod
    def no_left(y: tuple = None):
        return Padding.pad(((0, Padding.DEF_X), y or Padding.DEF_Y))

    @staticmethod
    def btm_right():
        return Padding.pad(((0, Padding.DEF_X), (0, Padding.DEF_Y)))


class Style:
    """Provides default styles for text and button widgets."""

    @staticmethod
    def def_btn(width: int = 10, bg: str = Colours.M_BLUE, font: tuple = Font.NORMAL):
        return {"width": width, "font": font, "fg": Colours.INPUT, "bg": bg, "relief": tk.FLAT}

    @staticmethod
    def txt_btn(width: int = 10, font: tuple = (Font.DEF_FAMILY, 9, "underline")):
        return {"width": width, "font": font, "fg": Colours.TEXT, "bg": Colours.BG, "relief": tk.FLAT}

    @staticmethod
    def def_txt(font: tuple = Font.NORMAL, fg: str = Colours.TEXT, justify: str = "left"):
        return {"font": font, "fg": fg, "justify": justify}

    @staticmethod
    def def_combo(values: list, textvariable: tk.StringVar, width: int = 3):
        return {"values": values, "textvariable": textvariable, "width": width, "state": "readonly"}


class SubjectEditor(tk.Toplevel):
    """Displays a window for editing registered subjects."""

    def __init__(self, parent: "MainWindow"):
        """
        Initialises widgets and builds the registered subjects editor window.
        :param parent: the parent MainWindow instance
        """

        super().__init__(master=parent)
        self._refresh_f = parent.refresh

        try:
            self._subjects = Subjects(parent.smart_sch)
        except CommonError:
            self.destroy()
            raise

        self._subjects_list = {sub_code: f"{sub_code} - {sub_name}" for sub_code, sub_name in
                               self._subjects.subjects_info.items()}

        self.title("Edit Subjects")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.__close__)

        self.main_f = tk.Frame(self)
        self.reg_subs_f = tk.LabelFrame(self.main_f, relief=tk.GROOVE, labelanchor='n', bd=1, labelwidget=tk.Label(
            self.main_f, text="Registered Subjects", **Style.def_txt(Font.HEADING, Colours.M_BLUE)))
        self.btn_f = tk.Frame(self.main_f)
        self.reg_sub_b = tk.Button(self.btn_f, text="Register Subject", **Style.def_btn(26),
                                   command=self.__reg_sub__)
        self.exit_b = tk.Button(self.btn_f, text="Save and Exit", **Style.def_btn(26, bg=Colours.M_RED),
                                command=self.__upd_subs__)

        self.main_f.grid(sticky="nsew")
        self.reg_subs_f.grid(row=1, column=1, sticky="nsew", **Padding.default())
        self.btn_f.grid(row=2, column=1, sticky="nsew")
        self.btn_f.grid_columnconfigure(2, weight=10)
        self.reg_sub_b.grid(row=1, column=1, **Padding.col_elem())
        self.exit_b.grid(row=1, column=3, **Padding.col_elem())
        self.disp_subjects()
        self.geometry("+%d+%d" % GUtils.win_pos(self, 0.35, 0.35))
        GUtils.lift_win(self)

    def disp_subjects(self):
        """Refreshes list of displayed subjects."""

        i = 1
        for sub_f in self.reg_subs_f.winfo_children():
            sub_f.destroy()
        if not self._subjects.reg_subjects:
            no_sub_l = tk.Label(self.reg_subs_f, text="No registered subjects.", **Style.def_txt())
            return no_sub_l.grid(sticky="nsew", **Padding.default())
        for reg_code in self._subjects.reg_subjects.keys():
            sub_f = tk.Frame(self.reg_subs_f)
            sub_name_l = tk.Label(sub_f, text=self._subjects.subject_name(reg_code), anchor="w", width=30,
                                  wraplength=300, **Style.def_txt())
            sub_edit_b = tk.Button(sub_f, text="Edit", **Style.def_btn(),
                                   command=lambda rc=reg_code: self.__edit_sub__(rc))
            sub_del_b = tk.Button(sub_f, text="Delete", **Style.def_btn(bg=Colours.M_RED),
                                  command=lambda rc=reg_code: self.__del_sub__(rc))
            sub_f.grid(row=i, column=1, sticky="nsew", **Padding.pad((0, (Padding.DEF_Y if i == 1 else 0, 0))))
            sub_f.grid_columnconfigure(2, weight=10)
            sub_name_l.grid(row=1, column=1, sticky="nsew", **Padding.col_elem())
            sub_edit_b.grid(row=1, column=3, sticky="e", **Padding.col_elem())
            sub_del_b.grid(row=1, column=4, sticky="e", **Padding.btm_right())
            i += 1
        GUtils.lift_win(self)

    def __reg_sub__(self, edit_reg_code: str = None):
        """
        Register a new subject or edit an existing one.
        :param edit_reg_code: optional, will edit subject corresponding to this registration code if provided
        """

        def __close__():
            GUtils.destroy_all(inp_w)
            GUtils.lift_win(self)

        def __register__():
            s_name: str = sub_sel.get()
            c_type: str = class_type.get()
            c_link: str = class_link.get()
            try:
                if not s_name:
                    raise CommonError("Please choose a subject.")
                elif not c_type:
                    raise CommonError("Please choose a class type.")
                elif not c_link:
                    raise CommonError("Class link cannot be empty.")
                sub_code: str = s_name.split(" - ")[0]
                old_reg_code: str = edit_reg_code
                self._subjects.register_subject({
                    "s_code": sub_code,
                    "c_type": c_type,
                    "c_link": c_link,
                }, old_reg_code=old_reg_code)
            except CommonError as e:
                error: str = e.args[0]
                error_l = tk.Label(inp_f, text=error, **Style.def_txt(fg=Colours.M_RED))
                error_l.grid(row=1, column=1, sticky="w", **Padding.pad((Padding.DEF_X, (Padding.DEF_Y, 0))))
            else:
                GUtils.destroy_all(inp_w)
                return self.disp_subjects()

        init_s_code, init_c_type = self._subjects.sub_code_and_type(edit_reg_code) \
            if edit_reg_code is not None else (None, "Lecture")
        init_s_name = self._subjects_list[init_s_code] if init_s_code is not None else ""
        init_c_link = self._subjects.reg_subjects[edit_reg_code] if edit_reg_code is not None else ""
        inp_w = tk.Toplevel(self)
        inp_w.protocol("WM_DELETE_WINDOW", __close__)
        inp_f = tk.Frame(inp_w)
        sub_sel = tk.StringVar(inp_f)
        class_type = tk.StringVar(inp_f, init_c_type)
        class_link = tk.StringVar(inp_f, init_c_link)
        sub_l = tk.Label(inp_f, text="Choose subject:", **Style.def_txt())
        sub_c = ttk.Combobox(inp_f, values=list(self._subjects_list.values()), textvariable=sub_sel, width=55,
                             state="readonly")
        if init_s_name:
            sub_c.set(init_s_name)
        class_type_f = tk.LabelFrame(inp_f, relief=tk.GROOVE, bd=2, labelwidget=tk.Label(
            inp_f, text="Class type:", **Style.def_txt()))
        lec_c = tk.Radiobutton(class_type_f, text="Lecture", **Style.def_txt(), value="Lecture", variable=class_type)
        tut_c = tk.Radiobutton(class_type_f, text="Tutorial", **Style.def_txt(), value="Tutorial", variable=class_type)
        class_link_f = tk.LabelFrame(inp_f, relief=tk.GROOVE, bd=2, labelwidget=tk.Label(
            inp_f, text="Class link:", **Style.def_txt()))
        class_link_l = tk.Label(class_link_f, text=Utils.MEET_LINK, **Style.def_txt(fg=Colours.M_BLUE))
        class_link_e = tk.Entry(class_link_f, textvariable=class_link)
        submit_b = tk.Button(inp_f, text="Submit", **Style.def_btn(), command=__register__)

        inp_f.grid(sticky="nsew")
        sub_l.grid(row=2, column=1, **Padding.default(), sticky="w")
        sub_c.grid(row=3, column=1, **Padding.col_elem())
        class_type_f.grid(row=4, column=1, sticky="nsew", **Padding.col_elem())
        lec_c.grid(row=1, column=1, **Padding.default())
        tut_c.grid(row=1, column=2, **Padding.default())
        class_link_f.grid(row=5, column=1, sticky="nsew", **Padding.col_elem())
        class_link_l.grid(row=1, column=1, **Padding.default())
        class_link_e.grid(row=1, column=2, **Padding.no_left())
        submit_b.grid(row=6, column=1, **Padding.col_elem())

        GUtils.lift_win(inp_w)
        inp_w.geometry("+%d+%d" % GUtils.win_pos(self, 0.35, 0.35))

    def __del_sub__(self, reg_code: str):
        """
        Delete a subject from registered subjects.
        :param reg_code: the registration code of the subject to delete
        """

        self._subjects.unregister_subject(reg_code)
        self.disp_subjects()

    def __edit_sub__(self, reg_code: str):
        """
        Edit a subject from registered subjects.
        :param reg_code: the registration code of the subject to edit
        """

        self.__reg_sub__(reg_code)

    def __upd_subs__(self):
        """
        Attempt to update current registered subjects to the database and close subject editor window.

        Refreshes schedule if database is successfully updated.
        """

        loading_win = GUtils.loading_win(self, "Saving registered subjects")
        loading_win.update()
        try:
            reg_subs_changed = self._subjects.reg_subs_changed()
            if reg_subs_changed:
                self._subjects.update_subjects()
        except CommonError as e:
            if e.flag == "l_out":
                GUtils.disp_msg("You have been logged out.", "err", self)
                self.__close__(check_changed=False)
            else:
                loading_win.destroy()
                GUtils.disp_msg("Could not update registered subjects.\n" + e.args[0], "err", self)
        else:
            if reg_subs_changed:
                self._refresh_f()
            self.__close__(check_changed=False)

    def __close__(self, check_changed: bool = True):
        """
        Optionally warn about changes made to registered subjects and close subject editor window.
        :param check_changed: optional, will show a warning if registered subjects have been modified
        """

        if self._subjects.reg_subs_changed() and check_changed:
            if GUtils.disp_conf("Exit", "You have unsaved changes, exit?", self):
                GUtils.destroy_all(self)
        else:
            GUtils.destroy_all(self)


class ScheduleEditor:
    """Rebuilds displayed schedule or displays a window to edit schedule."""

    def __init__(self, parent: "MainWindow", edit_mode: bool):
        """
        Rebuild displayed schedule or initialise widgets and build window for editing schedule.
        :param parent: the parent MainWindow instance
        :param edit_mode: a boolean flag that signals if the schedule is to be refreshed or edited
        """

        self._smart_sch = parent.smart_sch
        self._refresh_f = parent.refresh
        self.edit_mode = edit_mode

        try:
            self.schedule = Schedule(self._smart_sch)
            self.disp_subs = {self.schedule.get_class_name(reg_code=reg_code): reg_code for reg_code in
                              self._smart_sch.get_reg_subjects().keys()}
        except CommonError:
            raise

        self._reg_subs = self._smart_sch.get_reg_subjects()

        if self.edit_mode:
            if not self._reg_subs:
                raise CommonError(flag="no_subs")
            self._edit_day = Utils.curr_day()
            self._root = tk.Toplevel(master=parent)
            self._root.title("Edit Schedule")
            self._root.resizable(False, False)
            self._root.protocol("WM_DELETE_WINDOW", self.__close__)

            self._main_f = tk.Frame(self._root)
            self._schedule_n = self.build_schedule(focus_day=self._edit_day)
            self._btn_f = tk.Frame(self._main_f)
            self._add_class_b = tk.Button(self._btn_f, text="Add Class", **Style.def_btn(26),
                                          command=self.__add_class__)
            self._exit_b = tk.Button(self._btn_f, text="Save and Exit", **Style.def_btn(26, Colours.M_RED),
                                     command=self.__upd_sch__)

            self._main_f.grid(sticky="nsew")
            self._schedule_n.grid(row=1, column=1, sticky="nsew", **Padding.default())
            self._btn_f.grid(row=2, column=1, sticky="nsew", **Padding.default())
            self._btn_f.grid_columnconfigure(2, weight=10)
            self._add_class_b.grid(row=1, column=1, **Padding.col_elem())
            self._exit_b.grid(row=1, column=3, **Padding.col_elem())

            self._root.geometry("+%d+%d" % GUtils.win_pos(self._root, 0.35, 0.35))
            GUtils.lift_win(self._root)

    def __refresh_sch__(self):
        """Reconstruct schedule widget to reflect any changes made to the schedule."""

        self._schedule_n.destroy()
        self._schedule_n = self.build_schedule()
        self._schedule_n.grid(row=1, column=1, sticky="nsew", **Padding.default())
        GUtils.lift_win(self._root)

    def __day_layout__(self, classes_: list, day_str_: str, schedule_n: ttk.Notebook) -> tk.Frame:
        """Build widgets to display each day in the schedule."""
        container_f = GUtils.ScrollableFrame(schedule_n, self.edit_mode)
        layout_f = container_f.frame
        if not classes_:
            status_l = tk.Label(layout_f, text=f"No classes on {day_str_}.", **Style.def_txt())
            status_l.grid(row=1, column=1, sticky="nsew", **Padding.pad((50, 50)))
        else:
            i = 1
            for class_ in classes_:
                class_f = tk.Frame(layout_f)
                class_time = Utils.time_str(class_.start_time) + " - " + Utils.time_str(class_.end_time)
                class_time_l = tk.Label(class_f, text=class_time, **Style.def_txt())
                class_name_l = tk.Label(class_f, text=self.schedule.get_class_name(class_=class_), anchor="w",
                                        width=30, wraplength=300, **Style.def_txt())
                class_f.grid(row=i, column=1, sticky="nsew", **Padding.pad((0, (10 if i == 1 else 0, 0))))
                class_time_l.grid(row=1, column=1, sticky="nsew", **Padding.col_elem())
                class_name_l.grid(row=1, column=2, sticky="nsew", **Padding.col_elem())
                if self.edit_mode:
                    class_f.grid_columnconfigure(2, weight=10)
                    class_edit_b = tk.Button(class_f, text="Edit", **Style.def_btn(),
                                             command=lambda c=class_: self.__edit_class(c))
                    class_del_b = tk.Button(class_f, text="Delete", **Style.def_btn(bg=Colours.M_RED),
                                            command=lambda c=class_: self.__del_class__(c))
                    class_edit_b.grid(row=1, column=3, sticky="e", **Padding.col_elem())
                    class_del_b.grid(row=1, column=4, sticky="e", **Padding.btm_right())
                else:
                    class_link_b = tk.Button(class_f, text="Open", **Style.def_btn(),
                                             command=lambda: Utils.open_class_link(self._reg_subs[class_.reg_code]))
                    class_link_b.grid(row=1, column=3, sticky="e", **Padding.col_elem())
                i += 1
        return container_f

    def __add_class__(self, edit_class: Class = None):
        """
        Add a new class to the schedule or optionally edit and existing one.
        :param edit_class: optional, will edit class corresponding to this Class object if provided
        """

        def close_reg_win():
            GUtils.destroy_all(inp_w)
            GUtils.lift_win(self._root)

        def reg_class():
            c_name = class_name.get()
            c_day = class_day.get()
            c_sth = class_sth.get()
            c_stm = class_stm.get()
            c_eth = class_eth.get()
            c_etm = class_etm.get()
            try:
                if not c_name:
                    raise CommonError("Please select a class.")
                if not c_day:
                    raise CommonError("Please select a class_day.")
                if not c_sth or not c_stm:
                    raise CommonError("Please select a valid start time.")
                if not c_eth or not c_etm:
                    raise CommonError("Please select a valid end time.")
                sub_code, class_type = Subjects.sub_code_and_type(self.disp_subs[class_name.get()])
                day = class_day.get()
                start = class_sth.get() + class_stm.get()
                end = class_eth.get() + class_etm.get()
                if start == end:
                    raise CommonError("Start time cannot be the same as end time.")
                if int(end) < int(start):
                    raise CommonError("End time must be after start time.")
                self.schedule.add_class(Class(sub_code, class_type, day, start, end), old_class_=edit_class)
            except CommonError as e_:
                tk.Label(inp_f, text=e_.args[0], **Style.def_txt(fg=Colours.M_RED)) \
                    .grid(row=1, column=1, sticky="w", **Padding.pad((Padding.DEF_X, (Padding.DEF_Y, 0))))
            else:
                self._edit_day = self.schedule.day2int(day)
                GUtils.destroy_all(inp_w)
                self.__refresh_sch__()

        inp_w = tk.Toplevel(self._main_f)
        inp_w.protocol("WM_DELETE_WINDOW", close_reg_win)
        class_name = tk.StringVar(inp_w)
        class_day = tk.StringVar(inp_w)
        class_sth = tk.StringVar(inp_w)
        class_stm = tk.StringVar(inp_w)
        class_eth = tk.StringVar(inp_w)
        class_etm = tk.StringVar(inp_w)

        inp_f = tk.Frame(inp_w)
        class_l = tk.Label(inp_f, text="Select class:", **Style.def_txt())
        class_c = ttk.Combobox(inp_f, **Style.def_combo(list(self.disp_subs.keys()), class_name, width=55))
        if edit_class is not None:
            class_c.set(self.schedule.get_class_name(edit_class))
        time_f = tk.Frame(inp_f)
        day_l = tk.Label(time_f, text="Day:", **Style.def_txt())
        day_c = ttk.Combobox(time_f, **Style.def_combo(list(self.schedule.CLASS_DAYS.values()), class_day, width=10))
        if edit_class is not None:
            day_c.set(edit_class.class_day)
        st_l = tk.Label(time_f, text="Start time:", **Style.def_txt())
        sth_c = ttk.Combobox(time_f, **Style.def_combo(self.schedule.CLASS_HOURS, class_sth))
        stc_l = tk.Label(time_f, text=":", **Style.def_txt())
        stm_c = ttk.Combobox(time_f, **Style.def_combo(self.schedule.CLASS_MINS, class_stm))
        if edit_class is not None:
            sth, stm = Utils.time_str(edit_class.start_time).split(":")
            sth_c.set(sth)
            stm_c.set(stm)
        et_l = tk.Label(time_f, text="End time:", **Style.def_txt())
        eth_c = ttk.Combobox(time_f, **Style.def_combo(self.schedule.CLASS_HOURS, class_eth))
        etc_l = tk.Label(time_f, text=":", **Style.def_txt())
        etm_c = ttk.Combobox(time_f, **Style.def_combo(self.schedule.CLASS_MINS, class_etm))
        if edit_class is not None:
            eth, etm = Utils.time_str(edit_class.end_time).split(":")
            eth_c.set(eth)
            etm_c.set(etm)
        submit_b = tk.Button(inp_f, text="Submit", **Style.def_btn(), command=reg_class)

        inp_f.grid(sticky="nsew")
        class_l.grid(row=1, column=1, sticky="w", **Padding.default())
        class_c.grid(row=2, column=1, **Padding.col_elem())
        time_f.grid(row=3, column=1, sticky="nsew", **Padding.col_no_x())
        day_l.grid(row=1, column=1, sticky="w", **Padding.col_elem())
        day_c.grid(row=1, column=2, sticky="w", **Padding.col_no_x())
        st_l.grid(row=2, column=1, sticky="w", **Padding.col_elem())
        sth_c.grid(row=2, column=2, sticky="w", **Padding.col_no_x())
        stc_l.grid(row=2, column=3, sticky="w", **Padding.col_no_x())
        stm_c.grid(row=2, column=4, sticky="w", **Padding.col_no_x())
        et_l.grid(row=3, column=1, sticky="w", **Padding.col_elem())
        eth_c.grid(row=3, column=2, sticky="w", **Padding.col_no_x())
        etc_l.grid(row=3, column=3, sticky="w", **Padding.col_no_x())
        etm_c.grid(row=3, column=4, sticky="w", **Padding.col_no_x())
        submit_b.grid(row=4, column=1, **Padding.col_elem())

        GUtils.lift_win(inp_w)
        inp_w.geometry("+%d+%d" % GUtils.win_pos(self._root, 0.35, 0.35))

    def __del_class__(self, class_: Class):
        """
        Delete a class from the schedule.
        :param class_: the Class object to delete
        """

        self.schedule.delete_class(class_)
        self._edit_day = self.schedule.day2int(class_.class_day)
        self.__refresh_sch__()

    def __edit_class(self, edit_class: Class):
        """
        Edit a class from the schedule
        :param edit_class: the Class object to edit
        """

        self.__add_class__(edit_class)

    def __upd_sch__(self):
        """
        Attempt to update current schedule to database.

        Refreshes schedule if database is successfully updated.
        """

        loading_win = GUtils.loading_win(self._root, "Saving schedule")
        loading_win.update()
        try:
            schedule_changed = self.schedule.schedule_changed()
            if schedule_changed:
                self.schedule.update_schedule()
        except CommonError as e:
            if e.flag == "l_out":
                GUtils.disp_msg("You have been logged out.", "err", self._root)
                self.__close__(check_changed=False)
            else:
                loading_win.destroy()
                GUtils.disp_msg("Could not update schedule.\n" + e.args[0], "err", self._root)
        else:
            if schedule_changed:
                self._refresh_f(self)
            self.__close__(check_changed=False)

    def __close__(self, check_changed=True):
        """
        Optionally warn about changes made to schedule and close schedule editor window.
        :param check_changed: optional, will show a warning if schedule has been modified
        """

        if self.schedule.schedule_changed() and check_changed:
            if GUtils.disp_conf("Exit", "You have unsaved changes, exit?", self._root):
                GUtils.destroy_all(self._root)
        else:
            GUtils.destroy_all(self._root)

    def build_schedule(self, schedule_n: ttk.Notebook = None, focus_day: int = None) -> ttk.Notebook:
        """
        Discard old schedule display widget and return a new, updated schedule display widget.
        :param schedule_n: the old schedule display widget to discard
        :param focus_day: the day of the week to focus the schedule on
        :return: the new, updated schedule display widget
        """

        new_schedule_n = ttk.Notebook(schedule_n.master if schedule_n is not None else self._main_f)
        for day_str in self.schedule.day_strs:
            classes = self.schedule.dict_schedule[day_str]
            layout_f = self.__day_layout__(classes, day_str, new_schedule_n)
            new_schedule_n.add(child=layout_f, text=day_str)
        if schedule_n is not None:
            schedule_n.destroy()
        new_schedule_n.select(focus_day if focus_day is not None else self._edit_day)
        return new_schedule_n


class LoginWindow(tk.Toplevel):
    """Displays a window for the user to login, sign up, or change password."""

    def __init__(self, root: tk.Tk, smart_sch: SmartScheduler, action: str = "login"):
        """
        Initialises widgets and builds login, sign up, or change password window.
        :param root: the root tk.Tk instance
        :param smart_sch: an instance of SmartScheduler to serve as the backend for executing any action
        :param action: indicates whether the window is for login, sign up or change password
        """

        super().__init__(master=root)
        self.root = root
        self.action = action
        self.smart_sch = smart_sch
        self.loading_win = GUtils.loading_win(self)
        self.loading_win.withdraw()

        self.title(self.action.title())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.__close__)

        self.inp_s_id = tk.StringVar(self)
        self.inp_pswrd = tk.StringVar(self)
        if self.action == "change password":
            self.inp_n_pswrd = tk.StringVar(self)
        if self.action == "sign up" or action == "change password":
            self.inp_c_pswrd = tk.StringVar(self)
        self.login_f = tk.Frame(self)
        self.stu_id_l = tk.Label(self.login_f, text="Student ID:", **Style.def_txt())
        self.stu_id_e = tk.Entry(self.login_f, textvariable=self.inp_s_id, **Style.def_txt())
        self.pswrd_l = tk.Label(self.login_f, text="Password:", **Style.def_txt())
        self.pswrd_e = tk.Entry(self.login_f, textvariable=self.inp_pswrd, show="*", **Style.def_txt())
        if self.action == "change password":
            self.n_pswrd_l = tk.Label(self.login_f, text="New Password:", **Style.def_txt())
            self.n_pswrd_e = tk.Entry(self.login_f, textvariable=self.inp_n_pswrd, show="*", **Style.def_txt())
        if self.action == "sign up" or action == "change password":
            self.c_pswrd_l = tk.Label(self.login_f, text="Confirm:", **Style.def_txt())
            self.c_pswrd_e = tk.Entry(self.login_f, textvariable=self.inp_c_pswrd, show="*", **Style.def_txt())
        self.btn_f = tk.Frame(self.login_f)
        if self.action == "login":
            self.login_b = tk.Button(self.btn_f, text="Login", **Style.def_btn(width=15),
                                     command=lambda: self.__btn_cmd__("login"))
        else:
            self.cancel_b = tk.Button(self.btn_f, text="Cancel", **Style.def_btn(width=15, bg=Colours.M_RED),
                                      command=lambda: self.__change_win__("login"))
        self.signup_b = tk.Button(self.btn_f, text="Sign Up", **Style.def_btn(width=15),
                                  command=lambda: self.__btn_cmd__("sign up"))
        self.pswrd_b = tk.Button(self.btn_f, text="Change Password", **(
            Style.def_btn(width=15) if action == "change password" else Style.txt_btn(width=15)),
                                 command=lambda: self.__btn_cmd__("change password"))
        self.bind("<Return>", self.__btn_pressed__)

        self.login_f.grid(sticky="nsew")
        self.stu_id_l.grid(row=1, column=1, **Padding.no_right())
        self.stu_id_e.grid(row=1, column=2, **Padding.col_elem())
        self.pswrd_l.grid(row=2, column=1, **Padding.no_right(y=(0, 0)))
        self.pswrd_e.grid(row=2, column=2, **Padding.btm_elem())
        self.btn_f.grid(row=5, column=1, columnspan=2, **Padding.default())
        if self.action == "login":
            self.pswrd_b.grid(row=1, column=2, **Padding.col_elem(x=(0, 0)))
            self.login_b.grid(row=2, column=1, **Padding.btm_elem())
            self.signup_b.grid(row=2, column=2, **Padding.btm_elem())
        elif self.action == "sign up":
            self.c_pswrd_l.grid(row=3, column=1, **Padding.no_right())
            self.c_pswrd_e.grid(row=3, column=2, **Padding.btm_elem())
            self.signup_b.grid(row=1, column=1, **Padding.btm_elem())
            self.cancel_b.grid(row=1, column=2, **Padding.btm_elem())
        elif self.action == "change password":
            self.n_pswrd_l.grid(row=3, column=1, **Padding.no_right())
            self.n_pswrd_e.grid(row=3, column=2, **Padding.btm_elem())
            self.c_pswrd_l.grid(row=4, column=1, **Padding.no_right())
            self.c_pswrd_e.grid(row=4, column=2, **Padding.col_elem())
            self.pswrd_b.grid(row=1, column=1, **Padding.btm_elem())
            self.cancel_b.grid(row=1, column=2, **Padding.btm_elem())

        self.geometry("+%d+%d" % GUtils.win_pos(self, 0.4, 0.4))

    def __btn_pressed__(self, _):
        if self.action == "login":
            GUtils.btn_press_anim(self.login_b)
        elif self.action == "sign up":
            GUtils.btn_press_anim(self.signup_b)
        elif self.action == "change password":
            GUtils.btn_press_anim(self.pswrd_b)
        self.__btn_cmd__(self.action)

    def __change_win__(self, action: str):
        """
        Changes window widgets to accommodate a different action
        :param action: the new action to change to
        """

        GUtils.destroy_all(self)
        LoginWindow(self.root, self.smart_sch, action=action).mainloop()

    def __btn_cmd__(self, action: str):
        """
        Inserts a loading screen and executes a certain action depending on self.action.
        :param action: signals to change window if not identical to self.action
        """

        if action == self.action:
            if self.action == "login":
                GUtils.disp_loading(self.loading_win, self.__login__)
            elif self.action == "sign up":
                GUtils.disp_loading(self.loading_win, self.__sign_up__)
            elif self.action == "change password":
                GUtils.disp_loading(self.loading_win, self.__change_password__)
        else:
            self.__change_win__(action)

    def __change_password__(self):
        """Attempts to change password and displays any errors encountered."""

        try:
            self.smart_sch.change_pswrd(self.inp_s_id.get(), self.inp_pswrd.get(), self.inp_n_pswrd.get(),
                                        self.inp_c_pswrd.get())
        except CommonError as e:
            self.loading_win.withdraw()
            GUtils.disp_msg(e.args[0], "err", self)
        else:
            self.loading_win.withdraw()
            GUtils.disp_msg("Password changed successfully.", "info", self)
            GUtils.destroy_all(self)
            LoginWindow(self.root, self.smart_sch).mainloop()

    def __login__(self):
        """Attempts to login and displays any errors encountered."""

        try:
            self.smart_sch.login(self.inp_s_id.get(), self.inp_pswrd.get())
        except CommonError as e:
            self.loading_win.withdraw()
            if e.flag == "l_in":
                if GUtils.disp_conf("Warning", f"{e.message} Logout now?", self):
                    try:
                        self.smart_sch.logout(remote_student_id=self.inp_s_id.get())
                    except CommonError as e:
                        GUtils.disp_msg(e.args[0], "err", self)
                    else:
                        GUtils.disp_msg("Remote logout successful, you can now login.", "info", self)
            else:
                GUtils.disp_msg(e.args[0], "err", self)
        else:
            GUtils.destroy_all(self)
            temp_loading = GUtils.loading_win(self.root, "Initialising")
            GUtils.disp_loading(temp_loading, lambda: MainWindow(self.root, self.smart_sch, temp_loading).mainloop())

    def __sign_up__(self):
        """Attempts to sign up and displays any errors encountered."""

        try:
            self.smart_sch.sign_up(self.inp_s_id.get(), self.inp_pswrd.get(), self.inp_c_pswrd.get())
        except CommonError as e:
            self.loading_win.withdraw()
            GUtils.disp_msg(e.args[0], "err", self)
        else:
            self.loading_win.withdraw()
            GUtils.disp_msg("Profile created successfully, you can now login.", "info", self)
            GUtils.destroy_all(self)
            LoginWindow(self.root, self.smart_sch).mainloop()

    def __close__(self):
        GUtils.destroy_all(self.root)


class MainWindow(tk.Toplevel):
    """Displays the main window through which the user can avail most of Smart Scheduler's functionality."""

    def __init__(self, root: tk.Tk, smart_sch: SmartScheduler, temp_loading: tk.Toplevel):
        """
        Initialises widgets and builds the main window.
        :param root: the root tk.Tk instance
        :param smart_sch: An instance of SmartScheduler to serve as the backend for various functionality.
        :param temp_loading: A temporary loading window that is destroyed as soon as this window is ready
        """

        super().__init__(master=root)
        self.root = root
        self.smart_sch = smart_sch
        self.refresh = self.__refresh__
        self.c_name = tk.StringVar(self, "")
        self.c_duration = tk.StringVar(self, "")
        self.n_name = tk.StringVar(self, "")
        self.n_duration = tk.StringVar(self, "")
        self.stu_id = tk.StringVar(self, self.smart_sch.student_id)
        self.class_info_vars = {"c_name": self.c_name, "c_duration": self.c_duration,
                                "n_name": self.n_name, "n_duration": self.n_duration}
        self.loading_win = GUtils.loading_win(self)
        self.loading_win.withdraw()

        self.title("Smart Scheduler")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: self.__disp_loading__(self.__close__))
        self.main_f = tk.Frame(self)
        self.title_l = tk.Label(self.main_f, text="Welcome to Smart Scheduler",
                                **Style.def_txt(Font.TITLE, Colours.M_BLUE))

        # left side widgets
        l_btn_sz = 32
        self.left_f = tk.Frame(self.main_f)
        self.actn_f = tk.Frame(self.left_f)
        self.c_f = tk.LabelFrame(self.left_f, relief=tk.GROOVE, labelanchor='n', bd=1, labelwidget=tk.Label(
            self.left_f, text="Current Class", **Style.def_txt(Font.HEADING, Colours.M_BLUE)))
        self.c_f.after(900_000, self.__refresh__)
        self.n_f = tk.LabelFrame(self.left_f, relief=tk.GROOVE, labelanchor='n', bd=1, labelwidget=tk.Label(
            self.left_f, text="Next Class", **Style.def_txt(Font.HEADING, Colours.M_BLUE)))
        self.scan_attd_b = tk.Button(self.actn_f, text="Scan Attendance", **Style.def_btn(l_btn_sz),
                                     command=self.__scan_attd__)
        self.start_class_b = tk.Button(self.actn_f, text="Start Class", **Style.def_btn(l_btn_sz),
                                       command=lambda: self.__disp_loading__(self.__open_c_class__))
        self.edit_subs_b = tk.Button(self.actn_f, text="Edit Subjects", **Style.def_btn(l_btn_sz),
                                     command=lambda: self.__disp_loading__(self.__edit_subs__))
        self.del_acct_b = tk.Button(self.actn_f, text="Delete Account", **Style.def_btn(l_btn_sz, Colours.M_RED),
                                    command=lambda: self.__disp_loading__(self.__del_acct__))
        self.c_name_l = tk.Label(self.c_f, textvariable=self.c_name, width=30, wraplength=300, **Style.def_txt())
        self.c_duration_l = tk.Label(self.c_f, textvariable=self.c_duration, width=30, **Style.def_txt())
        self.n_name_l = tk.Label(self.n_f, textvariable=self.n_name, width=30, wraplength=300, **Style.def_txt())
        self.n_duration_l = tk.Label(self.n_f, textvariable=self.n_duration, width=30, **Style.def_txt())
        self.refresh_b = tk.Button(self.left_f, text="Refresh", **Style.def_btn(l_btn_sz),
                                   command=lambda: self.__disp_loading__(self.__refresh__))

        # right side widgets
        self.right_f = tk.Frame(self.main_f)
        self.sch_info_f = tk.Frame(self.right_f)
        self.logout_f = tk.LabelFrame(self.right_f, relief=tk.GROOVE, bd=2, labelwidget=tk.Label(
            self.right_f, text="Currently Logged In:", **Style.def_txt()))
        self.sch_for_l = tk.Label(self.sch_info_f, text="Schedule for", **Style.def_txt(justify="right"))
        self.sch_edit_b = tk.Button(self.sch_info_f, text="Edit", **Style.def_btn(),
                                    command=lambda: self.__disp_loading__(self.__edit_sch__))
        self.sch_clear_b = tk.Button(self.sch_info_f, text="Clear", **Style.def_btn(bg=Colours.M_RED),
                                     command=self.__clear_sch_conf__)
        self.schedule_n = ttk.Notebook(self.right_f)
        self.stu_id_tl = tk.Label(self.sch_info_f, textvariable=self.stu_id, **Style.def_txt())
        self.stu_id_bl = tk.Label(self.logout_f, textvariable=self.stu_id, **Style.def_txt(font=Font.HEADING,
                                                                                           fg=Colours.M_BLUE))
        self.logout_b = tk.Button(self.logout_f, text="Logout", **Style.def_btn(),
                                  command=lambda: self.__disp_loading__(self.__logout__))
        self.exit_b = tk.Button(self.logout_f, text="Exit", **Style.def_btn(bg=Colours.M_RED),
                                command=lambda: self.__disp_loading__(self.__close__))

        self.__build__()
        self.__refresh__()
        temp_loading.destroy()

        self.geometry("+%d+%d" % GUtils.win_pos(self, 0.3, 0.2))

    def __build__(self):
        self.main_f.grid(sticky="nsew")
        self.title_l.grid(row=1, column=1, columnspan=2, sticky="nsew", **Padding.pad((Padding.DEF_X, Padding.DEF_Y)))

        # build left column
        self.left_f.grid(row=2, column=1, sticky="nsew", **Padding.default())
        self.actn_f.grid(row=1, column=1, sticky="nsew", **Padding.pad((0, (0, Padding.DEF_Y))))
        self.scan_attd_b.grid(row=1, column=1, **Padding.col_elem())
        self.start_class_b.grid(row=2, column=1, **Padding.col_elem())
        self.edit_subs_b.grid(row=3, column=1, **Padding.col_elem())
        self.del_acct_b.grid(row=4, column=1, **Padding.col_elem())
        self.c_f.grid(row=2, column=1, sticky="nsew", **Padding.default())
        self.c_name_l.grid(row=1, column=1, **Padding.default())
        self.c_duration_l.grid(row=2, column=1, **Padding.col_elem(), sticky="w")
        self.n_f.grid(row=3, column=1, sticky="nsew", **Padding.default())
        self.n_name_l.grid(row=3, column=1, **Padding.default())
        self.n_duration_l.grid(row=4, column=1, **Padding.col_elem(), sticky="w")
        self.refresh_b.grid(row=4, column=1, **Padding.default())

        # build right column
        self.right_f.grid(row=2, column=2, sticky="nsew", **Padding.default())
        self.sch_info_f.grid(row=1, column=1, sticky="nsew", **Padding.btm_elem())
        self.sch_for_l.grid(row=1, column=1, **Padding.none())
        self.stu_id_tl.grid(row=1, column=2, **Padding.none())
        self.sch_info_f.grid_columnconfigure(3, weight=2)
        self.sch_edit_b.grid(row=1, column=4, **Padding.none())
        self.sch_clear_b.grid(row=1, column=5, **Padding.no_right(y=(0, 0)))
        self.right_f.grid_rowconfigure(3, weight=2)
        self.logout_f.grid(row=4, column=1, sticky="nsew", **Padding.no_left())
        self.stu_id_bl.grid(row=1, column=1, **Padding.no_right(y=(0, Padding.DEF_Y)))
        self.logout_f.grid_columnconfigure(2, weight=2)
        self.logout_b.grid(row=1, column=3, **Padding.default(y=(0, Padding.DEF_Y)))
        self.exit_b.grid(row=1, column=4, **Padding.no_left(y=(0, Padding.DEF_Y)))

    def __disp_loading__(self, gui_cmd, *args, **kwargs):
        """
        Inserts a loading screen before any gui commands are executed.
        :param gui_cmd: the command to execute
        :param args: arguments for the command
        :param kwargs: keyword arguments for the command
        """
        GUtils.disp_loading(self.loading_win, gui_cmd, *args, **kwargs)

    def __rem_loading__(self):
        """Removes the loading screen after a gui command has finished execution."""

        if self.loading_win.winfo_viewable():
            self.loading_win.withdraw()

    def __scan_attd__(self):
        """Displays a window through which user can attempt to scan a QR code. Any errors encountered are displayed."""

        def scan_qr():
            scan_l.configure(text="Scanning...")
            try:
                Utils.launch_browser(url=Utils.scan_qr())
            except CommonError as e:
                scan_l.configure(text=e.args[0], **Style.def_txt(fg=Colours.M_RED))
            else:
                scan_win.destroy()

        scan_win = tk.Toplevel(self.main_f)
        scan_win.title("Scan QR")
        scan_l = tk.Label(scan_win, text="Bring QR code to foreground,\nthen click Scan.", width=30, wraplength=300,
                          **Style.def_txt())
        scan_b = tk.Button(scan_win, text="Scan", command=scan_qr, **Style.def_btn())
        scan_l.grid(row=1, column=1, **Padding.default())
        scan_b.grid(row=2, column=1, **Padding.col_elem())
        GUtils.lift_win(scan_win, pin=True)
        scan_win.mainloop()

    def __open_c_class__(self):
        """Attempts to open the current class link in a browser and displays any errors encountered."""

        try:
            if self.smart_sch.curr_class_link is not None:
                Utils.open_class_link(self.smart_sch.curr_class_link)
            else:
                GUtils.disp_msg("No class right now.", "info", self)
            self.__rem_loading__()
        except CommonError as e:
            self.__rem_loading__()
            GUtils.disp_msg("Could not open class link.\n" + e.args[0], "err", self)

    def __edit_subs__(self):
        """Attempts to open a new window to edit registered subjects and displays any errors encountered."""

        try:
            SubjectEditor(self)
            self.__rem_loading__()
        except CommonError as e:
            if e.flag == "l_out":
                GUtils.disp_msg("You have been logged out.", "err", self)
                self.__logout__()
            else:
                self.__rem_loading__()
                GUtils.disp_msg("Could not retrieve registered subjects info.\n" + e.args[0], "err", self)

    def __del_acct__(self):
        """Attempts to delete currently logged in account and displays any errors encountered."""

        if GUtils.disp_conf("Delete Account", "Are you sure you want to delete your account and all of its data?\n"
                                              "This action is irreversible.", self):
            try:
                self.smart_sch.delete_acc()
                self.__rem_loading__()
            except CommonError as e:
                if e.flag == "l_out":
                    GUtils.disp_msg("You have been logged out.", "err", self)
                    self.__logout__()
                else:
                    self.__rem_loading__()
                    GUtils.disp_msg("Could not delete account.\n" + e.args[0], "err", self)
            else:
                self.stu_id.set("")
                GUtils.destroy_all(self)
                LoginWindow(self.root, self.smart_sch).mainloop()

    def __refresh_class_info__(self, schedule: Schedule):
        """Attempts to refresh class and schedule information and displays any errors encountered."""

        try:
            curr_class, next_class = schedule.get_class_info()
            schedule.update_curr_class_link(curr_class)
            self.c_name.set(
                schedule.get_class_name(curr_class) if curr_class is not None else "Waiting for next class.")
            self.c_duration.set(schedule.class_duration(curr_class) if curr_class is not None else "")
            self.n_name.set(schedule.get_class_name(next_class) if next_class is not None else "No upcoming class.")
            self.n_duration.set(schedule.class_duration(next_class) if next_class is not None else "")
        except CommonError:
            raise

    def __refresh__(self, sch_editor: ScheduleEditor = None):
        """
        Attempts to refresh schedule information and displays any errors encountered.
        :parameter sch_editor: optional, will be used instead of a new instance of ScheduleEditor if provided
        """

        try:
            editor = sch_editor or ScheduleEditor(self, edit_mode=False)
            editor.edit_mode = False
            new_schedule_n = editor.build_schedule(self.schedule_n, focus_day=Utils.curr_day())
            self.__refresh_class_info__(editor.schedule)
            self.__rem_loading__()
        except CommonError as e:
            if e.flag == "l_out":
                GUtils.disp_msg("You have been logged out.", "err", self)
                self.__logout__()
            else:
                self.__rem_loading__()
                GUtils.disp_msg("Could not refresh schedule and class information.\n" + e.args[0], "err", self)
        else:
            self.schedule_n.destroy()
            self.schedule_n = new_schedule_n
            self.schedule_n.grid(row=2, column=1, **Padding.default())
            self.__rem_loading__()

    def __edit_sch__(self):
        """Attempts to open a new window to edit schedule and displays any errors encountered."""

        try:
            ScheduleEditor(self, edit_mode=True)
            self.__rem_loading__()
        except CommonError as e:
            if e.flag == "l_out":
                GUtils.disp_msg("You have been logged out.", "err", self)
                self.__logout__()
            elif e.flag == "no_subs":
                self.__rem_loading__()
                GUtils.disp_msg("You must register a subject before you can edit the schedule.", "info", self)
            else:
                self.__rem_loading__()
                GUtils.disp_msg("Could not retrieve schedule info.\n" + e.args[0], "err", self)

    def __clear_sch_conf__(self):
        """This function is required for displaying the loading window while the schedule is being cleared."""
        if GUtils.disp_conf("Clear Schedule", "Are you sure you want to clear your schedule and remove all classes?\n"
                                              "This action is irreversible.", self):
            self.__disp_loading__(self.__clear_sch__)

    def __clear_sch__(self):
        """Attempts to clear the current schedule and displays any errors encountered."""
        try:
            Schedule.clear_schedule(self.smart_sch)
            self.__refresh__()
        except CommonError as e:
            if e.flag == "l_out":
                GUtils.disp_msg("You have been logged out.", "err", self)
                self.__logout__()
            else:
                self.__rem_loading__()
                GUtils.disp_msg("Could not clear schedule.\n" + e.args[0], "err", self)

    def __logout__(self, exit_prog=False):
        """
        Attempts to logout.

        Either The main window is destroyed and the login window is displayed, or the application exits completely.
        :param exit_prog: optional, the application will exit instead of displaying the login window if true.
        """

        try:
            self.smart_sch.logout()
        except CommonError as e:
            self.__rem_loading__()
            if exit_prog:
                if GUtils.disp_conf("Logout Error", f"Unable to logout properly.\n{e.args[0]}\nExit anyway?", self):
                    GUtils.destroy_all(self.root)
            else:
                GUtils.disp_msg("Unable to logout properly.\n" + e.args[0], "err", self)
        else:
            self.stu_id.set("")
            if exit_prog:
                GUtils.destroy_all(self.root)
            else:
                GUtils.destroy_all(self)
                LoginWindow(self.root, self.smart_sch).mainloop()

    def __close__(self):
        """Calls self.__logout__ with the intention of exiting the application."""

        self.__logout__(exit_prog=True)


def main():
    """
    The entry point of the Smart Scheduler Application.

    Any fatal error encountered while initialising the SmartScheduler backend will cause the program to terminate after
    displaying the error in a pop up dialog box.
    """

    root = tk.Tk()
    root.withdraw()
    loading_win = GUtils.loading_win(root, "Starting")
    loading_win.update()
    try:
        smart_sch = SmartScheduler()
        LoginWindow(root, smart_sch)
        loading_win.destroy()
    except FatalError as e:
        loading_win.destroy()
        GUtils.disp_msg(e.args[0], "err", root)
        GUtils.destroy_all(root)
        raise SystemExit
    else:
        root.mainloop()


if __name__ == "__main__":
    main()
