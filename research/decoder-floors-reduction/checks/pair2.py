# Can two outside columns (t=1) BOTH have label deficiency >=2? Need 2-dim Z_a, Z_b (Z = U_A^perp) and h != 0 with
# O(Z_a) ∩ O(Z_b) ∩ Off(h) = ∅  (lines in both agreement sets are ⊥ h = η_a − η_b). O(Z) = lines whose label is outside Z^perp.
# h ranges over the |Off|<=76 list; others have |Off|>=77 and |O(Z_a)∩O(Z_b)|>=40 > 112-77, so the intersection meets Off(h).
exec(open('cat1.py').read().split("res=[]")[0])
import itertools
pk=lambda S: sum(1<<i for i in S)
Ob={phi:pk(O[phi]) for phi in O}
# 2-dim subspaces Z={0,a,b,a^b}: O(Z) = O_a ∪ O_b ∪ O_{a^b}
Zs={}
for a in range(1,512):
    for b in range(a+1,512):
        c=a^b
        if c<b: continue
        Zs[(a,b,c)]=Ob[a]|Ob[b]|Ob[c]
print('2-dim Z:',len(Zs))
offs=[(pk(o),kind) for o,(kind,h) in sel.items()]
# For every direction h (|Off| <= 76) decide whether two 2-dim classes Z_a, Z_b with disjoint O(Z_a)∩Off(h), O(Z_b)∩Off(h) exist.
# Exhaustive: a disjoint pair (A, B) has min(|A|,|B|) <= |Off(h)|/2, so A ranges over the sets of size <= |Off|/2 and B over all sets (exact 0/1 matmul).
Zl=list(Zs.values()); ok_kinds=set(); tested=0
allbits=np.array([[(x>>i)&1 for i in range(v)] for x in Zl],dtype=np.int32)
for o,(kind,h) in sel.items():
    m=np.zeros(v,dtype=np.int32); m[list(o)]=1; tested+=1
    S=np.unique(allbits*m,axis=0); sz=S.sum(1)
    A=S[sz<=len(o)//2]
    hit=bool(A.shape[0]) and bool(((A@S.T)==0).any())
    if hit: ok_kinds.add((kind,len(o)))
print('directions tested:',tested)
print('direction types admitting two deficiency>=2 columns:', sorted(ok_kinds))
