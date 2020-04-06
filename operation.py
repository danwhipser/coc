import sqlite3 as lite
import sys
import time
import re
import random
from flask import session
# import hashlib


class opt:
    def __init__(self, database):
        try:
            self.con = lite.connect('db/' + database)
            self.cur = self.con.cursor()
        except lite.Error:
            print("Error %s:" % lite.Error)
            sys.exit(1)

    def comsql(self,sql):
        c = self.cur.execute(sql)
        self.con.commit()
        # print(sql)
        # localtime = time.asctime(time.localtime(time.time()))
        # print(localtime)
        return c

    def select_c(self, table, class_id=0):
        # cur = self.con.cursor()
        if class_id:
            sql = "select * from %s where id=%d" % (table, class_id)
        else:
            sql = "select * from %s" % table

        c = self.comsql(sql)
        cc = c.fetchall()
        return cc


    def class_sel(self, class_id=0):
        cc = self.select_c("class", class_id)
        return cc

    def name_sel(self, name_id=0):
        cc = self.select_c("name", name_id)
        return cc

    def atrn_sel(self, atrn_id=0):
        cc = self.select_c("attr", atrn_id)
        return cc

    def select_u(self, uid):
        # cur = self.con.cursor()
        sql = "select * from %s where uid=%d" % ("plyer", uid)
        c = self.comsql(sql)
        cc = c.fetchall()
        return cc


    def select_w(self,table,where):
        sql = "select * from %s where %s" % (table, where)
        c = self.comsql(sql)
        cc = c.fetchall()
        return cc
        # pass


    def select_n(self, kind, nid, aid=0, uid=0):
        # cur = self.con.cursor()
        if uid == 0:
            uid = int(session.get('uid'))
        if aid == 0:
            sql = "select * from %s where kind=%d and nid=%d and uid=%d" % ("plyer", kind, nid, uid)
        else:
            sql = "select * from %s where kind=%d and nid=%d and aid=%d and uid=%d" % ("plyer", kind, nid, aid, uid)
        c = self.comsql(sql)
        cc = c.fetchall()
        return cc

    def add_u(self,kind,uid=0,nid=0,aid=0,value=0,c_a=0,c_id=0):
        table = "plyer"
        if uid == 0:
            uid = int(session.get('uid'))
        sql = "INSERT INTO %s VALUES(NULL,%d,%d,%d,%d,'%s',%d,%d)" % (table,uid,kind,nid,aid,value,c_a,c_id)
        self.cur.execute(sql)
        lid = self.cur.lastrowid
        self.con.commit()
        print(sql)
        # self.comsql(sql)
        return lid

    def add_r(self, aid, value1=0, value2=0, link_kind=0, link_id=0):
        table = "groupp"
        sql = "INSERT INTO %s VALUES(NULL,%d,'%s','%s',%d,%d)" % (table,aid,value1,value2,link_kind,link_id)
        print(sql)
        self.cur.execute(sql)
        lid = self.cur.lastrowid
        self.con.commit()
        # self.comsql(sql)
        return lid

    def updata_w(self,table, set, where):
        sql = "UPDATE %s SET %s WHERE %s" % (table, set, where)
        self.comsql(sql)
        localtime = time.asctime(time.localtime(time.time()))
        print(localtime)
        return 1

    def updata_r(self,id, value1=0, value2=0):
        table = "groupp"
        sql = "UPDATE %s SET value1 = '%s', value2 = '%s' WHERE id ='%d'" % (table, value1, value2, id)
        self.comsql(sql)
        localtime = time.asctime(time.localtime(time.time()))
        print(localtime)
        return 1

    def updata_ua(self,id,value):
        table = "plyer"
        sql = "UPDATE %s SET value = '%s' WHERE id ='%d'" % (table, value, id)
        self.cur.execute(sql)
        lid = self.cur.lastrowid
        self.con.commit()
        print(sql)
        localtime = time.asctime(time.localtime(time.time()))
        print(localtime)
        return lid

    def updata_u(self,id,value,uid=0):
        table = "plyer"
        if uid == 0:
            uid = int(session.get('uid'))
        sql = "UPDATE %s SET value = '%s' WHERE id ='%d' AND uid='%d'" % (table, value, id, uid)
        self.cur.execute(sql)
        lid = self.cur.lastrowid
        self.con.commit()
        print(sql)
        localtime = time.asctime(time.localtime(time.time()))
        print(localtime)
        return lid


    def add_c(self,table,kind,value,desc=0):
        sql = "INSERT INTO %s VALUES(NULL,%d,'%s','%s')" % (table,kind,value,desc)
        self.comsql(sql)
        return 1

    def add_v(self,nid,aid,value=0,link=0,value2=0):
        nid = int(nid)
        aid = int(aid)
        if link == 0:
            re = self.check_ve(nid,aid)
            if re == 1:
                return "exist"
        sql = "INSERT INTO infoe VALUES(NULL, %d, %d, %d,'%s','%s')" % (nid,aid,link,value,value2)
        self.comsql(sql)
        localtime = time.asctime(time.localtime(time.time()))
        print(localtime)
        return 1

    def add(self,table,plus):
        sql = "INSERT INTO %s VALUES(NULL,%s)" % (table, plus)
        print(sql)
        self.comsql(sql)
        return 1

    def addla(self,table,plus):
        sql = "INSERT INTO %s VALUES(NULL,%s)" % (table, plus)
        print(sql)
        self.cur.execute(sql)
        lid = self.cur.lastrowid
        self.con.commit()
        # self.comsql(sql)
        return lid

    def check_ve(self,nid,aid):
        sql = "select * from infoe where nid=%d and aid=%d" % (nid,aid)
        c = self.comsql(sql)
        cc = c.fetchall()
        print(cc)
        if not cc:
            return 0
        else:
            return 1

    def select_v(self):
        sql = "select * from infoe"
        c = self.comsql(sql)
        cc = c.fetchall()
        return cc

    def delet(self,table,id):
        sql = "DELETE FROM %s WHERE id = %d " % (table, id)
        self.comsql(sql)
        return 1

    def delet_w(self,table,where):
        sql = "DELETE FROM %s WHERE %s " % (table, where)
        self.comsql(sql)
        return 1


    def delet_w(self,table,where):
        sql = "DELETE FROM %s WHERE %s" % (table, where)
        self.comsql(sql)
        return 1

    def delet_me(self):
        uid = int(session.get('uid'))
        sql = "DELETE FROM plyer WHERE uid = %d " % (uid)
        self.comsql(sql)
        return 1


