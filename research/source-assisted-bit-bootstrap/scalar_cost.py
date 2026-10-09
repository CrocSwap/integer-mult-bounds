"""Count every literal payload shear and bound the defining integer lift without cancellation."""
if not __debug__: raise RuntimeError("Exact verifier requires assertions; do not use -O")
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();p=a.output_dir
m=json.loads((p/'emitted-word.json').read_text());resp=[int(x,16) for x in m['response']];z={q['role']:q for q in m['gauges']};R=m['R']
root_reads=sum(len(r['targets']) for r in m['roots']);old_reads=sum(x.bit_count() for x in resp);mix=len(m['k']['entries']);k_reads=sum(len(e['receivers']) for e in m['k']['entries'])
adjoint=[0]*R
for root,s in zip(m['roots'],m['rootroles']):adjoint[s]+=len(root['targets'])
xadj=[0]*m['v']
for kind,d,c,f in reversed(m['ops']):
 if kind=='a':adjoint[c]+=adjoint[d]
 else:xadj[c]+=adjoint[d]
forward=[1]*R;largest=1
for kind,d,c,f in m['ops']+list(reversed(m['ops'])):
 forward[d]+=forward[c] if kind=='a' else 1;largest=max(largest,forward[d])
r=dict(elementary_forward_xors=len(m['ops']),elementary_inverse_xors=len(m['ops']),old_value_response_xors=old_reads,root_read_xors=root_reads,partner_mix_forward_inverse_xors=2*mix,partner_delivery_xors=k_reads,total_scalar_xors=2*len(m['ops'])+old_reads+root_reads+2*mix+k_reads,original_X_controls=sum(o[0]=='x' for o in m['ops']),nongauged_response_xors=sum(x.bit_count() for s,x in enumerate(resp) if s not in z),gauged_response_xors=sum(x.bit_count() for s,x in enumerate(resp) if s in z),payload_coefficient_alphabet=[0,1],maximum_absolute_payload_shear_coefficient=1,integer_non_cancelling_majorants=dict(maximum_aux_old_read_row_l1=max(adjoint),sum_aux_old_read_row_l1=sum(adjoint),maximum_X_adjoint_row_l1=max(xadj),maximum_forward_and_inverse_row_l1=largest,interpretation='Noncancelling defining-integer-word coefficient majorants, not exact coefficient maxima or an integer identity. F2 adjoints are separately stored in emitted word.'),note='XOR scalar transcript counts only. Frame adapters, inverses and base-case bit implementation remain covered by assembled supplier guard. Every emitted payload shear already has unit coefficient overF2; no decomposition needed.')
(p/'scalar-cost.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
