"""Nontrivial signed chart MODEL: two hosts, intervening child, cover routes."""
from pathlib import Path
import json
N=10
def ident():return [[int(i==j) for j in range(N)] for i in range(N)]
def mm(A,B):return [[sum(A[i][k]*B[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
def inverse_word(w):return [((o[0],o[1],o[2],-o[3]) if o[0]=='add' else o) for o in w[::-1]]
def matrix(w):
 A=ident()
 for op in w:
  G=ident()
  if op[0]=='add':G[op[1]][op[2]]+=op[3]
  else:G[op[1]][op[1]]=-1
  A=mm(G,A)
 return A
def swap(a,b):return [('add',a,b,1),('add',b,a,-1),('add',a,b,1),('neg',b)]
U=[('add',2,6,1),('add',4,8,-1)]
def chart(w):return inverse_word(U)+w+U
active=[('add',0,1,1)]
r1=swap(2,3);r2=swap(4,5);idle=swap(6,7);rest=swap(8,9)
# Arbitrary host values borrow into active wire and are removed using their
# exact post-residual positions. Conjugation extends that identity to U basis.
local=[('add',0,2,1),('add',0,4,-1)]+active+r1+r2+[('add',0,3,-1),('add',0,5,1)]
L=matrix(chart(local));A=matrix(active);R1=matrix(chart(r1));R2=matrix(chart(r2));D=matrix(chart(idle));Q=matrix(chart(rest));parent=mm(Q,mm(R2,R1))
assert L==mm(R2,mm(R1,A))
assert mm(R1,R2)==mm(R2,R1)
assert mm(D,R1)==mm(R1,D) and mm(D,R2)==mm(R2,D)
old=mm(parent,mm(D,A));host=mm(Q,mm(D,L));assert old==host
oldword=active+chart(idle)+chart(r1+r2+rest)
hostword=chart(local)+chart(idle)+chart(rest)
assert matrix(oldword)==matrix(hostword)
assert matrix(inverse_word(hostword))==matrix(inverse_word(oldword))
assert mm(matrix(inverse_word(hostword)),host)==ident()
# Common basis is essential: same nominal idle pair without U conjugation fails.
wrong=matrix(idle);assert mm(wrong,R1)!=mm(R1,wrong)
assert mm(Q,mm(wrong,L))!=mm(parent,mm(wrong,A))
# Coordinate changes differ per slot. Abstract cover G=Z/4 uses exact
# translation sigma=0,1. For a fixed invocation class d owners differ.
# All classes are sequential here; this is not a PR442 scheduling assertion.
routes=[]
for d in range(4):
 owners=[(d-sigma)%4 for sigma in (0,1)]
 assert len(set(owners))==2
 for sigma,owner in zip((0,1),owners):assert (owner+sigma)%4==d
 routes.append({'invocation_cover_class':d,'slot_isometries':[0,1],'owners':owners,'inverse_owner_recovery':[int((owner+sigma)%4) for sigma,owner in zip((0,1),owners)]})
# Bill every literal signed update. All 10 words may be scanned each step;
# this intentionally conservative bound includes signs, source reads, writes.
def bill(w):
 adds=sum(o[0]=='add' for o in w);neg=sum(o[0]=='neg' for o in w)
 return {'adds':adds,'negations':neg,'steps':len(w),'full_10_word_scans_upper':len(w),'bit_work_upper':'O(10*w*steps), with w including intermediate coefficient/sign growth'}
result={'status':'PASS_NONTRIVIAL_CHART_MODEL_NOT_PR442_ADMISSION','basis_columns':N,'chart_word':U,'local_word':chart(local),'hosted_full_word':hostword,'old_model_full_word':oldword,'two_host_endpoint_identity':True,'all_intervening_model_children_commute':True,'inverse_all_columns_exact':True,'wrong_basis_idle_child_rejected':True,'cover_model':'Z/4 additive; per invocation injective slots, class invocations sequential','cover_routes':routes,'bill':{'hosted_forward':bill(hostword),'hosted_inverse':bill(inverse_word(hostword)),'old_factorized_model':bill(oldword),'coordinate_route_passes_per_invocation_upper':4,'setup':'O(1) fixed descriptors in model; 4 classes x 2 selector records fully listed','dirty_work':'No hidden scratch coordinates; every sign/update invertible. Intermediate host contents arbitrary and correlated.','charged_stock':'10 live signed words; no independent helper bank; consumes four existing idle coordinates. Cover class record serialization is charged separately, not free global stock.'},'missing_PR442_interface':['finite common-grid signed matrices or integer primitive words for each chart U_q and cover route sigma','explicit per-cover physical stream ownership and scheduling for simultaneous versus sequential class calls','actual conjugated matrix for every ignored intervening idle child, with exact commutator zero','all-column dirty local endpoint residual operator in that same chart, not only local rank/width','actual primitive/routing/selector/sign fee and stock invoice for those words'],'scope':'A model demonstrating sufficient operator conditions and a precise wrong-basis failure; not a replay of PR442 source geometry.'}
(Path(__file__).resolve().parent/'CHART-MODEL.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status']);print('hosted forward steps',len(hostword),'factorized old model steps',len(oldword))
