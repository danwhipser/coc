import sqlite3 as lite
import sys
import re
import json
import hashlib
import os
import time
import random
from flask import Flask,session, jsonify
from flask import redirect,url_for
from flask import render_template, request
from user import user
from stati import statics as stt
from operation import opt
from operation import page_opt as po
import operation as op


app = Flask(__name__)
app.config['SECRET_KEY'] = 'd0b9791a0c389833d872d899df744ca8'


@app.route('/')
def index():
    if session.get('uid'):
        # 权限是1是管理员
        if session.get('limit') == 1:
            limit = 1
        else:
            limit = 2
        page = "index"
        us = opt("user.db")
        uid = session.get('uid')
        kazu     = us.select_w("plyer", "uid=%d and nid=64" % uid)
        user_all = us.select_w("plyer", "uid=%d and kind=1 and c_kind=1" % uid)
        return render_template('dist/index.html', page=page, kazu=kazu, user_all=user_all,limit=limit)
    else:
        title = "欢迎来到深渊小屋,我们致力于开发与制作类克苏鲁跑团游戏"
        return render_template('dist/signin.html', message=title)


# 侧边栏列表数据
# 0:    0:name| 1:atrr| 2:infoe|
# 1:    0:列出所有房间| 1:列出自己的房间| 2:列出所有模板人物| 3:列出自己所有卡组(名字,头像)
@app.route('/set_index', methods=['GET'])
def set_index():
    myuid = session.get('uid')
    setus = opt("user.db")
    se = po(setus, myuid)
    out = se.general_sel()
    # out = se.out_all
    return jsonify(out)

# 新页面
@app.route('/imboss')
def imboss():
    if session.get('limit') == 1:
        title = "欢迎回来管理员！该继续加班啦！"
        us = opt("user.db")
        clss = us.class_sel()
        names = us.name_sel()
        atrr = us.atrn_sel()
        return render_template('manage.html', message=title, clss=clss, names=names, atrr=atrr)
    else:
        message = "出现了迷之错误！"
        return render_template('error.html', message=message)

# 统计数据
@app.route('/stati')
def stati():
    us = opt("user.db")
    tit = "检定"
    sta = stt(us)
    re = sta.get_jianding()
    return render_template('stati.html', sta=re)

#新页面
@app.route('/newpage')
def newpage():
    return render_template('dist/chat-1.html')

#地图页面
@app.route('/roommap', methods=['GET'])
def roommap():
    group_id = request.args.get("rid")
    group_id = int(group_id)
    page = "roommap"
    us = opt("user.db")
    re = us.select_w("groupp", "id=%d" % group_id)
    re = re[0]
    group_name = re[2]
    myuid = session.get('uid')
    re3 = us.select_w("groupp", "aid=82 and link_kind=5 and link_id=%d" % (group_id))
    uid = re3[0][3]
    uid = int(uid)
    if uid == int(myuid):
        token = re3[0][2]
    else:
        token = 0

    return render_template('dist/room_map.html', page=page, group_id=group_id, group_name=group_name, token=token)


#寻找游戏页面
@app.route('/roomp')
def roomp():
    if session.get('limit') == 1:
        limit = 1
    else:
        limit = 2
    page = "roomp"
    us = opt("user.db")
    uid = session.get('uid')
    kazu = us.select_w("plyer", "uid=%d and nid=64" % uid)
    user_all = us.select_w("plyer", "uid=%d and kind=1 and c_kind=1" % uid)
    return render_template('dist/index.html', page=page, kazu=kazu, user_all=user_all,limit=limit)


#创建人页面
@app.route('/roomc', methods=['GET'])
def roomc():
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('index'))

    group_id = request.args.get("rid")
    if group_id:
        group_id = int(group_id)
    else:
        group_id = 0
        return render_template('error.html', message="必须要有房间id")
    myuid = session.get('uid')
    us = opt("user.db")
    kazu = us.select_w("plyer", "uid=%d and nid=64" % uid)
    user_all = us.select_w("plyer", "uid=%d and kind=1 and c_kind=1" % uid)

    names = us.name_sel()
    atrr = us.atrn_sel()
    infoe = us.select_w("infoe","1=1")

    re = us.select_w("groupp", "id=%d" % group_id)
    re = re[0]
    group_name = re[2]
    re2 = us.select_w("groupp", "link_kind=5 and link_id=%d" % group_id)
    group_creater = int(re[3])
    if group_creater == uid:
        page = "roomc"
        # 获取token
        re3 = us.select_w("groupp", "aid=82 and value2='%d' and link_kind=5 and link_id=%d" % (myuid, group_id))
        token = re3[0][2]
    else:
        page = "roomp"
        token = 0

    return render_template('dist/room_c.html', page=page, kazu=kazu, user_all=user_all, group_name=group_name, names=names, atrr=atrr, infoe=infoe, group_deteil=re2, group_id=group_id, group_creater=group_creater, myuid=myuid,token=token)


#新建立人物页面
@app.route('/setting', methods=['GET', 'POST'])
def setting():
    page = "setting"
    checku()
    cid = request.args.get("c")
    if cid:
        cid = int(cid)
    else:
        return render_template('error.html', message="没有用户id")
    us = opt("user.db")
    clss = us.class_sel()
    names = us.name_sel()
    atrr = us.atrn_sel()
    uid = session.get('uid')
    uid = int(uid)
    user_all = us.select_w("plyer", "uid=%d and kind=1 and c_kind=1" % uid)
    user = us.select_w("plyer","uid=%d and kind=1 and c_kind=1 and c_id=%d" % (uid, cid))
    # 预设参数
    value = us.select_v()
    kazu=us.select_w("plyer","uid=%d and nid=64" % uid)
    obj_infos = us.select_c("infoe")
    return render_template('dist/creatplyr.html', page=page, clss=clss, names=names, atrr=atrr, user=user, user_all=user_all, value=value, kazu=kazu, cid=cid, obj_infos=obj_infos)

#获取图片
@app.route('/pic_upload', methods=['POST'])
def pic_upload():
    print('图像以上传')
    img = request.files['file']
    path = "/static/photo/"
    file_path = path + img.filename
    img.save(file_path)
    print('上传头像成功，上传的用户是：' + img.filename)
    return render_template('error.html', message="图片上传完成")

