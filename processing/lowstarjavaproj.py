import requests
import time
import os
root_ = r"https://github.com/search?l=Java&p=2&q=stars%3A%3C400&s=stars&type=Repositories&p="
shellscript = r"gitclonelowjava.sh"
devprojstar = r"devprojstarlowjava.txt"

with open(shellscript, 'a') as f:
    for pageindex in range(4,11):
        print(pageindex)

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

            [_, dev, projname] = projfullname.split('/')
            url = "https://github.com"+projfullname+"/stargazers"
            resstar = requests.get(url)
            resstar = resstar.text
            po1 = resstar.find("stargazers_main")
            po2 = resstar.find("Count", po1)
            po3 = resstar.find("span", po2)
            starNum = int(resstar[po2 + 9: po3 - 2].replace(',', ''))
            print(dev, projname, starNum)
            with open(devprojstar, 'a') as dpsf:
                dpsf.write(dev + ',' + projname + ',' + str(starNum) + ',' + '\n')
            time.sleep(100)
        time.sleep(100)


