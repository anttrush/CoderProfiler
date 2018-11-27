inpithead = ['id', 'login', 'Best Practices', 'Code Style','Design', 'Documentation','Error Prone', 'Multithreading','Performance', 'Security','java.lang', 'java.util', 'java.rmi', 'java.net', 'java.beans', 'java.nio', 'java.io', 'java.sql', 'java.security', 'java.math', 'java.text', 'java.awt', 'others','cLOC','effe']
outputhead = ['id', 'login', 'Code Style','Design', 'Documentation','Error Prone', 'Performance', 'Multithreading', 'Security', 'others', 'text', 'graph', 'math', 'net', 'IO', 'database', 'security', 'others','effe' ,'cLOC']
import pymysql
import math
db = pymysql.connect(host="10.1.1.61", port=36810, user="visitor", passwd="visitor", db="ghtorrent_restore")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print ("Database version : %s " % data)

class Coder:
    def __init__(self, datalist):
        self.id = datalist[0]
        self.login = datalist[1]
        self.Ascore = [float(datalist[3]), float(datalist[4]), float(datalist[5]), float(datalist[6]), float(datalist[8]), float(datalist[7]), float(datalist[9]), float(datalist[2])]
        self.Pscore = [float(datalist[20]), float(datalist[21]), float(datalist[19]), float(datalist[13])+float(datalist[14]), float(datalist[15])+float(datalist[16]), float(datalist[17]), float(datalist[18]), float(datalist[10])+float(datalist[11])+float(datalist[12])+float(datalist[22])]
        for i in range(8):
            self.Pscore[i] = math.log(self.Pscore[i]+1, 10)
        self.effe = float(datalist[24])
        self.cLOC = int(datalist[23])
        self.followerN = 0

followerlist = {}
with open("followers.txt") as fn:
    for line in fn.readlines():
        if not line or line == '':
            break
        data = line.strip().split()
        followerlist[data[0]] = data[2]

coderlist = []
with open("CoderProfileResults1127.csv", 'r') as f:
    for line in f.readlines():
        if not line or line == '':
            break
        data = line.strip().split(',')
        coder = Coder(data)
        coderlist.append(coder)
        if coder.id in followerlist.keys():
            coder.followerN = followerlist[coder.id]
        else:
            sql = "SELECT count(*) FROM ghtorrent_restore.followers where user_id=" + coder.id +";"
            cursor.execute(sql)
            data = cursor.fetchall()
            coder.followerN = str(data[0][0])


Mincoder = Coder(['inf'] * 23+['1000', 'inf'])
Maxcoder = Coder(['0'] * 25)
total = 0
for coder in coderlist:
    total += 1
    for i in range(8):
        Mincoder.Ascore[i] = min(Mincoder.Ascore[i], coder.Ascore[i])
        Mincoder.Pscore[i] = min(Mincoder.Pscore[i], coder.Pscore[i])
        Maxcoder.Ascore[i] = max(Maxcoder.Ascore[i], coder.Ascore[i])
        Maxcoder.Pscore[i] = max(Maxcoder.Pscore[i], coder.Pscore[i])
    Mincoder.effe = min(Mincoder.effe, coder.effe)
    Maxcoder.effe = max(Maxcoder.effe, coder.effe)
for coder in coderlist:
    for i in range(8):
        if coder.Ascore[i] != 0:
            coder.Ascore[i] = 30 + 70 * (coder.Ascore[i] - Mincoder.Ascore[i]) / (Maxcoder.Ascore[i] - Mincoder.Ascore[i])
        else:
            coder.Ascore[i] = 72
        coder.Pscore[i] = 0+ 100 * (coder.Pscore[i] - Mincoder.Pscore[i]) / (Maxcoder.Pscore[i] - Mincoder.Pscore[i])
    coder.effe = 30 + 70 * (coder.effe - Mincoder.effe) / (Maxcoder.effe - Mincoder.effe)



with open('processeddata.csv', 'w') as fout:
    for coder in coderlist:
        output = coder.id + ',' + coder.login + ','
        for s in coder.Ascore:
            output += str(s) + ','
        for s in coder.Pscore:
            output += str(s) + ','
        output += str(coder.effe) + ','
        output += str(coder.cLOC) + ','
        output += coder.followerN + '\n'
        fout.write(output)
