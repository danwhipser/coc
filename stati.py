import sqlite3 as lite
from flask import session
import re


# 统计类
class statics:
    # 初始化
    def __init__(self,setus):
        self.out_all = []
        self.setus = setus

    def get_jianding(self):
        us = self.setus
        tit = "检定"
        rr = us.select_w("msg", "msg like '%"+tit+"%'")
        # out = []
        see = [["特殊检定",1]]
        for r in rr:
            content = r[6]
            findword = u"([\u4e00-\u9fa5]{2}检定+)"
            pattern = re.compile(findword)
            results = pattern.findall(content)
            if results:
                ree = results[0]
                # 寻找数组中是否有这个检定
                i = 0
                for se in see:
                    # 如果有则计数器加1
                    if ree == se[0]:
                        se[1] = se[1]+1
                        i = 1
                        continue
                if i == 0:
                    new_se = [ree,1]
                    see.append(new_se)
        out = sorted(see,key=lambda x:x[1],reverse=True)
        return out

