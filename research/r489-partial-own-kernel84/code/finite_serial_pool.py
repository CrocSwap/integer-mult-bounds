"""OpenAI Codex exact Gaussian-dyadic finite regression of serial pooling.
Two complete normalized invocations borrow one physical helper family across
replicas. Actual candidate wrapper identities are separate source evidence.
CLI: OUT.json. Uses all40independent scalar input columns on five8-cell arrays.
"""
from pathlib import Path
import json,sys,copy
N=8;F=5;K=N*F
# Linear function arrays: integer real/imaginary coefficient rows divided by2^d.
def identity(f):return([[int(j==f*N+x)for j in range(K)]for x in range(N)],[[0]*K for x in range(N)],0)
def add(a,b,sgn=1):
 ar,ai,ad=a;br,bi,bd=b;d=max(ad,bd);u=2**(d-ad);v=sgn*2**(d-bd)
 return([[u*x+v*y for x,y in zip(arow,brow)]for arow,brow in zip(ar,br)],[[u*x+v*y for x,y in zip(arow,brow)]for arow,brow in zip(ai,bi)],d)
def equal(a,b):
 ar,ai,ad=a;br,bi,bd=b;return all(x*2**bd==y*2**ad for aa,bb in[(ar,br),(ai,bi)]for rowa,rowb in zip(aa,bb)for x,y in zip(rowa,rowb))
def C(a,axis):
 ar,ai,d=a;q=1<<axis
 return([[ar[x][j]-ai[x][j]+ar[x^q][j]+ai[x^q][j]for j in range(K)]for x in range(N)],[[ai[x][j]+ar[x][j]+ai[x^q][j]-ar[x^q][j]for j in range(K)]for x in range(N)],d+1)
def perm(a,k):
 ar,ai,d=a
 def idx(x):return x if not k else (x&4)|((x&1)<<1)|((x&2)>>1)
 return([ar[idx(x)][:]for x in range(N)],[ai[idx(x)][:]for x in range(N)],d)
def run(back=False,mut=None):
 a=[identity(f)for f in range(F)];sign=-1 if back else 1
 def call(rep,begin=True,end=True):
  src=2*rep;dst=src+1;h=perm(a[4],rep)
  private=copy.deepcopy(a[src]) # literal COPY of arbitrary source array
  if begin:a[dst]=add(a[dst],h,-1);h=add(h,private,sign)
  if end:
   a[dst]=add(a[dst],h)
   if mut!='omit-dirty-restoration':h=add(h,private,-sign)
   assert equal(private,a[src]);private=None # ERASE unchanged copy
   h=C(h,0)
   if mut=='touch-borrowed-spectator':h=C(h,1)
  a[4]=perm(h,rep if mut!='wrong-owner-chart'else 0)
 if mut=='interleave-invocations':
  call(0,end=False);call(1);call(0,begin=False)
 else:
  for rep in range(2):
   before=copy.deepcopy(a);call(rep)
   want=copy.deepcopy(before);want[2*rep+1]=add(want[2*rep+1],want[2*rep],sign);want[4]=C(want[4],rep)
   if not all(equal(x,y)for x,y in zip(a,want)):return False
 if mut!='omit-idle-remainder':a[4]=C(a[4],2)
 expected=[identity(f)for f in range(F)]
 for rep in range(2):expected[2*rep+1]=add(expected[2*rep+1],expected[2*rep],sign)
 for axis in range(3):expected[4]=C(expected[4],axis)
 return all(equal(x,y)for x,y in zip(a,expected))
controls=['interleave-invocations','omit-dirty-restoration','touch-borrowed-spectator','wrong-owner-chart','omit-idle-remainder']
for back in(False,True):
 assert run(back)
 for mut in controls:assert not run(back,mut),(back,mut)
out=dict(status='PASS_EXACT_GAUSSIAN_DYADIC_SERIAL_POOLING_OPERATOR',address_axes=3,addresses_per_array=8,physical_families=5,invocations=2,shared_whole_helper_families=1,all_independent_input_columns=40,scalar_field='Q(i), exact integer Gaussian numerators with explicit powers-of-two denominators',actual_C_definition='C_q=(1+i)I/2+(1-i)X_q/2',complete_scalar_add_copy_erase=True,both_shear_orientations=True,actual_owner_chart_permutations=True,borrowed_spectator_identity_checked=True,commuting_idle_completion=True,mutations_rejected=controls,scope='Finite regression of serial reuse of complete normalized local invocations on one helper family. The candidate serialized residual wrappers and local800column identity are separately admitted source484evidence; this is not a replacement local-word proof or enormouscover enumeration.')
Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