# -------------------------------------------------------------扔骰子
# xdxx只支持前面一位
def roll_out(strg, tihuan):
    it = re.finditer(tihuan, strg)
    for match in it:
        ce = match.group()
        before = ce[0] #d前面的数字
        if before == "d" or before == "D":
            cc = ce[1:]
            before = 1
        else:
            after = ce[1:]
            cc = after[1:] #d后面的数字
        r = roll(int(cc),int(before))
        ee = str(r)
        strg = re.sub(tihuan, ee, strg)
    return strg

# roll(最大值,几d)
def roll(max, times=1):
    number = 0
    rad = 0
    while number < times:
        rad = rad + random.randint(1, max)
        number += 1
    return rad

# 算加法
def plus_out(strg, tihuan):
    it = re.finditer(tihuan, strg)
    for match in it:
        ce = match.group()
        tt = re.finditer('\d+', ce)
        ee = 0
        for mm in tt:
            ee = ee + int(mm.group())
        strg = ee
    return strg

# 替换xdx成数字,并且将字符串中数字加和
def roll_str(strg):
    a = '\dd\d+'
    b = '\dD\d+'
    r = roll_out(strg,a)
    r = roll_out(r,b)
    return r

# 把数组拆分并把db和0.5db替换了
def roll_str2(strg,dbv):
    out = []
    dbv = roll_str(dbv)
    r = re.split('\+', strg)
    p1 = re.compile('(0.5db|0.5DB)')
    p2 = re.compile('(db|DB)')
    for ee in r:
        dbv2 = str(int(int(dbv)/2))
        ee = p1.sub(dbv2, ee)
        ee = p2.sub(dbv, ee)
        ee = roll_str(ee)
        out.append(ee)
    return out


# 重置算法
def reset_num(num):
    if num>=95:
        return num
    else:
        n = int(num/10)
        num = num-n
        return num

# -------------------------------------------------------------扔骰子
# us=opt("user.db")
# us.sele_v(5,8)