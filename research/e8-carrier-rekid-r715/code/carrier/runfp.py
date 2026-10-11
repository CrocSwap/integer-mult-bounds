import os,sys,json,ast,itertools
os.environ['E8COORD']='ham'
import e8lib as E, frames as Fm, compile2 as C2, compile as C, fullword
import ham2fp as H
import reuse as RU
from ham1 import blocks
_pf=sys.argv[1] if len(sys.argv)>1 and sys.argv[1].endswith('.json') else 'params-r740.json'
Pd={ast.literal_eval(k):v for k,v in json.load(open(_pf))}
H.P.clear(); H.P.update(Pd)
B=[frozenset(b) for b in blocks]
pairs=[frozenset(p) for p in itertools.combinations(range(8),2)]
def parallel(p,q): return not (p&q) and (p|q) in B
cls=[]; seen=set()
for p in pairs:
    if p in seen: continue
    c=[p]+[q for q in pairs if parallel(p,q)]
    assert len(c)==4; cls.append(c); seen|=set(c)
cid={p:i for i,c in enumerate(cls) for p in c}
def run(on,b0i=0,choice=0,a6=True,doreuse=True):
    H.FP['on']=on; H.FP['a6']=a6
    if on:
        b0=B[b0i]; dirs=set(cid[frozenset(s)] for s in [ (a,b) for a,b in itertools.combinations(sorted(b0),2)])
        P=set(tuple(sorted(p)) for i in dirs for p in cls[i]); H.FP['P']=P
        split={}
        for c in blocks:
            opts=[]
            for a,b in itertools.combinations(c,2):
                rest=tuple(q for q in c if q not in (a,b))
                if (a,b) in P and rest in P and (a,b)<rest: opts.append(((a,b),rest))
            assert opts,(c,)
            split[c]=opts[choice%len(opts)]
        H.FP['split']=split
    h=H.build(0,True); W=C2.compile2(h)
    bad=[len(z) for z in C.f2_check(W)]
    st=W.stats
    out=dict(R=st['R'],carriers=st['carriers'],copies=st['copies'],inplace=st['inplace'],Arules=st['Arules'],bad=bad)
    if doreuse:
        w=fullword.build(W); w2,n=RU.reuse(w); out['Rreuse']=w2['R']; out['nre']=(n['helpers'],n['totals'])
    return out
if __name__=="__main__":
    print('control',run(False),flush=True)
    for b0i in range(14):
        for ch in range(3):
            print('FP b0',b0i,'choice',ch,run(True,b0i,ch),flush=True)
            if b0i>0: break
