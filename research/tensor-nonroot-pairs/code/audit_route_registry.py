"""Exact route registry checks and nonvacuous matrix/inverse/projector/factor controls."""
import copy,json,sys
from pathlib import Path
from fractions import Fraction as Q
from audit_rational_route import check
source=Path(sys.argv[1]);data=json.loads(source.read_text());receipts={}
for frame,route in data['registry'].items():
 result=check(route);mutations=[]
 for name in ['route','projector','inverse','factor']:
  z=copy.deepcopy(route)
  if name=='route':z['route'][0][0]=str(Q(z['route'][0][0])+1)
  elif name=='inverse':z['inverse'][0][0]=str(Q(z['inverse'][0][0])+1)
  elif name=='projector':z['individual_residual_projectors'][0][0][0]=str(Q(z['individual_residual_projectors'][0][0][0])+1)
  else:z['elementary_reduction']=z['elementary_reduction'][:-1]
  try:check(z)
  except (AssertionError,ValueError):mutations.append(name)
  else:raise AssertionError('vacuous control: '+name)
 result['rejected_mutations']=mutations;receipts[frame]=result
Path(sys.argv[2]).write_text(json.dumps(dict(status='PASS_EXACT_ROUTE_REGISTRY_AND_CONTROLS',routes=receipts),indent=2)+'\n')
print('PASS',len(receipts),'routes',4*len(receipts),'controls')
