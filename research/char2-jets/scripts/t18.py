import sys, json
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from cr2 import realise
bads=[([[1, 1, 1], [0, 1, 1], [1, 0, -1], [1, 1, 0], [1, 1, 1], [0, 1, 1], [1, 1, 0], [1, 1, 1], [1, 1, 1], [1, 0, -1], [1, 1, 1]], [[1, 0, 1], [0, 1, 1], [1, -1, 0], [0, 1, -1], [1, -1, -2], [1, 0, 1], [1, 1, 0], [1, -1, -2], [1, -1, 1], [1, -1, 0], [1, -1, 1]]),
([[1, 1, -1], [1, -1, 0], [1, -1, 0], [1, -1, 1], [1, -1, 0], [1, -1, 0], [1, 1, -1], [0, 1, -1], [1, 0, 1]], [[1, 0, -1], [0, 1, 1], [0, 1, -1], [1, -1, -1], [1, 0, -1], [1, -1, 0], [1, 1, 0], [1, 1, -1], [1, 1, 0]]),
([[1, 1, 1], [1, 1, 0], [1, 1, 1], [0, 1, 1], [1, 0, 1], [0, 1, -1], [1, 1, 0], [1, 1, 1], [0, 1, 1]], [[0, 1, 1], [1, 0, -1], [0, 1, 1], [1, 0, 1], [1, 0, 1], [1, -1, 0], [1, 0, -1], [1, -1, -1], [0, 1, 1]])]
for i,(P,Q) in enumerate(bads):
    json.dump([P,Q], open('jf%d.json'%i,'w'))
    v=len(P); R,A,free=setup(P,Q); pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    cr=None
    for k in (1,2,3):
        r=realise(pi,sig,set(free),k=k,limit=10**6)
        if isinstance(r,dict): cr=k; break
    best=enum_raw(v,R,A,free,0)[0] if len(free)<=28 else None
    print(i,'v',v,'f',len(free),'fullCR2 over GF(2^%s)'%cr,'min cost',best)