#获取工作
@app.route('/getkazu', methods=['GET'])
def getkazu():
    r = []
    re = []
    us = opt("user.db")
    uid = session.get('uid')
    method = request.args.get("method")
    if method=="mykazu":
        kazu = us.select_w("plyer", "uid=%d and nid=64" % uid)
    elif method=="allkazu":
        gid = request.args.get("gid")
        gid = int(gid)
        kazu = us.select_w("groupp", "aid=72 and link_kind=5 and link_id=%d" % gid)

    for kk in kazu:
        if method == "mykazu":
            kazu_id = kk[0]
            kkr = kk
        elif method == "allkazu":
            kazu_id = int(kk[3])
            kkr = us.select_w("plyer", "id=%d and nid=64" % kazu_id)
            if kkr:
                kkr = kkr[0]
            else:
                us.delet_w("groupp","aid=72 and link_kind=5 and link_id=%d and value2='%s'" % (gid, kk[3]))
                kkr = str(0)
                continue
        kazu_deteils = us.select_w("plyer", "kind=1 and c_kind=1 and c_id=%d" % kazu_id)
        for ki in kazu_deteils:
            if ki[3] == 9:
                work_id = ki[5]
                work = us.select_w("name", "id=%d" % int(work_id))
                if not work:
                    work = str(0)
        r.append(kkr)
        r.append(kazu_deteils)
        r.append(work)
        re.append(r)
        r = []
    return jsonify(re)

#获取卡组人物详细信息
@app.route('/get_infodeteil', methods=['GET'])
def get_infodeteil():
    cid = request.args.get("cid")
    cid = int(cid)
    us = opt("user.db")
    deteil = us.select_w("plyer", "c_kind=1 and c_id=%d order by nid asc" % (cid))
    return jsonify(deteil)


#获取工作
@app.route('/getpdeteil', methods=['GET'])
def getpdeteil():
    uid = request.args.get("u")
    us = opt("user.db")
    # uid = session.get('uid')
    pp_name = us.select_w("plyer", "uid=%d and nid=64" % uid)
    for n in pp_name:
        pp_id = n[0]
        kazu_deteils = us.select_w("plyer", "c_kind=1 and c_id=%d" % int(pp_name))

    pass


#获取工作
@app.route('/getwork', methods=['GET'])
def getwork():
    us = opt("user.db")
    cid = request.args.get("c")
    cid = int(cid)
    uid = session.get('uid')
    uid = int(uid)
    # 找到职业
    work = us.select_w("plyer", "uid=%d and kind=1 and nid=9 and c_kind=1 and c_id=%d" % (uid,cid))
    if not work:
        worke = 0
    else:
        worke = int(work[0][5])

    return str(worke)

#获取技能点数相关
@app.route('/getworkskill', methods=['GET'])
def getworkskill():
    cid = request.args.get("cid")
    cid = int(cid)
    us = opt("user.db")
    uid = session.get('uid')

    # 是否已经点了技能点
    skills = us.select_w("plyer", "uid=%d AND kind=3 AND c_kind=1 AND c_id=%d" % (int(uid), cid))
    if skills:
        skills = skills
    else:
        skills = 0

    return jsonify(skills)

#获取技能点数相关
@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    method = request.args.get("method")
    r = []
    re = []
    us = opt("user.db")
    if method == "myroom":
        uid = session.get('uid')
        group_names = us.select_w("groupp","aid=68 and value2='%s'" % str(uid))
    else:
        group_names = us.select_w("groupp", "aid=68")
    for group_name in group_names:
        group_id = group_name[0]
        group_deteils = us.select_w("groupp", "link_kind=5 and link_id='%d'" % int(group_id))
        r.append(group_name)
        r.append(group_deteils)
        re.append(r)
        r = []
    return jsonify(re)

# 选择职业模板
@app.route('/set_temp', methods=['POST'])
def set_temp():
    # 64是卡组的id(具体查表)
    nid = 64
    kind = 1
    val    = request.form['v']
    tempid = request.form['tempid']
    tempid = int(tempid)
    if not val:
        return 0
    us = opt("user.db")
    uid = session.get('uid')
    uid = int(uid)

    tempinfo = us.select_w("plyer", "uid=%d and c_kind=1 and c_id=%d" % (22, tempid))
    if tempinfo:
        lastid = us.add_u(kind, uid, nid, 0, val)
        for info in tempinfo:
            us.add_u(info[2],uid,info[3],info[4],info[5],info[6],lastid)
    return str(lastid)

#添加卡组
@app.route('/add_kazu', methods=['POST'])
def add_kazu():
    # 64是卡组的id(具体查表)
    nid = 64
    kind = 1
    val = request.form['v']
    if not val:
        return 0
    us = opt("user.db")
    uid = session.get('uid')
    uid = int(uid)
    lastid = us.add_u(kind, uid, nid, 0, val)
    # 名称写入用户名称
    nid_name = 1
    us.add_u(kind, uid, nid_name, 0, val, kind, lastid)
    # 头像归0
    nid_pic = 75
    us.add_u(kind, uid, nid_pic, 0, 0, kind, lastid)
    return str(lastid)

#删除卡组
@app.route('/del_kazu', methods=['POST'])
def del_kazu():
    # 64是卡组的id(具体查表)
    kind = 1
    kid = request.form['id']
    if not kid:
        return 0
    kid = int(kid)
    us = opt("user.db")
    uid = session.get('uid')
    uid = int(uid)
    us.delet_w("plyer", "uid=%d and c_kind=%d and c_id=%d" % (uid, kind, kid))
    us.delet_w("plyer", "uid=%d and id=%d" % (uid, kid))
    us.delet_w("groupp", "aid=72 and value='%s' and value2='%s'" % (str(uid), str(kid)))
    return str(1)

#新注册页面
@app.route('/signin')
def signin():
    title = "欢迎来到克苏鲁pao团"
    return render_template('dist/signin.html', message=title)

