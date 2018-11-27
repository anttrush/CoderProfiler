import pymysql
import os
import logging
logging.basicConfig(level = logging.CRITICAL,format = '%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import requests
import datetime
db = pymysql.connect(host="10.1.1.61", port=36810, user="visitor", passwd="visitor", db="ghtorrent_restore")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print ("Database version : %s " % data)
emptyAPIs = {'java.lang':0, 'java.util':0, 'java.rmi':0, 'java.net':0, 'java.beans':0, 'java.nio':0, 'java.io':0, 'java.sql':0, 'java.security':0, 'java.math':0, 'java.text':0, 'java.awt':0, 'others':0}
EmptyVioClassDict = {'Best Practices':0, 'Code Style':0,'Design':0, 'Documentation':0,'Error Prone':0, 'Multithreading':0,'Performance':0, 'Security':0}
APIkeys = ['java.lang', 'java.util', 'java.rmi', 'java.net', 'java.beans', 'java.nio', 'java.io', 'java.sql', 'java.security', 'java.math', 'java.text', 'java.awt', 'others']
VioClasskeys = ['Best Practices', 'Code Style','Design', 'Documentation','Error Prone', 'Multithreading','Performance', 'Security']

class Project(object):
    def __init__(self, id, star=0, c0id=0):
        self.proj_id = id
        # get name from mysql, get star by func setProjStar --> change db table to add one column to store stars ?
        sql = 'select name, url from projects where id=' + str(self.proj_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.name = res[0][0]
        # https://api.github.com/repos/tosch/ruote-kit => https://github.com/tosch/ruote-kit/
        self.url = res[0][1].replace(r'//api.github','//github').replace(r'/repos/','/')
        self.star = star
        if c0id == 0:
            self.c0 = None
        else:
            self.c0 = Commit(c0id)

    def setProjDir(self, repdir):
        self.proj_dir = os.path.join(repdir, self.name)

    def setAvgVio(self, avgVio): # use this to replace v0 param
        self.avgVio = avgVio

class Developer(object):
    # not used
    @staticmethod
    def getAllTestld():
        dbSO_GH = pymysql.connect(host="10.1.1.61", port=36810, user="visitor", passwd="visitor", db="stackoverflow_github")
        cursorSO_GH = dbSO_GH.cursor()
        sql = 'select github_user_id from stackoverflow_github_users'
        cursorSO_GH.execute(sql)
        res = cursorSO_GH.fetchall()
        devList = []
        for idres in res:
            devList.append(int(idres[0]))
        # for debug
        logger.info("get test devs id from SO_GH dataset. All devs number and first 5 dev id show like below:")
        logger.info(len(devList), devList[:5])
        return devList

    def __init__(self, id, login=None):
        if not login:
            self.dev_id = id
            sql = 'select login from users where id=' + str(self.dev_id)
            cursor.execute(sql)
            res = cursor.fetchall()
            self.name = res[0][0]
            self.score = EmptyVioClassDict.copy()
            self.APIs = emptyAPIs.copy()
            self.fileNumber = 0
            # for 'efficiency'
            self.cLOC = 0
            self.ctime = 0
        else:
            self.dev_id = id
            self.name = login
            self.score = EmptyVioClassDict.copy()
            self.APIs = emptyAPIs.copy()
            self.fileNumber = 0
            # for 'efficiency'
            self.cLOC = 0
            self.ctime = 0

    # not used
    def isMemberOf(self, proj_id):
        sql = 'select * from project_members where repo_id=' + str(proj_id) + ' and user_id=' + str(self.dev_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        if res:
            return True
        else:
            return False

class Commit(object):
    def __init__(self, id):
        self.com_id = id
        self.vioFileList = []
        self.score = EmptyVioClassDict.copy()
        self.APIs = emptyAPIs.copy()
        self.cLOC = 0
        self.ctime = 0
        sql = 'select author_id, sha from commits where id=' + str(self.com_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        if res:
            self.dev_id = int(res[0][0])
            self.sha = res[0][1]
        else:
            print("CommitNotFoundException")

    def hasParent(self):
        # search db and set
        sql = 'select parent_id from commit_parents where commit_id=' + str(self.com_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        if not res:
            self.parent = None
            return False
        elif len(res) == 1:
            # new a commit and set self.parent
            self.parent = Commit(int(res[0][0]))
            return True
        else:
            # select real parent of a PR commit
            self.parent = Commit(int(res[1][0]))
            return True

    def getParent(self):
        if self.parent == None:
            self.hasParent()
        return self.parent

class Myfile(object):
    def __init__(self, filefullname, violist, loc, level=1):
        self.fileFullName = filefullname
        self.vioList = violist
        self.LOC = loc
        self.score = EmptyVioClassDict.copy()
        self.level = level

class Violation(object):
    # EmptyVioClassDict = {'Best Practices':0, 'Code Style':0,'Design':0, 'Documentation':0,'Error Prone':0, 'Multithreading':0,'Performance':0, 'Security':0}
    def __init__(self, vioname, vioclass, priority):
        self.vioName = vioname
        self.vioClass = vioclass
        self.priority = priority

class Viopresent(object):
    def __init__(self, vioname):
        self.vioName = vioname
        self.preList = [] # [[com_id, times], ...]
        # for counting importance according to "one-shot" theory
        self.distime = 0 # disapear times
        self.pretime = 0 # present times

class Issue(object):
    def __init__(self, issueId, proj_id):
        self.issue_id = issueId
        self.iss_proj_id = proj_id
        sql = 'select repo_id , reporter_id , assignee_id , pull_request , pull_request_id , created_at , issue_id from issues where issue_id=' + str(self.issue_id) + ' and repo_id=' + str(self.proj.proj_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.iss_reporter_id = int(res[0][1])
        self.iss_hasPr = (res[0][3] == '1' and True or False)
        self.iss_pr_id = int(res[0][4])
        self.iss_create_at = res[0][5]
        self.getEfficiencyData()

    def getEfficiencyData(self):
        if self.iss_hasPr == False:
            self.iss_devEff = 0
        pr = PullRequest(self.iss_pr_id, self.iss_proj_id)
        delta1 = pr.pr_merge_at - self.iss_create_at
        self.iss_duringTime = delta1.days+delta1.seconds/(24*60*60) # convert to days
        self.iss_workLoad = pr.pr_workLoad
        self.iss_devEff = self.iss_workLoad / self.iss_duringTime

class PullRequest(object):
    def __init__(self, prId, base_proj_id):
        self.pr_proj = base_proj_id
        self.pr_id = prId # id in proj, not in mysql.
        self.getEfficiencyData()

    def getEfficiencyData(self):
        addLineNum = 0
        subLineNum = 0
        self.pr_workLoad = 0
        self.created_at = 0
        # https://github.com/contao/core/pull/4542
        res = requests.get(self.pr_proj.url + '/pull/' + str(self.pr_id))
        res.encoding = 'utf-8'
        res = res.text
        posi0 = res.text.find("<relative-time datetime=")
        res1 = res[posi0:min(posi0+1000, len(res))]
        self.pr_merge_at = datetime.datetime.strptime(res[posi0 + 25: posi0 + 35], "%Y-%m-%d")

        posi0 = res1.find("diffstat")
        posi1 = res1.find("\n", posi0 + 1)
        posi2 = res1.find("\n", posi1 + 1)
        addLineNum = 0
        subLineNum = 0
        if res1.find("text-green", posi1 + 1, posi2) != -1:
            posi1 = posi2
            posi2 = res1.find("\n", posi1 + 1)
            addLineNum = int(res1[posi1:posi2].strip())
            posi1 = res1.find("\n", posi2 + 1)
            posi2 = res1.find("\n", posi1 + 1)
        if res1.find("text-red", posi1 + 1, posi2) != -1:
            posi1 = posi2
            posi2 = res1.find("\n", posi1 + 1)
            tmp = res1[posi1:posi2].strip()
            subLineNum = -int(tmp[1:])
        self.pr_workLoad = addLineNum + subLineNum


'''
...
<relative-time datetime="2013-02-19T16:19:55Z">Feb 19, 2013</relative-time>
...
<div class="tabnav tabnav-pr">
    <div class="tabnav-extra float-right">
      <span class="diffstat" id="diffstat">
        <span class="text-green">
          +84
        </span>
        <span class="text-red">
          −30
        </span>
        <span class="tooltipped tooltipped-s" aria-label="114 lines changed">

'''