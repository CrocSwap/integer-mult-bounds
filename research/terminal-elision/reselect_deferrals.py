#!/usr/bin/env python3
"""Apply pinned PR114's refined placement to a frozen explicit scalar word.

This is a credited composition experiment, not a new claim for radical
extraction or dim-squared/reach priority. Every old scalar operation, frame,
and exact adjoint is retained. A separate checker must verify the new schedule.
"""
import argparse
import ast
from collections import Counter,defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from functools import lru_cache
from fractions import Fraction
from types import SimpleNamespace


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--placement-repo',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert __debug__
    a.output.mkdir(parents=True,exist_ok=False)
    path=(a.placement_repo.resolve()/'research/cyclic-deferred/complex_deferred.py'
          if a.placement_repo else Path(__file__).with_name('references')/'placement_5633a2.py')
    assert hashlib.sha256(path.read_bytes()).hexdigest()=='910f86649f72dab4490562f1fa0ea7f887ee5849f888fa37dd4f8e832d3eb47d'
    # Extract the exact pure functions without executing upstream producer
    # imports or main. The entire unmodified, credited source is retained.
    names={'dot','reduce','kernel','restrict','contains','cap','nondeg',
           'sat_basis','sat_dot','sat_contained','sat_cap','sat_nondeg',
           'sat_nonsingular_part','saturated_placement'}
    tree=ast.parse(path.read_text())
    selected=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in names]
    assert {node.name for node in selected}==names
    ns={'defaultdict':defaultdict,'lru_cache':lru_cache,'Fraction':Fraction}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),ns)
    lib=SimpleNamespace(**ns)
    w=json.loads(gzip.decompress((a.source/'word.json.gz').read_bytes()))
    p=json.loads((a.source/'complex-profile.json').read_text())
    h,v,R=w['h'],w['v'],w['R'];m=h*h;N=v*v
    U={int(x):b for x,b in w['frames'].items()}
    rr={int(s):j for s,j in w['role_root'].items()}
    touched={s for s,j in rr.items() if w['kind'][j]}
    for i in w['phase_one']:
        o=w['ops'][i]
        if o[0] in ('add','copy'):touched.update(o[1:3])
    masks=[U[i+1][0] for i in range(v)]
    cand={}
    for s in range(R):
        if s in touched or any(w['adjoint_centre'][s] or []):continue
        X=lib.restrict(U[w['first_node'][s]],[masks[t] for t in w['reach'][s]])
        if X and lib.nondeg(X):cand[s]=X
    placed=lib.saturated_placement(cand,w['reach'])
    w['sigma']=placed;w['deferred']=sorted(placed,key=lambda s:(len(placed[s]),s))
    z=Counter();levels=defaultdict(set)
    for s,ds in enumerate(w['chain_dims']):
        ds[0]=len(placed.get(s,()))
        for x,y in zip(ds[:-1],ds[1:-1]):
            assert y>=x
            if y>x:z[y-x]+=2*v
        if s in rr and w['kind'][rr[s]]:z[h-1]+=2*v
        z[h-ds[-2]]+=2*v;z[m-h+ds[0]]+=2*v
    for s,X in placed.items():
        assert lib.nondeg(X) and lib.contains(X,U[w['first_node'][s]])
        for t in w['reach'][s]:
            assert all(not lib.dot(x,masks[t]) for x in X)
            levels[t].add(len(X))
    for t in range(v):
        ds=sorted(levels[t]|{0,h-1})
        for x,y in zip(ds,ds[1:]):z[y-x]+=2*v
    z[h-1]+=2*N;z[(h-1)**2]+=2*N;z[1]+=N;z.pop(0,None)
    assert sum(t*c for t,c in z.items())==p['total_rank']
    p.update(deferred_roles=len(placed),deferred_dims=dict(sorted(Counter(map(len,placed.values())).items())),
        child_multiplicities=dict(sorted(z.items())),maxchild=max(z),
        replay={'scope':'Changed placement; independent exact verifier required, no inherited random replay claim'},
        placement='Unchanged saturated_placement from PR114 pin5633a22443940f424dc2a09f44b2f447890e0074')
    (a.output/'word.json.gz').write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode(),mtime=0))
    (a.output/'complex-profile.json').write_text(json.dumps(p,indent=2)+'\n')
    # This frozen original producer is provided solely as the same F2 helper
    # library consumed by salvage_deferrals.py, not the new placement entrypoint.
    shutil.copyfile(a.source/'producer.py',a.output/'producer.py')
    (a.output/'REPRODUCE.txt').write_text('Use reselect_deferrals.py, not producer.py, to regenerate this changed placement.\n')
    paths=[a.source/'word.json.gz',a.source/'complex-profile.json',a.source/'producer.py',path,Path(__file__)]
    (a.output/'SOURCE.json').write_text(json.dumps({str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
    (a.output/'reselection-source.py').write_bytes(Path(__file__).read_bytes())
    print('PASS credited reselect; candidates',len(cand),'placed',len(placed),flush=True)


if __name__=='__main__':main()
