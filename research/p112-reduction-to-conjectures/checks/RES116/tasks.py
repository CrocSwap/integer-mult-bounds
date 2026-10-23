import csv,ast
from countm import scen_w,g
rows=[r for r in csv.DictReader(open('ledger_v2.csv')) if r['audit_status']=='OPEN']
T={}
for r in rows:
    ws=ast.literal_eval(r['weights']); d=int(r['d']); s=int(r['slack'])
    if s==5: continue
    for tag,w2,dd,ex in scen_w(ws,d,s):
        comp=tuple(sorted(w2[dd-2:]+[1]*ex,reverse=True)); cap=sum(g[w] for w in comp)
        T.setdefault((comp,cap),[]).append((int(r['row']),tag))
import collections
for (comp,cap),v in sorted(T.items(),key=lambda kv:kv[0][1]):
    if cap<90: print(cap,comp,sorted(set(x[0] for x in v)))
