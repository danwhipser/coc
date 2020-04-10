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

class page_opt_m:
    aid_group_name = 68  # 组团名称
    aid_group_plyr = 72  # 玩家id/玩家卡组
    aid_playr_job  = 9   # 职业aid
    aid_playr_kazu = 64  # 用户卡组aid
    aid_playr_tou  = 75  #头像地址

    temp_uid = 22

    def __init__(self,setus, myuid):
        self.myuid = myuid
        self.setus = setus

    # 列出房间
    def list_room(self, ifme=0):
        us = self.setus
        gnameaid = self.aid_group_name
        myuid = self.myuid
        re = []
        if ifme == 1:
            group_names = us.select_w("groupp", "aid=%d and value2='%s'" % (gnameaid, str(myuid)))
        else:
            group_names = us.select_w("groupp", "aid=%d" % gnameaid)
        for group_name in group_names:
            group_id = group_name[0]
            group_deteils = us.select_w("groupp", "link_kind=5 and link_id='%d'" % int(group_id))
            r = []
            r.append(group_name)
            r.append(group_deteils)
            re.append(r)
        return re

    # 列出自己的人物卡组(房间/自己, group id)   输出: 自己的卡组/房间内所有加入人的卡组
    def list_kazu(self, method, gid=0):
        us = self.setus
        myuid = self.myuid
        jobaid = self.aid_playr_job #9
        kazuaid = self.aid_playr_kazu  #64
        group_plyeraid = self.aid_group_plyr  #72
        playr_tou = self.aid_playr_tou  #75
        r = []
        re = []
        if method == "me":
            kazu = us.select_w("plyer", "uid=%d and nid=%d" % (myuid, kazuaid))
        elif method == "group":
            gid = int(gid)
            kazu = us.select_w("groupp", "aid=%d and link_kind=5 and link_id=%d" % (group_plyeraid, gid))

        for kk in kazu:
            if method == "me":
                kazu_id = kk[0]
                kkr = kk
            elif method == "group":
                kazu_id = int(kk[3])
                kkr = us.select_w("plyer", "id=%d and nid=%d" % (kazu_id, kazuaid))
                if kkr:
                    kkr = kkr[0]
                else:
                    us.delet_w("groupp", "aid=%d and link_kind=5 and link_id=%d and value2='%s'" % (group_plyeraid, gid, kk[3]))
                    kkr = str(0)
                    continue
            kazu_deteils = us.select_w("plyer", "kind=1 and c_kind=1 and c_id=%d" % kazu_id)
            for ki in kazu_deteils:
                if ki[3] == jobaid:
                    work_id = ki[5]
                    work = us.select_w("name", "id=%d" % int(work_id))
                    if not work:
                        work = str(0)
                elif ki[3] == playr_tou:
                    pic = ki
            r.append(kkr)
            r.append(pic)
            r.append(work)
            re.append(r)
            r = []

        return re

    # 列出模板人物
    def list_temp(self):
        us = self.setus
        kazuaid = self.aid_playr_kazu
        jobaid = self.aid_playr_job
        temp_uid = self.temp_uid
        outa = []

        # nid=64是卡组,先取卡组
        list = us.select_w("plyer", "kind=1 and nid=%d and uid=%d" % (kazuaid, temp_uid))
        for ll in list:
            pid = ll[0]
            workname = ll[5]
            jobt = us.select_w("plyer", "kind=1 and nid=%d and uid=%d and c_kind=1 and c_id=%d" % (jobaid,temp_uid, pid))
            if not jobt:
                continue
            jobid = jobt[0][5]
            jobname = us.select_w("name", "id=%d" % int(jobid))
            jobname = jobname[0][2]
            outo = []
            outo.append(pid)
            outo.append(workname)
            outo.append(jobname)
            outa.append(outo)
        return outa

    # 获取用户详细信息
    def get_user_deteil(self, uid=0, cid=0):
        us = self.setus
        if uid == 0:
            uid = self.myuid
        user = us.select_w("plyer", "uid=%d and kind=1 and c_kind=1 and c_id=%d order by nid asc" % (uid, cid))
        return user

    # 获取房间的详细信息
    def get_room_deteil(self, gid):
        re = []
        us = self.setus
        gnameaid = self.aid_group_name
        group_names = us.select_w("groupp", "aid=%d and id=%d" % (gnameaid, int(gid)))
        for group_name in group_names:
            group_deteils = us.select_w("groupp", "link_kind=5 and link_id='%d'" % int(gid))
            r = []
            r.append(group_name)
            r.append(group_deteils)
            re.append(r)
        return re

    # 录入用户信息,如果存在则修改
    def add_user(self, kind, uid, nid, aid, value, cid):
        us = self.setus
        myuid = self.myuid
        if uid == 0:
            uid = myuid
        kind = int(kind)
        nid = int(nid)
        uid = int(uid)
        aid = int(aid)
        value = str(value)
        cid = int(cid)
        if kind == 1:
            res = us.select_w("plyer", "uid=%d and nid=%d and kind=%d and c_id=%d" % (uid, nid, kind, cid))
            if res:
                # 姓名和卡组名称保持相同
                if nid == 1:
                    us.updata_u(cid, value)

                id = int(res[0][0])
                re = us.updata_u(id, value)
                return re
            else:
                re = us.add_u(kind, 0, nid, aid, value, 1, cid)
        elif kind == 3:
            res = us.select_w("plyer", "uid=%d and nid=%d and aid=%d and kind=%d and c_kind=1 and c_id=%d" % (
            uid, nid, aid, kind, cid))
            if res:
                id = int(res[0][0])
                re = us.updata_u(id, value)
                return re
            else:
                re = us.add_u(kind, 0, nid, aid, value, 1, cid)
        elif kind == 4:
            re = us.add_u(kind, 0, nid, 0, 0, 1, cid)
        return re



