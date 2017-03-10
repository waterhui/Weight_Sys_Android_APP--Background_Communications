#coding :utf-8

import sqlite3
import os

class DbHelper(object):
    #类变量
    __conn_sql_obj = None

    @classmethod
    def get_db_helper(cls):
        if cls.__conn_sql_obj == None:
            cls.__conn_sql_obj = sqlite3.connect(os.getcwd() + "\weight.db", check_same_thread = False); #不检查是否处于同一个线程
        return cls.__conn_sql_obj

    @classmethod
    def db_execute(cls, sql):
        cur = cls.__conn_sql_obj.cursor()
        cur.execute(sql)
        cls.__conn_sql_obj.commit()
        return True

    @classmethod
    def db_query(cls, sql):
        cur = cls.__conn_sql_obj.cursor()
        cur.execute(sql)
        return cur.fetchall()

    @classmethod
    def db_is_exist_user(cls, sql):
        cur = cls.__conn_sql_obj.cursor()
        cur.execute(sql)
        lst = cur.fetchall()
        if len(lst) != 0:
            return True
        else:
            return False



