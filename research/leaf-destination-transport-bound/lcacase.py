"""Exact max mass per LCA phase pair (alpha,beta) at the top call of word(m,s)."""
import sys
from census import word
from lemmas import step, mass
def phases(m,s):
    b=m//2; a=m-b; L=lambda k:len(word(k,1))
    names=['U','V',"U'","V'"] if s==1 else ['V','U',"V'","U'"]
    sizes=[L(b),L(a),L(b),L(a)] if s==1 else [L(a),L(b),L(a),L(b)]
    out=[];
    for nm,z in zip(names,sizes): out+= [nm]*z
    return out
def table(m,s):
    w=word(m,s); ph=phases(m,s); res={}
    for p in range(len(w)):
        col={w[p][1]:{():1}}
        for t in range(p+1,len(w)):
            step(col,*w[t])
            if ph[t]==ph[p]: continue
            k=(ph[p],ph[t]); mm=max(mass(v) for v in col.values())
            if mm>res.get(k,0): res[k]=mm
    return res
if __name__=='__main__':
    for m in map(int,sys.argv[1:]):
        for s in (1,-1):
            r=table(m,s); print(m,s,max(r.values()),' '.join(f'{a}{b}={v}' for (a,b),v in sorted(r.items())),flush=True)
