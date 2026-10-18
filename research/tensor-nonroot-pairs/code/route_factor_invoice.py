from pathlib import Path
from fractions import Fraction as Q
import json,sys,hashlib
from quaternion_route import primes
geo=Path(sys.argv[1]);allocation=Path(sys.argv[2]);out=Path(sys.argv[3]);g=json.loads(geo.read_text());a=json.loads(allocation.read_text());bad=set();counts=[];maxfactor=0
for p in g['ports']:
 cols=[[Q(x,2)for x in p['q']]]+[[Q(row[j])for row in p['complement_columns']]for j in range(7)];A=list(map(list,zip(*cols)));count=0
 for j in range(8):
  k=next(i for i in range(j,8)if A[i][j])
  if k!=j:A[j],A[k]=A[k],A[j];count+=1
  x=A[j][j]
  if x!=1:
   for v in (x,1/x):bad.update(primes(v.denominator));maxfactor=max(maxfactor,abs(v.numerator),v.denominator)
   A[j]=[y/x for y in A[j]];count+=1
  for i in range(8):
   if i!=j and A[i][j]:
    x=A[i][j];bad.update(primes(x.denominator));maxfactor=max(maxfactor,abs(x.numerator),x.denominator);A[i]=[y-x*z for y,z in zip(A[i],A[j])];count+=1
 assert A==[[Q(i==j)for j in range(8)]for i in range(8)];counts.append(count)
for z in a['registry'].values():
 for op in z['elementary_reduction']:
  if op[0]!='swap':
   x=Q(op[-1]);bad.update(primes(x.denominator));maxfactor=max(maxfactor,abs(x.numerator),x.denominator)
   if op[0]=='scale':bad.update(primes(abs(x.numerator)))
iso=max(x['elementary_count']for x in a['registry'].values());total=iso+8+77+77+max(counts)
r=dict(status='PASS_EXACT_FIXED_ROUTE_FACTOR_INVOICE',geometry_sha256=hashlib.sha256(geo.read_bytes()).hexdigest(),allocation_sha256=hashlib.sha256(allocation.read_bytes()).hexdigest(),port_bases_checked=len(counts),max_port_basis_gaussian_factors=max(counts),max_pair_gaussian_factors=iso,copy_swap_bound=8,placement_permutation_bound=77,pending_axes_permutation_bound=77,total_one_direction_bound=total,charged_residual_isometry=512,inverse_charged_by_outer_leading_two=True,all_factor_bad_primes=sorted(bad),max_factor_numerator_denominator=maxfactor,scope='Fixed dyadic translations, same inherited GL routing contract. Finite literal factor count enters selector invoice; no new asymptotic assumption.')
assert total<=512 and maxfactor<2**128
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
