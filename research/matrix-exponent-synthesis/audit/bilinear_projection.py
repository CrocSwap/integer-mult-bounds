import sys as _checked_runtime
if _checked_runtime.flags.optimize:
    raise SystemExit('Checked audit requires Python without -O')
from pathlib import Path
from collections import defaultdict,Counter
from math import gcd
from functools import reduce
import json,sys,time,hashlib
base=Path(sys.argv[1]);outdir=Path(sys.argv[2]); start=time.perf_counter()
data=json.loads((base/'circuit/flat16_2208_integer_circuit.json').read_text())
groups={}; mappings=[]; families=Counter()
def primitive(xs):
 d=reduce(gcd,(abs(c) for c in xs.values()))
 sign=1 if xs[min(xs)]>0 else -1
 scale=d*sign
 return tuple(sorted((v,c//scale) for v,c in xs.items())),scale
for g in data['gates']:
 L=dict(g['left']);R=dict(g['right']);terms=[]
 for af,bf in (({v:c for v,c in L.items() if v<256},{v:c for v,c in R.items() if v>=256}),({v:c for v,c in R.items() if v<256},{v:c for v,c in L.items() if v>=256})):
  if not af or not bf:continue
  A,sa=primitive(af);B,sb=primitive(bf);key=(A,B)
  idx=groups.setdefault(key,{'id':len(groups),'weights':defaultdict(int)})['id']
  terms.append((key,sa*sb));families[g['leaf_family']]+=1
 mappings.append(terms)
for output in data['output_numerators']:
 for g,weight in output['terms']:
  for key,scale in mappings[g]:groups[key]['weights'][output['id']]+=weight*scale
active={key:rec for key,rec in groups.items() if any(rec['weights'].values())}
by_output=[defaultdict(int) for _ in range(256)]
for (A,B),rec in active.items():
 for o,weight in rec['weights'].items():
  if not weight:continue
  for a,ac in A:
   for b,bc in B:by_output[o][a,b]+=weight*ac*bc
for o,coeff in enumerate(by_output):
 r,c=divmod(o,16);coeff={m:v for m,v in coeff.items() if v}
 expected={(16*r+j,256+16*j+c):8 for j in range(16)}
 assert coeff==expected,(o,len(coeff))
receipt={'status':'PASS_exact_bilinear_projection','raw_AB_products':sum(families.values()),'families':dict(families),'primitive_AB_pairs_before_output_cancellation':len(groups),'cancelled_groups':len(groups)-len(active),'active_bilinear_products':len(active),'known_tensor_square48_upper_bound':48**2,'projection_beats48_squared':len(active)<48**2,'exact_output_identities':256,'output_denominator':8,'time_seconds':time.perf_counter()-start,'scope':'A-domain/B-domain bilinear projection over Q; only equality/primitive-product grouping, not general tensor rank optimization. Characteristic2 requires separate certification.'}
(outdir/'bilinear_projection_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
