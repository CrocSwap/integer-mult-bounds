"""Exact obstruction for independent bit/complex packet composition. Apache-2.0."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json, hashlib, importlib.util
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
base=ROOT/'experiments/stage-search/pr440-signed-retime'
assembly=base/'composition/REFINED-ASSEMBLY.json'
bit=base/'full/bit426-source-centres/global/GLOBAL.json'
cx=ROOT/'experiments/stage-search/pr433-split/full/split-centres/INTEGRATION.json'
engine=ROOT/'experiments/stage-search/pr434-kernel/full/baseline/baseline/work/pr361/code/engines/moment.py'
s=importlib.util.spec_from_file_location('moment',engine); moment=importlib.util.module_from_spec(s);s.loader.exec_module(moment)
read=lambda p:json.loads(p.read_text())
b,c,a=read(bit),read(cx),read(assembly)
HB={int(r):n for r,n in b['profile'].items()}; HC={int(r):n for r,n in c['global_profile'].items()}
# Emit all tensor child ranks. Each child contracts by rb*rc/(64*73);
# its multiplicity is nb*nc and its mass is that rank/(Wb*Wc*64*73).
H=Counter()
for rb,nb in HB.items():
 for rc,nc in HC.items():H[rb*rc]+=nb*nc
assert sum(r*n for r,n in H.items())==sum(r*n for r,n in HB.items())*sum(r*n for r,n in HC.items())
# Independent rare fallback combinations multiply as well. The product
# intervals include bit-only, complex-only and double fallback, hence do
# not silently omit the dirty/exceptional branches.
results={}
for z in (Q(1,100),Q(1,99)):
 mb=moment.moment(HB,64,113829,z,True);mc=moment.moment(HC,73,12720,z,True)
 product=(mb[0]*mc[0],mb[1]*mc[1]);core=moment.moment(dict(H),64*73,113829*12720,z,False)
 pb=moment.moment(HB,64,113829,z,False);pc=moment.moment(HC,73,12720,z,False)
 assert core[0]<=pb[1]*pc[1] and pb[0]*pc[0]<=core[1]
 assert mb[0]>1 and mc[0]>1 and product[0]>1
 results[str(z)]={'bit':list(map(str,mb)),'complex':list(map(str,mc)),'joint_with_all_fallback_combinations':list(map(str,product)),'joint_core':list(map(str,core))}
rate=Q(a['bit_c']);complex_rate=Q(a['complex_b']);k=Q(a['kappa'])
cap=rate/(1+rate);optimistic=complex_rate/(1+complex_rate)
assert k<cap<optimistic<Q(1,100)
result={'status':'PASS_SCOPED_INDEPENDENT_PACKET_OBSTRUCTION','source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (assembly,bit,cx,engine)},'tensor_profile':dict(sorted(H.items())),'tensor_m':64*73,'tensor_W':113829*12720,'exact_tests':results,'balanced_bit_cap':str(cap),'optimistic_complex_only_cap':str(optimistic),'current_kappa':str(k),'gap_to_bit_cap':str(cap-k),'rate_needed_for_kappa_0.01':str(Q(1,99)),'scope':'Independent sequential/tensor packets and stationary convex mixtures with the existing normalized supplier interfaces. Extra wrapper/setup/movement/recovery costs are nonnegative; omitted costs cannot rescue a moment already above one. No claim about correlated rank sharing, a new joint kernel, or a compiler that changes contracts.'}
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(result['status']);print('bit cap',float(cap),'complex-only cap',float(optimistic),'tensor ranks',len(H))
