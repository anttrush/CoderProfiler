import requests
import time
import os
root_ = r"https://github.com/search?l=Java&q=stars%3A%3E1000&s=stars&type=Repositories&p="

with open("moststarjavaproj.txt", 'a') as f:
    for pageindex in range(1,101):
        url = root_ + str(pageindex)
        res = requests.get(url)
        res.encoding = 'utf-8'
        res = res.text
        posi3 = 0
        for i in range(10):
            posi0 = res.find("repo-list-item",posi3+1)
            posi1 = res.find("href",posi0+1)
            posi2 = res.find("\"",posi1+1) # 前引号
            posi3 = res.find("\"",posi2+1) # 后引号
            # print(posi0, posi1, posi2, posi3)
            projfullname = res[posi2+1:posi3]
            print(projfullname)
            f.write("git clone https://github.com"+projfullname+".git\n")
            # os.popen("git clone https://github.com"+projfullname+".git ./repos/"+projfullname.split('/')[2]).read()
        time.sleep(100)



