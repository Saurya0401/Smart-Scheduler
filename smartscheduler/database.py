import sqlite3 as sql
from threading import Thread
from smartscheduler.exceptions import CommonDatabaseError


__all__ = ["SmartSchedulerDB"]


class SmartSchedulerDB:

    TAB_SCHEDULES = "schedules"
    COL_STU_ID = "stu_ID"
    COL_PAS_HASH = "pass_hash"
    COL_SESSION_ID = "session_id"
    COL_SCHEDULE = "db_schedule"
    COL_SUBJECTS = "subjects"
    TAB_SUB_INFO = "sub_info"
    COL_SUB_CODE = "sub_code"
    COL_SUB_NAME = "sub_name"

    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.db_ret: list = []
        self.db_wait: bool = False
        self.__create_table__()

    def __create_table__(self):
        self.__send_cmd__(f'''
        CREATE TABLE IF NOT EXISTS {self.TAB_SCHEDULES} 
        ({self.COL_STU_ID} text NOT NULL PRIMARY KEY,
        {self.COL_PAS_HASH} text,
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
        self.db_wait = True
        Thread(target=self.__db_cmd__, args=(cmd, params)).start()

    def fetch_all(self, query_col: str, table: str) -> list:
        self.__send_cmd__(f"SELECT {query_col} FROM {table}")
        while self.db_wait:
            continue
        return self.db_ret

    def fetch_all_data(self, table: str) -> list:
        self.__send_cmd__(f"SELECT * FROM {table}")
        while self.db_wait:
            continue
        return self.db_ret

    def new_record(self, s_id: str, pass_hash: str, sch: str, subs: str):
        self.__send_cmd__(f"INSERT INTO {self.TAB_SCHEDULES} VALUES (:s_id, :pass_hash, :sch, :subs, :session)",
                          {"s_id": s_id, "pass_hash": pass_hash, "sch": sch, "subs": subs, "session": "0"})
        while self.db_wait:
            continue

    def fetch_record(self, s_id: str, query_col) -> tuple:
        self.__send_cmd__(f"SELECT {query_col} FROM {self.TAB_SCHEDULES} WHERE {self.COL_STU_ID}=:s_id",
                          {"s_id": s_id})
        while self.db_wait:
            continue
        return self.db_ret[0] if self.db_ret else ()

    def update_record(self, s_id: str, update_col: str, update_val: str):
        self.__send_cmd__(f"UPDATE {self.TAB_SCHEDULES} SET {update_col}=:val WHERE {self.COL_STU_ID}=:s_id",
                          {"s_id": s_id, "val": update_val})
        while self.db_wait:
            continue

    def delete_record(self, s_id: str):
        self.__send_cmd__(f"DELETE FROM {self.TAB_SCHEDULES} WHERE {self.COL_STU_ID}=:s_id", {"s_id": s_id})
        while self.db_wait:
            continue

    def new_sub(self, s_code: str, s_name: str):
        self.__send_cmd__(f"INSERT INTO {self.TAB_SUB_INFO} VALUES (:s_code, :s_name)",
                          {"s_code": s_code, "s_name": s_name})
        while self.db_wait:
            continue

    def fetch_sub_name(self, s_code: str) -> tuple:
        self.__send_cmd__(f"SELECT {self.COL_SUB_NAME} FROM {self.TAB_SUB_INFO} WHERE {self.COL_SUB_CODE}=:s_code",
                          {"s_code": s_code})
        while self.db_wait:
            continue
        return self.db_ret[0] if self.db_ret else ()

    def make_subs_list(self, subs_info):
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
    pass
