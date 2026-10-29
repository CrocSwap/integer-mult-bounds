import sys; sys.path.insert(0,'../OS-CHARGE')
from base import *
import json
out={'LAB':LAB,'Z':Z,'FC':FC.tolist(),'L':[[float(c) for c in r] for r in L],'F0':[[float(c) for c in f] for f in F0],'E8':[[float(c) for c in r] for r in E8L]}
json.dump(out,open('data.json','w'))
print(v,len(E8L),FC[:3])