#kp数据获取
@app.route('/getkprom', methods=['POST'])
def getkprom():
    gid = request.form['gid']
    token = request.form['token']
    if token == "0":
        return jsonify("")
    check = checktoken(token)
    if check != 1:
        return jsonify("")
    myuid = session.get('uid')
    setus = opt("user.db")
    se = po(setus, myuid)
    out = se.kp_sel(gid)
    # out = se.out_all
    return jsonify(out)


#地图页面
@app.route('/usermap', methods=['GET'])
def usermap():
    nid = request.args.get("nid")
    aid = 63
    us = opt("user.db")
    img = us.select_w("infoe","nid=%d and aid=%d" % (nid, aid))
    return render_template('usermap.html',img=img)


@app.route('/logout')
def logout():
    session['uid'] = False
    session['token'] = False
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    uid = session.get('uid')
    if uid:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        uu = user("user.db")
        uu.checkusr(username, password)
        if uu.result == 1:
            session['uid'] = uu.uid
            session['token'] = uu.token
            session['limit'] = uu.limit
            return redirect(url_for('index'))
            if session.get('limit') == 1:
                return render_template('manage.html')
            return render_template('index.html')
        else:
            message = "用户名或者密码错啦！"
            return render_template('dist/signin.html', message=message)
            # return render_template('login.html', message=message)
    else:
        message = "欢迎来到克苏鲁pao团,我们致力于开发与制作类克苏鲁游戏"
        return render_template('dist/signin.html', message=message)
        # return render_template('login.html', message="克苏鲁炮团")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # repassword = request.form['repassword']
        code = request.form['code']
        name = username
        if code != "@dZe41jt#.7":
            return render_template('dist/signup.html', message="邀请码错误")
        if (not name) or (not username) or (not password):
            return render_template('dist/signup.html', message="不能为空")
        uu = user("user.db")
        uu.setusr(username, password, name)
        if uu.result == 1:
            return redirect(url_for('index'))
        elif uu.result == 2:
            return render_template('error.html', message="此用户已存在")
        else:
            message = "出现了迷之错误！"
            return render_template('dist/signup.html', message=message)
    else:
        return render_template('dist/signup.html', message="深渊登记处")

@app.route('/masg')
def masg():
    return render_template('masg.html')

@app.route('/addn', methods=['GET', 'POST'])
def addn():
    if session.get('limit') != 1:
        return render_template('error.html', message="没有权限")
    if request.method == 'POST':
        table = request.form['table']
        kind = request.form['kind']
        name = request.form['name']
        desc = request.form['desc']
        if not desc:
            desc = 0
        table = int(table)
        if table == 1:
            table = "name"
        elif table == 2:
            table = "attr"
        # elif table == 3:
        #     table = "class"
        else:
            return render_template('error.html', message="table不对")
        us = opt("user.db")
        us.add_c(table, int(kind), name, desc)
        return redirect('imboss#class_%s' % kind)
    else:
        return render_template('error.html', message="没有post")

@app.route('/updaten', methods=['GET', 'POST'])
def updaten():
    if session.get('limit') != 1:
        return render_template('error.html', message="没有权限")
    if request.method == 'POST':
        table = request.form['table']
        kind = request.form['kind']
        name = request.form['name']
        desc = request.form['desc']
        naid = request.form['naid']
        table = int(table)
        if table == 1:
            table = "name"
        elif table == 2:
            table = "attr"
        else:
            return render_template('error.html', message="table不对")
        us = opt("user.db")
        us.updata_w(table,"name='%s', desc='%s'" % (name,desc),"id=%d" % int(naid))
        return redirect('imboss#a_%s' % naid)



#预设点数管理
@app.route('/man_point', methods=['GET', 'POST'])
def man_point():
    limit = session.get('limit')
    if(limit != 1):
        return redirect(url_for('index'))
    kind = request.args.get("k")
    if not kind:
        kind = 1
    else:
        kind = int(kind)
    title = "欢迎回来管理员！该继续加班啦！"
    us = opt("user.db")
    if request.method == 'POST':
        nid = request.form['nid']
        aid = request.form['aid']
        value = request.form['value']
        # iflink = request.form['iflink']
        link = request.form['link']
        nid = int(nid)
        aid = int(aid)
        value = str(value)
        if link:
            link = int(link)
        # 如果是附加技能,添加附加技能
        if aid == 47:
            value2 = request.form['value2']
            re = us.add_v(nid, aid, value, link, value2)
        else:
            re = us.add_v(nid, aid, value, link)

        if re != 1:
            return render_template('msg.html', message=re)
        return redirect("/man_point?k="+str(kind))

    clss = us.class_sel(kind)
    names = us.name_sel()
    atrr = us.atrn_sel()
    value = us.select_v()

    if kind == 1:
        users = us.select_w("login","1=1")
        players = us.select_w("plyer","1=1")
    else:
        users = ""
        players = ""

    if kind == 11:
        clss = us.class_sel(2)
        kind = 2
        return render_template('man_job.html', message=title, clss=clss, names=names, atrr=atrr, kind=kind,
                               value=value, users=users, players=players)

    return render_template('man_point.html', message=title, clss=clss, names=names, atrr=atrr, kind=kind, value=value, users=users,players=players)

#kp对所有用户的操控
@app.route('/showallplyer', methods=['GET', 'POST'])
def showallplyer():
    limit = session.get('limit')
    if limit == 1:
        pass
    elif limit == 3:
        pass
    else:
        return redirect(url_for('index'))

    uid = request.args.get("u")
    if not uid:
        uid = 3
    us = opt("user.db")
    user = us.select_u(int(uid))
    names = us.name_sel()
    atrr = us.atrn_sel()

    users = us.select_w("login", "1=1")
    players = us.select_w("plyer", "1=1")
    value = us.select_v()

    myuid = session.get('uid')

    return render_template('showallplyer.html', names=names, user=user, atrr=atrr, users=users, players=players, myuid=myuid, value=value, thisuid=uid)


