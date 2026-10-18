# survivors of the (DP-enumerated) multisets with cost(T) = 8d + k, k=0..K, under the symmetrised quotient LP
import sys,subprocess,ast
from symlp import lp
from collections import Counter
import os
K=int(sys.argv[1]); ds=[int(x) for x in sys.argv[2].split(',')]
def lists(d,target):
    src=open('enum.py').read().replace("for x in out[:15]: print(x)","for x in out: print(repr(x))")
    out=subprocess.run([sys.executable,'-c',src,str(d),str(target)],capture_output=True,text=True).stdout.splitlines()
    return [ast.literal_eval(l) for l in out if l.startswith('(')]
need={6:109,7:111,8:112}; codim={6:2,7:1,8:0}
for d in ds:
    tot=Counter(); surv=Counter(); ex={}
    for wt,ws in lists(d,8*d+K+1):
        if wt<8*d: continue
        val,bd=lp(dict(Counter(ws)),codim=codim[d],NL=112)
        k=wt-8*d; tot[k]+=1
        if bd>=need[d]-1e-9: surv[k]+=1; ex.setdefault(k,[]).append(ws)
    for k in range(K+1): print('d',d,'slack',k,'multisets',tot[k],'LP-survivors',surv[k],(ex.get(k) or []),flush=True)
