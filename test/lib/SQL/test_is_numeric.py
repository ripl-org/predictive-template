import unittest, pyodbc
from riipl import *

class test_is_numeric(unittest.TestCase):
    def test_basic_functionality(self):
        with Connection() as cxn:
            result_num = cxn.execute("SELECT IS_NUMERIC(1) FROM DUAL").fetchall()[0][0]
            result_str = cxn.execute("SELECT IS_NUMERIC('A') FROM DUAL").fetchall()[0][0]
        self.assertTrue(result_num == 1)
        self.assertTrue(result_str == 0)

    def test_bad_syntax(self):
        with Connection() as cxn:
            with self.assertRaises(pyodbc.Error):
                cxn.execute("SELECT IS_NUMERIC(1, 2) FROM DUAL")
            with self.assertRaises(pyodbc.Error):
                cxn.execute("SELECT IS_NUMERIC(COL_NAME) FROM DUAL")
    
if __name__ == "__main__":
    unittest.main()
