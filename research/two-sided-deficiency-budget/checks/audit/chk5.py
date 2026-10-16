# Which cells close with SIZE tests only, using audited facts: d_2=78, per-target cap7=32 on all |Off|<=72 targets, completeness (|Off|>=73 => global caps).
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import itertools
G={0:2,1:4,2:8,3:12,4:20,5:36}; G32=dict(G); G32[5]=32
d={1:53,2:78,3:92,4:100,5:106,6:109,7:111,8:112}
def lev1(ss): return sum(G32[x] for x in ss)>=53 or sum(G[x] for x in ss)>=73
def feas(ss,b):   # ss nonincreasing
    a=[G[x] for x in ss]
    if any(sum(a[j:])<d[b-j] for j in range(b-1)): return False
    return lev1(ss[b-1:])
for b in (3,4):
    for t in range(1,7):
        out=[]
        for k in range(1,t+b+1):
            for ss in itertools.combinations_with_replacement(range(5,-1,-1),k):
                if sum(ss)<6*b and feas(ss,b): out.append(ss)
        mn=min(map(sum,out)) if out else None
        print((b,t),'#feasible below 6b:',len(out),'deficit',0 if mn is None else 6*b-mn, 'needs exact oracle' if out else 'CLOSED by size', sorted(out,key=sum)[:3])