#kp对所有用户的操控
@app.route('/showme', methods=['GET', 'POST'])
def showme():
    uid = int(session.get('uid'))
    us = opt("user.db")
    user = us.select_u(int(uid))
    names = us.name_sel()
    atrr = us.atrn_sel()

    users = us.select_w("login", "1=1")
    players = us.select_w("plyer", "1=1")
    value = us.select_v()

    myuid = uid

    return render_template('showme.html', names=names, user=user, atrr=atrr, users=users, players=players, myuid=myuid, value=value)




#色子
@app.route('/saizi', methods=['GET', 'POST'])
def saizi():
    k = request.args.get("k")
    if k:
        # k = request.args.get("k")
        k = int(k)
        msg = random.randint(1,k)
        msg = str(msg)
    else:
        msg = "无数字"

    return render_template('saizi.html', message=msg)


@app.route('/delet', methods=['POST'])
def delet():
    table = request.form['table']
    id = request.form['id']
    id = int(id)
    us = opt("user.db")
    if table == "clss":
        table = "class"
        us.delet_w("name", "kind=%d" % id)
        us.delet_w("attr", "kind=%d" % id)
        us.delet_w("plyer", "kind=%d" % id)
    elif table == "name":
        table = "name"
        us.delet_w("infoe", "nid=%d" % id)
        us.delet_w("plyer", "nid=%d" % id)
    elif table == "atrr":
        table = "attr"
        us.delet_w("infoe", "aid=%d" % id)
        us.delet_w("plyer", "aid=%d" % id)
    elif table == "info":
        table = "infoe"
    # print("delet table %s id:%s"%(table,id))

    re = us.delet(table, id)
    if re == 1:
        re = "成功删除！刷新页面后此条消失"
    return re


@app.route('/sel', methods=['GET'])
def sel():
    table = request.args.get("table")
    id = request.args.get("id")
    us = opt("user.db")
    if table == "clss":
        table="class"
    elif table == "name":
        table = "name"
    elif table == "atrr":
        table = "attr"
    elif table == "info":
        table = "infoe"
    re = us.select_c(table, id)

    return re

@app.route('/updateu', methods=['POST'])
def updateu():
    pid = request.form['pid']
    value = request.form['v']
    token = request.form['token']
    pid = int(pid)
    myuid = int(session.get('uid'))
    us = opt("user.db")
    if token == "0":
        re = us.updata_u(pid, value, myuid)
        return str("自己")
    row = us.select_w("plyer","id=%d" % pid)
    if row:
        cid = row[0][7]
        tokenl = us.select_w("groupp", "value='%s'" % token)
        # 确认这个卡片的人物已经加入这个group
        group = us.select_w("groupp", "value2='%s' and link_kind=5 and link_id=%d" % (str(cid),int(tokenl[0][5])))
        if not group:
            return str("group不对 你的group:%s 应该的group:%s icd:%s" % (group[0][5],tokenl[0][5],cid))
        if int(tokenl[0][3]) == myuid:
            re = us.updata_ua(pid, value)
            return str(1)
        else:
            re = us.updata_u(pid, value, myuid)
            return str("自己")
    else:
        return str("没有row")

@app.route('/addgame', methods=['POST'])
def addgame():
    # 卡组id 和 房间id
    cid = request.form['cid']
    gid = request.form['gid']

    uid = session.get('uid')
    us = opt("user.db")
    # value是text类型
    ifin = us.select_w("groupp", "value='%s' and value2='%s' and link_kind=5 and link_id=%d" % (str(uid),str(cid),int(gid)))
    if ifin:
        # 卡组在这个group的id
        inid = ifin[0][0]
        us.delet("groupp",inid)
    else:
        us.add_r(72,uid,cid,5,int(gid))
    return str(1)

@app.route('/delgame', methods=['POST'])
def delgame():
    # 卡组id 和 房间id
    cid = request.form['cid']
    gid = request.form['gid']
    uid = request.form['uid']
    token = request.form['token']
    us = opt("user.db")
    if token == "0":
        myuid = session.get('uid')
        us.delet_w("groupp","aid=72 and value='%s' and value2='%s' and link_kind=5 and link_id=%d " % (myuid, cid,int(gid)))
        return str(1)
    check = checktoken(token)
    if check == 1:
        # value是text类型
        ifin = us.select_w("groupp", "value='%s' and value2='%s' and link_kind=5 and link_id=%d" % (str(uid),str(cid),int(gid)))
        if ifin:
            # 卡组在这个group的id
            inid = ifin[0][0]
            us.delet("groupp",inid)
        return str(1)
    else:
        return str(0)


@app.route('/addu', methods=['POST'])
def addu():
    # table = request.form['table']
    # id = request.form['id']
    kind = request.form['kind']
    nid = request.form['nid']
    aid = request.form['aid']
    value = request.form['v']
    cid = request.form['cid']
    uid = session.get('uid')
    # id = int(id)
    re = add_user(kind, uid, nid, aid, value, cid)
    return str(re)


@app.route('/addu3', methods=['POST'])
def addu3():
    arry = request.form['ary']
    arry_list = json.loads(arry)
    cid = request.form['cid']
    myuid = session.get('uid')
    setus = opt("user.db")
    se = po(setus, myuid)
    se.setting_add(arry_list,cid)
    return jsonify(arry)

@app.route('/addu2', methods=['POST'])
def addu2():
    # table = request.form['table']
    # id = request.form['id']
    kind = request.form['kind']
    nid = request.form['nid']
    aid = request.form['aid']
    uid = request.form['uid']
    value = request.form['v']
    cid = request.form['cid']
    # id = int(id)
    if session.get('limit') == 1:
        pass
    elif session.get('limit') == 3:
        pass
    else:
        return render_template('error.html', message="权限错误")
    re = add_user(kind, uid, nid, aid, value, cid)
    return str(re)

