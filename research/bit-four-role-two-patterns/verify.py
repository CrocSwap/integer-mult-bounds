"""Exact finite pattern-space classification; stdlib only. Apache-2.0."""
from itertools import combinations, permutations
from pathlib import Path
import json, hashlib, subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok,msg):
    if not ok: raise ValueError(msg)
def rank(rows):
    basis={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k not in basis: basis[k]=x; break
            x^=basis[k]
    return len(basis)
def span(rows):
    s={0}
    for r in rows: s|={x^r for x in tuple(s)}
    return frozenset(s)
def apply(N,v,w):
    return sum((((N>>(w*i))&((1<<w)-1)&v).bit_count()%2)<<i for i in range(w))
def outer(x,y,w):
    return sum(y<<(w*i) for i in range(w) if x>>i&1)
def patterns(w):
    diagonal=sum(1<<(i*w+i) for i in range(w))
    projs=sorted({outer(x,y,w) for x in range(1,1<<w) for y in range(1,1<<w) if (x&y).bit_count()%2})
    pools={}
    for n in projs: pools.setdefault(n&~diagonal,[]).append(n)
    return projs,pools
def subspaces(w):
    result={frozenset({0})}
    for d in range(w):
        for s in tuple(result):
            if len(s)==1<<d:
                for v in range(1,1<<w):
                    if v not in s: result.add(frozenset(s|{x^v for x in s}))
    return sorted(result,key=lambda s:(len(s),sorted(s)))
def classify(w):
    projs, pools=patterns(w)
    pats=sorted(set(pools)-{0})
    spaces=sorted({tuple(sorted((a,b,a^b))) for a,b in combinations(pats,2)})
    subs=subspaces(w); proper=[s for s in subs if 1<len(s)<1<<w]
    dims={d:[s for s in proper if len(s)==1<<d] for d in range(1,w)}
    flags=[f for f in __import__('itertools').product(*(dims[d] for d in range(1,w))) if all(f[i]<f[i+1] for i in range(len(f)-1))]
    inv={n:{s for s in proper if all(apply(n,v,w) in s for v in s)} for n in projs}
    # Separate dense tuple oracle enumerates every binary matrix, selecting rank-one
    # images by cardinality and idempotence by actual action rather than outer factors.
    if w==4:
        def dense_action(n,v):
            return tuple(sum(((n>>(i*w+j))&1)*v[j] for j in range(w))%2 for i in range(w))
        vectors=list(__import__('itertools').product((0,1),repeat=w))
        independent=[]
        for n in range(1<<(w*w)):
            images={dense_action(n,v) for v in vectors}
            if len(images)==2 and all(dense_action(n,v)==v for v in images): independent.append(n)
        require(independent==projs,'dense projector oracle')
        for n in projs:
            for sub in proper:
                tuples={tuple(v>>i&1 for i in range(w)) for v in sub}
                require((sub in inv[n])==all(dense_action(n,v) in tuples for v in tuples),'dense invariant oracle')
    flagmasks={n:sum(1<<i for i,f in enumerate(flags) if all(s in inv[n] for s in f)) for n in projs}
    def perm(n,p,transpose=False):
        return sum(1<<(p[j]*w+p[i] if transpose else p[i]*w+p[j]) for i in range(w) for j in range(w) if n>>(i*w+j)&1)
    sym=list(permutations(range(w)))
    reps={}; realized_flags=[]; counts={'spaces':len(spaces),'flagged':0,'no_flag_reducible':0,'irreducible':0}
    allmask=(1<<len(flags))-1
    for s in spaces:
        pool=sorted(n for pat in s for n in pools.get(pat,[]))
        mask=allmask; common=set(proper)
        for n in pool: mask&=flagmasks[n]; common&=inv[n]
        # Independent invariant-subspace dynamic program, without enumerated flags.
        reachable={frozenset({0})}
        for d in range(1,w):
            reachable={v for v in common if len(v)==1<<d and any(u<v for u in reachable)}
        has_flag=bool(reachable)
        require(has_flag==bool(mask),'flag oracle disagreement')
        key='flagged' if has_flag else ('no_flag_reducible' if common else 'irreducible')
        counts[key]+=1
        if all(a in pools for a in s):
            require(has_flag,'fully realized plane without full flag')
            f=flags[(mask&-mask).bit_length()-1]
            realized_flags.append({'patterns':list(s),'flag':[sorted(v) for v in f]})
        rep=min(tuple(sorted(perm(a,p,t) for a in s)) for p in sym for t in (False,True))
        if rep not in reps: reps[rep]={'patterns':list(rep),'orbit_size':0,'classification':key,'pool_size':len(pool),'common_invariant_dimensions':sorted({(len(v).bit_length()-1) for v in common}),'flag_count':mask.bit_count()}
        require(reps[rep]['classification']==key,'symmetry mismatch')
        reps[rep]['orbit_size']+=1
    counts.update(projectors=len(projs),nonzero_patterns=len(pats),proper_subspaces=len(proper),full_flags=len(flags),symmetry_orbits=len(reps))
    records=sorted(reps.values(),key=lambda r:r['patterns'])
    require(sum(r['orbit_size'] for r in records)==len(spaces),'orbit coverage')
    return {'dimension':w,'counts':counts,'orbits':records,'fully_realized_flags':realized_flags}
def main():
    # Preserve immutable source byte pins, including Git provenance.
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for s in pins['files']:
        data=subprocess.check_output(['git','cat-file','blob',s['git_blob']],cwd=ROOT)
        require(hashlib.sha256(data).hexdigest()==s['sha256'],'provenance mismatch')
        if s['usage']=='input': require((ROOT/s['path']).read_bytes()==data,'input drift')
    # All-three-realized is not true for W3? The same enumerator checks it explicitly.
    small=classify(3); result=classify(4)
    ref=json.loads((HERE/'RELATED-SOURCE.json').read_text())
    raw=(HERE/ref['local']).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==ref['sha256'],'PR1733 byte drift')
    old=json.loads(raw)['pattern_census']
    edges=[(i,j) for i in range(4) for j in range(4) if i!=j]
    def unpack(v): return sum((v>>k&1)<<(4*i+j) for k,(i,j) in enumerate(edges))
    full={tuple(x['patterns']) for x in result['fully_realized_flags']}
    require(len(full)==old['realizable_two_dimensional_pattern_planes']==196,'196 domain')
    exceptions={tuple(sorted(unpack(a) for a in row['patterns'])) for row in old['nontriangular_planes']}
    require(len(exceptions)==20 and exceptions<=full,'20 coordinate-cyclic cases')
    require(result['counts']['no_flag_reducible']==72 and result['counts']['irreducible']==0,'reducible is not flag control')
    require(small['counts']['spaces']==129 and small['counts']['flagged']==123,'three-role predecessor regression')
    # Acceptance and failure controls are exact invariant-space examples.
    tri=[outer(1,3,4),outer(2,2,4)]
    cyc=[outer(7,7,4),outer(1,1,4),outer(2,2,4),outer(4,4,4)]
    require(all((n&sum(1<<(4*i+j) for i in range(4) for j in range(i)))==0 for n in tri),'triangular fixture')
    # The cyclic 3x3 J plus coordinate projectors has no invariant line inside its active cube.
    require(not any(all(apply(n,v,4) in (0,v) for n in cyc) for v in range(1,8)),'nonflag control')
    payload={'three_role_control':small['counts'],'four_role':result,'controls':4,'scope':'Complete scalar pattern spaces only; no realizable frame relation, paid word or kappa claim.'}
    if '--write' in sys.argv: (HERE/'CERTIFICATE.json').write_text(json.dumps(payload,indent=2)+'\n')
    else: require(json.loads((HERE/'CERTIFICATE.json').read_text())==payload,'certificate mismatch')
    print('PASS_FOUR_ROLE_TWO_PATTERNS',json.dumps(result['counts'],sort_keys=True))
if __name__=='__main__': main()
