# For each d=1..8 and |I|=0..8: every multiset of weights<=7 with total = 8d+|I|-1 (padding w1 only increases LP)
# must have exact LP bound < need = 112+|I| - N_{8-d}.  Prune: sum g < need (trivially fails to cover).
import sys, time
from symlp import lp, g, NE8
from collections import Counter
def parts(B,maxw=7):
    if B==0: yield {}; return
    if maxw==0: return
    for c in range(B//maxw,-1,-1):
        for p in parts(B-c*maxw,maxw-1):
            q=dict(p)
            if c: q[maxw]=c
            yield q
Is=[int(x) for x in sys.argv[1].split(',')] if len(sys.argv)>1 else range(9)
for I in Is:
  for d in range(1,9):
    B=8*d+I-1; NL=112+I; need=NL-(NE8[8-d] if d<8 else 0)
    t0=time.time(); nlp=0; worst=(-1,None); bad=[]
    for p in parts(B):
        if sum(g[w]*c for w,c in p.items())<need: continue
        val,bd=lp(p,codim=8-d,NL=NL); nlp+=1
        if bd>=need: bad.append((p,val,float(bd)))
        if val>worst[0]: worst=(val,p)
    print(f'I={I} d={d} budget={B} need={need} LPs={nlp} worstLP={worst[0]:.3f} {worst[1]} FAIL={len(bad)} {bad[:3]} {time.time()-t0:.0f}s',flush=True)
