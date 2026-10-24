"""Independent exact signed binary transport at every actual event. Apache-2.0."""
from copy import deepcopy
from . import source

def need(ok,msg):
    if not ok:raise ValueError(msg)
def span(b):
    out={0}
    for x in b:out|={v^x for v in list(out)}
    need(len(out)==2**len(b),'frame rank');return out
def apply(cols,x):
    out=0
    for j,g in enumerate(cols):
        if x>>j&1:out^=g
    return out
def audit(w):
    c=w['canonical'];spaces=[span(b) for b in c['frames']];maps={x['op']:x['G_columns'] for x in c['warps']}
    need(set(maps)==set(range(1,73)),'exact native maps')
    for op,cols in maps.items():need(len({apply(cols,x) for x in range(512)})==512,'invertible map')
    counts={};classes=set()
    for direction,word in w['programs'].items():
        n=0
        for e in word:
            if e[0]!='warp':continue
            _,role,op,a,b=e;src,dst=(a,b) if op>0 else (b,a)
            need({apply(maps[abs(op)],x) for x in spaces[src]}==spaces[dst],'signed warp transport does not carry actual source frame')
            n+=1;classes.add((op,a,b))
        counts[direction]=n
    need(counts=={'forward':240,'backward':240} and len(classes)==180,'exact complete warp-event coverage')
    return counts,classes

def run():
    w=source.js('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz');counts,classes=audit(w);controls=[]
    for direction in w['programs']:
        bad=deepcopy(w);p=bad['programs'][direction]
        need(p[3]==['warp',['L',273],-59,0,0] and p[4]==['warp',['L',273],59,0,0],'source-bound issue4571 fixture')
        p[3][4]=1;p[4][3]=1
        try:audit(bad)
        except ValueError as e:controls.append({'direction':direction,'mutated_object_sha256':source.digest(__import__('json').dumps(bad,sort_keys=True).encode()),'semantic_rejection':str(e)})
        else:raise ValueError('binary-frame mutation accepted')
    return {'status':'PASS_ALL480_SIGNED_WARP_EVENTS','counts':counts,'classes':len(classes),'semantic_controls_with_recomputed_hash':controls}
