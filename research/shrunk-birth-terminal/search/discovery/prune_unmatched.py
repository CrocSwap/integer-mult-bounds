"""Bounded birth-aware post-placement pruning; discovery profile only.

Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0.
Retains the PR125 saturated placement and root R12 weighted birth pairs.
Only unmatched deferrals with negative complete marginal gain are removed.
No scalar-word correctness claim is made by this screening program.
"""
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
import gzip,json,math,pickle,sys,time

W=Path(__file__).resolve().parent
SOURCE=W/'pure-frame-full/FRAMES.pkl'
MATCH=Path('/Users/chafreaky/Documents/personal/integer-mult-research-20261008/r12-composition/research/composed-shrunk-birth/variants/weighted/BIRTH_MATCHES.json.gz')
OUT=W/(sys.argv[1] if len(sys.argv)>1 else 'protected-prune')
OUT.mkdir(exist_ok=True)
start=time.monotonic()
g=pickle.loads(SOURCE.read_bytes())
raw=json.loads(gzip.decompress(MATCH.read_bytes()))
protected={r['recipient']:tuple(r['birth_frame']) for r in raw['pairs']}
assert all(g['placed'][s]==F for s,F in protected.items())
v=g['v'];h=g['h'];m=h*h;ext=m-h
level_counts=defaultdict(Counter)
for t,roles in g['bytarget'].items():
    for s in roles:level_counts[t][len(g['placed'][s])]+=1
weight=[0]+[round(d*math.log(d)*10**9) for d in range(1,m+1)]

def targets(s):
    mask=g['reach'][s]
    while mask:
        b=mask&-mask;mask-=b;yield b.bit_length()-1

def gain(s):
    d=len(g['placed'][s]);r=len(g['U'][g['first'][s]])
    score=weight[r-d]+weight[ext+d]-weight[r]-weight[ext]
    for t in targets(s):
        counts=level_counts[t]
        if counts[d]>1:continue
        a=max((x for x in counts if x<d),default=0)
        b=min((x for x in counts if x>d),default=h-1)
        score+=weight[d-a]+weight[b-d]-weight[b-a]
    return score

def histogram():
    H=Counter()
    for s,ds in enumerate(g['chain_dims']):
        for a,b in zip(ds,ds[1:]):
            if b>a:H[b-a]+=2*v
        if s in g['terminal'] and g['terminal'][s]>=len(g['roots'])-h:H[h-1]+=2*v
        H[h-ds[-1]]+=2*v
        H[ext+ds[0]]+=2*v
    for t in range(v):
        ds=sorted(set(level_counts[t])|{0,h-1})
        for a,b in zip(ds,ds[1:]):H[b-a]+=2*v
    N=v*v;H[h-1]+=2*N;H[(h-1)**2]+=2*N;H[1]+=N;H.pop(0,None)
    return dict(sorted((t,n)for t,n in H.items()if n))

assert histogram()==dict(g['histogram'])
removed=[]
while True:
    candidates=[(gain(s),s) for s in g['placed'] if s not in protected]
    score,s=min(candidates,default=(0,-1))
    if score>=0:break
    d=len(g['placed'].pop(s));g['chain_dims'][s][0]=0
    for t in targets(s):
        g['bytarget'][t].remove(s);level_counts[t][d]-=1
        if not level_counts[t][d]:del level_counts[t][d]
    removed.append(dict(role=s,dimension=d,integer_gain_on_removal=-score))
assert all(g['placed'][s]==F for s,F in protected.items())
g['histogram']=histogram()
p=g['base_profile'];p.update(child_multiplicities=g['histogram'],deferred_roles=len(g['placed']),deferred_dims=dict(Counter(map(len,g['placed'].values()))),replay=dict(screening_only=True,scratch_restored=None,y_plus_x=None))
assert sum(t*n for t,n in g['histogram'].items())==p['total_rank']
assert p['deficit']==m*p['W']-p['total_rank']
receipt=dict(status='SCREEN ONLY complete histogram and protected birth frames preserved; scalar word not replayed',source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),protected_matches_sha256=sha256(MATCH.read_bytes()).hexdigest(),protected=len(protected),original_deferred=p['deferred_roles']+len(removed),remaining_deferred=len(g['placed']),removed=removed,seconds=time.monotonic()-start)
p['birth_aware_pruning']=receipt
data=pickle.dumps(g,protocol=4);(OUT/'FRAMES.pkl').write_bytes(data);receipt['checkpoint_sha256']=sha256(data).hexdigest()
(OUT/'PRUNE.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:x for k,x in receipt.items()if k!='removed'},indent=2))
