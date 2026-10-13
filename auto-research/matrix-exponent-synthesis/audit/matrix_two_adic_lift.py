import sys as _checked_runtime
if _checked_runtime.flags.optimize:
    raise SystemExit('Checked audit requires Python without -O')
from pathlib import Path
import itertools,json,random,sys,time
base=Path(sys.argv[1]); dest=Path(sys.argv[2]); d=json.loads((base/'circuit/flat16_2208_integer_circuit.json').read_text());start=time.perf_counter()
forms=[(g['left'],g['right']) for g in d['gates']];outforms=[o['terms'] for o in d['output_numerators']]
def run(values,p):
 modulus=1<<(p+3)
 gatevals=[(sum(k*values[v] for v,k in l)*sum(k*values[v] for v,k in r))%modulus for l,r in forms]
 nums=[sum(c*gatevals[g] for g,c in row)%modulus for row in outforms]
 assert all(n%8==0 for n in nums)
 got=[n//8 for n in nums]
 mask=(1<<p)-1
 expect=[sum(values[16*r+j]*values[256+16*j+c] for j in range(16))&mask for r in range(16) for c in range(16)]
 assert got==expect
 return nums
binary_trials=0
for bits in itertools.product((0,1),repeat=8):
 v=[0]*512
 for k,(r,c) in enumerate(((0,0),(0,1),(1,0),(1,1))):v[16*r+c]=bits[k];v[256+16*r+c]=bits[k+4]
 run(v,1);binary_trials+=1
rng=random.Random(20261008);signed_trials=0
for p in (1,2,3,4,8,16,31):
 for _ in range(6):
  v=[rng.randrange(-(1<<p),1<<p) for _ in range(512)]
  run(v,p);signed_trials+=1
sharp=[]
for p in (1,2,3,4,8,16,31):
 # Values zero versus2^(p-1) give equal numerator residue if only p+2 bits retained.
 zero=0;product=1<<(p-1)
 assert (8*zero)%(1<<(p+2))==(8*product)%(1<<(p+2))
 assert zero%(1<<p)!=product%(1<<p)
 sharp.append({'p':p,'zero_product':zero,'other_product':product,'same_numerator_mod_p_plus_2':True})
one=[0]*512;one[0]=one[256]=1
num=run(one,1);assert num[0]==8 and num[0]%2==0 and num[0]//8==1
receipt={'status':'PASS','source_pin':'7203497dc990e47c2391bff1b9863408d817faeb','actual_circuit_modulus':'2^(p+3)','decoded_output':'AB mod2^p','all_binary_2x2_embedded_trials':binary_trials,'signed_dense_trials':signed_trials,'tested_precisions':[1,2,3,4,8,16,31],'negative_control_naive_mod2_numerator_zero_but_product_one':True,'sharp_numerator_only_precision_witnesses':sharp,'time_seconds':time.perf_counter()-start,'scope':'Controlsfor actualserializedintegercircuit; universalidentityN=8AB independentlyverifiedpolynomially. p+3 precision necessaryfor decodingfromnumerator residue alone, notlowerboundonallmultiplicationalgorithms.'}
dest.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
