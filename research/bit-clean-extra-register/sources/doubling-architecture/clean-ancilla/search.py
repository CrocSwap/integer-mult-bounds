"""Search a finite scalar ansatz with one clean discarded ancilla."""
from pathlib import Path
import importlib.util
import itertools
import json
import time

src=Path(__file__).resolve().parents[2]/'four-register/dirty_ancilla.py'
spec=importlib.util.spec_from_file_location('returned_engine',src)
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
OFF=sum(1<<(4*i+j) for i in range(3) for j in range(3) if i!=j)
MAXREL=3


def solve(word):
    poly=d.polynomial(word);seen=set();found=[]
    first=[sum(((d.outer(x,y)>>bit)&1)<<j for j,(x,y) in enumerate(word)) for bit in range(16) if OFF>>bit&1]
    stats={'nodes':0,'terminals':0,'low_rank_targets':0,'parity_prunes':0}
    def rec(state):
        if state in seen:return False
        seen.add(state);stats['nodes']+=1
        if d.gf2_rank(first+[d.primitive_parity(r) for r in state])>MAXREL:
            stats['parity_prunes']+=1;return False
        grouped={}
        for s,c in poly:
            key=d.rep(state,d.BITS[s]);grouped[key]=grouped.get(key,0)^c
        terms=[(v,c) for v,c in grouped.items() if c]
        bad=[]
        for i in range(3):
            for j in range(3):
                vv=[v for v,c in terms if c>>(4*i+j)&1]
                if i!=j and vv:bad.append((False,vv))
                elif i==j and len(vv)!=1:bad.append((True,vv))
        if not bad:
            stats['terminals']+=1
            targets=[next(v for v,c in terms if c>>(5*i)&1) for i in range(3)]
            for t in targets:
                if any(not any(d.rep(d.rref(state+(d.UNIT[a],d.UNIT[b])),t)) for a,b in itertools.combinations(range(8),2)):
                    stats['low_rank_targets']+=1;return False
            found.append({'relations':[[str(x) for x in r] for r in state],
                          'targets':[[str(x) for x in r] for r in targets]})
            return True
        if len(state)>=MAXREL:return False
        diagonal,vv=min(bad,key=lambda x:len(x[1]))
        if len(vv)<2:return False
        pairs=(((vv[0],v) for v in vv[1:]) if not diagonal else
               itertools.chain(((vv[0],v) for v in vv[1:]),((vv[1],v) for v in vv[2:])))
        for a,b in pairs:
            nxt=d.add(state,tuple(x-y for x,y in zip(a,b)))
            if nxt is not None and len(nxt)<=MAXREL and rec(nxt):return True
        return False
    rec(())
    return {'word':word,'stats':stats,'found':found}


def canonical(layers):
    choices=[]
    # Fix the clean fourth coordinate. Reversal need not preserve the model.
    for p3 in itertools.permutations(range(3)):
        p=p3+(3,)
        ls=[tuple(sorted((d.permute_vector(x,p),d.permute_vector(y,p)) for x,y in layer)) for layer in layers]
        choices.append(tuple(pair for layer in ls for pair in layer))
    return min(choices)


def main():
    I=[(1<<i,1<<i) for i in range(4)]
    H=[(15^(1<<i),15^(1<<i)) for i in range(4)]
    jobs=set()
    for sizes in ((4,4),(3,2,3),(2,2,2,2),(3,3,2),(2,3,3)):
        for start in (0,1):
            bases=[(I,H)[(i+start)%2] for i in range(len(sizes))]
            for layers in itertools.product(*(itertools.combinations(b,n) for b,n in zip(bases,sizes))):
                jobs.add(canonical(layers))
    print(json.dumps({'jobs':len(jobs),'relation_budget':MAXREL,'scope':'finite I/H scalar-layer ansatz; exact rational collision search'}),flush=True)
    out=[]
    for i,word in enumerate(sorted(jobs)):
        t=time.monotonic();r=solve(word);r.update(job=i,seconds=time.monotonic()-t)
        out.append(r);print(json.dumps(r),flush=True)
        Path(__file__).with_name('SEARCH.json').write_text(json.dumps(out,indent=2)+'\n')
        d.rref.cache_clear();d.rep.cache_clear();d.add.cache_clear()
        if r['found']:break

if __name__=='__main__':main()
