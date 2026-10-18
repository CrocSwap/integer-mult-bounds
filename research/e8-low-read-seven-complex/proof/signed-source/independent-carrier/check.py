"""Dense integer audit independent of the sparse defining-source checker. OpenAI Codex assistance; Apache-2.0."""
import json,gzip,struct,hashlib,sys
from pathlib import Path
import numpy as np
S=Path('/private/tmp/pr370-inspection');W=Path('/private/tmp/pr370-signed-defining-source-v1');O=Path(__file__).resolve().parent
w=json.load(gzip.open(S/'data/bit/bitE8-r865.json.gz','rt'));n=2*w['v']+w['R'];v=w['v'];raw=(W/'signed-records.bin').read_bytes();ev=list(struct.iter_unpack('<6i',raw))
assert n==1105 and v==120
# Bounds are tracked as unbounded Python integers before any fixed-width operation.
def replay(events,reverse=False,initial=None):
 A=np.zeros((n+1,n),dtype=np.int64);A[:n]=np.eye(n,dtype=np.int64)
 if initial is not None:A[:]=initial
 bound=[sum(abs(int(x)) for x in row) for row in A];peak=max(bound);borrowed=None
 for op,a,b,c,f,z in reversed(events) if reverse else events:
  if op==1:
   coef=-c if reverse else c;new=bound[a]+abs(coef)*bound[b];assert new<2**63
   A[a]+=coef*A[b];bound[a]=new;peak=max(peak,new)
  elif op==(3 if reverse else 2):
   assert borrowed is None and b==n;borrowed=a;A[n]=A[a];bound[n]=bound[a]
  elif op==(2 if reverse else 3):
   assert borrowed==a and np.array_equal(A[n],A[a]);borrowed=None;A[n]=0;bound[n]=0
 assert borrowed is None
 return A,peak
# Define the clean signed target operator directly from the public A/scatter/B words.
C=np.zeros((n,v),dtype=np.int64);C[:v]=np.eye(v,dtype=np.int64)
for f,a,ss in w['A']:
 for b in ss:C[a]+=C[b]
ret=C[w['ret']].copy()
for t,ks in enumerate(w['scatter']):
 for k in ks:C[v+t]+=ret[k]
for f,a,ss in w['B']:
 for b in ss:C[a]+=C[b]
M=C[v:2*v].copy();assert np.array_equal(M%2,np.eye(v,dtype=np.int64))
E=np.zeros((n+1,n),dtype=np.int64);E[:n]=np.eye(n,dtype=np.int64);E[v:2*v,:v]+=M
A,fw=replay(ev);assert np.array_equal(A,E)
B,bw=replay(ev,True);F=np.zeros_like(E);F[:n]=np.eye(n,dtype=np.int64);F[v:2*v,:v]-=M;assert np.array_equal(B,F)
J,jw=replay(ev,True,A);assert np.array_equal(J[:n],np.eye(n,dtype=np.int64)) and not J[n].any()
orig=(Path('/private/tmp/pr370-full-cp312-proof-v2/records')/'249-records.bin').read_bytes()
parity=b''.join(struct.pack('<6i',op,a,b,c%2 if op==1 else c,f,z) for op,a,b,c,f,z in ev)
assert parity==orig
r=dict(status='PASS_INDEPENDENT_DENSE_EXACT_SIGNED_E8_SOURCE',signed_sha256=hashlib.sha256(raw).hexdigest(),parity_sha256=hashlib.sha256(orig).hexdigest(),all_integer_columns=n,source_restored=True,dirty_helpers_restored=True,targets_equal_independent_clean_network=True,inverse_exact=True,forward_then_inverse_exact=True,clean_decoder_mod2_identity=True,forward_majorant=fw,inverse_majorant=bw,composition_majorant=jw,all_fixed_width_steps_bounded_by_unbounded_integer_l1=True,scope='Independent scalar audit of signed defining source; no bank/address/assembly admission inferred.')
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
