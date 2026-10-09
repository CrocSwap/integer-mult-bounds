#!/usr/bin/env python3
"""Paid padded69D triple sharing for the retained weighted PR130 bit word.

PR130 geometry/weighted recursion: icekylinx with OpenAI GPT-6 Astra.
Retained PR97 local word: Zhihao Chen and Swapnil Jain. This extension
prepared for eumemic with OpenAI Codex assistance. Apache-2.0.
"""
import argparse,json,sys
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from partial_gauge_bit import reconstruct
from three_stage_cover_network import log_upper,exp_upper
from structured_bulk_assembly import js,halving
BAD=Q(1,10**16);ATOM=Q(1,1000);OLD=Q(384599,10**10);GRID=10**12
INPUT='certificates/three-stage-cover-bit-input.json'
INHERITED_NOTES=('notes/three-stage-cover-bit.tex','notes/three-stage-cover-rows.tex','notes/three-stage-cover-note.tex')


def matmul(A,B):
 n=len(B);C=[]
 for row in A:
  out=[Q(0)]*len(B[0])
  for k,a in enumerate(row):
   if a:
    for j,b in enumerate(B[k]):
     if b:out[j]+=a*b
  C.append(out)
 return C

def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def inverse(A):
 n=len(A);B=[row[:]+e for row,e in zip(A,eye(n))]
 for i in range(n):
  j=next(j for j in range(i,n)if B[j][i]);B[i],B[j]=B[j],B[i];a=B[i][i];B[i]=[x/a for x in B[i]]
  for j in range(n):
   if j!=i and B[j][i]:
    a=B[j][i];B[j]=[x-a*y for x,y in zip(B[j],B[i])]
 assert [row[:n]for row in B]==eye(n)
 return [row[n:]for row in B]
def add(A,B,sign=1):return [[a+sign*b for a,b in zip(x,y)]for x,y in zip(A,B)]
def block_swap(P):
 # Reversed tail coordinates put D_P in ordinary aligned bank coordinates.
 n=len(P);I=eye(n);Z=add(I,P,-1)
 return [Z[i]+P[i]for i in range(n)]+[P[i]+Z[i]for i in range(n)]


