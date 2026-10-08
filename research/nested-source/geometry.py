#!/usr/bin/env python3
"""Exact h32 five-subset matching and central-source geometry controls.

The full producer/physical-role verification is a separate dependency.
"""
from fractions import Fraction as Q
from itertools import combinations
from math import comb
from pathlib import Path
import json,sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from prime_field_checks import matching,edge_cycle

def determinant(A):
 A=[[Q(x) for x in row] for row in A];result=Q(1)
 for j in range(len(A)):
  k=next((i for i in range(j,len(A)) if A[i][j]),None)
  if k is None:return Q(0)
  if k!=j:A[k],A[j]=A[j],A[k];result=-result
  p=A[j][j];result*=p
  for i in range(j+1,len(A)):
   c=A[i][j]/p
   for k in range(j,len(A)):A[i][k]-=c*A[j][k]
 return result

def run(h=32):
 assert h%4==0
 n=h-2
 # All triples on the first four outside coordinates, followed by (0,1,i).
 # The 4x4 seed has determinant -3; each additional column has a unique 1.
 triples=list(combinations(range(4),3))+[(0,1,i) for i in range(4,n)]
 X=[[int(i in T) for i in range(n)] for T in triples]
 det=determinant(X);assert abs(det)==3
 gram=[[sum(a*b for a,b in zip(x,y)) for y in X] for x in X]
 assert determinant(gram)==9
 checked_pairs=0;digest=hashlib.sha256()
 for C in combinations(range(h),2):
  outside=[i for i in range(h) if i not in C]
  vectors=[sum(1<<a for a in C)+sum(1<<outside[i] for i in T) for T in triples]
  assert len(vectors)==n and all(v.bit_count()==5 for v in vectors)
  for i,u in enumerate(vectors):
   for j,v in enumerate(vectors):
    # t_S^t(I-2J/25)t_T = |S intersect T|-2.
    rational_gram=(u&v).bit_count()-2
    assert rational_gram==gram[i][j]
    checked_pairs+=1
  digest.update(json.dumps([C,vectors],separators=(',',':')).encode())
 # Exact ambient nondegeneracy. Rank-one determinant lemma and inverse.
 ambient_det=1-Q(2*h,25);assert ambient_det
 coef=Q(2,25-2*h)
 assert -Q(2,25)+coef-Q(2,25)*coef*h==0
 # Norm, orthogonality, and the F3 scalar kernel hold independently of h.
 for k in range(6):assert (comb(k,2)-int(k==2))%3==int(k==5)
 assert Q(5)-Q(2,25)*25==3
 match=matching(h)
 assert match['distinct_images']==comb(h,5)
 v=comb(h,5);m=h**3;centers=comb(h,2);local_loss=centers*(h-2)
 numerator=v-6*local_loss
 assert numerator>0
 return dict(status='PASS H32 MATCHING AND FORMAL CENTRAL GEOMETRY; FULL PRODUCER SEPARATE',
  h=h,m=m,vertex_count=v,matching=match,
  ambient_form='I-(2/25)J',ambient_determinant=str(ambient_det),
  inverse_rank_one_coefficient=str(coef),source_norm='3',
  centers=centers,center_span_dimension=n,
  center_identity='For u_C1=u_C2=t and sum(u)=5t, u^T H u = sum_(i outside C) u_i^2. Zero outside forces 3t=0, hence u=0.',
  explicit_center_basis_size=n,outside_basis_determinant=str(det),
  center_gram_determinant='9',all_center_gram_entries_checked=checked_pairs,
  basis_sha256=digest.hexdigest(),
  scalar_kernel_identity='binom(k,2)-[k=2] = [k=5] in F3 for 0<=k<=5',
  local_total_loss=local_loss,global_deficit_fraction=str(Q(numerator,v)),
  bitpacking=dict(ground_bits=32,max_local_pair_coordinate=29,
    global_pair_bits=comb(h,2),required_64_bit_data_words=(comb(h,2)+63)//64,
    required_key_words_including_core=1+(comb(h,2)+63)//64),
  producer_scope='The source-span proof holds for every cancellation-free node whose five-subset sources have a common pair. Full h32 producer must independently verify this property, all coefficient supports, retained totals, role schedule, both directions, source/sink frames, and optimized-template boundaries.')
if __name__=='__main__':
 result=run();Path(__file__).with_name('h32-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
