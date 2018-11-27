import os
path = r"D:\科研\CodeQualityAnalysis\CodeAnalysis\PMD"
for parent, dirnames, filenames, in os.walk(path, followlinks=True):
    for filename in filenames:
        filepath = os.path.join(path, filename)
        flag = False
        with open(filepath, 'r') as f:
            if f.readline() == '{}':
                flag = True
        try:
            os.remove(filepath)
            print("remove ",filepath)
        except Exception as err:
            print("yo, mf")