# 添加用户信息
def add_user(kind, uid, nid, aid, value, cid):
    kind = int(kind)
    nid = int(nid)
    uid = int(uid)
    aid = int(aid)
    value = str(value)
    cid = int(cid)

    us = opt("user.db")
    if kind == 1:
        res = us.select_w("plyer", "uid=%d and nid=%d and kind=%d and c_id=%d" % (uid, nid, kind, cid))
        # res = us.select_n(kind, nid)
        if res:
            # 姓名和卡组名称保持相同
            if nid == 1:
                us.updata_u(cid, value)

            #如果职业被修改把技能也重置了
            if nid == 9:
                us.delet_w("plyer", "kind=3 and uid=%d and c_kind=1 and c_id=%d" % (uid, cid))
                us.delet_w("plyer", "kind=4 and uid=%d and c_kind=1 and c_id=%d" % (uid, cid))

            id = int(res[0][0])
            re = us.updata_u(id, value)
            return re
        else:
            re = us.add_u(kind, 0, nid, aid, value, 1, cid)
    elif kind == 3:
        res = us.select_w("plyer", "uid=%d and nid=%d and aid=%d and kind=%d and c_kind=1 and c_id=%d" % (uid, nid, aid, kind, cid))
        # res = us.select_n(kind, nid, aid)
        if res:
            id = int(res[0][0])
            re = us.updata_u(id, value)
            return re
        else:
            re = us.add_u(kind, 0, nid, aid, value, 1, cid)
    elif kind == 4:
        re = us.add_u(kind, 0, nid, 0, 0, 1, cid)
    return re

# 添加房间
@app.route('/add_room', methods=['POST'])
def add_room():
    us = opt("user.db")
    method = request.form['method']
    aid    = request.form['aid']
    value1 = request.form['value1']
    value2 = request.form['value2']
    if value2 == "myid":
        value2 = int(session.get('uid'))
    aid = int(aid)
    if method == "create":
        value2 = str(session.get('uid'))
        lastid = us.add_r(aid,value1,value2,0,0)
        us.add_u(1,int(value2),58,0,value1,1,int(lastid))
        lastid = str(lastid)
        return lastid
    elif method == "addin_room":
        link_kind = request.form['lk']
        link_id = request.form['li']
        link_kind = int(link_kind)
        link_id = int(link_id)
        us.add_r(aid, value1, value2, link_kind, link_id)
        return str(1)
    # 给建立房间的用户一个安全密码
    elif method == "set_token":
        link_kind = request.form['lk']
        link_id = request.form['li']
        link_kind = int(link_kind)
        link_id = int(link_id)
        rand = random.randint(1000, 9999)
        rand = str(rand)
        hl = hashlib.md5()
        hl.update(rand.encode(encoding='utf-8'))
        token = hl.hexdigest()
        value2 = session.get('uid')
        us.add_r(aid, token, value2, link_kind, link_id)
        return str(1)
    else:
        link_kind = request.form['lk']
        link_id   = request.form['li']
        link_kind = int(link_kind)
        link_id = int(link_id)
        res = us.select_w("groupp", "aid=%d and link_kind=%d and link_id=%d" % (aid, link_kind, link_id))
        if res:
            id = int(res[0][0])
            us.updata_r(id,value1,value2)
            return str(1)
        us.add_r(aid,value1,value2,link_kind,link_id)
        return str(1)

#添加地图
@app.route('/add_map', methods=['POST'])
def add_map():
    gid = request.form['gid']
    url = request.form['url']
    token = request.form['token']
    # myuid = session.get('uid')
    us = opt("user.db")
    check = checktoken(token)
    if check == 0:
        return "token错误"
    else:
        us.add_r(83,url,"0",5,int(gid))
        return str(1)

#删除地图
@app.route('/del_map', methods=['POST'])
def del_map():
    gid = request.form['gid']
    url = request.form['url']
    token = request.form['token']
    gid = int(gid)
    # myuid = session.get('uid')
    us = opt("user.db")
    check = checktoken(token)
    if check == 0:
        return "token错误"
    else:
        us.delet_w("groupp", "aid=83 and value='%s' and link_kind=5 and link_id=%d" % (url, gid))
        us.updata_w("groupp", "value=0", "aid=84 and value='%s' and link_kind=5 and link_id=%d" % (url, gid))
        path = os.getcwd()+url
        os.remove(path)
        return str(1)

# 想用户显示图片
@app.route('/showh_map', methods=['POST'])
def showh_map():
    gid = request.form['gid']
    url = request.form['url']
    token = request.form['token']
    gid = int(gid)
    # myuid = session.get('uid')
    us = opt("user.db")
    check = checktoken(token)
    if check == 0:
        return "token错误"
    else:
        us.updata_w("groupp", "value='%s'" % url, "aid=84 and link_kind=5 and link_id=%d" % gid)
        return str(1)

# 显示图片列表
@app.route('/show_map', methods=['POST'])
def show_map():
    out = 0
    gid = request.form['gid']
    token = request.form['token']
    gid = int(gid)
    us = opt("user.db")
    check = checktoken(token)
    if check == 0:
        return jsonify(out)
    else:
        maps = us.select_w("groupp", "aid=83 and link_kind=5 and link_id=%d" % (gid))
        if not maps:
            out = 0
        else:
            out = maps
        return jsonify(out)

#添加物品
@app.route('/add_obj', methods=['POST'])
def add_obj():
    obj_id = request.form['obj_id']
    uid = request.form['uid']
    cid = request.form['cid']

    us = opt("user.db")
    us.add_u(4,int(uid),int(obj_id),0,0,1,int(cid))
    return str(1)

#添加自定义物品
@app.route('/add_objc', methods=['POST'])
def add_objc():
    name = request.form['name']
    use_skill = request.form['use_skill']
    zhong = request.form['zhong']
    damage = request.form['damage']
    desc = request.form['desc']
    uid = request.form['uid']
    cid = request.form['cid']
    if not name:
        return str(0)
    if not use_skill:
        use_skill=0
    if not zhong:
        zhong=0
    if not damage:
        damage=0
    if not desc:
        desc=0
    uid = int(uid)
    us = opt("user.db")
    lastid = us.addla("custom", "4, %d, %d, '%s', '%s', 0" % (uid,85,name,"0"))
    us.add("custom", "4, %d, %d, '%s', '%s',%d" % (uid, 90, name, "0", int(lastid)))
    us.add("custom", "4, %d, %d, '%s', '%s',%d" % (uid, 86, use_skill, zhong, int(lastid)))
    us.add("custom", "4, %d, %d, '%s', '%s',%d" % (uid, 87, damage, "0", int(lastid)))
    us.add("custom", "4, %d, %d, '%s', '%s',%d" % (uid, 88, desc, "0", int(lastid)))
    us.add_u(9,uid,79,0,lastid,1,int(cid))
    return str(1)

