from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent exported-record replay, exact containment and frame-rank audit.
All row spaces are cleared to primitive integer bases; modular nonzero ranks
certify rational ranks and nondegeneracy, while orthogonality is exact integer.
"""
from pathlib import Path
from fractions import Fraction
from math import gcd,lcm
from collections import Counter
import hashlib,json,gzip
P=support.FRAME
if not __debug__:raise RuntimeError('Assertions must be enabled')
def read(n):
 raw=(P/n).read_bytes();return json.loads(gzip.decompress(raw)if n.endswith('.gz')else raw)
def integer(row):
 row=list(map(Fraction,row));den=lcm(*(x.denominator for x in row));out=[int(x*den)for x in row];g=gcd(*out)
 return [x//g for x in out]if g else out
MOD=(1<<61)-1
def rank(rows,width):
 a=[[x%MOD for x in row]for row in rows];k=0
 for j in range(width):
  p=next((i for i in range(k,len(a))if a[i][j]and gcd(a[i][j],MOD)==1),None)
  if p is None:continue
  a[k],a[p]=a[p],a[k];inv=pow(a[k][j],-1,MOD);a[k]=[(x*inv)%MOD for x in a[k]]
  for i in range(k+1,len(a)):
   v=a[i][j]
   if v:a[i]=[(x-v*y)%MOD for x,y in zip(a[i],a[k])]
  k+=1
 return k
def dot(a,b):return sum(x*y for x,y in zip(a,b)if x and y)
def run():
 result=read('RESULT.json')
 assert result['checker_sha256']==hashlib.sha256((support.HERE/'frame/build_local.py').read_bytes()).hexdigest()
 for n,h in result['artifacts'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
 endpoint=read('local-endpoints.json');n=endpoint['n'];initial={int(k):v for k,v in endpoint['initial'].items()};final={int(k):v for k,v in endpoint['final'].items()};raw=read('local-records.json.gz');frames=read('local-frames.json.gz')
 B={int(k):[integer(row)for row in z['basis']]for k,z in frames.items()};A={int(k):[integer(row)for row in z['annihilator']]for k,z in frames.items()};dim={int(k):z['rank']for k,z in frames.items()}
 for f in dim:
  b,a,d=B[f],A[f],dim[f];assert len(b)==d and len(a)==20-d
  assert rank(b,20)==d and rank(a,20)==20-d
  assert all(dot(x,y)==0 for x in a for y in b)
  rows,mult=(b,9)if d<=10 else(a,11)
  gram=[[mult*dot(x,y)-sum(x)*sum(y)for y in rows]for x in rows]
  assert rank(gram,len(rows))==len(rows),('degenerate G frame',f)
 print('All',len(dim),'frame bases/annihilators and G-nondegeneracy passed',flush=True)
 state=dict(initial);temporary=None;H=Counter();adds=0;units=0;pairs=set();copies=0
 for i,row in enumerate(raw):
  assert len(row)==6;op,a,b,c,f,z=row
  if op==0:
   assert state[a]==b and f==dim[c]-dim[b]>=0
   if(b,c)not in pairs:
    assert all(dot(x,y)==0 for x in A[c]for y in B[b]),('nonnested MOVE',i,b,c);pairs.add((b,c))
   state[a]=c
   if f:H[f]+=1
  elif op==1:
   assert a!=b and c%2 and state[a]==state[b]==f;adds+=1;units+=abs(c)
   assert 0<=z<len(endpoint['categories'])
  elif op==2:
   assert temporary is None and b==n and state[a]==c and dim[f]==0 and z==dim[c];temporary=(a,b,c,f,z);state[b]=f;H[z]+=1;copies+=1
  else:
   assert op==3 and temporary==(a,b,c,f,z)and state[a]==c and state[b]==f;temporary=None;del state[b]
 assert temporary is None and state==final and H==Counter({int(k):v for k,v in result['one_stage_paid_histogram'].items()})
 assert adds==336253 and units==338173
 def replay(reverse=False,omit_moved=False):
  col=[1<<q for q in range(n+1)];norm=[1]*(n+1);tmp=None
  for row in reversed(raw)if reverse else raw:
   op,a,b,c,f,z=row
   if op==1:
    if omit_moved and endpoint['categories'][z]=='reorder_moved':continue
    col[a]^=col[b];norm[a]+=abs(c)*norm[b]
   elif op==(3 if reverse else 2):assert tmp is None;tmp=a;col[b]=col[a];norm[b]=norm[a]
   elif op==(2 if reverse else 3):assert tmp==a and col[a]==col[b];tmp=None
  assert tmp is None
  wrong=[q for q in range(n)if col[q]!=((1<<q)^((1<<(q-960))if 960<=q<1920 else 0))]
  if omit_moved:assert wrong
  else:assert not wrong
  return max(norm)
 fn=replay();bn=replay(True);replay(omit_moved=True);assert(fn,bn)==(132143,1307556)
 # Rank mutation controls reject a zeroed basis row for every positive frame.
 controls=0
 for f in dim:
  if B[f]:assert rank(B[f][1:]+[[0]*20],20)<dim[f];controls+=1
 out=dict(status='PASS_INDEPENDENT_FULL_LOCAL_RECORD_AND_FRAME_AUDIT',head=result['head'],candidate_sha256=result['candidate_sha256'],checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),builder_receipt_sha256=hashlib.sha256((P/'RESULT.json').read_bytes()).hexdigest(),frames=len(dim),all_frame_ranks_and_annihilators_exact=True,all_frame_G_nondegeneracy_certified=True,exact_MOVE_containment_pairs=len(pairs),source_and_target_and_helper_final_states_exact=True,records=len(raw),columns=n,copies=copies,paid_calls=sum(H.values()),paid_rank_mass=sum(k*v for k,v in H.items()),weighted_additions=adds,literal_units=units,forward_norm=fn,inverse_norm=bn,moved_ADD_omission_rejected=True,zeroed_basis_row_controls_rejected=controls,scope='Independent verification of exported local records and every used frame. G=I-J/9, with G_inverse=I-J/11. Nonzero modular pivots are units, certifying rational full ranks; zero cross-products are checked exactly over integers. Global lowering, bank completion, prime/all-size interfaces remain separate.')
 (P/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
