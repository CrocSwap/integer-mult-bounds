#!/usr/bin/env python3
"""Exact local-profile packing ceiling; the modern outer claim is separate."""
import importlib.util,json
from fractions import Fraction as Q
from decimal import Decimal,localcontext
from pathlib import Path
HERE=Path(__file__).resolve().parent
ENGINE=HERE.parents[1]/'research/complex-local-word-ceiling/ceiling.py'
IDLE={1:21829,3:6495,5:612,7:172,8:49,32:31,48:26508}
def calculate():
 spec=importlib.util.spec_from_file_location('packing_ceiling',ENGINE)
 engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
 h={int(r):n for r,n in json.loads((HERE/'evidence/SWAP-PROFILE.json').read_bytes()).items()}
 local={r:Q(h[r]-IDLE.get(r,0),666) for r in h if h[r]!=IDLE.get(r,0)}
 model=engine.model(local,73,896,9,64)
 assert model['total_mass']*666==4816512 and model['local_mass']==5251
 lo,hi=engine.ceiling(local,73,896,9,64)
 endpoint=Q(json.loads((HERE/'evidence/SWAP-MOMENT.json').read_bytes())['endpoint']['lower'])
 with localcontext() as ctx:
  ctx.prec=50
  dec=lambda x:str(Decimal(x.numerator)/Decimal(x.denominator))
  return dict(local_per_call={str(r):str(n) for r,n in sorted(local.items())},replicas=74,calls=666,dimension=73,families=896,stages=9,centre_rank_per_call=64,max_idle_rank=model['R'],complex_cap_lower=str(lo),complex_cap_upper=str(hi),complex_cap_decimal=dec(hi),realized_fraction_lower=str(endpoint/hi),realized_fraction_decimal=dec(endpoint/hi),scope='Hosted nine-stage coverage-law relaxation with fixed aggregate local profile and idle ranks at most 51. Fraction measures the complex endpoint against its packing ceiling. No historical a/(1+a) outer map is applied; the current outer ledger is checked separately.')
if __name__=='__main__':
 (HERE/'evidence/PACKING-CAP.json').write_bytes((json.dumps(calculate(),indent=2)+'\n').encode())
