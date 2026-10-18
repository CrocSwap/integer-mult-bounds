# The A2 family (CONJB section 1): exact construction of rank-9 realisations of the iff pattern on P112 / P104 / E8 (UNIT env).
#   rows a_u = (r_u, 0) off X, a_{u_i} = (r_i + g_i, 1);  cols b_s = (r_s, z_s),  z_s = -g_i . r_s on O_{u_i},  z free on X.
# Checks (all exact over Q): (i) every line off X is orthogonal to a line of X (section 1.1(b)); (ii) the zeros of M = A B^T are exactly the orthogonal pairs
# and the diagonal is nonzero (the iff pattern); (iii) rank M = 9 (A and B have exact rank 9 and M = A B^T); (iv) M equals the Gram matrix off the three rows X.
import random
from a2lib import *
print('unit',UNIT,'lines',v,'A2 triangle X',list(X))
assert all(Gm[X[i]][X[j]]!=0 for i in range(3) for j in range(3) if i!=j)
assert all(any(Gm[x][s]==0 for x in X) for s in range(v) if s not in X)
print('PASS (i) every line off X is orthogonal to some line of X')
E6=[s for s in range(v) if all(Gm[x][s]==0 for x in X)]
assert all(set(O[i])&set(O[j])==set(E6) for i in range(3) for j in range(3) if i<j)
print('PASS O_i cap O_j = lines orthogonal to the whole triangle (%d lines)'%len(E6))
rnd=random.Random(1); good=0; tried=0
while good<3:
    tried+=1
    th=tuple(Fr(rnd.randint(-9,9)) for _ in range(4)); zX=tuple(Fr(rnd.randint(-50,50),rnd.randint(1,7)) for _ in range(3))
    A,B=build(th,zX); M=Mof(A,B)
    if pattern_ok(M)!=0: continue          # an unlucky parameter point creates an extra zero; skip it
    good+=1
    assert rank(A,9)==9 and rank(B,9)==9    # exact: M = A B^T with both factors of full column rank 9, so rank M = 9
    off=[u for u in range(v) if u not in X]
    assert all(M[u][s]==Gm[u][s] for u in off for s in range(v))
    print('PASS member %d: theta=%s zX=%s: iff pattern exact, rank 9, rows off X equal the Gram rows'%(good,[str(x) for x in th],[str(x) for x in zX]))
print('PASS A2 family on',UNIT,': 3 exact members with the iff pattern and rank 9 (%d parameter draws)'%tried)
