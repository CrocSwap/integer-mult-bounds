"""Independent arithmetic gate for actual helper240 first/last flags."""
from fractions import Fraction as F
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;p=O/'source-closure/experiments/architecture/cross-copy-inventory/BOUND-SPLITS.json'
q=3;m=8;N=q**(2*m)
L=F(N,4)*(1-F(1,q)+F(1,q**8)-F(1,q**7))
rows=[]
for a in [7,1]:
 P=F(N,4)*(1-F(1,q)+F(1,q**a)-F(1,q**(a-1)))
 assert L.denominator==P.denominator==1 and L>P
 assert L-P==F(N*(q-1),4)*(F(1,q**a)-F(1,q**8))
 rows.append({'carrier_width':a,'logical_joint_minus_plus_dimension':int(L),'physical_joint_minus_plus_dimension':int(P),'missing_logical_dimensions':int(L-P)})
r=json.loads((O/'ACTUAL-FIRST-LAST.json').read_text());r['binding_source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();r['q3_m8_exact_dimensions']=rows
(O/'ACTUAL-FIRST-LAST.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
