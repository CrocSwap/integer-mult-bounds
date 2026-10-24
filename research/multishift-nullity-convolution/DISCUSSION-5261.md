DONE: exact joint nullities at any number of distinct scalar shifts.

This answers the first open question in Nick Petalas's [PR #4803](https://github.com/CrocSwap/integer-mult-bounds/pull/4803), which asks for a three-shift formula. The result counts all shifts at once and retains their dependence. It does not change kappa or supply a paid header cover.

**Source and scope.** Start point: canonical main `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7. The [source question and two-shift result](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/schur-rank-pair-law/README.md) credit @petalas for the two-eigenspace count and ssafwann's [PR #4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678) for the binary Schur-header application. The argument below extends the same subspace-counting method. Gaussian binomial inversion is classical; no priority claim outside this repository is made.

**Formula.** Let q be a prime power, V=F_q^n, and let lambda_1,...,lambda_t be distinct elements of F_q, so t<=q. Let a_i be nonnegative integers. Write G(N,k) for the Gaussian binomial coefficient, with value zero outside 0<=k<=N. For k=(k_1,...,k_t), put K=sum_i k_i and s_i=sum_{j<i} k_j. Define

```text
M(k) = q^[n(n-K)] * product_i (G(n-s_i,k_i) * q^[s_i*k_i])
mu(d) = (-1)^d * q^[d(d-1)/2].
```

The number of matrices H in Mat_n(F_q) with dim ker(H-lambda_i I)=a_i for every i is

```text
N(a) = sum_{k_i>=a_i, sum_i k_i<=n}
         M(k) * product_i (G(k_i,a_i) * mu(k_i-a_i)).
```

If sum a_i>n, the count is zero. An empty shift list gives q^(n*n). The formula depends on the number of distinct shifts, not on their values. For one vector a it has at most binomial(n-sum(a)+t,t) summands. This is a bound on arithmetic summands for fixed t, not a bit-complexity or measured runtime claim.

**Proof.** Count pairs (H,(W_i)), where each W_i has dimension k_i and H acts as lambda_i I on W_i. Eigenspaces for distinct eigenvalues have a direct sum. Given the first i-1 subspaces, their sum has dimension s_i. Choose the image of W_i in V/(sum_{j<i} W_j) in G(n-s_i,k_i) ways. Each image has q^(s_i*k_i) graph lifts disjoint from the preceding sum. Once all W_i are fixed, H is fixed on their K-dimensional direct sum. It is arbitrary on a complement, with q^(n(n-K)) choices. Thus M(k) counts the stated pairs.

If e_i is the actual nullity at shift i, a fixed H contributes product_i G(e_i,k_i) to M(k). Substitute this in the displayed sum and exchange the finite sums. For one coordinate,

```text
sum_{k=a}^e G(e,k) G(k,a) mu(k-a)
 = G(e,a) * sum_{d=0}^{e-a} G(e-a,d) (-1)^d q^[d(d-1)/2]
 = 1 if e=a, and 0 otherwise.
```

The last sum is product_{j=0}^{e-a-1}(1-q^j). For e>a it contains the zero factor at j=0; for e=a it is the empty product. Applying this identity to every coordinate gives exactly the required indicator. This proves the formula for every n, q and set of distinct shifts.

**Checks and use.** The script below compares the formula to an independent Gaussian-elimination census in ten contexts: q=2 and q=3, n=0,...,3, using all scalar shifts; and q=5, n=2, using three and five shifts. It checks 21,549 matrix/context cases and all 400 nullity bins. It also checks impossible dimensions and an empty shift list. Calibrations over F_3 are N_2(0,0,0)=18, N_3(0,0,0)=3456, and N_3(1,1,1)=1404. These are exact finite checks, not the proof of the all-size claim.

Save the following block as `multiple_shift_nullities.py` and run CPython 3.12:

```sh
python3.12 -I -W error -B multiple_shift_nullities.py
python3.12 -I -W error -O -B multiple_shift_nullities.py
```

Both modes passed with CPython 3.12.13. Expected output:

```text
PASS_MULTIPLE_SHIFT_NULLITIES contexts=10 matrices=21549 bins=400 no_new_kappa
```

```python
from itertools import product
from collections import Counter

