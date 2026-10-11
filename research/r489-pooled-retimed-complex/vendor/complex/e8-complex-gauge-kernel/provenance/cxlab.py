"""cx lab helpers.  Paths come from the environment: CXG_BASE = output directory of
`python -B research/idle-axis-hosting/verify.py $CXG_BASE` (PR #442 replay, which contains parent/changed/split-centres)."""
import gzip,json,copy,os,sys
from fractions import Fraction as Q
from collections import Counter,defaultdict
CX=os.environ.get('CXG_BASE','')
CH=CX+'/parent/changed/split-centres/'
v=120
def load(path=None):
    return json.load(gzip.open(path or (CH+'FULL-WORD.json.gz')))
def apply(e,rows):
    if e[0]=='scale':
        _,t,a,b,*_=e;q=Q(a,b)
        rows[t]={j:q*x for j,x in rows[t].items()}
    else:
        _,t,s,a,b,*_=e;q=Q(a,b)
        for j,x in list(rows[s].items()):
            z=rows[t].get(j,Q(0))+q*x
            if z:rows[t][j]=z
            else:rows[t].pop(j,None)
def inv(e):
    e=copy.deepcopy(e)
    if e[0]=='add':e[3]*=-1
    else:e[2],e[3]=e[3],e[2]
    return e
def basis(vs):
    b={}
    for x in vs:
        for k in sorted(b,reverse=True):
            if x>>k&1:x^=b[k]
        if x:
            k=x.bit_length()-1
            for j in b:
                if b[j]>>k&1:b[j]^=x
            b[k]=x
    return tuple(b[k] for k in sorted(b,reverse=True))
def inside(a,b):return basis(list(a)+list(b))==tuple(b) if basis(b)==tuple(b) else basis(list(a)+list(b))==basis(b)
def ident(n):return [{r:Q(1)} for r in range(n)]
