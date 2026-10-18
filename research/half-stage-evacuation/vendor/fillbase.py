"""Construction-search helpers (not part of the verification; reconstruct.py checks the shipped fill literally): T74 windows/bins, the predecessor fill, re-indexing after helper removals, literal idle/profile check, mpmath pricing.
Search path used here: reindex.py (PR2526 fill, the two removed helpers dropped) -> odd.py -> evac.py with EVMAX=24, 44, 48 -> new/borrow-fill/FILL.json.gz."""
import json,gzip,importlib.util,collections
from pathlib import Path
import os
P=Path(os.environ.get('FILLPKG') or Path(__file__).resolve().parents[3])   # package whose ORDER/DISPATCH/windows/fill are read; for reindex.py point FILLPKG at the PR2526 package (its fill and removed set)
def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
plan=read(P/'inputs/PLAN.json');parent=read(P/'inputs/GLOBAL-TEMPLATE.json.gz');T=plan['T']
order=read(P/'new/borrow-fill/ORDER.json');dispatch={(s,r):pid for s,r,pid in read(P/'new/borrow-fill/DISPATCH.json')}
sp=importlib.util.spec_from_file_location('windows',P/'vendor/build_parent.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
windows,schedule=mod.actual_windows(parent,order)
pairs,sides=plan['pairs'],plan['sides']
prov=read(P/'new/BORROW-PROVIDERS.json')
fill=read(P/'new/borrow-fill/FILL.json.gz')
for s_,r_,p_ in fill['dispatch_overrides']:dispatch[s_,r_]=p_
def family(rep,child,port):return rep*896+(2*pairs[str(child)]+sides[str(child)])*112+port
def remaining(removed):return [r for r in range(224,704) if r not in set(removed)]
def reindex_rows(rows,old_removed,new_removed):
    old=remaining(old_removed);new=remaining(new_removed);nid={r:i for i,r in enumerate(new)}
    out=[]
    for t,hh,rep,ch,port,off in rows:
        r=old[hh]
        if r in nid:out.append([t,nid[r],rep,ch,port,off])
    return out
def compact(rows,widths_of):
    byb=collections.defaultdict(list)
    for i,x in enumerate(rows):byb[x[2],x[3],x[4]].append(i)
    out=[list(x) for x in rows]
    for k,ids in byb.items():
        off=0
        for i in sorted(ids,key=lambda i:rows[i][5]):
            out[i][5]=off;off+=widths_of(rows[i])
    return out
def check(rows,widths,paid):
    """literal reconstruct.py checks; returns idle Counter and total profile"""
    R=len(next(iter(widths.values())))
    helpers=collections.defaultdict(set);fams=collections.defaultdict(set);used=collections.defaultdict(set)
    assert len(rows)==len(order)*R
    for t,hh,rep,ch,port,off in rows:
        stage,replica=order[t];call=(stage,replica);w=widths[dispatch[call]][hh]
        cap,allowed=windows[f'{rep},{ch}']
        assert t in allowed and 0<=port<112 and 0<=hh<R
        f=family(rep,ch,port)
        assert hh not in helpers[call] and f not in fams[call]
        helpers[call].add(hh);fams[call].add(f)
        cells=set(range(off,off+w));assert off>=0 and off+w<=cap and not used[rep,ch,port]&cells
        used[rep,ch,port]|=cells
    assert all(s==set(range(R)) for s in helpers.values())
    idle=collections.Counter()
    for key,(cap,times) in windows.items():
        r,ch=map(int,key.split(','))
        for port in range(112):
            c=used[r,ch,port];assert c==set(range(len(c))),'gap'
            if cap-len(c):idle[cap-len(c)]+=1
    H=collections.Counter(idle)
    for sr in order:
        for r,n in paid[dispatch[tuple(sr)]].items():H[int(r)]+=n
    assert 73*plan['live']*2-sum(r*n for r,n in H.items())==2*plan['deficit'],'rank-mass deficit'
    return idle,H
def kappa(H,dps=40):
    import mpmath as mp
    mp.mp.dps=dps;m=73;W=66304
    f=lambda k:sum(mp.mpf(n*r)/(m*W)*mp.power(mp.mpf(m)/r,k) for r,n in H.items())-1
    return mp.findroot(f,(mp.mpf('0.0016'),mp.mpf('0.0018')),solver='anderson')
