"""Complete bit profile for explicit orthogonal sunflower completed-core groups.

Uses PR128's frozen minimal-V bit word and PR104's opposite-bank compiler.
This script proves finite rational projector algebra and recomputes the full
histogram; inherited literal bit-word replay/physical interfaces remain inputs.
"""
from pathlib import Path
from itertools import combinations
from collections import Counter
import json,gzip,math,hashlib,struct
D=Path(__file__).resolve().parent;P=D/'inputs/research'
h=23;m=h*h;v=math.comb(h,3);N=v*v

def factors(points):
 pts=list(points)
 if len(pts)%2:pts.append(None)
 if len(pts)<2:return []
 out=[]
 for _ in range(len(pts)-1):
  out.append([tuple(sorted((pts[i],pts[-1-i])))for i in range(len(pts)//2)if pts[i]is not None and pts[-1-i]is not None])
  pts=[pts[0],pts[-1]]+pts[1:-1]
 return out

groups=json.loads((D/'groups161.json').read_text())
groups=[[tuple(T)for T in G]for G in groups]
trip=list(combinations(range(h),3));flatten=[T for G in groups for T in G];assert len(flatten)==v and len(set(flatten))==v and set(flatten)==set(trip)
for G in groups:
 for i,T in enumerate(G):
  for j,S in enumerate(G):assert len(set(T)&set(S))==(3 if i==j else 1)
 # Six times each H-orthogonal rank-one projector has exact integer entries.
 Q=[[sum(int(i in T)*(3*int(j in T)-1)for T in G)for j in range(h)]for i in range(h)]
 assert all(sum(Q[i][k]*Q[k][j]for k in range(h))==6*Q[i][j]for i in range(h)for j in range(h))
 assert sum(Q[i][i]for i in range(h))==6*len(G)
 # Projector self-adjointness for H scaled by9: HQ=(HQ)^T.
 HQ=[[9*Q[i][j]-sum(Q[k][j]for k in range(h))for j in range(h)]for i in range(h)]
 assert all(HQ[i][j]==HQ[j][i]for i in range(h)for j in range(h))
raw=(P/'round8-foundations-minimal-v-word.json.gz').read_bytes();word=json.loads(gzip.decompress(raw));base=json.loads((P/'round8-network-opposite-profile.json').read_text());deferred=json.loads(gzip.decompress((P/'round7-public/tree/certificates/round7/deferred_23.json.gz').read_bytes()))
sigma=dict(zip(deferred['readout_order'],deferred['sigma']))
for s in word['removed_original_slots']:sigma.pop(s)
sigma.update({int(s):B for s,B in word['new_frames'].items()});R=base['R'];assert R==deferred['R']==28866
z=Counter({int(r):n for r,n in base['hist'].items()});old_ext=Counter({int(r):n for r,n in base['classes']['auxiliary_exteriors']['hist'].items()});z.subtract(old_ext);new_ext=Counter()
for G in groups:
 for s in range(R):
  width=m-(h-len(sigma.get(s,())))*len(G);assert 0<width<m;new_ext[width]+=2
z.update(new_ext);assert min(z.values())>=0;z=Counter({r:n for r,n in z.items()if n});W=2*N+2*len(groups)*R;mass=sum(r*n for r,n in z.items());assert W*m-mass==base['deficit'];assert mass==W*m-N+2*v*h*(h-1)
lo,hi=0.,.001
for _ in range(60):
 b=(lo+hi)/2
 if math.fsum(n*r*math.exp(b*math.log(m/r))for r,n in z.items())<m*W:lo=b
 else:hi=b
ledger=D/'literal-replay'
physical=gzip.decompress((ledger/'forward-events.i32.gz').read_bytes())
assert hashlib.sha256(physical).hexdigest()=='f98d52b6d8fb04e30a0a46df4df95d2e7999ff97a89826e5b0f44b4120a69e28'
event_counts=Counter(k for k,*_ in struct.iter_unpack('<iiiii',physical))
frame_raw=(ledger/'frames-and-paths.json').read_bytes();frame_data=json.loads(frame_raw)
classes={name:part for name,part in base['classes'].items()if name!='auxiliary_exteriors'}
classes['auxiliary_exteriors']=dict(calls=sum(new_ext.values()),rank=sum(r*n for r,n in new_ext.items()),hist=dict(sorted(new_ext.items())))
assert sum(c['calls']for c in classes.values())==sum(z.values())
out=dict(h=h,m=m,v=v,N=N,R=R,L=2*v*h*(h-1),groups=len(groups),group_sizes=dict(sorted(Counter(map(len,groups)).items())),W=W,total_rank=mass,deficit=W*m-mass,maxchild=max(z),complex_saving_numerical=None,bit_saving_numerical=lo,child_multiplicities=dict(sorted(z.items())),classes=classes,paid_projector_calls=sum(z.values()),local_forward_event_counts=dict(sorted(event_counts.items())),literal_frame_keys=len(frame_data['keys']),literal_frame_inventory_sha256=hashlib.sha256(frame_raw).hexdigest(),literal_event_sha256=hashlib.sha256(physical).hexdigest(),old_exteriors=dict(sorted(old_ext.items())),new_exteriors=dict(sorted(new_ext.items())),minimal_v_word_sha256=hashlib.sha256(raw).hexdigest(),exact_coverage=True,exact_pairwise_H_orthogonality=True,exact_projector_idempotence=True,exact_projector_self_adjointness=True,scope='Exact completed-core rational projector identities and complete one-child profile. Requires unchanged PR128 minimal-V literal-word contract, common generic-basis/opposite-bank compiler and scalar/adapter work charge. Each recorded projector call pays its fixed PR104 atom adapters; the generic-basis existence argument does not specify a numerical primitive-operation constant.')
(D/'profile161.json').write_text(json.dumps(out,indent=2)+'\n');print({k:v for k,v in out.items()if k not in('child_multiplicities','old_exteriors','new_exteriors')},flush=True)