class page_opt:
    out_all = []
    aid_name = 1
    aid_headimg = 75

    def __init__(self,setus, myuid):
        self.out_all = []
        self.myuid = myuid
        self.setus = setus

    # 侧边栏列表数据
    # 0:    0:name| 1:atrr| 2:infoe|
    # 1:    0:列出所有房间| 1:列出自己的房间| 2:列出所有模板人物| 3:列出自己所有卡组(名字,头像)
    def general_sel(self):
        myuid = self.myuid
        us = self.setus

        optm = page_opt_m(us, myuid)
        listroom_all = optm.list_room()
        listroom_me  = optm.list_room(1)

        listtemp = optm.list_temp()
        # col = [self.aid_name, self.aid_headimg]
        listkazu = optm.list_kazu("me")
        # out = []
        # names = us.name_sel()
        # atrr = us.atrn_sel()
        # infoe = us.select_w("infoe", "1=1")
        #
        # out.append(names)
        # out.append(atrr)
        # out.append(infoe)
        # self.out_all.append(out)

        out = []
        out.append(listroom_all)
        out.append(listroom_me)
        out.append(listtemp)
        out.append(listkazu)
        self.out_all.append(out)
        return out

    # 获取自己的个人信息数据
    def setting_sel(self, cid):
        myuid = self.myuid
        us = self.setus
        optm = page_opt_m(us,myuid)
        out = optm.get_user_deteil(0, cid)
        self.out_all.append(out)
        return out

    # 输入数组(0:kind 1:nid 2:aid 3:value 4:cid)
    def setting_add(self, arry):
        myuid = self.myuid
        us = self.setus
        optm = page_opt_m(us,myuid)
        for p in arry:
            kind= p[0]
            nid = p[1]
            aid = p[2]
            value=p[3]
            cid = p[4]
            optm.add_user(kind,0,nid,aid,value,cid)
        return 1

    # 获取roomc需要的数据
    # 0: 房间详细信息| 1: 列出房间所有卡组| 2: 列出我的卡组
    def roomc_sel(self, gid):
        myuid = self.myuid
        us = self.setus
        optm = page_opt_m(us,myuid)
        room_deteil = optm.get_room_deteil(gid)
        list_allkazu = optm.list_kazu("group", gid)
        list_mykazu = optm.list_kazu("me")
        out = []
        out.append(room_deteil)
        out.append(list_allkazu)
        out.append(list_mykazu)
        self.out_all.append(out)
        return out








# -------------------------------------------------------------扔骰子
# xdxx只支持前面一位 如果ifbomb是max,取最大值
def roll_out(strg, tihuan,ifbomb=0):
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
        if ifbomb == "max":
            r = int(cc)*int(before)
        else:
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
def roll_str(strg,ifbomb=0):
    a = '\dd\d+'
    b = '\dD\d+'
    r = roll_out(strg,a,ifbomb)
    r = roll_out(r,b,ifbomb)
    return r

# 把数组拆分并把db和0.5db替换了   ifbomb=0失败,max最大值,其他 正常
def roll_str2(strg,dbv,ifbomb):
    if ifbomb == 0:
        return 0
    out = []
    dbv = roll_str(dbv)
    r = re.split('\+', strg)
    p1 = re.compile('(0.5db|0.5DB)')
    p2 = re.compile('(db|DB)')
    for ee in r:
        dbv2 = str(int(int(dbv)/2))
        ee = p1.sub(dbv2, ee)
        ee = p2.sub(dbv, ee)
        ee = roll_str(ee,ifbomb)
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