#捡起物品
@app.route('/add_objt', methods=['POST'])
def add_objt():
    kkind = request.form['kkind']
    kind = request.form['kind']
    pname = request.form['pname']
    pid = request.form['pid']
    uid = request.form['uid']
    cid = request.form['cid']
    toid = request.form['toid']
    obj = request.form['obj']
    pid = int(pid)
    kind = int(kind)
    uid = int(uid)
    cid = int(cid)
    toid = int(toid)
    kkind = int(kkind)
    us = opt("user.db")
    # 0预设物品 1自定义物品
    if kind == 0:
        us.add("plyer", "%d, %d, %d, %d,'%s', %d, %d" % (uid, 4, pid, 0, '0', 1, cid))
    elif kind == 1:
        us.add("plyer", "%d, %d, %d, %d,'%s', %d, %d" % (uid, 9, 79, 0, pid, 1, cid))
    msg = pname+"捡起了 "+obj
    re = send_msg(kkind,uid,cid,toid,msg)
    return str(re)


#获取自定义物品
@app.route('/get_objc', methods=['GET'])
def get_objc():
    ccid = request.args.get("id")
    us = opt("user.db")
    objc_list = us.select_w("custom","link_id=%d" % int(ccid))
    return jsonify(objc_list)

# 验证token合法性
def checktoken(token):
    myuid = session.get('uid')
    us = opt("user.db")
    toch = us.select_w("groupp", "value='%s'" % (token))
    cuid = toch[0][3]
    if int(cuid) == int(myuid):
        return 1
    else:
        return 0

# 删除房间
@app.route('/del_room', methods=['POST'])
def del_room():
    id = request.form['id']
    id = int(id)
    uid = session.get('uid')
    uid = int(uid)
    us = opt("user.db")
    re = us.select_w("groupp", "id=%d" % id)
    guid = re[0][3]
    if uid == int(guid):
        us.delet_w("groupp", "id=%d and value2='%s'" % (id, uid))
        us.delet_w("groupp", "link_kind=5 and link_id=%d" % (id))
        us.delet_w("msg", "kindid=5 and toid=%d" % id)
    else:
        return str("出现迷之错误")
    return str(1)

# 删除房间内对话
@app.route('/del_room_msg', methods=['POST'])
def del_room_msg():
    id = request.form['id']
    id = int(id)
    uid = session.get('uid')
    uid = int(uid)
    us = opt("user.db")
    re = us.select_w("groupp", "id=%d" % id)
    guid = re[0][3]
    if uid == int(guid):
        us.updata_w("msg","kindid=0","kindid=5 and toid=%d" % id)
        # us.delet_w("msg", "kindid=5 and toid=%d" % id)
    else:
        return str("出现迷之错误")
    return str(1)

# 删除物品
@app.route('/delobj', methods=['POST'])
def delobj():
    pid = request.form['pid']
    pid = int(pid)
    kind = request.form['kind']
    token = request.form['token']
    myuid = session.get('uid')
    myuid = int(myuid)
    us = opt("user.db")
    if token == "0":
        if kind == "custom":
            # us.delet_w("custom", "id=%d and uid=%d" % (pid, myuid))
            # us.delet_w("custom", "link_id=%d and uid=%d" % (pid, myuid))
            us.delet_w("plyer", "nid=79 and value='%s' and uid=%d" % (str(pid), myuid))
        else:
            us.delet_w("plyer", "id=%d and uid=%d" % (pid, myuid))
        return str(1)
    check = checktoken(token)
    if check == 1:
        if kind == "custom":
            us.delet_w("plyer", "nid=79 and value='%s'" % (str(pid)))
        else:
            us.delet_w("plyer", "id=%d" % (pid))
        return str(1)
    else:
        return str(0)



@app.route('/selu', methods=['GET'])
def selu():
    id = request.args.get("id")
    # table = request.form['table']
    # id = request.form['id']
    us = opt("user.db")
    re = us.select_c("", id)

    return re

@app.route('/deleme', methods=['GET'])
def deleme():
    us = opt("user.db")
    re = us.delet_me()

    return str(re)

@app.route('/sendmsg', methods=['POST'])
def sendmsg():
    kind = int(request.form['kind'])
    toid = int(request.form['toid'])
    fromcid = int(request.form['fromcid'])
    toid_p = int(request.form['toid_p'])

    msg = request.form['msg']
    myuid = int(session.get('uid'))
    msg = msg.replace("'", "\"")
    re = send_msg(kind, myuid, fromcid, toid, msg,toid_p)
    return str(re)

#获取要显示的图片
@app.route('/get_showimg', methods=['GET'])
def get_showimg():
    gid = int(request.args.get("gid"))
    us = opt("user.db")
    re = us.select_w("groupp", "aid=84 and link_kind=5 and link_id=%d" % (gid))
    if re:
        show_img = re[0][2]
    else:
        show_img = 0
    return str(show_img)


# 获取聊天室最后一个id
@app.route('/getmsg_lastid', methods=['GET'])
def getmsg_lastid():
    gid = int(request.args.get("gid"))
    us = opt("user.db")
    re = us.select_w("msg", "kindid=5 and toid=%d order by id desc limit 1" % (gid))
    if re:
        lastid = re[0][0]
    else:
        lastid = 0
    return str(lastid)

# 获取聊天信息
@app.route('/getmsg_group', methods=['GET'])
def getmsg_group():
    rr = []
    out = []
    gid = int(request.args.get("gid"))
    if gid:
        gid = int(gid)
    else:
        return jsonify(0)
    us = opt("user.db")
    myuid = int(session.get('uid'))
    re = us.select_w("msg","(kindid=5 or (kindid=2 and (toid_p=%d or fromid=%d))) and toid=%d order by id desc limit 0,100" % (myuid, myuid, gid))
    for r in re:
        uid = r[2]
        fromcid = r[3]
        userinfo = us.select_w("plyer","kind=1 and c_kind=1 and c_id=%d" % fromcid)
        rr.append(uid)
        if userinfo:
            for info in userinfo:
                if info[3] == 1:
                    name = info[5]
                    rr.append(name)
                # 头像地址
                elif info[3] == 75:
                    pic = info[5]
                    rr.append(pic)
        else:
            rr.append("已删")
            rr.append("0")
        rr.append(r)
        out.append(rr)
        rr = []
    return jsonify(out)

