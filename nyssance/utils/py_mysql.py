import sys
from django.conf import settings
import MySQLdb as mysql


class py_mysql:
    queryNum = 0
    errorMsg = ""

    def __init__(self):
        '''construct function'''
        self.dbHost = settings.DATABASES['default']['HOST']
        self.dbUser = settings.DATABASES['default']['USER']
        self.dbPass = settings.DATABASES['default']['PASSWORD']
        self.dbName = settings.DATABASES['default']['NAME']
        self.port = 3306
        self._conn()

    def getMysqlVersion(self):
        '''return the mysql version'''
        return mysql.get_client_info()

    def _mysqlError(self, e):
        print(e)

    def _conn(self):
        '''mysql connect'''
        try:
            self.conn = mysql.Connection(self.dbHost, self.dbUser, self.dbPass, self.dbName, int(self.port), charset='utf8')
            self.conn.autocommit(True)
        except mysql.Error as e:
            self._mysqlError(e)
            return False
        try:
            self.conn.select_db(self.dbName)
        except mysql.Error as e:
            self._mysqlError(e)
            return False
        try:
            self.cur = self.conn.cursor()
        except mysql.Error as e:
            self._mysqlError(e)
            return False
        self.setName()

    def setName(self):
        '''set name for utf-8'''
        self.cur.execute("SET NAMES 'utf8'")
        self.cur.execute("SET CHARACTER SET 'utf8'")

    def getMysqlPythonVersion(self):
        '''get the python-mysql version'''
        try:
            mysql.version_info
        except mysql.Error as e:
            self._mysqlError(e)
            return False

    def _close(self):
        '''close the mysql connect'''
        self.cur.close()

    def nextRecord(self):
        self.cur.nextset()

    def selectQuery(self, params):
        par = ''.join(params['name'], ',')
        try:
            sql = "select " + par + " from " + params['tbl'] + ' ' + params['prefix']
            self.sql = sql
            self.queryNum = self.cur.execute(sql)
            self.params = params
        except mysql.Error as e:
            self._mysqlError(e)
            return False

    def in_id(self):
        return self.conn.insert_id()

    def query(self, sql):
        try:
            self.queryNum = self.cur.execute(sql)
            return True
        except mysql.Error as e:
            self._mysqlError(e)
            return False

    def getSql(self):
        fetch = self.cur.fetchall()
        for inv in fetch:
            yield dict(zip(self.params['name'], inv))

    def fn(self):
        return self.cur.rowcount

    def getTableList(self, tblName):
        try:
            self.cur.execute("desc " + tblName)
            return [row[0] for row in self.cur.fetchall()]
        except mysql.Error as e:
            self._mysqlError(e)
            sys.exit(0)

    def getDbList(self):
        try:
            self.cur.execute("show tables")
            return [row[0] for row in self.cur.fetchall()]
        except mysql.Error as e:
            self._mysqlError(e)
            sys.exit(0)

    def getDatabaseList(self):
        return 1

    def __del__(self):
        try:
            self.__close__()
        except:
            "the connect could not close"
