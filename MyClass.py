import pymysql
import os
#import requests
import datetime
db = pymysql.connect("192.168.3.123", "ght", "ght", "github")
cursor = db.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print ("Database version : %s " % data)

class Project(object):
    def __init__(self, id):
        self.proj_id = id
        # get name from mysql, don't know how to get star
        sql = 'select name, url from projects where id=' + str(self.proj_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.name = res[0][0]
        # https://api.github.com/repos/tosch/ruote-kit => https://github.com/tosch/ruote-kit/
        self.url = res[0][1].replace(r'//api.github','//github').replace(r'/repos/','/')

    def setProjStar(self, star):
        self.star = star

    def setProjDir(self, repdir):
        self.proj_dir = os.path.join(repdir, self.name)

    def setAvgVio(self, avgVio): # use this to replace v0 param
        self.AvgVio = avgVio

class Developer(object):
    @staticmethod
    def getAllIdFromMysql():
        dbSO_GH = pymysql.connect("192.168.3.123", "root", "123456", "SO_GH")
        cursorSO_GH = dbSO_GH.cursor()
        sql = 'select github_user_id from stackoverflow_github_users'
        cursorSO_GH.execute(sql)
        res = cursorSO_GH.fetchall()
        devList = []
        for idres in res:
            devList.append(int(idres[0]))
        # for debug
        print(len(devList), devList[:5])
        return devList

    def __init__(self, id):
        self.dev_id = id
        sql = 'select login from users where id=' + str(self.dev_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.name = res[0][0]
        self.score = Violation.EmptyVioClassDict.copy()
        self.fileNumber = 0
        # for 'efficiency'
        self.solvedIssueNumber = 0
        self.workingTime = 0

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
        self.score = Violation.EmptyVioClassDict.copy()
        sql = 'select author_id, sha from commits where id=' + str(self.com_id)
        cursor.execute(sql)
        res = cursor.fetchall()
        if res:
            self.dev_id = int(res[0][0])
            self.sha = res[0][1]
        else:
            print("CommitNotFoundException")

    def hasParent(self):
        # go into mysql and find self.parent
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
    def __init__(self, filefullname, violist, loc, level):
        self.fileFullName = filefullname
        self.vioList = violist
        self.LOC = loc
        self.score = Violation.EmptyVioClassDict.copy()
        self.level = level

class Violation(object):
    EmptyVioClassDict = {'Best Practices':0, 'Code Style':0,'Design':0, 'Documentation':0,'Error Prone':0, 'Multithreading':0,'Performance':0, 'Security':0}
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
    def __init__(self, issueId, proj):
        self.issue_id = issueId
        self.proj = proj
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
        pr = PullRequest(self.iss_pr_id, self.proj)
        delta1 = pr.pr_merge_at - self.iss_create_at
        self.iss_duringTime = delta1.days+delta1.seconds/(24*60*60) # convert to days
        self.iss_workLoad = pr.pr_workLoad
        self.iss_devEff = self.iss_workLoad / self.iss_duringTime

class PullRequest(object):
    def __init__(self, prId, base_proj):
        self.pr_proj = base_proj.proj_id
        self.pr_id = prId # id in proj, not in mysql.
        self.getEfficiencyData()
'''
    def getEfficiencyData(self):
        addLineNum = 0
        subLineNum = 0
        self.pr_workLoad = 0
        self.created_at = 0
        # https://github.com/contao/core/pull/4542
        res = requests.get(self.pr_proj.url + '/pull/' + str(self.pr_id))
        res.encoding = 'utf-8'
        posi0 = res.find("<relative-time datetime=")
        self.pr_merge_at = datetime.datetime.strptime(res[posi0 + 25: posi0 + 35], "%Y-%m-%d")



        posi0 = res.find("diffstat")
        posi1 = res.find("\n",beg=posi0)
        posi2 = res.find("\n",beg=posi1)
        if res.find("text-green",beg=posi1, end=posi2) != -1:
            posi1 = posi2
            posi2 = res.find("\n",beg=posi1)
            addLineNum = int(res[posi1+1:posi2])
            posi1 = res.find("\n", beg=posi2)
            posi2 = res.find("\n", beg=posi1)
        if res.find("text-red",beg=posi1, end=posi2) != -1
            posi1 = posi2
            posi2 = res.find("\n", beg=posi1)
            subLineNum = int(res[posi1 + 1:posi2])
        self.pr_workLoad = addLineNum + subLineNum
'''

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