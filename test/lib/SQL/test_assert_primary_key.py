import unittest, pyodbc
from riipl import *

class test_assert_primary_key(unittest.TestCase):

    def test_good_key(self):
        da_bears = ["grizzly", "panda", "black"]
        with Connection() as cxn:
            cxn.execute("CREATE TABLE DA_BEARS (BEARS VARCHAR2(30));")
            for bear in da_bears:
                cxn.execute("INSERT INTO DA_BEARS (BEARS) VALUES ('%bear%')")
            cxn.execute("CALL ASSERT_PRIMARY_KEY('DA_BEARS', 'BEARS')")
            cxn.execute("DROP TABLE DA_BEARS PURGE")

    def test_bad_key(self):
        da_bears = ["grizzly", "panda", "black", "black"]
        with Connection() as cxn:
            cxn.execute("CREATE TABLE DA_BEARS (BEARS VARCHAR2(30));")
            for bear in da_bears:
                cxn.execute("INSERT INTO DA_BEARS (BEARS) VALUES ('%bear%')")
            with self.assertRaises(pyodbc.Error):
                cxn.execute("CALL ASSERT_PRIMARY_KEY('DA_BEARS', 'BEARS')")
            cxn.execute("DROP TABLE DA_BEARS PURGE")

    def test_bad_syntax(self):
        with Connection() as cxn:
            with self.assertRaises(pyodbc.Error):
                cxn.execute("CALL ASSERT_PRIMARY_KEY(X)")
            with self.assertRaises(pyodbc.Error):
                cxn.execute("CALL ASSERT_PRIMARY_KEY('TABLE_NAME', 'KEY')")
        
if __name__ == "__main__":
    unittest.main()
