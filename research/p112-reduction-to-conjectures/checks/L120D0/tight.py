# impl A: tight-count kill test for the ClassI A_{p-1} pattern (rows 159 p=8 both A7 classes; 302/398 p=9).
exec(open('lab.py').read())
from collections import Counter
pc=lambda x: bin(x).count('1')
Zm=[sum(1<<i for i,l in enumerate(lab) if pc(u&l)%2==0) for u in range(512)]
FULL=(1<<120)-1
def rref_subspaces(k):  # all k-dim subspaces of F2^9 as basis lists (RREF)
  for piv in itertools.combinations(range(9),k):
    free=[(r,c) for r in range(k) for c in range(9) if c>piv[r] and c not in piv]
    for bits in range(1<<len(free)):
      rows=[1<<piv[r] for r in range(k)]
      for i,(r,c) in enumerate(free):
        if bits>>i&1: rows[r]|=1<<c
      yield rows
def km(rows):
  m=FULL
  for u in rows: m&=Zm[u]
  return m
fl7=set(km(r) for r in rref_subspaces(2)); fl6=[km(r) for r in rref_subspaces(3)]
print("7-flat line sets",len(fl7),"6-flat subspaces",len(fl6))
done=set()
for p in (8,9):
  for ch in chains(p):
    c=classify(ch)
    if (p,c) in done: continue
    done.add((p,c))
    g=[gvec(t,ch) for t in L]; need=[]; pat=[]; ex=[]
    for gv in g:
      cnt=Counter(gv).most_common(); m1=cnt[0][1]; m2=cnt[1][1] if len(cnt)>1 else 0
      need.append(p-m1)
      if m1>m2: pat.append({k for k in range(p) if gv[k]!=cnt[0][0]}); ex.append(m1-m2)
      else: pat.append(None); ex.append(0)
    TOT=sum(need); cap=36*p
    A=[sum(1<<i for i in range(120) if pat[i] is not None and a in pat[i]) for a in range(p)]
    m=[max(pc(A[a]&F) for F in fl7) for a in range(p)]
    flex=sum(1 for x in pat if x is None and True)
    r=min(ex[i]/need[i] for i in range(120) if pat[i] is not None and need[i]>0)
    worst=None; nk=0
    for L0 in fl6:
      s=sum(need[i] for i in range(120) if L0>>i&1)
      beta=cap-TOT+s
      H=sum(max(0,pc(A[a]&~L0)-m[a]) for a in range(p))
      ok_kill = (beta<0) or (r*H>beta)
      if not ok_kill:
        nk+=1
        if worst is None or beta-r*H>worst[0]: worst=(beta-r*H,beta,H,s)
    print(f"p={p} perp={c}: TOT={TOT} cap={cap} m_a={m} r={r} flexible={flex} surviving 6-flats={nk} worst={worst}")
