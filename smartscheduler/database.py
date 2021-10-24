import sqlite3 as sql
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

    def __init__(self, db_path: str):
        """
        Initialise database manager
        :param db_path: path to database
        """

        self.db_path: str = db_path
        self.db_ret: list = []
        self.db_wait: bool = False
        self.__create_tables__()

    def __create_tables__(self):
        """Create the required tables in the database, if they do not already exist"""

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
        self.__send_cmd__(f'''
        CREATE TABLE IF NOT EXISTS {self.TAB_SUB_INFO}
        ({self.COL_SUB_CODE} text NOT NULL PRIMARY KEY,
        {self.COL_SUB_NAME} text)
        ''')
        while self.db_wait:
            continue

    def __db_cmd__(self, cmd: str, params: dict = None):
        """
        Send a SQL command to the database. If the command is a query, store the result in self.db_ret
        :param cmd: the SQL command
        :param params: optional parameters for the SQL command
        """

        conn = None
        try:
            conn = sql.Connection(self.db_path)
            curs = conn.cursor()
            curs.execute(cmd, params) if params is not None else curs.execute(cmd)
        except (sql.IntegrityError, sql.OperationalError, sql.ProgrammingError) as e:
            raise CommonDatabaseError(e.args[0])
        else:
            conn.commit()
            self.db_ret = curs.fetchall()
        finally:
            if conn:
                conn.close()
            self.db_wait = False

    def __send_cmd__(self, cmd: str, params: dict = None):
        """
        Initialise a new thread to send a SQL command to the database
        :param cmd: the SQL command
        :param params: optional parameters for the SQL command
        """

        self.db_wait = True
        Thread(target=self.__db_cmd__, args=(cmd, params)).start()

    def retrieve_all(self, table: str) -> list:
        """
        Retrieve all data from a specific table
        :param table: the table to retrieve data from
        :return: a list containing tuples, one for each record in the table
        """

        self.__send_cmd__(f"SELECT * FROM {table}")
        while self.db_wait:
            continue
        return self.db_ret

    def new_account(self, s_id: str, pass_hash: str, sch: str, subs: str):
        """
        Add a new account to accounts table in the database
        :param s_id: the student ID of the account holder
        :param pass_hash: the account's password hash
        :param sch: the account's schedule
        :param subs: the account's registered subjects
        """

        self.__send_cmd__(f"INSERT INTO {self.TAB_ACCOUNTS} VALUES (:s_id, :pass_hash, :sch, :subs, :session)",
                          {"s_id": s_id, "pass_hash": pass_hash, "sch": sch, "subs": subs, "session": "0"})
        while self.db_wait:
            continue

    def query_account_info(self, s_id: str, query_col) -> tuple:
        """
        Retrieve a specific account information field in the accounts table via a SQL query
        :param s_id: the look up key for the SQL query
        :param query_col: the account information column to query
        :return: a tuple containing the field's information
        """

        self.__send_cmd__(f"SELECT {query_col} FROM {self.TAB_ACCOUNTS} WHERE {self.COL_STU_ID}=:s_id",
                          {"s_id": s_id})
        while self.db_wait:
            continue
        return self.db_ret[0] if self.db_ret else ()

    def update_account_info(self, s_id: str, update_col: str, update_val: str):
        """
        Update a specific account information field in the accounts table via a SQL command
        :param s_id: the look up key for the SQL command
        :param update_col: the account information column to update
        :param update_val: the updated value
        """

        self.__send_cmd__(f"UPDATE {self.TAB_ACCOUNTS} SET {update_col}=:val WHERE {self.COL_STU_ID}=:s_id",
                          {"s_id": s_id, "val": update_val})
        while self.db_wait:
            continue

    def delete_account(self, s_id: str):
        """
        Remove an account from the accounts table in the database via an SQL command
        :param s_id: the look up key for the SQL command
        """

        self.__send_cmd__(f"DELETE FROM {self.TAB_ACCOUNTS} WHERE {self.COL_STU_ID}=:s_id", {"s_id": s_id})
        while self.db_wait:
            continue

    def make_subs_list(self, subs_info: list):
        """
        Create or update the subjects table with the latest available subjects information
        :param subs_info: a list containing tuples like (subject_code, subject_name)
        """

        conn = None
        try:
            conn = sql.Connection(self.db_path)
            conn.executemany(
                f"INSERT INTO {self.TAB_SUB_INFO} ({self.COL_SUB_CODE}, {self.COL_SUB_NAME}) VALUES (?, ?)",
                subs_info)
            conn.commit()
        except sql.IntegrityError:
            return
        except (sql.OperationalError, sql.ProgrammingError) as e:
            raise CommonDatabaseError(e.args[0])
        finally:
            if conn:
                conn.close()


if __name__ == "__main__":
    # for quick testing

    pass
