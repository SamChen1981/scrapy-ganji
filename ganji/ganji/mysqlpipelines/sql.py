import mysql.connector
# from xuexi import settings

MYSQL_HOSTS = '192.168.90.170'
MYSQL_USER = 'root'
MYSQL_PWD = ''
MYSQL_PORT = '3306'
MYSQL_DB = 'scrapy'

cnx = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PWD, host=MYSQL_HOSTS, database=MYSQL_DB)
cur = cnx.cursor(buffered=True)

class Sql:

    @classmethod #修饰符，不需要初始化类就可以直接调用
    def start_urls(cls, sql, limit=1):
        
        if limit == 1:
            cur.execute(sql+' limit '+str(limit))
            return cur.fetchone()
        elif limit == 'all':
            cur.execute(sql)
            return cur.fetchall()
        else:
            cur.execute(sql+' limit '+str(limit))
            return cur.fetchall()
    @classmethod
    def change_status(cls, sql, value):
        # print(tuple(str(value)))
        cur.execute(sql, (value,))
        cnx.commit()
    @classmethod
    def exe(cls, sql, value):
        cur.execute(sql, value)
        cnx.commit()
    @classmethod
    def res(cls, sql, value,limit=1):
        cur.execute(sql, value)
        if limit == 1:
            return cur.fetchone()
        else:
            return cur.fetchall()