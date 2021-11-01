import unittest
from os import remove
from random import randint

from smartscheduler.database import SmartSchedulerDB
from smartscheduler.exceptions import CommonDatabaseError


class SmartSchedulerDBTest(unittest.TestCase):
    """TEST A.1"""

    test_db = "./test/test_server/Test.db"
    test_server = "http://127.0.0.1:8765/"

    @classmethod
    def setUpClass(cls):
        SmartSchedulerDB(cls.test_server)

    def test_a11_create_tables(self):
        """TEST_CASE_ID A.1.1"""
        db = SmartSchedulerDB(self.test_server)
        db.__db_cmd__("SELECT name FROM sqlite_master WHERE type = 'table'", None, False)
        tables = [res[0] for res in db.db_ret]
        db.__db_cmd__(f"SELECT name FROM pragma_table_info('{db.TAB_ACCOUNTS}')", None, False)
        retrieved_accounts_cols = [res[0] for res in db.db_ret]
        db.__db_cmd__(f"SELECT name FROM pragma_table_info('{db.TAB_SUB_INFO}')", None, False)
        retrieved_sub_info_cols = [res[0] for res in db.db_ret]
        account_cols = [db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS, db.COL_SESSION_ID]
        sub_info_cols = [db.COL_SUB_CODE, db.COL_SUB_NAME]
        self.assertIn(db.TAB_ACCOUNTS, tables)
        self.assertIn(db.TAB_SUB_INFO, tables)
        self.assertEqual(retrieved_accounts_cols, account_cols)
        self.assertEqual(retrieved_sub_info_cols, sub_info_cols)

    def test_a12_add_one_data(self):
        """TEST_CASE_ID A.1.2"""
        db = SmartSchedulerDB(self.test_server)
        test_data = [str(randint(10 ** 9, 10 ** 10 - 1)), "test_pass_hash", "test_sch", "test_subs"]
        db.new_account(*test_data)
        retrieved_data = [db.query_account_info(test_data[0], query)[0] for query in
                          (db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(retrieved_data, test_data)
        self.assertRaises(CommonDatabaseError, db.new_account, *test_data)
        return test_data

    def test_a13_upd_one_data(self):
        """TEST_CASE_ID A.1.3"""
        db = SmartSchedulerDB(self.test_server)
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
        self.assertRaises(CommonDatabaseError, db.update_account_info, test_data_id, invalid_column, 'value')

    def test_a14_del_one_data(self):
        """TEST_CASE_ID A.1.4"""
        db = SmartSchedulerDB(self.test_server)
        test_data = self.test_a12_add_one_data()
        db.delete_account(test_data[0])
        retrieved_data = [db.query_account_info(test_data[0], query) for query in
                          (db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(all([i == [] for i in retrieved_data]), True)

    @classmethod
    def tearDownClass(cls):
        remove(cls.test_db)


if __name__ == '__main__':
    unittest.main()
