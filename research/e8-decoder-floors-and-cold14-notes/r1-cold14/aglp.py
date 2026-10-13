"""aggregate free-dispatch LP (first-order, mass-neutral values V) over providers; patterns with any remainder."""
import json,sys,itertools
import numpy as np
from collections import Counter,defaultdict
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
V={int(k):v for k,v in json.load(open('V.json')).items()}
PLAN=json.load(open('/Users/joelpulikkan/imb-r1/research/complex-571-cold14-e1/data/PLAN.json'))
reg=PLAN['provider_registry']
provs=sys.argv[1].split(',') if len(sys.argv)>1 else ['jp8','atm3']
fixed=json.loads(sys.argv[2]) if len(sys.argv)>2 else None   # {time:provider} optional
inv={p:Counter(reg[p]['widths']) for p in provs}
val={p:sum(V[int(r)]*c for r,c in reg[p]['actual_paid_profile'].items()) for p in provs}
WID=sorted({w for p in provs for w in inv[p]})
print('values',val,'widths',WID)
def pats(cap,L):
    out=[]
    def rec(pre,i,tot):
        out.append(tuple(pre))
        for j in range(i,len(WID)):
            w=WID[j]
            if tot+w<=cap and len(pre)<L: rec(pre+[w],j,tot+w)
    rec([],0,0);return out
cols=[];cost=[];rows=defaultdict(dict);rhs_eq={};ub_rows=defaultdict(dict);ub={}
def var(c):
    cols.append(c);cost.append(-c);return len(cols)-1
sel={}
for t in range(72):
    for p in provs:
        if fixed and fixed.get(str(t))!=p: continue
        sel[t,p]=var(val[p])
    rows[('sel',t)].update({sel[t,p]:1 for p in provs if (t,p) in sel});rhs_eq[('sel',t)]=1
pv={}
for key,(cap,times) in PLAN['windows'].items():
    ps=pats(cap,len(times))
    for q in ps:
        i=var(V[cap-sum(q)]);pv[key,q]=i;rows[('ports',key)][i]=1
    rhs_eq[('ports',key)]=112
    for t in times:
        for w in WID:
            i=var(0);rows[('flow',key,w)][i]=1;rows[('inv',t,w)][i]=1
            ub_rows[('tcap',key,t)][i]=1;ub[('tcap',key,t)]=112
    for w in WID:
        for q in ps:
            c=q.count(w)
            if c: rows[('flow',key,w)][pv[key,q]]=-c
        rhs_eq[('flow',key,w)]=0
for t in range(72):
    for w in WID:
        for p in provs:
            if (t,p) in sel and inv[p][w]: rows[('inv',t,w)][sel[t,p]]=-inv[p][w]
        rhs_eq[('inv',t,w)]=0
def mat(R,keys):
    r,c,d=[],[],[]
    for i,k in enumerate(keys):
        for j,x in R[k].items():r.append(i);c.append(j);d.append(x)
    return coo_matrix((d,(r,c)),shape=(len(keys),len(cols))).tocsr()
ek=list(rows);uk=list(ub_rows)
res=linprog(cost,A_ub=mat(ub_rows,uk),b_ub=[ub[k] for k in uk],A_eq=mat(rows,ek),b_eq=[rhs_eq[k] for k in ek],bounds=(0,None),method='highs')
print(res.status,res.message,'objective',-res.fun,'vars',len(cols))
x=res.x
disp=Counter();
for (t,p),i in sel.items(): disp[p]+=x[i]
print('dispatch',dict(disp))
rem=Counter()
for (key,q),i in pv.items():
    if x[i]>1e-7: rem[PLAN['windows'][key][0]-sum(q)]+=x[i]
print('remainders',{k:round(v,3) for k,v in sorted(rem.items())})
cur=68*val.get('jp8',0)+4*val.get('atm3',0)
print('current solution value',cur,'LP gain over current (1e-9 b)',-res.fun-cur)
json.dump({'sel':{f'{t},{p}':x[i] for (t,p),i in sel.items()},'pv':{f'{k}|{list(q)}':x[i] for (k,q),i in pv.items() if x[i]>1e-9}},open('aglp-out.json','w'))
du=res.eqlin.marginals
d=defaultdict(dict)
for i,k in enumerate(ek):
    if k[0]=='inv': d[k[2]][k[1]]=-du[i]
for w in WID:
    vals=[d[w][t] for t in range(72)]
    print('dual width',w,'min %.2f max %.2f mean %.2f'%(min(vals),max(vals),sum(vals)/72))
print('per-time dual(9)-dual(8):',[round(d[9][t]-d[8][t],2) for t in range(72)])
print('per-time dual(8)-dual(7):',[round(d[8][t]-d[7][t],2) for t in range(72)])