def ck(x,s):
 if not x:raise ValueError(s)
def gb(n,k,q):
 if not 0<=k<=n:return 0
 a=b=1
 for i in range(k):a*=q**(n-i)-1;b*=q**(k-i)-1
 ck(a%b==0,'Gaussian integrality');return a//b
def count(q,n,a):
 t=len(a)
 if any(x<0 for x in a) or sum(a)>n:return 0
 ans=0
 for k in product(*(range(x,n+1) for x in a)):
  if sum(k)>n:continue
  taken=0;moment=1;weight=1
  for x,y in zip(k,a):
   moment*=gb(n-taken,x,q)*q**(taken*x);taken+=x
   d=x-y;weight*=gb(x,y,q)*(-1)**d*q**(d*(d-1)//2)
  moment*=q**(n*(n-taken));ans+=moment*weight
 return ans
def rank(a,q):
 a=[r[:] for r in a];r=0;n=len(a)
 for j in range(n):
  v=next((i for i in range(r,n) if a[i][j]%q),None)
  if v is None:continue
  a[r],a[v]=a[v],a[r];u=pow(a[r][j],-1,q);a[r]=[(x*u)%q for x in a[r]]
  for i in range(n):
   if i!=r:
    c=a[i][j];a[i]=[(x-c*y)%q for x,y in zip(a[i],a[r])]
  r+=1
 return r
contexts=[(2,n,2) for n in range(4)]+[(3,n,3) for n in range(4)]+[(5,2,3),(5,2,5)]
matrices=0;bins=0
for q,n,t in contexts:
 hist=Counter()
 for values in product(range(q),repeat=n*n):
  a=[list(values[i*n:(i+1)*n]) for i in range(n)]
  dims=tuple(n-rank([[(a[i][j]-(lam if i==j else 0))%q for j in range(n)] for i in range(n)],q) for lam in range(t))
  hist[dims]+=1;matrices+=1
 for dims in product(range(n+1),repeat=t):
  ck(count(q,n,dims)==hist[dims],('census',q,n,dims));bins+=1
 ck(sum(hist.values())==q**(n*n),'total')
ck(count(3,3,(0,0,0))==3456,'irreducible cubic calibration')
ck(count(3,3,(1,1,1))==1404,'three distinct eigenspaces')
ck(count(3,2,(1,1,1))==0,'dimension control')
ck(count(3,2,(0,0,0))==18,'irreducible quadratic calibration')
ck(count(3,3,())==3**9,'empty shift set')
print('PASS_MULTIPLE_SHIFT_NULLITIES contexts='+str(len(contexts))+' matrices='+str(matrices)+' bins='+str(bins)+' no_new_kappa')
```

**Limits and handoff.** No predecessor executable, extension-field matrix census, Lean proof, Docker run, selected cold replay or physical supplier was tested. The proof, rather than a modulo-prime implementation, supplies the extension-field claim. To use the result, replace a sum over compressed matrices by this exact joint-nullity distribution only when the weight depends on these nullities. The nonbinary Schur criterion, actual request weights, cover selection/emission, physical reads, dirty restoration and complete bill remain separate obligations. A useful next step is to state one nonbinary equal-scalar Schur weight and apply this distribution to it.

Before this work, the overlap helper covered all 7,091 current local notes, 323 open PRs and 4,526 Discussion records with complete pagination. Targeted all-state PR search and the current source question were also checked. The search found the predecessor question; arbitrary diffs and unpublished work remain outside that coverage. Prepared by @aliromman with OpenAI Codex assistance. No independent human or formal proof-kernel review is claimed. New text and code: Apache-2.0.
