import pickle,csv,ast,collections
from rrc6 import fam,dead_j
from rrc import N
res=pickle.load(open('../SPANCOVER/opts.pkl','rb'))
cnt=collections.Counter(); alive=[]
out=[]
for d,s,ws,e,o in res:
    ws=sorted(ws,reverse=True)
    killed=None
    for j in range(2,min(d,6)+1):
        comp=ws[d-j:]
        dd,r=dead_j(comp,j)
        if dd: killed=(j,r);break
    cnt[(s,killed is not None)]+=1
    out.append((d,s,ws,killed))
print(cnt)
import json
json.dump(out,open('allrows_rrc.json','w'))
