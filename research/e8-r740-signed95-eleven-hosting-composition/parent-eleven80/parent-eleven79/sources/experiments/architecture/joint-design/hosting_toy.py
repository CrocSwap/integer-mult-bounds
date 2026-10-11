"""Exact signed idle-data hosting toy; no actual PR442 circuit admission."""
from pathlib import Path
import json
N=6
I=lambda:[[int(i==j) for j in range(N)] for i in range(N)]
def mul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
def add(t,s,c):
 A=I();A[t][s]+=c;return A
# Signed swap uses 3 transvections and one sign flip: all integer reversible.
def swapword(a,b):return [('add',a,b,1),('add',b,a,-1),('add',a,b,1),('neg',b)]
def program(word):
 A=I()
 for op in word:
  if op[0]=='add':G=add(*op[1:])
  else:G=I();G[op[1]][op[1]]=-1
  A=mul(G,A)
 return A
def inv(word):
 return [((o[0],o[1],o[2],-o[3]) if o[0]=='add' else o) for o in word[::-1]]
# x=(0,1), idle data y=(2,3,4,5). Old pending child swaps
# the first coordinate pair and second coordinate pair. Hosted residual
# occupies first pair; remainder pays second pair.
local=[('add',0,2,1),('add',0,1,1)]+swapword(2,3)+[('add',0,3,-1)]
L=program(local);active=program([('add',0,1,1)]);R=program(swapword(2,3));remainder=program(swapword(4,5));child=mul(remainder,R)
assert L==mul(R,active) # all columns, hence arbitrary host dirt/state.
assert mul(remainder,L)==mul(child,active)
assert program(inv(local))==mul(program(inv(swapword(2,3))),program([('add',0,1,-1)]))
assert mul(program(inv(local)),L)==I()
# Endpoint-only idle ownership is insufficient if an intervening map
# couples pending coordinates. This operation changes coordinate 2 from 4.
T=add(2,4,1)
assert mul(T,R)!=mul(R,T)
unsafe_host=mul(remainder,mul(T,L));unsafe_old=mul(child,mul(T,active))
assert unsafe_host!=unsafe_old
# A disjoint intervening coordinate action does commute.
D=add(4,5,1);assert mul(D,R)==mul(R,D)
assert mul(remainder,mul(D,L))==mul(child,mul(D,active))
result={'status':'PASS_EXACT_SIGNED_HOSTING_TOY_AND_TOUCH_OBSTRUCTION','dimensions':N,'local_word':local,'all_columns_endpoint_block_diagonal':True,'arbitrary_correlated_host_contents':True,'inverse_exact':True,'safe_hosted_operator_equal':True,'disjoint_touch_operator_equal':True,'cross_coordinate_touch_rejected':True,'charges':{'local_signed_updates':len(local),'inverse_signed_updates':len(local),'remainder_child_signed_updates':4,'parent_child_signed_updates':8,'host_coordinate_isometry_updates':0,'full_forward_scan_passes_upper':len(local)+4,'full_inverse_scan_passes_upper':len(local)+4,'setup':'constant descriptors, each word step scans its affected coordinate streams','bank':'two already-live idle coordinates; no new independent bank in the toy','routing':'identity contiguous owner only; PR442 nonidentity routes not covered','recovery':'active endpoint and both idle swaps exact; inverse restores every input column'},'scope':'Toy proves factor reuse can be real under exact block-diagonal endpoint, matching coordinate basis and commutation window. Does not establish PR442 cover-class ownership, global chart bases, paid profile or bank lifecycle.'}
(Path(__file__).resolve().parent/'HOSTING-TOY.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
