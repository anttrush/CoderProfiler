
import os
import csv
import math
import pymysql
import os
import datetime

db = pymysql.connect("192.168.3.123", "ght", "ght", "github")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print ("Database version : %s " % data)

sql = "select created_at from commits where id=900702"
cursor.execute(sql)
res = cursor.fetchall()
data1 = datetime.datetime(2012,7,22)
delta1 = res[0][0] - data1
print(delta1)
print(delta1.days+delta1.seconds/(24*60*60))

res = "asdf<relative-time datetime='2013-02-19'"
posi0 = res.find("<relative-time datetime=")
c = datetime.datetime.strptime(res[posi0 + 25: posi0 + 35], "%Y-%m-%d")
print(c)