import pymysql
import os

import logging
logging.basicConfig(filename='log1.log', level = logging.INFO,format = '%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db = pymysql.connect(host="10.1.1.61", port=36810, user="visitor", passwd="visitor", db="ghtorrent_restore")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print ("Database version : %s " % data)
ProjInfoFile = 'ProjIdNameStar.txt'
ProjWithC0idFile = 'ProjIdNameStarC0id.txt'
REPDIR = r'D:\CodeRepertory\Java'
gbkwrongfile = r'gbkwrong.txt'
fout = open(ProjWithC0idFile, 'w')

gbklist = []
with open(gbkwrongfile, 'r') as f:
    for line in f.readlines():
        gbklist.append(line.strip())

with open(ProjInfoFile, 'r') as f:
    index = 0
    for line in f.readlines():
        data = line.strip().split(',')
        idstr, name, starstr = data[0], data[1], data[2]
        if idstr in gbklist:
            continue
        sql = "SELECT id, sha FROM ghtorrent_restore.commits where project_id=" + idstr + " order by id desc limit 10;"
        cursor.execute(sql)
        sqlres = cursor.fetchall()
        flag = False
        for data in sqlres:
            C0id, sha = data[0], data[1]
            try:
                checkres = os.popen('cd /d ' + os.path.join(REPDIR, name) + '&& git log %s -1' % sha).read()
                if checkres:
                    fout.write(idstr + ',' + name + ',' + starstr + ',' + str(C0id) + '\n')
                    flag = True
                    break
            except:
                print("gbk wrong.")
                break
        if not flag:
            logging.info(idstr + ',' + name + ',' + starstr + ': \t failed.')
        else:
            logging.info(idstr + ':\t success!')
        print(str(index) + "\t: " + line.strip() + ' done.')
        index += 1
