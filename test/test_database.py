import unittest
import sqlite3
from os import remove
from random import randint

from smartscheduler.database import SmartSchedulerDB
from smartscheduler.exceptions import CommonDatabaseError


class DatabaseTest(unittest.TestCase):
    """TEST A.1"""

    db_path = "./test/test_server/Test.db"

    @classmethod
    def setUpClass(cls):
        SmartSchedulerDB(cls.db_path)

    def test_a11_create_tables(self):
        """TEST_CASE_ID A.1.1"""
        db = SmartSchedulerDB(self.db_path)
        conn = sqlite3.connect(self.db_path)
        curs = conn.cursor()
        tables = [res[0] for res in curs.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()]
        account_cols = [db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS, db.COL_SESSION_ID]
        retrieved_accounts_cols = [res[0] for res in
                                   curs.execute(f"SELECT name FROM pragma_table_info('{db.TAB_ACCOUNTS}')").fetchall()]
        sub_info_cols = [db.COL_SUB_CODE, db.COL_SUB_NAME]
        retrieved_sub_info_cols = [res[0] for res in
                                   curs.execute(f"SELECT name FROM pragma_table_info('{db.TAB_SUB_INFO}')").fetchall()]
        conn.close()
        self.assertIn(db.TAB_ACCOUNTS, tables)
        self.assertIn(db.TAB_SUB_INFO, tables)
        self.assertEqual(retrieved_accounts_cols, account_cols)
        self.assertEqual(retrieved_sub_info_cols, sub_info_cols)

    def test_a12_add_one_data(self):
        """TEST_CASE_ID A.1.2"""
        db = SmartSchedulerDB(self.db_path)
        test_data = [str(randint(10 ** 9, 10 ** 10 - 1)), "test_pass_hash", "test_sch", "test_subs"]
        db.new_account(*test_data)
        retrieved_data = [db.query_account_info(test_data[0], query)[0] for query in
                          (db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(retrieved_data, test_data)
        duplicate_data_cmd = f"INSERT INTO {db.TAB_ACCOUNTS} VALUES ({', '.join(test_data)}, 0)"
        self.assertRaises(CommonDatabaseError, db.__db_cmd__, duplicate_data_cmd)
        return test_data

    def test_a13_upd_one_data(self):
        """TEST_CASE_ID A.1.3"""
        db = SmartSchedulerDB(self.db_path)
        test_data_id = self.test_a12_add_one_data()[0]
        updated = {
            db.COL_PSWRD_HASH: "updated_pass_hash",
            db.COL_SCHEDULE: "updated_sch",
            db.COL_SUBJECTS: "updated_subs",
        }
        for k, v in updated.items():
            db.update_account_info(test_data_id, k, v)
        retrieved_data = [db.query_account_info(test_data_id, query)[0] for query in
                          (db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(retrieved_data, list(updated.values()))
        invalid_column = "Non_existent_column"
        update_data_cmd = f"UPDATE {db.TAB_ACCOUNTS} SET {invalid_column}='value' WHERE {db.COL_STU_ID}={test_data_id}"
        self.assertRaises(CommonDatabaseError, db.__db_cmd__, update_data_cmd)

    def test_a14_del_one_data(self):
        """TEST_CASE_ID A.1.4"""
        db = SmartSchedulerDB(self.db_path)
        test_data = self.test_a12_add_one_data()
        db.delete_account(test_data[0])
        retrieved_data = [db.query_account_info(test_data[0], query) for query in
                          (db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(all([i == () for i in retrieved_data]), True)

    def test_a15_add_batch_data(self):
        """TEST_CASE_ID A.1.5"""
        db = SmartSchedulerDB(self.db_path)
        test_list = [(f"TestKey{i}", f"Test Name {i}") for i in range(200)]
        db.make_subs_list(test_list)
        retrieved_data = db.retrieve_all(db.TAB_SUB_INFO)
        self.assertEqual(retrieved_data, test_list)

    @classmethod
    def tearDownClass(cls):
        remove(cls.db_path)


if __name__ == '__main__':
    unittest.main()
