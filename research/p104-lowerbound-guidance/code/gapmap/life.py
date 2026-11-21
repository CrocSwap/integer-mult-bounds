# GAPMAP lifetime classifier for t7669 owned lifetimes: GTD / cold intake / shape. stdlib, 1 proc.
import sys, pickle
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from fractions import Fraction as Q
from collections import Counter, defaultdict
W=pk.load('<word-rung-package>/data/t7669.json.gz')
n=W['public']; N=n+W['owned_fields']; P=W['program']; F=W['frames']; dim=[len(b) for b in F]
ports=W['ports']; live=W['live']; H=W['hosted']; Dp=H['Dports']
dot=lambda a,b: bin(a&b).count('1')&1
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
SP=[span(b) for b in F]
lab={}   # symbol register -> (kind, port)
for p,r in enumerate(live): lab[r]=('X',p); lab[r+112]=('Y',p)
for j,p in enumerate(Dp): lab[H['X2'][j]]=('X2',p); lab[H['Y2'][j]]=('Y2',p)
# validate hosted labels
bad=0
for r,(k,p) in lab.items():
    q=ports[p]
    if k=='X2': bad+= q not in SP[W['initial'][r]]
    if k=='Y2': bad+= not all(dot(x,q)==0 for x in F[W['final'][r]])
print('hosted label validation bad=',bad)
rows=[{r:Q(1)} if r<n else {} for r in range(N)]
cur=list(W['initial'])+[None]*W['owned_fields']
ev=defaultdict(list); lid={}; cnt=0; lifes={}
def sup_cls(row):
    c=Counter()
    for k,v in row.items():
        c[lab[k][0] if k in lab else 'H']+=1
    return dict(c)
for i,e in enumerate(P):
    op,r=e[0],e[1]
    if op=='INIT':
        cnt+=1; lid[r]=cnt; lifes[cnt]=dict(reg=r,i0=i,evs=[('init',cur[r] if cur[r] is not None else e[2])]); rows[r]={}; cur[r]=e[2]
    elif op=='CLEAR':
        lifes[lid[r]]['evs'].append(('clear',i)); lifes[lid[r]]['i1']=i; rows[r]={}; cur[r]=None; del lid[r]
    elif op=='MOVE':
        a,b=e[2],e[3]; cur[r]=b
        if r>=n: lifes[lid[r]]['evs'].append(('move',a,b,i))
    elif op=='SCALE':
        q=Q(e[2]); rows[r]={k:v*q for k,v in rows[r].items()}
        if r>=n: lifes[lid[r]]['evs'].append(('scale',q))
    else:
        s=e[2]; q=Q(e[3]); f=e[4]; R=rows[r]
        if r>=n: # intake into owned
            lifes[lid[r]]['evs'].append(('in',s, s>=n, f, q, dict(rows[s]) ))
        if s>=n: # output from owned
            lifes[lid[s]]['evs'].append(('out',r, r>=n, f, q, dict(rows[s]) ))
        for k,v in rows[s].items():
            nv=R.get(k,0)+q*v
            if nv: R[k]=nv
            else: R.pop(k,None)
fin={r:dict(rows[r]) for r in lab if lab[r][0] in ('X','X2')}
pickle.dump(dict(lifes=lifes,lab=lab,fin=fin),open('code/gapmap/lifes.pkl','wb'))
print('lifetimes',len(lifes))
