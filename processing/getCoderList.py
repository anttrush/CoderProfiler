# coder list
import os
import requests
import pymysql
import json
db = pymysql.connect(host="10.1.1.61", port=36810, user="visitor", passwd="visitor", db="ghtorrent_restore")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print ("Database version : %s " % data)
CODERLISTFILE = r'coderlist.txt'

with open(r"D:\code\python\CoderProfiler\DumpCoders\CoderIdList.csv") as f:
    tiktok = 0
    loading = 0
    coderlisttmp = ""
    idstr = f.readline().strip()
    while idstr:
        coderlisttmp += idstr + ','
        tiktok += 1
        idstr = f.readline().strip()
        if tiktok == 100:
            print("loading: " + str(loading))
            sql = "select id, login from ghtorrent_restore.users where id in (" + coderlisttmp[:-1] + ");"
            cursor.execute(sql)
            datas = cursor.fetchall()
            with open(CODERLISTFILE, 'a') as resf:
                for data in datas:
                    id = data[0]
                    login = data[1]
                    resf.write(str(id) + "," + login + "\n")
            coderlisttmp = ""
            tiktok = 0
            print("loading down.")
            loading += 1
    sql = "select id, login from ghtorrent_restore.users where id in (" + coderlisttmp[:-1] + ");"
    cursor.execute(sql)
    datas = cursor.fetchall()
    with open(CODERLISTFILE, 'a') as resf:
        for data in datas:
            resf.write(str(data[0]) + "," + data[1] + "\n")



