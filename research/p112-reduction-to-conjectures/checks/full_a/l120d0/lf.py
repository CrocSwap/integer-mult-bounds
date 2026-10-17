# Lemma-F need counts for the A_{p-1} root pattern (ClassI scenario of rows 159 (p=8), 302/398 (p=9)).
# impl A: g-vector multiplicity formula; impl B: brute-force rank over subsets J. Exact integers (roots doubled).
import itertools, sys
from fractions import Fraction as Fr
R=[]
for i in range(8):
  for j in range(i+1,8):
    for si in (2,-2):
      for sj in (2,-2):
        v=[0]*8; v[i]=si; v[j]=sj; R.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
  if s.count(-1)%2==0: R.append(tuple(s))
assert len(R)==240
ip=lambda a,b: sum(x*y for x,y in zip(a,b))//4   # true inner product
L=[r for r in R if r>tuple(-x for x in r)]; assert len(L)==120
def chains(p):
  # all A_{p-1} chains up to sign starting from fixed beta1 (W(E8) transitive on roots); dedupe by root set
  b1=L[0]; out={}
  def ext(ch):
    if len(ch)==p-1:
      S=set()
      for a in range(p-1):
        for b in range(a+1,p):
          v=tuple(sum(ch[k][i] for k in range(a,b)) for i in range(8)); S.add(max(v,tuple(-x for x in v)))
      key=frozenset(S)
      if key not in out: out[key]=list(ch)
      return
    for r in R:
      if ip(r,ch[-1])==-1 and all(ip(r,c)==0 for c in ch[:-1]): ext(ch+[r])
      if len(out)>=60: return
  ext([b1]); return list(out.values())
def gvec(t,ch):
  g=[0]
  for b in ch: g.append(g[-1]-ip(t,b))
  return g
def needA(t,ch):
  g=gvec(t,ch); p=len(g); return p-max(g.count(v) for v in set(g))
def rank(rows):
  M=[[Fr(x) for x in r] for r in rows]; rk=0; n=len(M[0]) if M else 0
  for c in range(n):
    piv=next((i for i in range(rk,len(M)) if M[i][c]!=0),None)
    if piv is None: continue
    M[rk],M[piv]=M[piv],M[rk]
    for i in range(len(M)):
      if i!=rk and M[i][c]!=0:
        f=M[i][c]/M[rk][c]; M[i]=[a-f*b for a,b in zip(M[i],M[rk])]
    rk+=1
  return rk
def needB(t,ch):
  p=len(ch)+1
  # functionals on V in beta-coords: v=sum c_i beta_i. x_k(v)=c_k-c_{k-1} (c_0=c_p=0). f_t(v)=sum c_i <t,beta_i>
  X=[[ (1 if i==k else 0)-(1 if i==k-1 else 0) for i in range(p-1)] for k in range(p)]
  f=[ip(t,b) for b in ch]
  if all(x==0 for x in f): return 0
  for m in range(1,p+1):
    for J in itertools.combinations(range(p),m):
      rows=[X[k] for k in J]
      if rank(rows+[f])==rank(rows): return m
def classify(ch):
  span_perp=sum(1 for t in L if all(ip(t,b)==0 for b in ch)); return span_perp
for p in (int(a) for a in sys.argv[1:]):
  cs=chains(p); seen={}
  for ch in cs:
    c=classify(ch)
    if c in seen: continue
    nA=[needA(t,ch) for t in L]; nB=[needB(t,ch) for t in L]
    assert nA==nB, "impl mismatch"
    seen[c]=1
    from collections import Counter
    print(f"p={p} A{p-1} class(perp lines={c}): need hist {sorted(Counter(nA).items())} total {sum(nA)} cap 36*{p}={36*p}")
