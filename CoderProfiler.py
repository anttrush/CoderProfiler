from MyClass import *
import os
import csv
import math
import logging
import json
import codecs
import datetime
logging.basicConfig(filename='CoderProfilerRunnig.log',level = logging.CRITICAL,format = '%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
PMDcommand = r'D:\pmd-bin-6.4.0\bin\pmd '
APIcommand = r'java -classpath ".;D:\lib\*" UserAbilityModel.Parser.JavaParser '
REPDIR = r'D:\CodeRepertory\Java'
RESDIR = r'D:\科研\CodeQualityAnalysis\CodeAnalysis\PMD'
RULEDIR = r'D:\pmd-bin-6.4.0\bin\myRuleSet.xml'
CACHEDIR = r'D:\科研\CodeQualityAnalysis\CodeAnalysis\PMD\cache'
CODERLISTFILE = r'coderlist.txt'
PROJLISTFILE = r'projectlist.txt'
OUTPUTFILE = r'CoderProfileResults.csv'
projidlist1 = [21344089,12277769,29292799,9725093,5014894,22061213,10425739,4876188,11474326,2981995,17302594]
#[21344089,12277769,29292799,10920410,18680297,9725093,284252,5014894,22061213,10425739,4876188,11474326,2981995,17302594]
# name=["butterknife", "elasticsearch"]
projstarList = [133,163,135,235,799,972,9500,19900,31700,21375,31978]
# [133,163,135,455,303,235,566,799,972,9500,19900,31700,21375,31978]
c0List1 = [1012551930,929376248,969315452,529675602,1050905502,1053843017,1053257881,1056743217,1057000345,1041855752,1056684266]
# [1012551930,929376248,969315452,280576115,492336230,529675602,71022576,1050905502,1053843017,1053257881,1056743217,1057000345,1041855752,1056684266]   sha=[]
devIds = [49049, 165882, 2632242, 4589144, 75625, 4307816, 10844712, 64600, 114374, 199939, 1891264, 896, 4998106, 7924529, 436017]
# [49049, 165882, 2632242, 4589144, 75625, 4307816, 10844712, 64600, 114374, 199939, 1891264, 896, 4998106, 7924529, 436017]
# login=[]
COMMITWINDOW = 100

def getProjList(source='local', filedir=None):
    projList = []
    if source == 'local':
        for id in projidlist1:
            projList.append(Project(id, projstarList.pop(0), c0List1.pop(0)))
            projList[-1].setProjDir(REPDIR)
    elif source=='file':
        if filedir:
            with open(filedir) as f:
                for line in f.readlines():
                    idstr, name, starstr, c0idstr = line.strip().split(',')
                    projList.append(Project(int(idstr), int(starstr), int(c0idstr)))
                    projList[-1].setProjDir(REPDIR)
        else:
            print('Error: getProjList() param wrong, when source=file but file=none. ')
    logging.info("load %d projects done." %(len(projList)))
    return projList

def getDevList(source='local', filedir=None):
    devList = []
    if source == 'local':
        for id in devIds:
            devList.append(Developer(id))
    elif source == 'mysql':
        devList = Developer.getAllTestld()
    elif source == 'file':
        if filedir:
            with open(filedir) as f:
                for line in  f.readlines():
                    idstr, login = line.strip().split(',')
                    devList.append(Developer(int(idstr), login=login))
        else:
            print('Error: getDevList() param wrong, when source=file but file=none. ')
    logging.info("load %d coders done." %(len(devList)))
    return devList

def preAnalysis(proj, ci):
    # let git reset to ci, use PMD to analysis and gen <ci.com_id>.csv file.
    # popen has sync problem -- use .read() to sync
    if not os.path.exists(os.path.join(RESDIR, str(ci.com_id)+'.csv')):
        try:
            os.popen('cd /d ' + proj.proj_dir + '&& git reset --hard %s' % ci.sha).read()
            # ./run.sh pmd -d /home/act/elasticsearch -f csv -R ./myRuleSet.xml -language java -r /home/act/pmdresults/elasticsearch.csv -cache /home/act/pmdresults/cache
            os.popen('cd /d ' + proj.proj_dir + '&& git reset --hard %s' % ci.sha).read()
            os.popen(PMDcommand + '-d ' + proj.proj_dir + ' -f csv -R ' + RULEDIR + ' -language java -r ' + RESDIR + '/' + str(ci.com_id) + '.csv -cache ' + CACHEDIR + str(proj.proj_id), 'r').read()
        except:
            logging.critical("pmdAnalysis broken: " + str(ci.com_id) + ci.sha)

def preAnalysisDiff(proj, ci, cj):
    # get Commit changing file by git diff --name-only cj ci // cj = ci.parent()
    # let git reset to cj, use PMD to analysis and gen <cj.com_id>.csv file.
    if not os.path.exists(os.path.join(RESDIR, str(cj.com_id)+'.csv')):
        try:
            os.popen('cd /d ' + proj.proj_dir + '&& git reset --hard %s' % cj.sha).read()
        except:
            logging.critical("pmdAnalysisDiff broken: " + str(cj.com_id) + cj.sha)
            return 'No diff'

        diffres = os.popen('cd /d ' + proj.proj_dir + '&& git diff --name-only %s %s' % (cj.sha, ci.sha)).read()
        with open(os.path.join(RESDIR, str(cj.com_id)+"ChangedFile.txt"), 'w') as f:
            fnames = []
            if diffres:
                diffFiles = diffres.strip().split('\n')
                for difffile in diffFiles:
                    fname = os.path.join(proj.proj_dir, difffile)
                    if fname.endswith(".java") and os.path.exists(fname) and os.path.isfile(fname):
                        fnames.append(fname)
            if fnames:
                f.write(fnames[0])
                for i in range(1,len(fnames)):
                    f.write(',' + os.path.join(proj.proj_dir, fnames[i]))
            else: # return no diff to help comList not append cj
                return 'No diff'
        # pmd -filelist
        # ./run.sh pmd -filelist /xxx/xxx -f csv -R ./myRuleSet.xml -language java -r /home/act/pmdresults/elasticsearch.csv -cache /home/act/pmdresults/cache
        # pmd -filelist D:\CodeRepertory\PJCY\butterknife\testfilelist.txt -f csv -R ./myRuleSet.xml -language java -r D:\科研\CodeQualityAnalysis\CodeAnalysis\PMD\butterknife.csv -cache D:\科研\CodeQualityAnalysis\CodeAnalysis\PMD\cache2981995
        os.popen(PMDcommand + '-filelist ' + os.path.join(RESDIR, str(cj.com_id)+"ChangedFile.txt") + ' -f csv -R ' + RULEDIR + ' -language java -r ' + RESDIR + '/' + str(cj.com_id) + '.csv -cache ' + CACHEDIR + str(proj.proj_id), 'r').read()

    # API analysis
    if not os.path.exists(os.path.join(RESDIR, str(cj.com_id)+"API.json")):
        apires = "{}"
        try:
            apires = os.popen(APIcommand + ' \"' + os.path.join(RESDIR, str(cj.com_id)+"ChangedFile.txt") + ' \" ').read()
            if apires == '':
                apires = '{}'
        except:
            logging.critical("APIanalysis broken: " + str(cj.com_id) + cj.sha)
            logging.critical(apires)
            apires = '{}'
        # print("APIres: " + apires)
        with open(os.path.join(RESDIR, str(cj.com_id)+"API.json"), 'w') as f:
            f.write(apires)

    # effe analysis
    if not os.path.exists(os.path.join(RESDIR, str(cj.com_id)+"effe.txt")):
        cLOC, ctime = 0, 0
        try:
            res1 = os.popen('cd /d ' + proj.proj_dir + '&& git diff --numstat %s %s' % (cj.sha, ci.sha)).read()
            workline = 0
            for res in res1.split('\n'):
                if res and res != "":
                    LOCs = res.split()
                    workline += int(LOCs[0]) + int(LOCs[1])

            monthdict = {'Jan':'1', 'Feb':'2', 'Mar':'3', 'Apr': '4', 'May':'5', 'Jun': '6', 'Jul':'7', 'Aug':'8', 'Sep':'9', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
            res2 = os.popen('cd /d ' + proj.proj_dir + '&& git show '+ ci.sha).read()
            res3 = os.popen('cd /d ' + proj.proj_dir + '&& git show '+ cj.sha).read()
            pos1 = res2.find("Date")
            pos2 = res2.find("\n", pos1 + 1)
            time1 = res2[pos1 + 12:pos2 - 6]
            time1 = monthdict[time1[:3]] + time1[3:]
            dtime1 = datetime.datetime.strptime(time1, "%m %d %H:%M:%S %Y")
            pos1 = res3.find("Date")
            pos2 = res3.find("\n", pos1 + 1)
            time2 = res3[pos1 + 12:pos2 - 6]
            time2 = monthdict[time2[:3]] + time2[3:]
            dtime2 = datetime.datetime.strptime(time2, "%m %d %H:%M:%S %Y")
            worktime = (dtime1 - dtime2).seconds

            cLOC, ctime = workline, worktime
        except:
            logging.critical("APIanalysis broken: " + str(cj.com_id) + cj.sha)
        with open(os.path.join(RESDIR, str(cj.com_id)+"effe.txt"), 'w') as f:
            f.write(str(cLOC) + "," + str(ctime))

    return 'Well Done'

def analysisCommit(proj, ci, viopreDict, c0sig=False):
    # analysis ci with PMD result file.
    # get ci.vioFileList
    with open(os.path.join(RESDIR, str(ci.com_id) + '.csv'), 'r') as f:
        res = csv.DictReader(f)
        filetmp = Myfile('', [], 0,1)
        for row in res:
            # "Problem","Package","File","Priority","Line","Description","Rule set","Rule"
            # one row one vio, build viotmp and update file
            if row['File'] != filetmp.fileFullName:
                ci.vioFileList.append(filetmp)
                # can't get LOC safely(gbk codec) and efficiently(file read)
                # can't get level
                # should do understand first to get import times(level) and LOC, store in a res.csv and load when proj analysis begin.
                filetmp = Myfile(row['File'], [], 100,1)
                # get LOC
                try:
                    with open(os.path.join(proj.proj_dir, filetmp.fileFullName), 'r') as f:
                        LOC = len(f.readline())
                        filetmp.LOC = LOC
                except Exception as e:
                    # gbk  error
                    filetmp.LOC = 0
            viotmp = Violation(row['Rule'], row['Rule set'], int(row['Priority']))
            # update viopreDict
            if viotmp.vioName not in viopreDict:
                viopretmp = Viopresent(viotmp.vioName)
                viopretmp.preList = [[ci.com_id, 1]]
                viopreDict[viotmp.vioName] = viopretmp
            else:
                preListtmp = viopreDict[viotmp.vioName].preList
                if preListtmp[-1][0] == ci.com_id:
                    viopreDict[viotmp.vioName].preList[-1][1] += 1
                else:
                    viopreDict[viotmp.vioName].preList.append([ci.com_id, 1])
            filetmp.vioList.append(viotmp)
        ci.vioFileList.append(filetmp)
        ci.vioFileList.pop(0) # first empty filetmp

    if not c0sig:
        with open(os.path.join(RESDIR, str(ci.com_id)+"API.json"), 'r') as f:
            apires = json.load(f)
        for key in apires:
            if key not in ci.APIs:
                ci.APIs['others'] += apires[key]
            else:
                ci.APIs[key] += apires[key]
        with open(os.path.join(RESDIR, str(ci.com_id) + "effe.txt"), 'r') as f:
            effedata = f.readline().strip().split(',')
            cLOC, ctime = int(effedata[0]), float(effedata[1])
            ci.cLOC = cLOC
            ci.ctime = ctime

def getImpVios(viopreDict):
    # for each vio kind, get importance, compare and select import vios
    importantVios = []
    impVioName = []
    for vioName in viopreDict.keys():
        viopre = viopreDict[vioName]
        prelist = viopre.preList
        distime = 0
        pretime = prelist[-1][1]
        for i in range(len(prelist)-1):
            # prelist[i+1] is prelist[i].parent
            if prelist[i][1] < prelist[i+1][1]:
                distime += prelist[i+1][1] - prelist[i][1]
                # for debug
                logger.info("find one-shot vio[commit:%d, vio:%s, dispre:%d]" %(prelist[i][0],vioName,prelist[i+1][1] - prelist[i][1]))
            elif prelist[i][1] > prelist[i+1][1]:
                pretime += prelist[i][1] - prelist[i+1][1]
        viopre.distime = distime
        viopre.pretime = pretime
        importantVios.append(viopre)
    importantVios.sort(key=lambda viopre: viopre.distime / viopre.pretime,reverse=True)
    importantVios = importantVios[:int(len(importantVios) * 0.3) + 1]
    for i in range(len(importantVios)):
        if importantVios[i].distime == 0:
            importantVios = importantVios[:i]
            break
        else:
            impVioName.append(importantVios[i].vioName)
    # for debug
    # for viopre in importantVios:
    #    if viopre.distime != 0:
    #        logger.info(viopre.vioName, viopre.distime, viopre.pretime)
    # logger.info("importantVios len: ", len(importantVios), "; first impVio: ", importantVios[0].vioName)
    # return importantVios
    return impVioName

def getAvgScore(c0, importantVios, proj):
    for file in c0.vioFileList:
        if file.LOC == 0:
            continue
        for vio in file.vioList:
            if vio.vioName in importantVios:
                file.score[vio.vioClass] += 1
        for key in file.score:
            file.score[key] /= file.LOC
            c0.score[key] += file.score[key]
    if c0.vioFileList:
        for key in c0.score:
            c0.score[key] /= len(c0.vioFileList)
    return c0.score.copy()

def getDevScore(comList, importantVios, proj, devList, v0=EmptyVioClassDict):
    # loop comList to accumulate dev.score
    for com in comList:
        # get dev of the commit
        dev = None
        for d in devList:
            if d.dev_id == com.dev_id:
                dev = d
                break
        if not dev:
            # continue
            dev = Developer(com.dev_id)
            devList.append(dev)
        logger.info(str(com.com_id) + " -- " + dev.name)
        for file in com.vioFileList:
            if file.LOC == 0:
                continue
            # count every important vio to file score
            for vio in file.vioList:
                # for viopre in importantVios:
                    # if vio.vioName == viopre.vioName:
                if vio.vioName in importantVios:
                    # score formula
                    file.score[vio.vioClass] += 1
                    # com.score[vio.vioClass] += 1
                    # break
            # count every file score to dev score
            for key in file.score:
                file.score[key] /= file.LOC # V
                file.score[key] = 150 / (file.score[key] + 1.5 * v0[key] + 1) # S = 150 / (V+1.5V0)
                dev.score[key] = (dev.score[key] * dev.fileNumber + file.score[key] * file.level * math.log10(proj.star + 10) / file.LOC) / (dev.fileNumber + 1)
            dev.fileNumber += 1
        # APIs
        for key in com.APIs:
            dev.APIs[key] += com.APIs[key]
        # effe
        dev.cLOC += com.cLOC
        dev.ctime += com.ctime

def main():
    # devList = getDevList()
    devList = getDevList(source='file', filedir=os.path.join(os.getcwd(),CODERLISTFILE))
    # projList =  getProjList()
    projList = getProjList(source='file', filedir=os.path.join(os.getcwd(), PROJLISTFILE))
    for proj in projList:
        logger.critical("begin analysis project %d %s" %(proj.proj_id, proj.name))

        # viopreList = [] # list of Viopresent
        viopreDict = {} # dict of Viopresent
        comList = [] # list of Commit

        # get the last commit ci, PMD analysis, initial comList
        # c0 = Commit(c0List1.pop(0))
        c0 = proj.c0
        if not c0:
            continue

        preAnalysis(proj, c0)
        ci = c0
        # analysisCommit(proj, ci, viopreDict)
        # comList.append(ci)
        # above is the way see c0 and the others the same; belong is the way use c0 to calculate S0
        # loop to get father commit, analysis, update comList
        looptime = 0
        while ci.hasParent() and looptime < COMMITWINDOW:
            cj = ci.getParent()
            # pmdAnalysis(proj, cj)
            diffSig = preAnalysisDiff(proj, ci, cj)
            if diffSig == 'Well Done':
                try:
                    analysisCommit(proj, cj, viopreDict)
                except:
                    logging.critical("proj %s commit %s file %d Analysis wrong." %(proj.name, cj.sha, cj.com_id))
                comList.append(cj)
            ci = cj
            looptime += 1  # end of cij loop
            print('.',end='')  # processing bar

        # get important vios(according to one-shot theory)
        importantVios = getImpVios(viopreDict)
        # get v0
        try:
            analysisCommit(proj, c0, {}, c0sig=True)
        except:
            logging.critical("proj %s commit %s file %d Analysis wrong." %(proj.name, c0.sha, c0.com_id))
        v0 = getAvgScore(c0, importantVios, proj)
        # get dev score
        getDevScore(comList, importantVios, proj, devList, v0=v0)
        # for debug
        logger.info(proj.name + ", loop: " + str(looptime))
    # print dev profile
    noneScoreDevNum = 0
    with open(OUTPUTFILE, 'w') as f:
        for dev in devList:
            res = str(dev.dev_id)+',' + dev.name + ','
            for key in VioClasskeys:
                res += str(dev.score[key]) + ','
            for key in APIkeys:
                res += str(dev.APIs[key]) + ','
            if dev.ctime != 0:
                res += str(dev.cLOC) + ',' + str(dev.cLOC / dev.ctime)
            else:
                res += '0,0'
            if dev.score != EmptyVioClassDict or dev.APIs != emptyAPIs:
                f.write(res + '\n')
                # debug:
                noneScoreDevNum += 1
    print("%d dev has scores." %(noneScoreDevNum))
main()