@app.route('/getplyer', methods=['GET'])
def getplyer():
    uid = int(request.args.get("uid"))
    us = opt("user.db")
    re = us.select_w("plyer","kind=1 and nid=1 and uid=%d" % (uid))
    return jsonify(re)

# 获取模板职业的信息
@app.route('/gettemplates', methods=['GET'])
def gettemplates():
    outo = []
    out  = []
    method = request.args.get("method")
    us = opt("user.db")
    if method == "list":
        # nid=64是卡组,先取卡组
        list = us.select_w("plyer", "kind=1 and nid=64 and uid=%d" % (22))
        for ll in list:
            pid = ll[0]
            workname = ll[5]
            jobt = us.select_w("plyer", "kind=1 and nid=9 and uid=%d and c_kind=1 and c_id=%d" % (22, pid))
            if not jobt:
                continue
            jobid = jobt[0][5]
            jobname = us.select_w("name","id=%d" % int(jobid))
            jobname = jobname[0][2]
            outo.append(pid)
            outo.append(workname)
            outo.append(jobname)
            out.append(outo)
            outo = []
    return jsonify(out)


# 获取职业的信息
@app.route('/getwinfo', methods=['GET'])
def getwinfo():
    workatr = []
    workopt = []
    worksx = []
    out = []
    nid = int(request.args.get("nid"))

    # 0 职业技能id + 名称
    # 1 职业特殊
    # 2 职业属性id + 次数 + 名称
    # 3 信誉
    us = opt("user.db")

    re = us.select_w("infoe","nid=%d" % (nid))
    for r in re:
        if r[2] == 12:
            nnid = r[3]
            name = us.select_w("name", "id=%d" % (nnid))
            workatr.append([nnid,name[0][2]])
        elif r[2] == 76:
            teshu = r[4]
            workopt.append(teshu)
        elif r[2] == 4:
            shuxing  = r[3]
            shuxingt = r[4]
            name = us.select_w("attr", "id=%d" % (shuxing))
            worksx.append([shuxing,shuxingt,name[0][2]])
        elif r[2] == 44:
            xingyu = r[4]
    skilllist = us.select_w("name","kind=3")

    out.append(workatr)
    out.append(workopt)
    out.append(worksx)
    out.append(xingyu)
    out.append(skilllist)
    return jsonify(out)

# 上传信息
@app.route('/uploadmap', methods=['GET', 'POST'])
def upload_map():
    #若更改函数名 在chat1里搜索函数名 替换
    if request.method == 'POST':
        for f in request.files.getlist('file'):
            changedFilename = "map_"+change_filename(f.filename)
            imgurl= os.path.join(app.config['UPLOADED_PATH'], changedFilename)
            imgur = '/static/upload/' + changedFilename
            f.save(imgurl)
    return imgur

@app.route('/uploadavatar', methods=['GET', 'POST'])
def upload_avatar_img():
    #若更改函数名 在chat1里搜索函数名 替换
    if request.method == 'POST':
        for f in request.files.getlist('file'):
            changedFilename = "avatar_"+change_filename(f.filename)
            imgurl= os.path.join(app.config['UPLOADED_PATH'], changedFilename)
            imgur = '/static/upload/'+changedFilename
            f.save(imgurl)
    return imgur

@app.route('/uploadroompic', methods=['GET', 'POST'])
def uploadroompic():
    #若更改函数名 在chat1里搜索函数名 替换
    if request.method == 'POST':
        for f in request.files.getlist('file'):
            changedFilename = "roompic_"+change_filename(f.filename)
            imgurl= os.path.join(app.config['UPLOADED_PATH'], changedFilename)
            imgur = '/static/upload/'+changedFilename
            f.save(imgurl)
    return imgur

def checku():
    uid = session.get('uid')
    if not uid:
        return redirect(url_for('index'))

app.config['UPLOADED_PATH'] = os.getcwd() + '/static/upload'
# need 上传路径需要更改
def change_filename(filename):
    rannum = random.randint(10000,99999)
    timenum = int(time.time())
    fileinfo = os.path.splitext(filename)
    filename = str(timenum)+"_"+str(rannum)+fileinfo[-1]
    return filename


@app.route('/toul', methods=['POST'])
def toul():
    kind = int(request.form['kind'])
    toid = int(request.form['toid'])
    toid_p = int(request.form['toid_p'])
    fromcid = int(request.form['fromcid'])

    nnid = int(request.form['nnid'])
    shuxing = int(request.form['sx'])
    jineng = int(request.form['jn'])
    diffi = int(request.form['diffi'])
    ppname = request.form['ppname']

    us = opt("user.db")
    nnamei = us.select_w("name","kind=10 and id=%d" % nnid)
    nname = nnamei[0][2]
    # 产生3个随机数
    ro1 = op.roll(100)
    ro1 = op.reset_num(ro1)
    ro2 = op.roll(100)
    ro2 = op.reset_num(ro2)
    ro3 = op.roll(100)
    ro3 = op.reset_num(ro3)

    msg = ppname+" "+nname + "检定:"
    ms = set_secces(ro1, shuxing)
    inf1 = ms[0]
    seccnum1 = ms[1]-7
    ms = set_secces(ro2, jineng)
    inf2 = ms[0]
    seccnum2 = ms[1]-7
    if diffi == 0:
        ro3 = 100
        inf3 = "大失败!100"
        seccnum3 = -7
    elif diffi == 100:
        ro3 = 1
        seccnum3 = 7
        inf3 = "大成功!1"
    else:
        ms = set_secces(ro3, diffi)
        inf3 = ms[0]
        seccnum3 = ms[1] - 7
    sse = seccnum1+seccnum2
    mmsg = "%s + %s | %s" % (inf1, inf2, inf3)
    # mmsg = "%d/%d(%d)+%d/%d(%d) | %d/%d(%d)" % (ro1,shuxing,seccnum1,ro2,jineng,seccnum2,ro3,diffi,seccnum3)
    if sse > seccnum3:
        msg = msg+"成功!"
    else:
        msg = msg + "失败!"
    msg = "<h5 title=\""+mmsg+"\">"+msg+"</h5>"
    myuid = int(session.get('uid'))
    re = send_msg(kind, myuid, fromcid, toid, msg, toid_p)
    return msg



