import sys
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
P,Pinv,comp=main_maps(w)
hf={int(k):span(f) for k,f in w['helper_final'].items()}
# frames after tail
cur=list(endB)
for i,f in w['early_cleanup']:
    for r in regs(w['cleanup'][i]):cur[r]=span(f)
U=span([256,128,64,32,18,10,6,1])
liftedU={g for g in range(n) if cur[g]==U}
print('registers at U after tails:',len(liftedU),sorted(liftedU))
print('endB==U:',sorted(g for g in range(n) if endB[g]==U))
for k in (608,610):
    print(k,'row',{g:(str(x),len(endB[g]),g in liftedU) for g,x in Pinv[k].items()})
    print(k,'col',{g:(str(P[g][k]),len(endB[g])) for g in range(n) if P[g].get(k)})
# per tail gate partner listing
tl=defaultdict(list)
for i,f in w['early_cleanup']:
    e=w['cleanup'][i]
    for r in regs(e): tl[r].append(i)
E=(30,)
H=[h for h in range(2*v,n) if start[h]==E]
first={}
for part in ('A','B'):
    for e in w[part]:
        for r in regs(e): first.setdefault(r,span(e[-1]))
Hc=[h for h in range(2*v,n) if start[h]==() and h not in hf and first.get(h)==E]
for drop in ([438],[440],[438,440]):
    F=(liftedU-set(drop))
    for HH,name in ((H,'E-group'),(H+Hc,'E-group+cold')):
        S={g for h in HH for g,x in Pinv[h].items() if x and g not in F}
        rb=nullspace_rows([Pinv[h] for h in HH],S)
        print('drop',drop,name,'nullity',len(rb),[{HH[j]:str(c) for j,c in r.items()} for r in rb.values() if any(HH[j] in (608,610) for j in r) or len(r)>1][:6])
