import csv,ast,json,sys
sys.path.insert(0,'.')
from margin import best
from countm import scen_w,g
sys.path.insert(0,'../AUDIT-SC')
rows=[r for r in csv.DictReader(open('ledger_v2.csv')) if r['audit_status']=='OPEN']
out=[]
for r in rows:
    ws=ast.literal_eval(r['weights']); d=int(r['d']); s=int(r['slack'])
    if s==5: continue
    for tag,w2,dd,ex in scen_w(ws,d,s):
        gv=[g[w] for w in w2]
        imm,b=best(gv,dd,ex)
        comp=tuple(sorted(w2[dd-2:]+[1]*ex,reverse=True)); cap=sum(g[w] for w in comp)
        out.append(dict(row=int(r['row']),tag=tag,w=w2,d=dd,ex=ex,rrc=b[0],imm=imm,comp=comp,cap=cap))
        print(out[-1]['row'],tag,'rrc',b[0],'cap',cap,comp,flush=True)
json.dump(out,open('scenmargin.json','w'))
