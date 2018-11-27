# proj list
import pymysql
pFile = "D:\code\python\CoderProfiler\others\projtmp2.txt"
PROJLISTFILE = r'projIdList.txt'
db = pymysql.connect(host="10.1.1.61", port=36810, user="visitor", passwd="visitor", db="ghtorrent_restore")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()

with open(pFile) as f:
    for i in range(10):
        url = ''
        for j in range(100):
            url += '"' + f.readline().strip() + '",'
        print('%d\turl ready'%(i))
        cursor.execute('SELECT id,name FROM ghtorrent_restore.projects where url in (' + url[:-1] +');' )
        datas = cursor.fetchall()
        with open(PROJLISTFILE,'a') as resf:
            for data in datas:
                resf.write(str(data[0]) + ',' + data[1] + '\n')
        print('%d\tfile write ready'%(i))
