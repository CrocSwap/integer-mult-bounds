"""Exact gap to a linear ADDRESS-only spectator restoration."""
from pathlib import Path
from fractions import Fraction as F
import json
O=Path(__file__).resolve().parent;cases=[]
for q in(3,5,7):
 for m,a,b in[(2,1,1),(8,7,1),(64,7,1),(78,7,1)]:
  N=q**(2*m);wanted=N*(F(1,q**a)+F(1,q**b)-F(1,q**(a+b)));lower=F(N,q**min(a,b));upper=F(N,q**(min(a,b)-1));assert lower<wanted<upper and wanted.denominator==1
  assert (N-wanted)/2==F(N,2)*(1-F(1,q**a))*(1-F(1,q**b))
  cases.append({'q':q,'m':m,'parts':[a,b],'spectator_trace':str(wanted),'consecutive_address_involution_trace_lower':str(lower),'upper':str(upper),'required_spectator_negative_value_rank':str((N-wanted)/2)})
r={'status':'EXACT_ADDRESS_ONLY_SPECTATOR_RESTORATION_GATE','cases':cases,'proof':'For any oddq ADDRESS-linear involution overFq, diagonalizable withnegativeaddressrankinteger r, the inducedVALUE permutation hastrace q^(2m-r)=N/q^r. Requiredspectatortrace N*(q^-a+q^-b-q^-(a+b)) liesstrictlybetweenN/q^b andN/q^(b-1) aftera>=b. No rankr canmatch. Products oflinearADDRESSselectors remainlinear; ifthefinaloperator isthis involution, thesametrace test applies.','scope':'This is a boundary for restoring the invariant N-dimensional spectator by one physical stream carrying only a linear ADDRESS permutation. Does not exclude cross-family VALUE mixing, arbitrary partial VALUE selectors, additional encoded streams, a time-dependent encoding or a changed paid local endpoint. Negative VALUE rank is not a primitive or recursive-rank cost.'};(O/'SPECTATOR-ADDRESS-GATE.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
