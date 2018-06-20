import unittest, os, sys, pyodbc
import numpy as np
import pandas as pd
from riipl import *

GLOBAL_PARAM = 3.14159

class TestConnection(unittest.TestCase):

    def test_connection_context_manager(self):
            with Connection() as cxn:
                cxn.clear_tables("test_connection")
                cxn.execute("CREATE TABLE test_connection (person_name VARCHAR2(30))")
                person_name = "Scarlatti"
                cxn.execute("INSERT INTO test_connection (person_name) VALUES ('%person_name%')")
                person_name = "Rachmaninoff"
                cxn.execute("INSERT INTO test_connection (person_name) VALUES ('%person_name%')")

            with Connection() as cxn:
                cursor = cxn.execute("SELECT * FROM test_connection")
                results = cursor.fetchall()
                cxn.execute("DROP TABLE test_connection PURGE")

            results = map(lambda x: x[0], results)
            self.assertTrue(results == ["Scarlatti", "Rachmaninoff"])

    def test_parameter_substitution(self):
        local_param = 8.2702
        with Connection() as cxn:
            cxn.execute(("CREATE TABLE test_connection(scope VARCHAR2(30), value NUMBER)"))
            cxn.execute("""
                        INSERT INTO test_connection(scope, value)
                        VALUES('global', %GLOBAL_PARAM%)""")
            cxn.execute("""
                        INSERT INTO test_connection(scope, value)
                        VALUES('local', %local_param%)""")
            local_param = 5.3298
            cxn.execute("""
                        INSERT INTO test_connection(scope, value)
                        VALUES('localer', %local_param%)""")
            cursor = cxn.execute("SELECT * FROM test_connection")
            results = cursor.fetchall()
            cxn.execute("DROP TABLE test_connection PURGE")

        results = {r[0]: r[1] for r in results}
        self.assertTrue(results["global"] == 3.14159)
        self.assertTrue(results["local"] == 8.2702)
        self.assertTrue(results["localer"] == 5.3298)

    def test_connection_basic(self):
        me = pyodbc.connect("DSN=RIIPL").cursor().execute("SELECT USER FROM DUAL").fetchall()[0][0]
        cxn = Connection()
        self.assertTrue(cxn.schema == me)
        self.assertTrue(cxn.password == "/")
        self.assertTrue(cxn.cxn_string == "DSN=RIIPL")

        sql = "CREATE TABLE test_connection (person_id NUMBER(2))"
        cxn.execute(sql)

        # test that parameters are substituted into strings
        person_id = 1
        sql = "INSERT INTO test_connection (person_id) VALUES (%person_id%)"
        cxn.execute(sql)
        person_id += 1
        cxn.execute(sql)

        # test that results were as expected
        cursor = cxn.execute("SELECT * FROM test_connection")
        results = map(lambda x: x[0], cursor.fetchall())
        self.assertTrue(results == [1,2])

        cxn.execute("DROP TABLE test_connection PURGE")
        cxn.close()

    def test_read_dataframe(self):
        df = pd.DataFrame({"df_float":  np.arange(0.0, 10.0),
                           "df_int":    np.arange(0, 10, dtype="u4"),
                           "df_string": map(str, xrange(10)),
                           "df_dt":     pd.date_range("2017-01-01", "2017-01-10")})
        with Connection() as cxn:
            cxn.read_dataframe(df, "test_read_dataframe")
            cxn.save_table("test_read_dataframe")
            cxn.clear_tables("test_read_dataframe")

    def test_read_csv(self):
        filename = os.path.join(os.path.dirname(__file__), "test_read_csv.csv")
        schema = (("df_dt", "DATE 'YYYYMMDD'"),
                  ("df_float", "NUMBER"),
                  ("df_int", "NUMBER"),
                  ("df_string", "CHAR(1)"))
        with Connection() as cxn:
            cxn.read_csv(filename, schema, "test_read_csv")
            cxn.save_table("test_read_csv")
            cxn.clear_tables("test_read_csv")

    def test_connection_exceptions(self):
        cxn = Connection()
        cxn.close()
        with self.assertRaises(IllegalStateException):
            cxn.execute("SELECT USER FROM DUAL")
        with self.assertRaises(NameError):
            with Connection() as cxn:
                cxn.execute("SELECT * FROM %POTATOES%")

    def test_clear_tables(self):
        with Connection() as cxn:
            cxn.execute("CREATE TABLE test_clear_tablesA (varname NUMBER(1));")
            cxn.execute("CREATE TABLE test_clear_tablesB (varname NUMBER(1));")
            cxn.clear_tables(["test_clear_tablesA", "test_clear_tablesB"])
            with self.assertRaises(pyodbc.ProgrammingError):
                cxn.execute("DROP TABLE test_clear_tablesA PURGE;")

    def test_clear_tables_casecade(self):
        rivers = ["Columbia", "Yukon", "Platte", "Colorado"]
        with Connection() as cxn:
            cxn.execute("CREATE TABLE test_clear_tablesA (rivers VARCHAR2(30))")
            for river in rivers:
                cxn.execute("INSERT INTO test_clear_tablesA (rivers) VALUES ('%river%')")
            cxn.execute("""
                    ALTER TABLE test_clear_tablesA ADD CONSTRAINT pk_test_clear_tablesA
                        PRIMARY KEY (rivers) 
                """)
            cxn.execute("CREATE TABLE test_clear_tablesB (river_name VARCHAR2(30))")
            for river in rivers[:2]:
                cxn.execute("INSERT INTO test_clear_tablesB (river_name) VALUES ('%river%')")
            cxn.execute("""
                        ALTER TABLE test_clear_tablesB ADD CONSTRAINT fk_river_name
                        FOREIGN KEY (river_name) REFERENCES test_clear_tablesA (rivers)
                        """)
            cxn.clear_tables("test_clear_tablesA")
            constraints = cxn.execute("""
                                      SELECT *
                                        FROM USER_CONSTRAINTS
                                       WHERE TABLE_NAME = 'TEST_CLEAR_TABLESB'
                                      """).fetchall()
            self.assertTrue(constraints == [])
            cxn.clear_tables("test_clear_tablesB")

if __name__ == "__main__":
    unittest.main()
