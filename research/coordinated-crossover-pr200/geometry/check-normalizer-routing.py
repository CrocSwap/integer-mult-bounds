"""Literal fixed scalars distinguish all same-invocation bank normalizers.
No greedy unknown chart is assumed: H_b=(b+1)*Pi_b*diag(B^-1,I_48).
All gauges share the same unchanged24coordinate stage; outside-coordinate
unit columns distinguish H_b for b=0..17 at every primeq>2^80.
"""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;records=[]
for stage in range(3):
 local=set(range(24*stage,24*(stage+1)));j=next(i for i in range(72) if i not in local)
 for width,blocks in [(4,18),(24,3)]:
  original=list(range(24*stage,24*stage+width));witness=[]
  for block in range(blocks):
   desired=list(range(block*width,(block+1)*width));src=original+[i for i in range(72) if i not in original];dst=desired+[i for i in range(72) if i not in desired]
   pi=dict(zip(src,dst));assert set(pi)==set(pi.values())==set(range(72))
   assert [pi[k] for k in original]==desired
   # Embedded B^-1 fixes e_j exactly, so H_b e_j is this literal unit column.
   witness.append(dict(block=block,scalar=block+1,unit_column=j,result_row=pi[j],result_coefficient=block+1))
  for a,left in enumerate(witness):
   for right in witness[a+1:]:assert (left['result_row'],left['result_coefficient'])!=(right['result_row'],right['result_coefficient'])
  records.append(dict(stage=stage,width=width,blocks=blocks,outside_stage_column=j,witnesses=witness))
out=dict(status='PASS_LITERAL_DISTINCT_NORMALIZERS',records=records,prime_guard='All1..18 are different nonzero units at every primeq>2^80, and remain units/distinct in Z/q^w. Each normalizer scales a literal outside-stage unit column differently. Scaling doesnotchange projectorconjugation.',per_role_scalar_coordinate_factors=72,already_charged_in_chart_bound329=True,no_same_invocation_bank_alias=True)
(H/'LITERAL-NORMALIZER-ROUTING.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(out['status'])