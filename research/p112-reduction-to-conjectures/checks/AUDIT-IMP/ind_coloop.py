# AUDIT-IMP: coloop facts (#2816 coloop.py / K1-T2 row spans), independent of repo data. Run after ind_e8.py builds objects.
exec(open('ind_e8.py').read().split("# directions:")[0])
off=lambda h: [t for t in range(v) if ip(L[t],h)!=0]
bad=0
for s in range(v):
    T=off(L[s]); assert rk([LAB[t] for t in T])==9
    co=[t for t in T if rk([LAB[u] for u in T if u!=t])<9]
    if co!=[s]: bad+=1
    # pairs other than the coloop: removing any two non-coloop lines keeps rank 8 after removing s?  (rank of Off(r_s)\{s}\{a} == 8)
print('root targets with coloop set != {itself}:',bad)
bad2=0
for i,f in enumerate(F0):
    T=off(f); assert rk([LAB[t] for t in T])==8
    for t in T:
        if rk([LAB[u] for u in T if u!=t])!=8: bad2+=1
print('frame targets Off(f_i)\\{v} not spanning W_i:',bad2)
# caveat for K1-T2 L3: l_v in W_j (=z_j^perp) iff <r_v,f_j> odd; count per v
from collections import Counter
print('#j with l_v in W_j, distribution over v:',Counter(sum(beta(LAB[t],Zf[j])==0 for j in range(8)) for t in range(v)))
print('beta(z_i,z_j)==1 all i,j:',all(beta(a,b)==1 for a in Zf for b in Zf))
