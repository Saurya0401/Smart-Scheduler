import unittest
from os import remove
from random import randint

from smartscheduler.database import SmartSchedulerDB


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.db_path = "./test/test_server/Test.db"

    def test_add_one_data(self):
        db = SmartSchedulerDB(self.db_path)
        test_data = [str(randint(10**9, 10**10 - 1)), "test_pass_hash", "test_sch", "test_subs"]
        db.new_account(*test_data)
        retrieved_data = [db.query_account_info(test_data[0], query)[0] for query in
                          (db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(retrieved_data, test_data)
        return test_data

    def test_upd_one_data(self):
        db = SmartSchedulerDB(self.db_path)
        test_data_id = self.test_add_one_data()[0]
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

    def test_del_one_data(self):
        db = SmartSchedulerDB(self.db_path)
        test_data = self.test_add_one_data()
        db.delete_account(test_data[0])
        retrieved_data = [db.query_account_info(test_data[0], query) for query in
                          (db.COL_STU_ID, db.COL_PSWRD_HASH, db.COL_SCHEDULE, db.COL_SUBJECTS)]
        self.assertEqual(all([i == () for i in retrieved_data]), True)

    def test_add_batch_data(self):
        db = SmartSchedulerDB(self.db_path)
        test_list = [(f"TestKey{i}", f"Test Name {i}") for i in range(200)]
        db.make_subs_list(test_list)
        retrieved_data = db.retrieve_all(db.TAB_SUB_INFO)
        self.assertEqual(retrieved_data, test_list)

    def tearDown(self):
        remove(self.db_path)


if __name__ == '__main__':
    unittest.main()
