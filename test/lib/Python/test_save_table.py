import unittest, os, sys, pyodbc
import numpy as np
import pandas as pd
from riipl import *

np.random.seed(32989)

class TestSaveTable(unittest.TestCase):

    def setUp(self):
        person_id = pd.DataFrame(data = {
                        "person_id" : np.kron(np.arange(1,10), np.ones(10, dtype = np.int))
                    })
        person_name = pd.DataFrame(data = {
                          "person_name" : np.array(["Vivaldi", "Bach", "Handel", "Lully", "Chopin"
                                                    "Hayden", "Scarlatti", "Monteverdi", "Telemann",
                                                    "Rostropovitch"]),
                          "person_id"   : np.arange(1,10)
                      })
        test_table = pd.merge(person_id, person_name)

        toucan_purchase_date = np.random.choice(
                                    pd.date_range("2003-04-02", "2009-02-04").values,
                                    len(test_table.index),
                                    replace = False
                               )
        
        test_table.loc[:,"toucan_purchase_date"] = pd.DatetimeIndex(toucan_purchase_date)
        test_table.loc[:,"toucan_weight"] = np.random.normal(12, 2, len(test_table.index))
        test_table.loc[:,"num_toucans"] = np.random.randint(3, 80, len(test_table.index))

        create_table_stmt = """CREATE TABLE test_save_table (
                                   person_id            NUMBER(3),
                                   toucan_purchase_date DATE,
                                   person_name          VARCHAR2(30),
                                   toucan_weight        NUMBER,
                                   num_toucans          NUMBER(2)
                                )
                             """
        insert_row_stmt = """INSERT INTO test_save_table
                                 (person_id, toucan_purchase_date, person_name, 
                                  toucan_weight, num_toucans) VALUES
                                 (%person_id%, TO_DATE('%purchase_date%', 'YYYY-MM-DD'), 
                                  '%person_name%', %toucan_weight%, %num_toucans%)
                          """

        with Connection() as cxn:
            cxn.execute(create_table_stmt)
            for row in test_table.iterrows():
                person_id, person_name, toucan_weight, \
                purchase_date, num_toucans = self.parse_row(row[1])
                cxn.execute(insert_row_stmt, verbose=False)

        self.test_table = test_table

    def tearDown(self):
        with Connection() as cxn:
            cxn.execute("DROP TABLE test_save_table PURGE")

    def parse_row(self, table_row):
            return (table_row["person_id"], table_row["person_name"], table_row["toucan_weight"],
                    str(table_row["toucan_purchase_date"])[:10], table_row["num_toucans"])

    def test_basic_functionality(self):
        key = ["person_id", "toucan_purchase_date"]
        with Connection() as cxn:
            table_summary = cxn.save_table("test_save_table", key)

        # check that the returned summary stats are correct
        stats = self.test_table.describe()
        table_summary = table_summary.set_index("Variable")
        for varname in ["NUM_TOUCANS", "TOUCAN_WEIGHT", "PERSON_ID"]:
            self.assertAlmostEqual(table_summary.ix[varname, "COUNT"], 
                                   stats.ix["count", varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, "AVG"],
                                   stats.ix["mean", varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, "STDDEV"],
                                   stats.ix["std", varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, "MIN"],
                                   stats.ix["min", varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, "MAX"],
                                   stats.ix["max", varname.lower()])

        self.assertEqual(table_summary.ix["TOUCAN_PURCHASE_DATE", "MIN"],
                         self.test_table["toucan_purchase_date"].min().to_pydatetime())
        self.assertEqual(table_summary.ix["TOUCAN_PURCHASE_DATE", "MAX"],
                         self.test_table["toucan_purchase_date"].max().to_pydatetime())

    def get_pk_info(self):
        sql = """
              SELECT cols.table_name, cols.column_name,
                     const.status, const.constraint_name
                FROM all_constraints const, all_cons_columns cols
               WHERE cols.table_name = 'TEST_SAVE_TABLE' AND 
                     const.constraint_type = 'P'         AND
                     const.constraint_name = cols.constraint_name
              """
        with Connection() as cxn:
            pk_info = cxn.execute(sql).fetchall()
        return pk_info

    def test_single_column_key(self):
        with Connection() as cxn:
            cxn.execute("ALTER TABLE test_save_table ADD contrived_key NUMBER(2)")
            cxn.execute("UPDATE test_save_table SET contrived_key = ROWNUM")
            cxn.save_table("test_save_table", "contrived_key")
        pk_info = self.get_pk_info()
        self.assertTrue(pk_info[0][1] == "CONTRIVED_KEY")

    def test_bad_table(self):
        with self.assertRaises(pyodbc.ProgrammingError):
            with Connection() as cxn:
                cxn.save_table("no_such_table", "potato")

    def test_bad_key(self):
        table = "test_save_table"
        key = ["person_id", "toucan_purchase_date"]
        with Connection() as cxn:
            with self.assertRaises(pyodbc.Error):
                cxn.save_table(table, "person_id")
            with self.assertRaises(pyodbc.ProgrammingError):
                cxn.save_table(table, "no_such_column")
            cxn.execute("UPDATE test_save_table SET person_id = NULL WHERE ROWNUM < 2")
            with self.assertRaises(pyodbc.Error):
                cxn.save_table(table, key)

if __name__ == "__main__":
    unittest.main()
