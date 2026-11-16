from cov4 import *
gens=load_gens('grp.out')
print(len(gens))
T=[t for t in range(n) if t not in set(parabolic((0,1,2,3,4,5)))]
t0=time.time(); print(cover_set4(T,[6,6,6,5,5,1,1,1],gens,verbose=True),time.time()-t0)
