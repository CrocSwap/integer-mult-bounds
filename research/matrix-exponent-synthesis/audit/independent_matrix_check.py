import sys as _checked_runtime
if _checked_runtime.flags.optimize:
    raise SystemExit('Checked audit requires Python without -O')
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
import hashlib,json,time,sys
base=Path(sys.argv[1]); dest=Path(sys.argv[2]); start=time.perf_counter()
coeff_path=base/'input/outer48_exact_rational_and_integer_data.json'
coeff=json.loads(coeff_path.read_text())['rational_coefficients']
a,b,c=[[list(map(Fraction,row)) for row in coeff[key]] for key in ('alpha','beta','gamma')]
assert all(len(table)==48 and all(len(row)==16 for row in table) for table in (a,b,c))
fail=[]; checks=0
for p in range(16):
 for q in range(16):
  for o in range(16):
   actual=sum((a[t][p]*b[t][q]*c[t][o] for t in range(48)),Fraction())
   target=int(p//4==o//4 and p%4==q//4 and q%4==o%4)
   checks+=1
   if actual!=target:fail.append((p,q,o,str(actual),target))
assert not fail,fail[:5]
path=base/'circuit/flat16_2208_integer_circuit.json'
raw=path.read_bytes(); data=json.loads(raw); assert len(data['gates'])==2208 and len(data['output_numerators'])==256
products=[]
for gate in data['gates']:
 forms=[]
 for side in ('left','right'):
  form={}
  for var,k in gate[side]:
   assert isinstance(var,int) and 0<=var<512 and isinstance(k,int)
   assert var not in form
   form[var]=k
  assert form and all(form.values())
  forms.append(form)
 poly=defaultdict(int)
 for l,lc in forms[0].items():
  for r,rc in forms[1].items():
   poly[tuple(sorted((l,r)))]+=lc*rc
 products.append({mon:k for mon,k in poly.items() if k})
 assert products[-1]
used=set(); expanded=0
for out in data['output_numerators']:
 row,col=out['row'],out['col']; actual=defaultdict(int)
 for gate,k in out['terms']:
  assert isinstance(gate,int) and 0<=gate<2208 and isinstance(k,int)
  used.add(gate)
  for mon,v in products[gate].items():actual[mon]+=k*v;expanded+=1
 actual={mon:k for mon,k in actual.items() if k}
 expected={(16*row+j,256+16*j+col):8 for j in range(16)}
 assert actual==expected,(row,col,list(actual.items())[:5])
assert used==set(range(2208))
receipt={'status':'PASS','source_pin':'7203497dc990e47c2391bff1b9863408d817faeb','outer_rank48_exact_rational_coefficients':checks,'outer_has_integer_left_right':all(x.denominator==1 for table in(a,b) for row in table for x in row),'outer_output_denominators':sorted(set(x.denominator for row in c for x in row)),'flat_scheduled_products':len(products),'flat_outputs':256,'flat_target_mixed_coefficients':4096,'AA_BB_residuals':0,'all_products_nonzero_and_used':True,'expanded_output_contributions':expanded,'circuit_sha256':hashlib.sha256(raw).hexdigest(),'time_seconds':time.perf_counter()-start,'claim':'Exact numerator circuit N=8AB over any commutative ring; exact final division over integers. No tensor rank or bit-runtime claim.'}
dest.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
