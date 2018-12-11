import SCons
import atexit
import cx_Oracle

_owner = env.USERNAME.upper()
_table_cache = {}
_cxn = cx_Oracle.connect("/")
_cxn.autocommit = 1
atexit.register(_cxn.close)

env.Default(".")

class _SQLTable(SCons.Node.Node):

    NodeInfo = SCons.Node.FS.FileNodeInfo
    BuildInfo = SCons.Node.FS.FileBuildInfo

    def __init__(self, name):
        SCons.Node.Node.__init__(self)
        self.name = name
        self.store_info = 1
        self.ninfo = self.new_ninfo()
        self.changed_since_last_build = 1
        self.dir = Dir("#.")
        self.set_nocache()

    def __str__(self):
        return self.name

    def built(self):
        SCons.Node.Node.built(self)
        SCons.Node.store_info_map[self.store_info](self)

    def str_for_display(self):
        return "'" + self.__str__() + "'"

    def is_up_to_date(self):
        if not self.exists():
            return None
        else:
            return not self.changed()

    @SCons.Memoize.CountMethodCall
    def exists(self):
        """
        The table exists if it has an entry in all_tables.
        """
        try:
            return self._memo["exists"]
        except KeyError:
            pass
        cur = _cxn.cursor()
        cur.execute("""
                    SELECT table_name
                      FROM user_tables
                     WHERE table_name = '{}'
                    """.format(self.name.upper()))
        exists = cur.fetchone() is not None
        if exists:
            cur.execute("""
                        SELECT COUNT(*)
                          FROM {}
                        """.format(self.name.upper()))
            count = cur.fetchone()
            exists = count is not None and count[0] > 0
        cur.close()
        self._memo["exists"] = exists
        return exists

    def get_csig(self):
        ninfo = self.get_ninfo()
        try:
            return ninfo.csig
        except AttributeError:
            pass
        if self.exists():
            csig = SCons.Util.MD5signature(self.get_contents())
        else:
            csig = 0
        ninfo.csig = csig
        return csig

    @SCons.Memoize.CountMethodCall
    def get_size(self):
        """
        The table's size is the bytes on disk as reported by the segments table.
        """
        try:
            return self._memo["get_size"]
        except KeyError:
            pass
        if self.exists():
            cur = _cxn.cursor()
            cur.execute("""
                        SELECT bytes
                          FROM user_segments
                         WHERE segment_type = 'TABLE' AND
                               segment_name = '{}'
                        """.format(self.name.upper()))
            size = cur.fetchone()[0]
            cur.close()
        else:
            size = 0
        self._memo["get_size"] = size
        return size

    @SCons.Memoize.CountMethodCall
    def get_timestamp(self):
        """
        The table's timestamp is its last DDL time from all_objects.
        """
        try:
            return self._memo["get_timestamp"]
        except KeyError:
            pass
        if self.exists():
            cur = _cxn.cursor()
            cur.execute("""
                        SELECT FLOOR(last_ddl_time - TO_DATE('19700101', 'YYYYMMDD'))*24*3600 AS mtime
                          FROM user_objects
                         WHERE object_type = 'TABLE' AND
                               object_name = '{}'
                        """.format(self.name.upper()))
            ts = cur.fetchone()[0]
            cur.close()
        else:
            ts = 0
        self._memo["get_timestamp"] = ts
        return ts

    @SCons.Memoize.CountMethodCall
    def get_stored_info(self):
        try:
            return self._memo['get_stored_info']
        except KeyError:
            pass
        try:
            sconsign_entry = self.dir.sconsign().get_entry(self.name)
        except (KeyError, EnvironmentError):
            sconsign_entry = SCons.SConsign.SConsignEntry()
            sconsign_entry.binfo = self.get_binfo()
            sconsign_entry.ninfo = self.get_ninfo()
        self._memo['get_stored_info'] = sconsign_entry
        return sconsign_entry

    @SCons.Memoize.CountMethodCall
    def get_contents(self):
        try:
            return self._memo['get_contents']
        except KeyError:
            pass
        cur = _cxn.cursor()
        cur.execute("""
                    SELECT comments
                      FROM user_tab_comments
                     WHERE table_name = '{}'
                    """.format(self.name.upper()))
        contents = cur.fetchone()[0]
        self._memo['get_contents'] = contents
        return contents


def SQLTable(name):
    name = name.upper()
    try:
        return _table_cache[name]
    except KeyError:
        node = _SQLTable(name)
        _table_cache[name] = node
        env.Default(node)
        return node


Export(['SQLTable'])
