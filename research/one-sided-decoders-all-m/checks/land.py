# landscape: for d=1..8 and slack k<=K: DP-enumerated multisets -> quotient LP -> Pencil (d>=4, anchors = e-1 smallest pieces, sum g<=4) -> e=2 (<=6)-triple rule
import sys,subprocess,ast
from symlp import lp
from collections import Counter
import os
K=int(sys.argv[1]); ds=[int(x) for x in sys.argv[2].split(',')]
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
N8=[0,1,3,6,12,20,36,63,120]
def lists(d,target):
    src=open('enum.py').read().replace("for x in out[:15]: print(x)","for x in out: print(repr(x))")
    out=subprocess.run([sys.executable,'-c',src,str(d),str(target)],capture_output=True,text=True).stdout.splitlines()
    return [ast.literal_eval(l) for l in out if l.startswith('(')]
for d in ds:
    codim=8-d; need=112-N8[8-d]
    res=Counter(); surv={}
    for wt,ws in lists(d,8*d+K+1):
        if wt<8*d: continue
        k=wt-8*d; a=len(ws); e=a-d
        val,bd=lp(dict(Counter(ws)),codim=codim,NL=112)
        if bd<need-1e-9: res[(k,'LP')]+=1; continue
        anc=sorted(ws)[:e-1]
        if d>=4 and e>=2 and sum(g[w] for w in anc)<=4: res[(k,'pencil')]+=1; continue
        if e==2 and sum(1 for w in ws if w<=6)>=5: res[(k,'666')]+=1; continue
        res[(k,'SURV')]+=1; surv.setdefault(k,[]).append(ws)
    for k in range(K+1):
        print('d',d,'slack',k,{t:res[(k,t)] for t in ('LP','pencil','666','SURV')},(surv.get(k) or [])[:6],flush=True)
