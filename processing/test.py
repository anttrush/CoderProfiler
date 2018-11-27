import os
import datetime

res0 = os.popen(r"cd /d D:/CodeRepertory/Java/AboutLibraries/ && git reset --hard 9c2f5649155a056e9d3e0c13a3e8d43c0dc166dc").read()
res1 = os.popen(r"cd /d D:/CodeRepertory/Java/AboutLibraries/ && git diff %s %s --numstat" %("9c2f5649155a056e9d3e0c13a3e8d43c0dc166dc", "ff47b69292f6bc06439a8cd8d4a04a6e1e8d4144")).read()
print(res1)
workline = 0
for res in res1.split('\n'):
    if res and res != "":
        LOCs = res.split()
        workline += int(LOCs[0]) + int(LOCs[1])
monthdict = {'Apr':'1', 'Jun':'6'}
print(workline)

res2 = os.popen(r"cd /d D:/CodeRepertory/Java/AboutLibraries/ && git show 9c2f5649155a056e9d3e0c13a3e8d43c0dc166dc").read()
res3 = os.popen(r"cd /d D:/CodeRepertory/Java/AboutLibraries/ && git show ff47b69292f6bc06439a8cd8d4a04a6e1e8d4144").read()

pos1 = res2.find("Date")
pos2 = res2.find("\n", pos1+1)
time1 = res2[pos1+12:pos2-6]
time1 = monthdict[time1[:3]] + time1[3:]
dtime1 = datetime.datetime.strptime(time1, "%m %d %H:%M:%S %Y")

pos1 = res3.find("Date")
pos2 = res3.find("\n", pos1+1)
time2 = res3[pos1+12:pos2-6]
time2 = monthdict[time2[:3]] + time2[3:]
dtime2 = datetime.datetime.strptime(time2, "%m %d %H:%M:%S %Y")

worktime = (dtime1-dtime2).seconds
print(worktime)

print(workline/worktime)