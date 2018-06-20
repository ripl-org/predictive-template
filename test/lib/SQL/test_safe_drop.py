import unittest, pyodbc
from riipl import *

class test_safe_drop(unittest.TestCase):

    def test_basic_functionality(self):
        with Connection() as cxn:
            cxn.execute("CALL SAFE_DROP('DA_BEARS')")
            cxn.execute("CREATE TABLE DA_BEARS (BEARS VARCHAR2(30));")
            cxn.execute("CALL SAFE_DROP('DA_BEARS')")

    def test_bad_syntax(self):
        with Connection() as cxn:
            cxn.execute("CREATE TABLE DA_BEARS (BEARS VARCHAR2(30));")
            with self.assertRaises(pyodbc.Error):
                cxn.execute("CALL SAFE_DROP(DA_BEARS)")
            with self.assertRaises(pyodbc.Error):
                cxn.execute("CALL SAFE_DROP('DA_BEARS', 'BEARS')")
        
if __name__ == "__main__":
    unittest.main()
