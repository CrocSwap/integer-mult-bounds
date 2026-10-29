import csv,ast,json,sys
from rrc_audit import *
rows=list(csv.DictReader(open('../SPANCOVER/ledger.csv')))
out=[]
for idx,r in enumerate(rows):
    ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d']); s=int(r['slack'])
    sc=scen(ws,d,s)
    if sc is None: out.append((idx,d,s,ws,'NA',[])); continue
    res=[]; dead=True
    for tag,gv,dd,ex in sc:
        c=kill(tuple(gv),dd,ex)
        if c: verify(c,gv,dd,ex)
        res.append((tag,c))
        if not c: dead=False
    out.append((idx,d,s,ws,dead,res))
json.dump(out,open('rrc_results.json','w'))
from collections import Counter
print(Counter((o[2],o[4]) for o in out))
