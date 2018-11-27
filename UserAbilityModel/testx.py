import json
import os
RESDIR = r'D:\科研\CodeQualityAnalysis\CodeAnalysis\PMD'
com_id = 1055441549
with open(os.path.join(RESDIR, str(com_id)+"API.json"), 'r') as f:
    apires = json.load(f)
print(apires)