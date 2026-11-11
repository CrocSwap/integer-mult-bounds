"""Price existing-chart rank-one endpoint extensions before scalar support."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy

PINS = {
 'complex/audit.py':'67b006627fd4e07c349f48f31e6d541c62804416bdc85f664a3607dd1b386efb',
 'complex/source/inputs/WORD.json.gz':'2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
 'complex/source/inputs/EARLY-RESULT.json':'691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
 'complex/source/inputs/CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
 'complex/source/powers.py':'c0c460b464d7c836fb887010b57119be322aae686736b86820aae3544d380bee',
}


def space(rows):
    span = {0}
    for row in rows:
        assert row not in span
        span |= {v^row for v in span}
    return span


def screen(root):
    for name, digest in PINS.items():
        assert sha256((root/name).read_bytes()).hexdigest()==digest, name
    source=root/'complex/source'
    w=json.loads(gzip.decompress((source/'inputs/WORD.json.gz').read_bytes()))
    audit=runpy.run_path(str(root/'complex/audit.py'))
    _,_,_,_,_,_,copies,paid,targets,_=audit['read_model']()
    assert copies==17
    k=Q(json.loads((source/'inputs/EARLY-RESULT.json').read_bytes())['price']['independent_raw_bracket'][1])
    power=cache(runpy.run_path(str(source/'powers.py'))['power'])
    def moment(net):
        terms=[sorted(n*x for x in power(r,k)) for r,n in net.items() if n]
        return tuple(sum(t[i] for t in terms) for i in (0,1))
    signed=targets.copy()
    signed.subtract(paid)
    baseline=moment(signed)
    assert baseline[1]<0
    dims=list(map(len,w['frames']))
    spaces=[space(v) for v in w['frames']]
    main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2']+w['hosted']['Y2'])
    roles=defaultdict(list)
    for h,(u,v) in enumerate(zip(w['initial'],w['final'],strict=True)):
        if h not in main:
            assert spaces[u]<spaces[v]
            roles[u,v].append(h)
    frames=defaultdict(list)
    for f,rank in enumerate(dims):
        frames[rank].append(f)
    stock=[]
    @cache
    def gain(r,a,b):
        assert a+b==r+1 and a>=2 and b>=2
        delta=Counter((a,b))
        delta[r]-=1
        delta[1]-=1
        assert sum(n*j for j,n in delta.items())==0
        return moment({j:copies*n for j,n in delta.items()})
    for (u,v),helpers in sorted(roles.items()):
        r=dims[v]-dims[u]
        if not 3<=r<=8:
            continue
        start=[('input',f,v) for f in frames[dims[u]-1] if spaces[f]<spaces[u]]
        end=[('output',u,f) for f in frames[dims[v]+1] if spaces[v]<spaces[f]]
        for side,a0,b0 in start+end:
            for a in range(2,(r+1)//2+1):
                b=r+1-a
                lo,hi=gain(r,a,b)
                assert lo>0
                stock.append({'side':side,'prior':[u,v],'new':[a0,b0],
                    'old_rank':r,'parts':[a,b],'extender_roles':helpers,
                    'new_cohort_before_extension':roles.get((a0,b0),[]),
                    'complete_margin_interval':[str(baseline[0]+lo),str(baseline[1]+hi)],
                    'margin_lower':lo})
    stock.sort(key=lambda r:(-r['margin_lower'],r['side'],r['prior'],r['new'],r['parts']))
    for row in stock:
        row.pop('margin_lower')
    return {'head':audit['HEAD'],'source_pins':PINS,'copies':copies,'crossing_upper':str(k),
        'baseline_moment_interval':list(map(str,baseline)),'typed_signatures':len(stock),
        'rank_hist':dict(Counter(r['old_rank'] for r in stock)),
        'side_hist':dict(Counter(r['side'] for r in stock)),
        'all_source_helpers':sum(map(len,roles.values())),'rows':stock,
        'physical_sites':0,'support_tested':0}


if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    print(json.dumps(screen(args.root),indent=2,sort_keys=True))
