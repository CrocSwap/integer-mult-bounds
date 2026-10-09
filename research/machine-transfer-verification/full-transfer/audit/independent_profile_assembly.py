"""Rebuild complete PR71/73 child multiplicities from the two paid axis profiles.

No contributor module is imported. This does not repeat CRT computation: it
binds the exact freshly reprofiled inputs and independently assembles them.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from math import comb
from pathlib import Path

ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
r=args.repo; m=575;N=comb(23,3)*comb(25,3)
c=json.loads((r/'research/round6-pr71/parameter-certificate.json').read_text());bit=c['bit']
profiles=[json.loads((r/f'certificates/split-pair-profiles-{h}.json').read_text()) for h in (23,25)]
record=json.loads((r/'certificates/split-pair-compiler.json').read_text())
W=2*N;L=0;parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}),'paid_endpoint_copy':Counter({1:N})};hashes={}
for h,p in zip((23,25),profiles):
 assert p['h']==h and p['v']==comb(h,3) and p['loss']==h*(h-1)
 assert p['R']==record['axes'][str(h)]['compiled']['roles']==record['axes'][str(h)]['replay']['roles']
 assert p['crt_disagreements']==0 and p['field_prime']==2**61-1
 assert sum(t*n for t,n in enumerate(p['blocks']))==h*p['R']+p['loss']==p['rank_sum']
 assert p['blocks'][0]==p['blocks'][h]==0
 rep=N//p['v'];assert rep*p['v']==N
 bank=rep*p['R'];W+=bank;L+=rep*p['loss']
 parts[f'internal_{h}']=Counter({t:rep*n for t,n in enumerate(p['blocks']) if n})
 parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
 parts[f'data_growth_{h}']=Counter({1:2*N,h-2:2*N})
 path=r/f'certificates/split-pair-profiles-{h}.json';hashes[str(path.relative_to(r))]=sha256(path.read_bytes()).hexdigest()
rows=sum(parts.values(),Counter());mass=sum(t*n for t,n in rows.items())
assert rows=={int(t):n for t,n in bit['child_multiplicities'].items()}
assert {k:dict(v) for k,v in parts.items()}=={k:{int(t):n for t,n in v.items()} for k,v in bit['parts'].items()}
assert (m,N,W,L,mass,max(rows),m*W-mass)==(bit['m'],bit['N'],bit['W'],bit['L'],bit['total_rank'],bit['maxchild'],bit['deficit'])
assert mass==m*W-N+L and m*W-mass==1846900 and max(rows)==529
args.output.write_text(json.dumps(dict(status='PASS independent complete paid-profile assembly',m=m,N=N,W=W,L=L,rank_mass=mass,deficit=m*W-mass,parts=parts,child_multiplicities=dict(sorted(rows.items())),profile_input_sha256=hashes,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),scope='Exact reconstruction from freshly checked axis profiles plus inherited fixed data/exterior recipe; ambient physical realization remains separate'),indent=2)+'\n')
print('PASS independent complete paid-profile assembly:',len(rows),'rows, W',W,'rank mass',mass)
