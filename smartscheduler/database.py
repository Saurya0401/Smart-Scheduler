import requests
from threading import Thread
from smartscheduler.exceptions import CommonDatabaseError

__all__ = ["SmartSchedulerDB"]


class SmartSchedulerDB:
    """Manages the database for the Smart Scheduler application."""

    TAB_ACCOUNTS = "Accounts"
    COL_STU_ID = "Student_ID"
    COL_PSWRD_HASH = "Pswrd_hash"
    COL_SCHEDULE = "Schedule"
    COL_SUBJECTS = "Reg_subjects"
    COL_SESSION_ID = "Session_ID"
    TAB_SUB_INFO = "Subjects"
    COL_SUB_CODE = "Subject_code"
    COL_SUB_NAME = "Subject_name"

    def __init__(self, server: str = None):
        """
        Initialise database manager
        :param server: address of the server that contains the database
        """

        self.server: str = server
        self.db_ret: list = []
        self.db_err: bool = False
        self.db_wait: bool = False
        self.__create_tables__()

    def __create_tables__(self):
        """Create the required tables in the database, if they do not already exist."""

        self.__send_cmd__(f'''
        CREATE TABLE IF NOT EXISTS {self.TAB_ACCOUNTS} 
        ({self.COL_STU_ID} text NOT NULL PRIMARY KEY,
        {self.COL_PSWRD_HASH} text,
        {self.COL_SCHEDULE} text,
        {self.COL_SUBJECTS} text,
        {self.COL_SESSION_ID} text)
        ''')
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)
        self.__send_cmd__(f'''
        CREATE TABLE IF NOT EXISTS {self.TAB_SUB_INFO}
        ({self.COL_SUB_CODE} text NOT NULL PRIMARY KEY,
        {self.COL_SUB_NAME} text)
        ''')
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)

    def __db_cmd__(self, cmd: str, params: list or None, upd_subs: bool):
        """
        Send a SQL command to the database, encapsulated in a HTTP POST request made to self.server.

        The SQL command and any additional command parameters are sent in JSON format.
        :param cmd: A SQL command
        :param params: Any additional parameters for the SQL command
        :param upd_subs: A special flag that signals the server to update the list of available subjects
        """

        try:
            if upd_subs:
                request_json = {"cmd": cmd, "cmd_params": ["upd_subs"]}
            else:
                request_json = {"cmd": cmd, "cmd_params": params}
            server_resp: requests.Response = requests.post(self.server, json=request_json)
            server_resp.raise_for_status()
            db_resp = server_resp.json()
            self.db_ret = db_resp["db_ret"]
            self.db_err = db_resp["db_err"]
        except requests.ConnectionError:
            self.db_err = True
            self.db_ret = "Cannot reach database (server connection failed)."
        except requests.HTTPError as e:
            self.db_err = True
            self.db_ret = e.args[0]
        finally:
            self.db_wait = False

    def __send_cmd__(self, cmd: str, params: list = None, upd_subs: bool = False):
        """
        Initialise a new thread to send a SQL command to the database.
        :param cmd: the SQL command
        :param params: optional parameters for the SQL command
        """

        self.db_err = False
        self.db_wait = True
        Thread(target=self.__db_cmd__, args=(cmd, params, upd_subs)).start()

    def retrieve_all(self, table: str) -> list:
        """
        Retrieve all data from a specific table.
        :param table: the table to retrieve data from
        :return: a list containing tuples, one for each record in the table
        """

        self.__send_cmd__(f"SELECT * FROM {table}")
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)
        return self.db_ret

    def new_account(self, s_id: str, pass_hash: str, sch: str, subs: str):
        """
        Add a new account to accounts table in the database.
        :param s_id: the student ID of the account holder
        :param pass_hash: the account's password hash
        :param sch: the account's schedule
        :param subs: the account's registered subjects
        """

        self.__send_cmd__(f"INSERT INTO {self.TAB_ACCOUNTS} VALUES (?, ?, ?, ?, ?)", [s_id, pass_hash, sch, subs, "0"])
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)

    def query_account_info(self, s_id: str, query_col) -> tuple:
        """
        Retrieve a specific account information field in the accounts table via a SQL query.
        :param s_id: the look up key for the SQL query
        :param query_col: the account information column to query
        :return: a tuple containing the field's information
        """

        self.__send_cmd__(f"SELECT {query_col} FROM {self.TAB_ACCOUNTS} WHERE {self.COL_STU_ID}=?", [s_id])
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)
        return self.db_ret[0] if self.db_ret else []

    def update_account_info(self, s_id: str, update_col: str, update_val: str):
        """
        Update a specific account information field in the accounts table via a SQL command.
        :param s_id: the look up key for the SQL command
        :param update_col: the account information column to update
        :param update_val: the updated value
        """

        self.__send_cmd__(f"UPDATE {self.TAB_ACCOUNTS} SET {update_col}=? WHERE {self.COL_STU_ID}=?",
                          [update_val, s_id])
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)

    def delete_account(self, s_id: str):
        """
        Remove an account from the accounts table in the database via an SQL command
        :param s_id: the look up key for the SQL command
        """

        self.__send_cmd__(f"DELETE FROM {self.TAB_ACCOUNTS} WHERE {self.COL_STU_ID}=?", [s_id])
        while self.db_wait:
            continue
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)

    def upd_sub_list(self):
        """Request the server to update the current list of available subjects."""
        self.__send_cmd__(f"INSERT OR REPLACE INTO {self.TAB_SUB_INFO} ({self.COL_SUB_CODE}, {self.COL_SUB_NAME}) "
                          f"VALUES (?, ?)", upd_subs=True)
        while self.db_wait:
            pass
        if self.db_err:
            raise CommonDatabaseError(self.db_ret)


if __name__ == "__main__":
    # for quick testing

    pass
