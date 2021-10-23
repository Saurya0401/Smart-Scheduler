import unittest
from os import remove
from random import randint

from smartscheduler.database import SmartSchedulerDB


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.db = SmartSchedulerDB("Test.db")

    def test_add_one_data(self):
        self.db = SmartSchedulerDB("Test.db")
        test_data = [str(randint(10**9, 10**10 - 1)), "test_pass_hash", "test_sch", "test_subs"]
        self.db.new_account(*test_data)
        retrieved_data = [self.db.query_account_info(test_data[0], query)[0] for query in
                          (self.db.COL_STU_ID, self.db.COL_PAS_HASH, self.db.COL_SCHEDULE, self.db.COL_SUBJECTS)]
        self.assertEqual(retrieved_data, test_data)
        return test_data

    def test_upd_one_data(self):
        self.db = SmartSchedulerDB("Test.db")
        test_data_id = self.test_add_one_data()[0]
        updated = {
            self.db.COL_PAS_HASH: "updated_pass_hash",
            self.db.COL_SCHEDULE: "updated_sch",
            self.db.COL_SUBJECTS: "updated_subs",
        }
        for k, v in updated.items():
            self.db.update_account_info(test_data_id, k, v)
        retrieved_data = [self.db.query_account_info(test_data_id, query)[0] for query in
                          (self.db.COL_PAS_HASH, self.db.COL_SCHEDULE, self.db.COL_SUBJECTS)]
        self.assertEqual(retrieved_data, list(updated.values()))

    def test_del_one_data(self):
        self.db = SmartSchedulerDB("Test.db")
        test_data = self.test_add_one_data()
        self.db.delete_account(test_data[0])
        retrieved_data = [self.db.query_account_info(test_data[0], query) for query in
                          (self.db.COL_STU_ID, self.db.COL_PAS_HASH, self.db.COL_SCHEDULE, self.db.COL_SUBJECTS)]
        self.assertEqual(all([i == () for i in retrieved_data]), True)

    def test_add_batch_data(self):
        self.db = SmartSchedulerDB("Test.db")
        test_list = [(f"TestKey{i}", f"Test Name {i}") for i in range(200)]
        self.db.make_subs_list(test_list)
        retrieved_data = self.db.retrieve_all(self.db.TAB_SUB_INFO)
        self.assertEqual(retrieved_data, test_list)

    def tearDown(self):
        remove("Test.db")


if __name__ == '__main__':
    unittest.main()