@app.route('/tou', methods=['POST'])
def tou():
    kind = int(request.form['kind'])
    toid = int(request.form['toid'])
    toid_p = int(request.form['toid_p'])
    fromcid = int(request.form['fromcid'])
    value = request.form['value']
    obj = request.form['obj']
    max = request.form['max']

    value = int(value)
    max = int(max)
    ro = op.roll(max)
    ro = op.reset_num(ro)
    if value == 0:
        msg = obj + "检定:" + str(ro)
    else:
        if obj == "0":
            obj = "特殊"
        msg = obj + "检定:"
        ms = set_secces(ro, value, msg)
        msg = ms[0]
    myuid = int(session.get('uid'))
    re = send_msg(kind,myuid,fromcid,toid, msg,toid_p)
    return str(re)

# 把伤害投出来
@app.route('/tou_demage', methods=['POST'])
def tou_demage():
    kind = int(request.form['kind'])
    toid = int(request.form['toid'])
    fromcid = int(request.form['fromcid'])
    damage = request.form['damage']
    db = request.form['db']
    obj = request.form['obj']
    skillplu  = request.form['skillplu']
    skillplu2 = request.form['skillplu2']
    myuid = int(session.get('uid'))

    if obj == "0":
        obj = "特殊"
    dama = op.roll_str2(damage,db)
    cc = 0
    for a in dama:
        cc = cc+int(a)
    title = "伤害计算:"+damage
    dmsg = "<a title=\"%s\">%s伤害检定:%s</a>" % (title, obj, str(cc))
    re = send_msg(kind, myuid, fromcid, toid, dmsg)
    return str(re)

# 把伤害投出来
@app.route('/tou_demage2', methods=['POST'])
def tou_demage2():
    kind = int(request.form['kind'])
    toid = int(request.form['toid'])
    toid_p = int(request.form['toid_p'])
    fromcid = int(request.form['fromcid'])
    damage = request.form['damage']
    db = request.form['db']
    obj = request.form['obj']
    skillname = request.form['skillname']
    pname = request.form['pname']
    zhong = request.form['zhong']
    desctip = request.form['desc']
    myuid = int(session.get('uid'))

    zhong = int(zhong)
    msg = pname + " 使用" + obj + "<br />"
    if zhong != 0:
        ro = op.roll(100)
        ro = op.reset_num(ro)
        if skillname == "0" or skillname == "自定义":
            skillname = "特殊"
        msg = msg + skillname + "检定:"
        ms = set_secces(ro, zhong, msg)
        msg = ms[0]+"<br />"
        seccnum = ms[1]
    else:
        seccnum = 3

    if seccnum >= 12:
        ifbomb = "max"
    elif seccnum >= 8 and seccnum < 12:
        ifbomb = "normal"
    elif seccnum < 7:
        ifbomb = 0
    dama = op.roll_str2(damage,db,ifbomb)
    cc = 0
    if dama != 0:
        for a in dama:
            cc = cc+int(a)
    title = "伤害计算:"+str(damage)+"| DB:"+str(db)
    if damage != "0":
        dmsg = "<a title=\"%s\">伤害检定:%s</a>" % (title, str(cc))
        smsg = msg + dmsg
    else:
        smsg = msg

    if ifbomb != 0 and desctip != "0":
        smsg = smsg + "<p>效果："+desctip+"</p>"
    re = send_msg(kind, myuid, fromcid, toid, smsg,toid_p)
    return str(re)

# 疯狂检定
@app.route('/tou_creacy', methods=['POST'])
def tou_creacy():
    kind = int(request.form['kind'])
    toid = int(request.form['toid'])
    fromcid = int(request.form['fromcid'])
    myuid = int(session.get('uid'))
    # 获取1d10
    radnum = op.roll(10)
    # radnum = radnum
    us = opt("user.db")
    cr_names = us.select_w("name", "kind=8 order by id asc")
    # 找到第一个疯狂id
    firstid = cr_names[0][0]
    # 加上随机数
    getid = radnum + firstid
    re = 0
    ii = 1
    for cr in cr_names:
        if ii >= radnum:
            creacy_name = cr[2]
            creacy_desc = cr[3]
            msg = "<p class=\"font-weight-bold\">%s %s</p>%s" % (creacy_name, radnum, creacy_desc)
            re = send_msg(kind, myuid, fromcid, toid, msg)
            break
        ii += 1

    return str(re)



# 检测成功程度 c参数,value最大值,msg+"成功"+数字
def set_secces(c,value,msg=""):
    out = []
    v2 = int(value / 2)
    v3 = int(value / 5)
    if c > value:
        if c > 95:
            msg = msg+"大失败!"+str(c)
            re =0
        else:
            msg = msg+"失败!"+str(c)
            re = 6
    elif c <= value and c > v2:
        msg = msg+"成功!"+str(c)
        re = 8
    elif c == 1:
        msg = msg+"大成功!"+str(c)
        re = 14
    elif c <= v2 and c > v3:
        msg = msg+"困难成功!"+str(c)
        re = 10
    elif c <= v3:
        msg = msg+"极限成功!"+str(c)
        re = 12
    out.append(msg)
    out.append(re)
    return out

def send_msg(kind,myuid,fromcid,toid,msg,toid_p=0):
    us = opt("user.db")
    myuid = int(myuid)
    t = int(time.time())
    plus = "%d, %d, %d, %d, '%s', '%s', %d " % (kind, myuid, fromcid, toid, t, msg,toid_p)
    re = us.add("msg", plus)
    return re