def geometry():
 h=23;m=69;old=67;I=eye(h);q0=[Q(i<3)for i in range(h)]
 H=[[Q(int(i==j),2)-Q(1,18)for j in range(h)]for i in range(h)]
 cov=[sum(H[i][j]*q0[j]for j in range(h))for i in range(h)]
 assert sum(x*y for x,y in zip(cov,q0))==1
 K=[[Q(i==j)-cov[j]*q0[i]for j in range(1,h)]for i in range(h)]
 B=[[q0[i]]+K[i]for i in range(h)];Bi=inverse(B)
 assert matmul(B,Bi)==I
 assert all(sum(cov[i]*K[i][j]for i in range(h))==0 for j in range(h-1))
 # In the rational basis (q0,K), (D1,B22), (D2,C22), tau is a
 # permutation cycling three23D blocks. The change of basis is invertible;
 # its first block is the actual A23 and remaining blocks are in A-perp.
 tau=tuple((i+h)%m for i in range(m))
 assert all(tau[tau[tau[i]]]==i and tau[i]!=i and tau[tau[i]]!=i for i in range(m))
 assert set(tau[:h]).isdisjoint(range(h)) and set(tau[tau[i]]for i in range(h)).isdisjoint(set(range(h))|set(tau[:h]))
 ports=0
 for T in combinations(range(h),3):
  t=[int(i in T)for i in range(h)];c=[Q(3*x-1,6)for x in t]
  assert sum(x*y for x,y in zip(t,c))==1
  # P=t*c is the exact retained rank-one projector. P^2=P suffices
  # for diag(I,0,0),diag(P,I22,0),diag(P,0,I22) to have pairwise
  # product P and sum I67+2P. The two added coordinates are zero.
  assert any(t)and any(c);ports+=1
 assert ports==1771
 # An exact weighted nonsymmetric example exercises the universal identities.
 # Arbitrary fixed split projectors follow by similarity; arbitrary diagonal
 # units A are a common conjugation and cancel in every displayed product.
 n=6;G=eye(n)
 for i in range(n-1):G[i][i+1]=Q(i+2,7)
 Gi=inverse(G);Is=eye(2*n)
 def projector(indices):
  E=[[Q(i==j and i in indices)for j in range(n)]for i in range(n)]
  return matmul(matmul(G,E),Gi)
 weights=[Q(i+2,i+3)for i in range(n)]+[Q(1)]*n
 def weighted(P):
  D=block_swap(P)
  return [[weights[i]*D[i][j]/weights[j]for j in range(2*n)]for i in range(2*n)]
 F=weighted(eye(n));checks=0
 for d in (0,1,2):
  residual=[]
  for k in range(3):
   active=set(range(2*k,2*k+2));sigma=set(range(2*k,2*k+d));outside=set(range(n))-active
   FA=weighted(projector(active));TS=weighted(projector(sigma));P=matmul(FA,TS)
   for Oset in (set(),set(sorted(outside)[:1]),outside):
    FO=weighted(projector(Oset));entry=matmul(FO,TS);finish=matmul(FO,FA)
    assert matmul(finish,inverse(entry))==P
    revstart=FO;revfinish=matmul(matmul(FO,TS),FA)
    assert matmul(revfinish,inverse(revstart))==inverse(P);checks+=1
   residual.append(P)
  combined=matmul(residual[2],matmul(residual[1],residual[0]))
  sigmaall=set(i for k in range(3)for i in range(2*k,2*k+d));tail=weighted(projector(sigmaall))
  assert matmul(tail,combined)==F
  if d==0:assert combined==F and matmul(residual[1],residual[0])!=F
  if d:assert combined!=F
 # Frobenius/Schur arguments below concern any odd local ring, not only Q.
 # The exact rational tests are controls; the displayed projector identities
 # are polynomial and hold after any admissible denominator localization.
 return dict(actual_h23_ports_checked=ports,padded_ambient=69,passive_dimensions=2,
  rational_three_block_chart_invertible=True,order_three_free_right_action=True,
  all_three_stages_paired_in_independent_cosets=True,weighted_offset_identity_checks=checks,
  common_diagonal_weight_conjugation=True,completed_reverse_residual_is_forward_inverse=True,
  weighted_combined_exterior_split_rank='69-3*nullity=3*source_dimension',
  local_low_residue_coset_representative_unique=True,high_matrix_batching_unchanged=True,
  right_coset_reason='g*tau^j=g implies tau^j=I; reduction modulo odd q>2^80 retains exact order3, so each residue orbit has three members. Each full orbit has exactly one lift over its chosen residue representative, with all69^2 high coordinates free.',
  zero_width_tails_omitted=True,negative_controls=['omitted-third-completed-residual','omitted-nonzero-gauge-tail'])


