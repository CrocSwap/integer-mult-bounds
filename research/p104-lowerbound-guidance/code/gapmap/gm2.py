import sys, pickle
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk, math
from collections import Counter, defaultdict
W=pk.load('<word-rung-package>/data/t7669.json.gz')
n=W['public']; P=W['program']; dim=[len(f) for f in W['frames']]
live=set(W['live']); H=W['hosted']
cls={}
for r in live: cls[r]='X'; cls[r+112]='Y'
for r in H['X2']: cls[r]='X2'
for r in H['Y2']: cls[r]='Y2'
kf=0.00372142604386357; s=1-kf
g=lambda r: r**s
mv=defaultdict(list)
for e in P:
    if e[0]=='MOVE' and e[1]<n: mv[e[1]].append(dim[e[3]]-dim[e[2]])
# mains: climb check and excess by class
for c in ['X','Y','X2','Y2']:
    regs=[r for r,k in cls.items() if k==c]
    climbs=Counter(dim[W['final'][r]]-dim[W['initial'][r]] for r in regs)
    ex=sum(sum(g(x) for x in mv[r])-g(8) for r in regs)
    nm=sum(len(mv[r]) for r in regs)
    print('main',c,len(regs),'climbs',dict(climbs),'moves',nm,'excess@kf',round(ex,3),'per main',round(ex/len(regs),4))
# helpers by climb
grp=defaultdict(lambda:[0,0,0.0,0])
for r in range(n):
    if r in cls: continue
    cl=dim[W['final'][r]]-dim[W['initial'][r]]; L=mv.get(r,[])
    ex=sum(g(x) for x in L)-(g(cl) if cl>0 else 0)
    k=(cl,); G_=grp[k]; G_[0]+=1; G_[1]+=len(L); G_[2]+=ex; G_[3]+= (len(L)>1)
tot=0
print('helper by climb: climb count moves excess split')
for k in sorted(grp): print(k[0],*[ (round(v,3) if isinstance(v,float) else v) for v in grp[k]]); tot+=grp[k][2]
print('helper net total',tot, 'helpers with 0 climb', grp.get((0,),None))
# helper split by #moves
byn=Counter(); exn=Counter()
for r in range(n):
    if r in cls: continue
    cl=dim[W['final'][r]]-dim[W['initial'][r]]; L=mv.get(r,[])
    byn[len(L)]+=1; exn[len(L)]+=sum(g(x) for x in L)-(g(cl) if cl>0 else 0)
print('helpers by #moves',sorted(byn.items())); print('excess by #moves',{k:round(v,2) for k,v in sorted(exn.items())})
# D/R masses & costs, one-jump ideal
d=pickle.load(open('lifes.pkl','rb'))
mass=Counter(); cost=Counter()
for lid,L in d['lifes'].items():
    ms=[e for e in L['evs'] if e[0]=='move']
    if not ms: continue
    ds=[dim[e[2]]-dim[e[1]] for e in ms]; t='D' if ds[0]<0 else 'R'
    mass[t]+=sum(abs(x) for x in ds); cost[t]+=sum(g(abs(x)) for x in ds)
print('mass',mass,'cost@kf',cost,' ideal 8*7^s',8*g(7),' 56*psi',56*(9**s-8**s))
