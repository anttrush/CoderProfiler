import os
IdFile = "projIdList.txt"
StarFile = "projStarList1.txt"
OutFile = "ProjIdNameStar.txt"
REPDIR = r'D:\CodeRepertory\Java'

idf = open(IdFile, 'r')
starf = open(StarFile, 'r')
outf = open(OutFile, 'w')

starfdict = {} # {'name': star}
for line in starf.readlines():
    data = line.strip().split(',')
    name, starstr = data[0], data[1]
    starfdict[name] = starstr

for line in idf.readlines():
    data = line.strip().split(',')
    idstr, name = data[0], data[1]
    if name in starfdict and os.path.exists(os.path.join(REPDIR, name)):
        outf.write(idstr + ',' + name + ',' + starfdict[name] + '\n')

idf.close()
starf.close()
outf.close()