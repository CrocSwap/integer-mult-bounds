"""Write the plan PR508's emitter checks: profile = sum over the 72 calls of the variant's local paid profile +
one climb per idle remainder (from the nominated owner map, recounted here from the roles alone).
Usage: compose_profile.py PLAN.json OWNERS.json.gz RETIMED_VARIANT OUT-PLAN.json"""
import gzip,json,sys,hashlib
from collections import Counter,defaultdict
PLAN,OWN,RET,OUT=sys.argv[1:5]
read=lambda p:json.loads(gzip.decompress(open(p,'rb').read())if p.endswith('.gz')else open(p,'rb').read())
plan=read(PLAN);roles=read(OWN);t=read(RET+'/split-centres/GLOBAL-TEMPLATE.json.gz');chk=read(RET+'/split-centres/LOCAL-CHECKS.json');canon=read(RET+'/split-centres/CANONICAL-WORD.json.gz')
R=560;V=120;T=8;M=73;DATA=7680
widths=[9-len(canon['frames'][canon['start'][240+h]])for h in range(R)];assert widths==plan['baseline_widths']
children={(z['child'],z['port']):z['rank']for z in t['idle_children']}
used=defaultdict(set)
for z in roles:
    i,orp,port,off,w=z['child'],z['owner_replica'],z['port'],z['offset'],z['width']
    assert w==widths[z['helper']]and off+w<=children[i,port]
    cells=set(range(off,off+w));assert not used[i,orp,port]&cells;used[i,orp,port]|=cells
rem=Counter()
for (i,port),r in children.items():
    for rep in range(T):
        u=used[i,rep,port];assert u==set(range(len(u)));left=r-len(u)
        if left:rem[left]+=1
paid=Counter(rem)
for c in t['calls']:
    for r,k in chk[c['orientation']]['paid_profile'].items():paid[int(r)]+=k
mass=sum(r*k for r,k in paid.items());assert M*DATA-mass==2496 and M*M>2*max(paid)**2
plan['profile']={str(r):k for r,k in sorted(paid.items())};plan['remainders']={str(r):k for r,k in sorted(rem.items())}
plan['local_profile']={str(r):k for r,k in sorted(Counter({int(r):k for r,k in next(iter(chk.values()))['paid_profile'].items()}).items())}
plan['owner_map_sha256']=hashlib.sha256(open(OWN,'rb').read()).hexdigest()
json.dump(plan,open(OUT,'w'),indent=1);print(json.dumps(dict(profile=plan['profile'],remainders=plan['remainders'],local=plan['local_profile'],mass=mass)))
