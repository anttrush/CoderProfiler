lineindex = 2
with open("processeddata1128.csv") as f:
    for line in f.readlines():
        line = str(lineindex) + ',' + line
        lineindex += 1
        with open("res2mysql.csv", 'a') as fmy:
            fmy.write(line)