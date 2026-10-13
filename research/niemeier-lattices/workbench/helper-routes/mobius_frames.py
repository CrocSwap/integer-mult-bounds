"""Exact paid-frame obstruction for the unfused D16 spinor Mobius circuit."""
from pathlib import Path
import sys,json
from math import comb
import numpy as np
PACKAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PACKAGE / 'code'))
import e8_cubed as e
n=14;N=1<<n
ports=np.array([[1]+[(-1)**((x>>i)&1)for i in range(n)]+[(-1)**x.bit_count()]for x in range(N)],dtype=np.int16)
sequence=[]
for k in range(n+1):
 face=ports[:1<<k]
 rank=len(e.modular_rank_witnesses(face,prime=3));expected=1 if k==0 else 2 if k==1 else k+2
 e.require(rank==expected,'Exact canonical Boolean-face rational rank')
 sequence.append(rank)
# Physical frames carry the union for BOTH operands, even if one scalar is unchanged.
footprints=[1<<i for i in range(N)];checks=[]
for bit in range(n):
 for low in range(N):
  if (low>>bit)&1:continue
  high=low|(1<<bit);union=footprints[low]|footprints[high];footprints[low]=footprints[high]=union
 expected_size=1<<(bit+1)
 e.require(all(mask.bit_count()==expected_size for mask in footprints),'Every wire has a full Boolean-face footprint')
 checks.append(dict(layer=bit+1,wires=N,footprint_size=expected_size,rational_frame_dimension=sequence[bit+1]))
e.require(all(mask==(1<<N)-1 for mask in footprints),'All roles have visited the full source span')
neighbors=[x for x in range(N)if x.bit_count()in(7,8)]
caprank=len(e.modular_rank_witnesses(ports[neighbors],prime=3))
e.require(caprank==15 and np.all(ports[neighbors]@ports[0]==0),'Exact target cap span')
degree=comb(14,7)+comb(14,8);e.require(degree==6435 and degree%2==1,'Odd adjacency degree gives an involution in characteristic two')
print(json.dumps(dict(status='PASS_SCOPED_MOBIUS_FRAME_OBSTRUCTION',ports=N,ambient_dimension=16,
 rational_face_rank_sequence=sequence,butterfly_layers=checks,
 final_frame_dimension_every_role=16,target_cap_dimension=15,
 adjacency_degree=degree,adjacency_binary_rank=N,
 adjacency_invertibility_proof='The orthogonality adjacency is convolution by the6435 translations of weights7 and8 in the elementary abelian2-group. In characteristic2, every distinct pair of translations occurs twice in its square, while each translation squares to the identity. Thus A^2=6435 I=I.',
 mandatory_full_to_cap_rank_mass=N,
 spinor_center_rank=576,spinor_center_bill=9216,spinor_per_call_asymptotic_surplus=N-9216,
 scoped_failure='The16384 necessary full-to-cap output descents exceed the spinor per-call asymptotic surplus7168 before any other helpers. Output reassignment cannot help because every role is full and every target cap has dimension15; the adjacency outputs are independent.',
 full_shell=dict(ports=30960,center_bill=13040,extra_copy_rank1=16384,effective_bill=29424,remaining_asymptotic_surplus=1536),
 proof='After each complete coordinate butterfly layer, both operands must share the union of their incoming frames. Induction gives every role the complete Boolean face in all coordinates already processed. The port coordinates on a k-face are the constant character, k single-coordinate characters, and their product; their ranks are1,2,k+2 as checked modulo3. Sign translations are diagonal real isometries, so the canonical-face calculation applies to every face. At the last layer every wire reaches dimension16. Scalar cancellations in the Darboux shear or inverse Mobius stage cannot reduce a visited physical frame for free.',
 scope='This excludes the straightforward in-place14-layer Mobius / middle-shear / inverse-Mobius realization under the stated center models. It does not exclude fused, copied, partially transformed, or differently framed circuits.'),indent=2,sort_keys=True))
