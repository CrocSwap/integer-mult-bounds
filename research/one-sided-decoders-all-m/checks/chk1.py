from base import *
# linear iso between oscommon labels and mylab: combined rank 9
comb=[D['lab'][t] | (LAB[t]<<16) for t in range(v)]
print('rank lab',f2rank(D['lab']),'rank mylab',f2rank(LAB),'rank combined',f2rank(comb))
print('distinct labels',len(set(LAB)))
print('FC row supports',set(int((FC[t]!=0).sum()) for t in range(v)))
# kappa check: KA for f_i equals mylab(f_i) under iso -> test via term_cost equivalence on random sets
import random
random.seed(1)
def cost_my(R,i=None):
    bs=span_basis([LAB[t] for t in R]); c=len(bs)
    if i is not None and in_span(bs,Z[i]): c-=1
    return c
ok=True
for trial in range(300):
    i=random.randrange(8); R=random.sample(range(v),random.randint(1,12))
    K=KA(D,F0[i])
    if term_cost(D,R,K)!=cost_my(R,i): ok=False;print('mismatch',i,R);break
print('kappa formula ok',ok)
