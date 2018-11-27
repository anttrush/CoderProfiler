import time
import requests
pFile = "D:\code\python\CoderProfiler\others\projtmp.txt"
PROJLISTFILE = r'projStarList.txt'

with open(pFile) as f:
    for line in f.readlines():
        url = line.strip()[10:-4] + "/stargazers"
        res = requests.get(url)
        res = res.text
        po1 = res.find("stargazers_main")
        po2 = res.find("Count",po1)
        po3 = res.find("span", po2)
        starNum = int(res[po2+9: po3-2].replace(',',''))
        print(url,starNum)
        with open(PROJLISTFILE,'a') as resf:
            resf.write(url + ", " + str(starNum) + '\n')
        time.sleep(10)