"""Supplementary fixed-mixture packing ceiling, not a supplier construction."""
import json,sys
from pathlib import Path
from fractions import Fraction as Q
import ceiling
P=Path(__file__).resolve().parent
spec=json.loads((Path(sys.argv[1])/'inputs/SOURCE-SPEC.json').read_text())
claim=json.loads((Path(sys.argv[1])/'CLAIM.json').read_text())
h={int(k):int(v) for k,v in spec['expected']['global_profile'].items()}
assert spec['expected']['live']==74*896 and spec['geometry']['dimension']==73
local={k:Q(v,666) for k,v in h.items() if k!=48}
assert sum(k*v for k,v in h.items())==72*66304+64*666
lo,hi=ceiling.ceiling(local,73,896,9,64)
k=Q(claim['kappa'])
r=dict(status='PASS_FIXED_MIXTURE_PACKING_CEILING',native_saving_ceiling_bracket=[str(lo),str(hi)],rank_cap=51,local_profile={str(k):str(v) for k,v in local.items()},kappa_over_native_cap_interval=[str(k/hi),str(k/lo)],scope='Fixed 249-A/417-B mixture, nine stages, 896 live families per replica, centre64, retained coverage law and rank51 halving guard. Native saving ceiling, not the historical balanced a/(1+a) transfer. Current outer ledger has kappa<q<b, so this native upper ceiling also upper-bounds its kappa. No universal ceiling or improved construction.')
(P/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS_FIXED_MIXTURE_PACKING_CEILING',float(lo),float(hi),'fraction',float(k/hi))
