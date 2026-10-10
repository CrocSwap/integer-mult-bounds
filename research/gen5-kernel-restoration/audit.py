import sys
if not __debug__:raise SystemExit("Assertions must be enabled")
sys.dont_write_bytecode=True
from pathlib import Path
import json,struct,hashlib,signal,time,argparse
start=time.monotonic()
ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--base-export',type=Path,required=True);ap.add_argument('--old',type=Path,required=True);ap.add_argument('--bank-export',type=Path,required=True);args=ap.parse_args()
p=args.candidate;base=args.base_export
st=json.loads((base/'249-states.json').read_text());n,v=st['n'],st['v']
candidate=json.loads((p/'249-states.json').read_text());candidate['initial']=st['initial']
o=args.bank_export;o.mkdir(exist_ok=True)
(o/'249-states.json').write_text(json.dumps(candidate));(o/'frames.json').write_bytes((base/'frames.json').read_bytes())
raw=(p/'COHORT249-RECORDS.bin').read_bytes();es=list(struct.iter_unpack('<6i',raw));checks=[]
for reverse in (False,True):
 for omit in (False,True):
  rows=[1<<i for i in range(n)]+[0];center=None
  for op,a,b,c,f,z in (reversed(es) if reverse else es):
   if op==1:
    assert c%2 and a!=b
    if not(omit and z==33):rows[a]^=rows[b]
   elif op==(3 if reverse else 2):
    assert center is None and b==n;center=a;rows[n]=rows[a]
   elif op==(2 if reverse else 3):
    assert center==a and rows[a]==rows[n];rows[n]=0;center=None
  assert center is None
  wrong=sum(rows[i]!=((1<<i)^((1<<(i-v)) if v<=i<2*v else 0)) for i in range(n))
  assert (wrong>0)==omit
  checks.append({'reverse':reverse,'omit_restoration':omit,'wrong_rows':wrong,'formal_columns':n})
old=list(struct.iter_unpack('<6i',(args.old/'COHORT249-RECORDS.bin').read_bytes()))
receipt=json.loads((p/'CLEANUP.json').read_text());cut=receipt['cut'];edits=receipt['edits']
dest={x['helper'] for x in edits};donor={x['source'] for x in edits}
assert len(dest)==len(donor)==len(edits)==440 and not dest&donor
drop=set()
for x in edits:
 i,=x['old_indices'];e=old[i];a,b=x['helper'],x['source']
 assert e[0]==1 and (e[1],e[2],e[3])==(a,b,x['coefficient'])
 assert i>=cut
 for op,aa,bb,c,f,z in old[cut:i]:
  assert op not in (2,3)
  if op==1:assert a not in (aa,bb) and aa!=b
 drop.add(i)
projection=lambda seq:[(k,a,b,c,z) for k,a,b,c,f,z in seq if k]
expected=[]
for i,e in enumerate(old):
 if i==cut:expected.extend((1,x['helper'],x['source'],x['coefficient'],33) for x in edits)
 if e[0] and i not in drop:expected.append((e[0],e[1],e[2],e[3],e[5]))
assert projection(es)==expected
result={'word_sha256':hashlib.sha256(raw).hexdigest(),'checks':checks,'exact_signed_commutation':{'moved_gates':440,'distinct_destinations_and_donors':True,'no_destination_touch_or_donor_write_during_commuted_interval':True,'surviving_signed_scalar_and_copy_projection_equal':True,'argument':'Each signed shear commutes over its entire relocated interval because its destination is untouched and its donor is never written; relocated shears commute pairwise. Thus the scalar program is identical over the integers, not merely F2.'},'seconds':time.monotonic()-start,'scope':'Independent F2 replay/controls and exact signed commutation; geometry, global lowering and finite invoice checked separately.'}
(p/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
