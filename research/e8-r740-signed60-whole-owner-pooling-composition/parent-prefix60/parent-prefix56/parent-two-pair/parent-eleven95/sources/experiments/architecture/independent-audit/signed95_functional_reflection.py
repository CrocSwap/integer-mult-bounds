from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,struct,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/stage-search/pr445-signed95-eleven/signed';word=json.load(gzip.open(S/'word.json.gz','rt'));st=json.load(open(S/'records/249-states.json'));F={int(k):v for k,v in json.load(open(S/'records/frames.json'))['frames'].items()};events=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()));source=[{i:1} if i<120 else {} for i in range(981)];checks=0
for op,a,b,c,f,z in events:
 if op==1:
  for role in (a,b):
   if role==980 or 120<=role<240:continue
   for s in source[role]:
    assert all(sum(x*y for x,y in zip(word['lines'][s],ann))==0 for ann in F[f]['A']);checks+=1
  for k,v in list(source[b].items()):
   source[a][k]=source[a].get(k,0)+c*v
   if not source[a][k]:del source[a][k]
 elif op==2:source[b]=dict(source[a])
 elif op==3:assert source[b]==source[a];source[b]={}
assert source[:120]==[{i:1} for i in range(120)] and all(not row for row in source[240:])
state={int(k):v for k,v in st['final'].items()};H=Counter();copies=0
for op,a,b,c,f,z in reversed(events):
 if op==0:
  old,new=c,b;assert state[a]==old and F[old]['dim']>=F[new]['dim']
  assert all(sum(Q(x)*Q(y) for x,y in zip(u,w))==0 for u in F[old]['A'] for w in F[new]['B']);state[a]=new
  fee=F[old]['dim']-F[new]['dim'];assert fee==f
  if fee:H[fee]+=1
 elif op==1:assert state[a]==state[b]==f
 elif op==3:assert b==980 and 980 not in state and state[a]==c and f==st['ZERO'];state[980]=f;H[8]+=1;copies+=1
 else:assert op==2 and b==980 and state[a]==c and state[b]==f;del state[980]
assert state=={int(k):v for k,v in st['initial'].items()} and copies==9 and sum(k*v for k,v in H.items())==7553
out={'status':'PASS_INDEPENDENT_SIGNED95_FORWARD_FUNCTIONALS_AND_REFLECTED_RATIONAL_FRAME_LEDGER','forward_original_source_support_checks':checks,'reflected_profile':dict(H),'reflected_rank_mass':7553,'scope':'Exact defining signed source functional support at every forward common rational frame, and full reflected complement-frame inclusion/ADD/COPY/ERASE ledger. Forward source valuations do not certify general reflected rational chart functionals; those remain the retained reflected/compiler interface, separately supported by source-bound native geometry and the exact address operator involutions. No all-size compiler claim.', 'signed_sha256':hashlib.sha256((S/'signed-records.bin').read_bytes()).hexdigest()}
(P/'SIGNED95-FUNCTIONAL-REFLECTION.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],checks)
