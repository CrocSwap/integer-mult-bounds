# labels l(t)=(r mod 2E8, 1) in F2^9; rank of A_a sets; |Lambda(6-flat)| max; deletion number delta_a
import itertools, sys
sys.argv=[sys.argv[0]]; exec(open('lf.py').read().split("for p in (int")[0])
# E8 lattice basis (doubled coords): simple roots
B=[(2,-2,0,0,0,0,0,0),(0,2,-2,0,0,0,0,0),(0,0,2,-2,0,0,0,0),(0,0,0,2,-2,0,0,0),(0,0,0,0,2,-2,0,0),(0,0,0,0,0,2,-2,0),(0,0,0,0,0,2,2,0),(-1,-1,-1,-1,-1,-1,-1,-1)]
def coords(v):
  M=[[Fr(B[j][i]) for j in range(8)]+[Fr(v[i])] for i in range(8)]
  for c in range(8):
    piv=next(i for i in range(c,8) if M[i][c]!=0); M[c],M[piv]=M[piv],M[c]
    for i in range(8):
      if i!=c and M[i][c]!=0:
        f=M[i][c]/M[c][c]; M[i]=[a-f*b for a,b in zip(M[i],M[c])]
  x=[M[i][8]/M[i][i] for i in range(8)]; assert all(q.denominator==1 for q in x); return [int(q)%2 for q in x]
lab=[sum(b<<i for i,b in enumerate(coords(t)))|(1<<8) for t in L]
assert len(set(lab))==120
def rk2(vs):
  basis=[]
  for v in vs:
    for b in basis: v=min(v,v^b)
    if v: basis.append(v)
  return len(basis)
assert rk2(lab)==9
# 6-flats and 7-flats via dual functionals
def mask(us):
  return [i for i,l in enumerate(lab) if all(bin(u&l).count('1')%2==0 for u in us)]
