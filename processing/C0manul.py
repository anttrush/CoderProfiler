c0notfoundfile = 'log1.log'
gbkwrongfile = 'gbkwrong.txt'
gbklist = []
with open(gbkwrongfile, 'r') as f:
    for line in f.readlines():
        gbklist.append(line.strip())

with open(c0notfoundfile, 'r') as f:
    for line in f.readlines():
        data = line.strip().split(',')
        idstr, name, starstr = data[0], data[1], data[2]
        if idstr in gbklist:
            continue
        else:
            print(line)
