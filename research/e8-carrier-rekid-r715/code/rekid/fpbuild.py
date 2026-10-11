import os,sys,json,ast,itertools
os.environ['E8COORD']='ham'
import ham2fpx as H, ham1
from ham1 import blocks
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r740.json'))}
H.P.clear(); H.P.update(Pd)
B=[frozenset(b) for b in blocks]
pairs=[frozenset(p) for p in itertools.combinations(range(8),2)]
def parallel(p,q): return not (p&q) and (p|q) in B
cls=[]; seen=set()
for p in pairs:
    if p in seen: continue
    c=[p]+[q for q in pairs if parallel(p,q)]
    cls.append(c); seen|=set(c)
cid={p:i for i,c in enumerate(cls) for p in c}
def build_fp(b0i=0,choice=0,a6=True):
    H.FP['on']=True; H.FP['a6']=a6
    b0=B[b0i]; dirs=set(cid[frozenset(s)] for s in itertools.combinations(sorted(b0),2))
    P=set(tuple(sorted(p)) for i in dirs for p in cls[i]); H.FP['P']=P
    split={}
    for c in blocks:
        opts=[]
        for a,b in itertools.combinations(c,2):
            rest=tuple(q for q in c if q not in (a,b))
            if (a,b) in P and rest in P and (a,b)<rest: opts.append(((a,b),rest))
        split[c]=opts[choice%len(opts)]
    H.FP['split']=split
    return H.build(0,True),P
if __name__=='__main__':
    import hx2, pickle
    h,P=build_fp(); print('FP h built; score',hx2.score(h))
    pickle.dump(h,open('../out/fp_base.h','wb'))