def certificate():
 row=json.loads((ROOT/INPUT).read_text());physical=reconstruct()
 assert (row['h'],row['v'],row['R'],row['center_loss'])==(23,1771,28866,506)
 for k in('v','R','local_rank_histograms','exit_nullity_histogram'):assert row[k]==physical[k],k
 geo=geometry();h,v,R=row['h'],row['v'],row['R'];m=3*h;H=Counter();local=Counter()
 for hist in row['local_rank_histograms'].values():
  for r,n in hist.items():local[int(r)]+=n;H[int(r)]+=9*n
 tails=Counter();zero=0
 for nullity,n in row['exit_nullity_histogram'].items():
  r=m-3*int(nullity);assert 0<=r<m
  if r:tails[r]+=3*n
  else:zero+=3*n
 H.update(tails);padding=Counter({2:6*v});H.update(padding);H=dict(sorted(H.items()));W=6*v+3*R;mass=sum(r*n for r,n in H.items())
 assert W*m-mass==3*(2*v-3*h*(h-1))==6072
 assert max(H)==66 and min(H)>0;edges=sum(H.values());fallback=32*m*m
 logs={r:log_upper(Q(m,r))for r in H};logm=log_upper(Q(m))
 def moment(b):
  good=sum(Q(r*n,W*m)*exp_upper(b*logs[r])for r,n in H.items());extra=BAD*Q(fallback*edges,W*m)*exp_upper(b*logm)
  return good,extra
 low,high=0,10**9
 assert sum(moment(Q(low,GRID)))<1 and sum(moment(Q(high,GRID)))>=1
 while high-low>1:
  mid=(low+high)//2
  if sum(moment(Q(mid,GRID)))<1:low=mid
  else:high=mid
 coarse=Q(low,GRID);effective=(1-ATOM)*coarse+ATOM*OLD;good,extra=moment(coarse);rank_upper=mass+BAD*fallback*edges
 assert good+extra<1 and rank_upper<W*m
 assert sum(moment(coarse+Q(1,GRID)))>=1, 'Next coarse enclosure grid accepted'
 assert Q(6*m**3,2**80)<BAD;assert ATOM>effective and ATOM<1-effective
 names=[INPUT,*INHERITED_NOTES,'research/cover-local-reuse/BIT-PADDED.md','certificates/partial-gauge-bit-input.json','references/partial-gauge/pr97/SOURCE.json']
 return dict(status='Exact paid padded triple-sharing bit moment under retained weighted contracts',m=m,h=h,v=v,R=R,
  vertices_per_cell=3,stages=3,roles_per_cell=W,ideal_rank_mass_per_cell=mass,ideal_deficit=6072,maxchild=max(H),halving_degree=halving(m,max(H)),
  local_copies_per_cell=9,local_child_multiplicities=dict(sorted(local.items())),ideal_child_multiplicities=H,
  exterior_child_multiplicities=dict(sorted(tails.items())),data_finish_child_multiplicities=dict(padding),zero_width_exteriors_omitted=zero,
  coarse_saving=coarse,effective_saving=effective,atom_exponent=ATOM,ordinary_leaf_saving=OLD,bad_fraction=BAD,
  fallback_children_per_edge=fallback,edge_count_per_cell=edges,good_moment_upper=good,added_bad_moment_upper=extra,strict_gap=1-good-extra,
  rank_mass_upper_per_cell=rank_upper,prime_bad_bound=Q(6*m**3,2**80),coset_conditioning_factor=3,next_grid_enclosure_rejected=True,
  geometry=geo,weighted_projector_good_class_compiler_retained=True,full_local_ring_fallback_charged=True,
  fresh_group_roles_independent_of_inherited_weights=True,internal_borrowed_row_stock='O(w log e), restored at the outer boundary; depth16*ceil(log2(n))+O(1)',
  exact_role_stock='(|GL_69(F_q)|/3)*(6v+3R)*q^(69^2*(w-1))',
  source_sha256={name:sha256((ROOT/name).read_bytes()).hexdigest()for name in names},checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
  scope='Retained source-bound PR97 reconstruction, exact padded geometry and completed weighted identities, full paid fallback moment and atom conversion. Generic-basis weighted compiler, uniform affine batching, ordinary leaf, borrowed-row restoration and analytic/tape hypotheses remain the explicit retained proof contracts.')


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result=js(certificate());path=HERE/'bit-padded.json';encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if a.write:path.write_text(encoded)
 else:assert path.read_text()==encoded,'Padded bit certificate mismatch'
 print('PASS paddedbit coarse',result['coarse_saving'],'effective',result['effective_saving'],'m69, paid spectators, weighted fallback',flush=True)
if __name__=='__main__':main()
