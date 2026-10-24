"""Exact controls for the written projection-profile theorem; standard library only."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

SEED = (0, 27456, 48576, 68320, 86592)
LIMIT = F(439277, 149175)
FSTAR = F(451, 130)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def counts(k, r):
    return (2**(k-r)-1+4**k-2**(k+r),
            2*(2**k-2**(k-r))+(2**r-1)*2**(k-1),
            (2**r-1)*(2**(r-1)-1)*2**(k-r) if r >= 2 else 0)

def step(previous):
    k = len(previous)
    return tuple(sum(c*previous[r-j] for j,c in enumerate(counts(k,r))
                     if 0 <= r-j < len(previous)) for r in range(k+1))

def h(r):
    return 1-F(3,2**(r+1))

def profiles(last=20, seed=SEED):
    out = {4: tuple(seed)}
    for k in range(5,last+1):
        out[k] = step(out[k-1])
    return out

def check_boundary(rows):
    certificate=[]
    for k in range(4,15):
        a=rows[k]
        # Integer cross products, no float conversions.
        n3=32*(10*a[3]-13*a[2])-10*a[1]
        n4=16*(26*a[4]-29*a[3])-26*a[1]
        require(n3>0 and n4>0, f'boundary gap at {k}')
        certificate.append({'k':k,'D3_gt_1_over_32':True,'D4_gt_1_over_16':True,
                            'positive_numerator_sha256': hashlib.sha256(f'{n3},{n4}'.encode()).hexdigest()})
    e3=4*FSTAR*(8+F(13,10)*4)/2**14
    e4=4*FSTAR*(16+F(29,26)*8)/2**14
    require(e3==F(14883,1331200)<F(1,64), 'first infinite-tail margin')
    require(e4==F(36531,1730560)<F(1,32), 'second infinite-tail margin')
    return certificate

def check_weighted_rows():
    checks=0
    for k in range(5,21):
        M=2**k
        for r in range(5,k+1):
            x=2**r
            def row(t):
                return {t-j:F(c)*h(t-j)/h(t) for j,c in enumerate(counts(k,t))}
            current,previous=row(r),row(r-1)
            S=lambda y:M*M-1-3*M-F(3*M,2)/(y*(y-F(3,2)))
            require(sum(current.values())==S(x), 'weighted mass identity')
            require(sum(previous.values())==S(x//2), 'preceding mass identity')
            delta=current[r]+current[r-1]-previous[r-1]
            require(delta==F(3*M,4)*(x*x-10*x+10)/(x*(x-F(3,2))), 'upper-tail identity')
            for t in range(r-3,r+1):
                require(sum(v for s,v in current.items() if s>=t)>=sum(v for s,v in previous.items() if s>=t), 'tail order')
            beta=F(2*M*M-6*M+1,2*M*M-3*M+1)
            require(beta-F(2*M-6,2*M-3)==F(3,(2*M-3)*(2*M*M-3*M+1)), 'strict gap identity')
            checks+=1
    return checks

def sources(package):
    root=package.parents[1]
    manifest=json.loads((package/'SOURCES.json').read_text())
    require(manifest['base_commit']=='a5df48c55ea806d7952b65acc9c76d878ff09b13','base pin')
    live=[row for row in manifest['files'] if row.get('usage')=='input']
    require(len(live)==2,'both source inputs required')
    for row in live:
        require(hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'], 'source mismatch: '+row['path'])
    original=(root/'research/projection-recursion-check/README.md').read_text()
    require(all(str(x) in original.replace(',','') for x in SEED[1:]), 'source seed')
    return {row['path']:row['sha256'] for row in live}

def result(package):
    pins=sources(package)
    rows=profiles()
    boundary=check_boundary(rows)
    weighted=check_weighted_rows()
    for k,a in rows.items():
        require(a[0]==0 and all(v>0 for v in a[1:]), 'profile positivity')
        require(max(F(v,a[1]) for v in a)<FSTAR,'global bound')
        require(all(F(a[r],1)/h(r)>=F(a[r-1],1)/h(r-1) for r in range(3,k+1)), 'weighted profile')
        if k>4:
            p=rows[k-1]
            require(F(a[k],a[1])<F(p[k-1],p[1]), 'finite descent control')
        require(F(a[k],a[1])>LIMIT,'limit calibration')
    require(F(rows[5][5],rows[5][1])==F(834241,278850),'source block5')
    require(F(rows[6][6],rows[6][1])==F(1188222,399685),'source block6')
    rejected=[]
    altered=list(SEED);altered[3]=0
    try: check_boundary(profiles(14,altered))
    except ValueError: rejected.append('missing_block3_seed_demand')
    else: raise ValueError('altered seed accepted')
    # A monotone concave seed alone cannot imply the claimed descent.
    flat=profiles(5,(0,1,1,1,1))
    require(F(flat[5][5],flat[5][1])>1,'generic monotone-seed negative control')
    return {'scope':'written all-k recurrence theorem; finite controls are not its quantifier proof',
            'seed':list(SEED),'strict_descent_from':4,'infimum':str(LIMIT),
            'infimum_attained':False,'source_sha256':pins,'boundary_certificate':boundary,
            'weighted_row_controls':weighted,'profile_controls_through':20,
            'negative_controls':rejected+['monotone_concave_seed_is_insufficient'],
            'first_ratios':{str(k):str(F(rows[k][k],rows[k][1])) for k in (4,5,6)}}
