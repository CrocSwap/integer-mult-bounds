"""Exact F3-address/F2-value whole-owner bit operator regression.
OpenAI Codex audit. Six physical whole arrays: two data plus one shared helper
family, each with two cover classes. Tests every independent dirty scalar column.
"""
import json,sys
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve()
Q=3;M=3;N=Q**(2*M);COLS=6*N
PERMS=[]
for axis in range(M):
 a=Q**axis;b=Q**(M+axis)
 PERMS.append([x+((x//b)%Q-(x//a)%Q)*(a-b) for x in range(N)])
 assert sorted(PERMS[-1])==list(range(N))

def run(reverse=False,mutation=None):
 z=[[1<<(family*N+x) for x in range(N)] for family in range(6)]+[[0]*N]
 def add(a,b):
  assert frame[a]==frame[b], 'ADD operands have unequal actual frame projectors'
  z[a]=[x^y for x,y in zip(z[a],z[b])]
 def D(a,k):z[a]=[z[a][x] for x in PERMS[k]]
 def helpers(d):return 4+d,4+(d^1)
 for d in range(2):
  src,target=(2+d,d) if reverse else (d,2+d)
  h1,h2=helpers(d)
  if mutation=='alias-owner':h2=h1
  common=1 if reverse else 2  # residual R=span(e0), entrance E=span(e1)
  frame={src:common,target:common,h1:0 if reverse else 2,h2:0 if reverse else 2,6:None}
  # sigma=id and swap(0,1), so at fixed d actual owners are H_d,H_(d*s).
  # Reflected local frame ledger: complement(I)=0 -> complement(E)=R,
  # then all ADDs at R. Forward all ADDs at E -> MOVE E to I afterwards.
  if reverse:
   for h in (h1,h2):
    D(h,d);frame[h]=1
  z[6]=z[src][:];frame[6]=frame[src]
  add(h1,h2);add(target,h1);add(h1,6);add(target,h1)
  if mutation!='omit-dirty-restoration':add(h1,6)
  add(h1,h2)
  assert z[6]==z[src] and frame[6]==frame[src];z[6]=[0]*N;frame[6]=None
  if not reverse:
   for h in (h1,h2):
    if mutation!='omit-endpoint' or h!=h2:D(h,d)
    frame[h]=3
  elif mutation=='omit-endpoint':D(h2,d) # cancels one required reflected endpoint
  assert frame[h1]==frame[h2]==(1 if reverse else 3)
 if mutation!='omit-idle-remainder':
  for h in (4,5):D(h,2)
 expect=[[1<<(family*N+x) for x in range(N)] for family in range(6)]+[[0]*N]
 for d in range(2):
  src,target=(2+d,d) if reverse else (d,2+d)
  expect[target]=[x^y for x,y in zip(expect[target],expect[src])]
 for h in (4,5):
  for k in range(M):expect[h]=[expect[h][x] for x in PERMS[k]]
 return z==expect

def main():
 controls=['alias-owner','omit-dirty-restoration','omit-endpoint','omit-idle-remainder']
 for rev in (False,True):
  assert run(rev)
  for c in controls:assert not run(rev,c),(rev,c)
 r=dict(status='PASS_COMPLETE_FINITE_BIT_WHOLE_OWNER_OPERATOR',address_field=3,value_field=2,ambient_dimension=M,
  cover_classes=2,physical_arrays=6,addresses_per_array=N,independent_dirty_columns=COLS,orientations=2,
  nontrivial_reflected_frame_ledgers=True,actual_scalar_add_copy_erase=True,helpers_sharing_one_family=2,
  all_idle_residual_factors_completed=True,mutations_rejected=controls,
  scope='Complete small finite operator regression for the owner-reindexing theorem; candidate actual maps and all local columns are separate checks, not a claim to enumerate its huge cover.')
 (ROOT/'FINITE-BIT-COVER.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
