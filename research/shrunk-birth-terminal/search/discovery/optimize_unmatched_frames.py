"""Bounded coordinate search over unmatched deferral frame choices.

Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0.
Uses canonical binary algebra from the pinned PR125-derived source, preserves
all protected matched birth frames, and reports complete profiles only.
"""
from pathlib import Path
from collections import Counter,defaultdict
from functools import lru_cache
from hashlib import sha256
import ast,gzip,json,math,pickle,sys,time

W=Path(__file__).resolve().parent;SOURCE=W/'protected-prune/FRAMES.pkl'
MATCH=W/'protected-prune/BIRTH_MATCHES.json.gz';OUT=W/'protected-coordinates';OUT.mkdir(exist_ok=True)
ALG=W/'repo/research/r12-logical-frames/complex_deferred.py'
names={'sat_basis','sat_dot','sat_contained','sat_cap','sat_nondeg','sat_nonsingular_part'}
tree=ast.parse(ALG.read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
assert {n.name for n in nodes}==names
env=dict(lru_cache=lru_cache);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ALG),'exec'),env)
basis,inside,cap,nondeg,part=(env[n]for n in ('sat_basis','sat_contained','sat_cap','sat_nondeg','sat_nonsingular_part'))
start=time.monotonic();g=pickle.loads(SOURCE.read_bytes());raw=json.loads(gzip.decompress(MATCH.read_bytes()))
protected={r['recipient']:tuple(r['birth_frame'])for r in raw['pairs']};assert all(g['placed'][s]==F for s,F in protected.items())
v=g['v'];h=g['h'];m=h*h;ext=m-h
weight=[0]+[round(d*math.log(d)*10**9)for d in range(1,m+1)]
level_counts=defaultdict(Counter)
for t,roles in g['bytarget'].items():
    for s in roles:level_counts[t][len(g['placed'][s])]+=1
@lru_cache(None)
def targets(s):
    mask=g['reach'][s];out=[]
    while mask:b=mask&-mask;mask-=b;out.append(b.bit_length()-1)
    return out
@lru_cache(None)
def kernel(A):
    A=basis(A);piv={a.bit_length()-1 for a in A};out=[]
    for j in range(h):
        if j not in piv:
            x=1<<j
            for r in A:
                if r>>j&1:x|=1<<(r.bit_length()-1)
            out.append(x)
    return basis(out)
def gain(s,d):
    r=len(g['U'][g['first'][s]])
    score=weight[r-d]+weight[ext+d]-weight[r]-weight[ext]
    for t in targets(s):
        counts=level_counts[t]
        if counts[d] or d==0:continue
        a=max((x for x in counts if x<d),default=0)
        b=min((x for x in counts if x>d),default=h-1)
        score+=weight[d-a]+weight[b-d]-weight[b-a]
    return score
def histogram():
    H=Counter()
    for s,ds in enumerate(g['chain_dims']):
        for a,b in zip(ds,ds[1:]):
            if b>a:H[b-a]+=2*v
        if s in g['terminal']and g['terminal'][s]>=len(g['roots'])-h:H[h-1]+=2*v
        H[h-ds[-1]]+=2*v;H[ext+ds[0]]+=2*v
    for t in range(v):
        ds=sorted(set(level_counts[t])|{0,h-1})
        for a,b in zip(ds,ds[1:]):H[b-a]+=2*v
    N=v*v;H[h-1]+=2*N;H[(h-1)**2]+=2*N;H[1]+=N;H.pop(0,None)
    return dict(sorted((t,n)for t,n in H.items()if n))
assert histogram()==dict(g['histogram'])
original=pickle.loads((W/'pure-frame-full/FRAMES.pkl').read_bytes())
roles=sorted(set(original['placed'])-protected.keys())
moves=[]
for sweep in range(3):
    count=0
    for s in roles:
        old=g['placed'].pop(s,());d0=len(old)
        for t in targets(s):
            if d0:
                g['bytarget'][t].remove(s);level_counts[t][d0]-=1
                if not level_counts[t][d0]:del level_counts[t][d0]
        neighbors={g['placed'][w]for t in targets(s)for w in g['bytarget'][t]}
        limit=cap(g['U'][g['first'][s]],kernel(tuple(g['tm'][t]for t in targets(s))))
        candidates={(),old,part(limit)}
        for F in neighbors:
            if inside(F,limit):candidates.add(F)
            else:candidates.add(part(cap(F,limit)))
        feasible=[F for F in candidates if nondeg(F)and inside(F,limit)and all(inside(F,B)or inside(B,F)for B in neighbors)]
        assert old in feasible
        scores={len(F):gain(s,len(F))for F in feasible};best=max(feasible,key=lambda F:(scores[len(F)],F==old,-len(F),F))
        improvement=scores[len(best)]-scores[d0]
        if improvement>0:
            count+=1;moves.append(dict(sweep=sweep,role=s,before=list(old),after=list(best),integer_gain=improvement))
        else:best=old
        if best:g['placed'][s]=best
        g['chain_dims'][s][0]=len(best)
        for t in targets(s):
            if best:g['bytarget'][t].append(s);level_counts[t][len(best)]+=1
        if time.monotonic()-start>120:raise RuntimeError('Bounded coordinate search timed out; no partial candidate')
    print('sweep',sweep,'moves',count,'seconds',time.monotonic()-start,flush=True)
    if count==0:break
assert all(g['placed'][s]==F for s,F in protected.items())
for t,roles in g['bytarget'].items():
    roles.sort(key=lambda s:(len(g['placed'][s]),s))
    assert all(inside(g['placed'][a],g['placed'][b])for a,b in zip(roles,roles[1:]))
g['histogram']=histogram();p=g['base_profile'];p.update(child_multiplicities=g['histogram'],deferred_roles=len(g['placed']),deferred_dims=dict(Counter(map(len,g['placed'].values()))),replay=dict(screening_only=True,scratch_restored=None,y_plus_x=None))
assert sum(t*n for t,n in g['histogram'].items())==p['total_rank']
receipt=dict(status='SCREEN ONLY complete histogram and exact nested nondegenerate frames; scalar word not replayed',protected=len(protected),remaining_deferred=len(g['placed']),moves=moves,seconds=time.monotonic()-start,source_pins={str(q.resolve()):sha256(q.read_bytes()).hexdigest()for q in (SOURCE,MATCH,ALG,Path(__file__),W/'pure-frame-full/FRAMES.pkl')})
p['birth_aware_coordinates']=receipt
data=pickle.dumps(g,protocol=4);(OUT/'FRAMES.pkl').write_bytes(data);receipt['checkpoint_sha256']=sha256(data).hexdigest();(OUT/'COORDINATES.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:x for k,x in receipt.items()if k!='moves'},indent=2))
