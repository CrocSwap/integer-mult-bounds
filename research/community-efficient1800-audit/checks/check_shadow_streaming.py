"""Source-bound differential checks of #2840's bounded scheduling resolution."""
import ast, hashlib, importlib.util, json, random, sys, time
from pathlib import Path
P=Path('/tmp/pr-efficient1800'); rel=Path('research/dirty-shadow-8q-obstruction');pkg=P/'sources/2840'/rel
sys.path.insert(0,str(pkg))
import model, independent

def nodes(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def total(parts):
    from collections import Counter
    counts=[0,0];hs=[Counter(),Counter(),Counter()]
    for r in parts:
        for i in range(2):counts[i]+=r[i]
        for i in range(3):hs[i].update(r[i+2])
    return counts,hs

def main():
    start=time.monotonic();inputs={}
    rng=random.Random(2840)
    combos=[tuple(sorted(rng.sample(range(1,32),7))) for _ in range(333)]
    combos+=list(__import__('itertools').combinations(range(1,9),7))
    items=[(tuple(sorted(rng.sample(range(1,32),6))),None) for _ in range(333)]
    items=[(six,dup) for six,_ in items for dup in (0,)+six]
    checks=[]
    for name,module,worker,dup in [('model',model,'_spectrum_worker','_one_dup_worker'),('independent',independent,'_d7_worker','_dup_worker')]:
        old=P/'prior-revisions/2840-original'/rel/(name+'.py');new=pkg/(name+'.py')
        a,b=nodes(old),nodes(new);allowed=({'enumerate_distinct7_shadow_spectrum','enumerate_one_duplicate_shadow_spectrum'} if name=='model' else {'distinct7','one_dup'})
        assert set(b)==set(a)|{'_bounded_parts'}
        assert all(a[k]==b[k] for k in a if k not in allowed)
        for f in (old,new):inputs[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
        for kind,fn,seq in [('distinct',getattr(module,worker),combos),('duplicate',getattr(module,dup),items),('empty',getattr(module,worker),[])]:
            before=fn(seq);parts=module._bounded_parts(fn,iter(seq))
            assert total(parts)==total([before])
            if name=='model' and kind=='distinct':
                first={'even':{},'dirty':{},'clean':{}}
                for r in parts:
                    for k in first:module._merge_first(first[k],r[5][k])
                assert first==before[5]
            if name=='model' and kind=='duplicate':
                mins=[999]*3;wits=[None]*3
                for r in parts:
                    for i in range(3):
                        if r[5][i]<mins[i]:mins[i]=r[5][i];wits[i]=r[6][i]
                assert mins==before[5] and wits==before[6]
            checks.append(dict(module=name,kind=kind,records=len(seq),chunks=len(parts)))
    out=dict(status='passed',seconds=time.monotonic()-start,input_sha256=inputs,checks=checks,scope='All mathematical worker ASTs unchanged. Real bounded pools match serial workers on random full-label and rank-deficient cases, duplicate cases, empty input, all histograms and both witness selection rules. Full original-domain primary replay remains required.')
    (P/'provenance-2840-streaming.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS bounded scheduling',json.dumps(checks),'seconds',round(out['seconds'],3))
if __name__=='__main__':main()
