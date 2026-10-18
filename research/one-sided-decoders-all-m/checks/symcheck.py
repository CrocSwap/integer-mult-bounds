# Symmetry used to justify checking the cover facts for one root target Off(r0) and one frame target N(f0) only (cover.py, cover6.py, gT.py):
# the 1352 generators in gens.txt act on the 112 lines by |<r_t,r_s>|-preserving permutations, act F2-LINEARLY on the labels, permute the 8 frame
# targets N(f_i) = {t : c_t[i] != 0}, and generate a group transitive on the 112 lines and on the 8 frame targets.  Hence every Off(r) (resp. N(f_i))
# is carried to Off(r0) (resp. N(f0)) by a label-linear line permutation, which preserves every flat, every cover and every rank.
import json, numpy as np
D=json.load(open('data.json')); L=np.array(D['L']); FC=np.array(D['FC']); LAB=D['LAB']; n=112
G=np.rint(L@L.T).astype(int)
gens=[list(map(int,l.split())) for l in open('gens.txt')]
def is_linear(g):
    # linear iff for every F2-dependency among labels the images satisfy the same dependency: test via kernel of the 112 x 9 label matrix
    rows=[LAB[t] for t in range(n)]; imgs=[LAB[g[t]] for t in range(n)]
    # Gaussian elimination tracking images
    piv=[]  # (vector, image)
    for v,i in zip(rows,imgs):
        for pv,pi in piv:
            if v^pv<v: v^=pv; i^=pi
        if v: piv.append((v,i))
        elif i: return False   # dependency with nonzero image combination
    return True
Fsets=[frozenset(t for t in range(n) if FC[t][i]!=0) for i in range(8)]
ok=True
for g in gens:
    ok&= sorted(g)==list(range(n))
    ok&= all(abs(G[g[a]][g[b]])==abs(G[a][b]) for a in range(n) for b in range(n))
    ok&= is_linear(g)
    ok&= all(frozenset(g[t] for t in Fsets[i]) in Fsets for i in range(8))
def orbit(start,act):
    seen={start};st=[start]
    while st:
        x=st.pop()
        for g in gens:
            y=act(g,x)
            if y not in seen: seen.add(y);st.append(y)
    return seen
o1=orbit(0,lambda g,x:g[x]); o2=orbit(Fsets[0],lambda g,x:frozenset(g[t] for t in x))
print('generators:',len(gens),'; all permutations / |inner product|-preserving / label-linear / permute frame targets:',ok)
print('orbit of line 0:',len(o1),'of 112; orbit of N(f_0):',len(o2),'of 8')
assert ok and len(o1)==112 and len(o2)==8
print('symcheck OK')
