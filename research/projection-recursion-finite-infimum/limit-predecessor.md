# Exact limit of the projection recursion

This is a theorem about an explicit arithmetic recurrence. Its interpretation
as a complex-engine lower bound inherits the representation and hook premises
of Jacob Alan Sussman #4628 and Maximilian Lutz #4643. None of those premises
is proved or certified here.

## Statement

Fix an integer b >= 1 and a nonnegative real profile a_b(0),...,a_b(b),
with a_b(0)=0 and a_b(1)>0. For k>b and 0<=r<=k, define

```
a_k(r) = sum_s N_k(r,s) a_(k-1)(s),
N_k(r,r)   = 2^(k-r)-1 + 4^k-2^(k+r),
N_k(r,r-1) = 2(2^k-2^(k-r)) + (2^r-1)2^(k-1),
N_k(r,r-2) = (2^r-1)(2^(r-1)-1)2^(k-r).
```

The third entry is zero at r=0,1. The first entry is zero at r=k.
Zero entries outside the previous profile's range are omitted. At r=0
only N_k(0,0)=4^k-1 remains. These are the cited predecessor counts.
No optional triangle/max strengthening is part of this recurrence.

Write [b choose r]_2 for the Gaussian binomial coefficient and put

```
Z_b = product_(i=1)^b (2^i+1),
C_b = (2^(b+1)+1)/(2^b-1),
f(r) = a_b(r)/a_b(1),
F = max_(0<=r<=b) f(r),
T_m = a_m(m)/a_m(1).
```

Then the exact limit is

```
L_b = (C_b/2) / Z_b
      * sum_(r=0)^b [b choose r]_2 2^(r(r+1)/2) f(r).
```

For every pair of integers b<=K<m, the following explicit error bound holds:

```
|T_m-L_b| <= F * ((C_b/2) * (9/(2(m-K)) + 2^(2-K))
                   + 3 C_b/(2(2^(m+1)+1))).                 (1)
```

Choosing K=floor(m/2) for m>=2b proves convergence. The formula is exact
for every seed profile in the stated domain, rather than a decimal estimate
of one seed's tail. It does not assert monotonicity or that L_b is an
all-m lower bound.

For b=4 and the cited seed (0,27456,48576,68320,86592),

```
Z_4 = 2295,
([4 choose r]_2 2^(r(r+1)/2))_(r=0)^4 = (1,30,280,960,1024),
C_4/2 = 11/10,
L_4 = 439277/149175 = 2.9447092341209986... .
```

The exact rational limit and the general limit/error theorem are the new
result. The predecessor's quoted decimal 2.944709234 agrees to its displayed
precision; that agreement is not a new hook-rank verification.

## 1. Normalize the recurrence

Each row of N_k sums to 4^k-1. Thus P_k(r,s)=N_k(r,s)/(4^k-1)
is a stochastic reduction from block k to k-1. If X starts at distance m
at block m and follows these reductions down to b, then

```
a_m(m) = a_b(1) product_(k=b+1)^m (4^k-1) * E[f(X_b)].
```

At r=1 only the s=1 term contributes, with coefficient

```
N_k(1,1) = (2^(k-1)-1)(2^(k+1)+1).
```

Both products telescope to give

```
T_m = G_(m,b) E[f(X_b)],
G_(m,b) = C_b (2^m-1)/(2^(m+1)+1),
G_(m,b) -> C_b/2,
C_b/2-G_(m,b) = 3 C_b/(2(2^(m+1)+1)).            (2)
```

## 2. A coherent family of reference distributions

In a binary symplectic space of dimension 2k, fix a Lagrangian L.
There are

```
D_k(r) = [k choose r]_2 2^(r(r+1)/2)
```

Lagrangians M with distance r=k-dim(L intersect M). To see this, first
choose I=L intersect M of codimension r in L. In I-perp/I, a transverse
Lagrangian to L/I is the graph of a symmetric r-by-r binary matrix over
a chosen complementary Lagrangian. There are 2^(r(r+1)/2) such matrices.

The total number Z_k is product_(i=1)^k(2^i+1). An elementary induction
counts pairs (p,M), with 0!=p in M. There are 2^k-1 choices in each M,
and each of the 4^k-1 nonzero p belongs to Z_(k-1) Lagrangians, by
reduction in p-perp/<p>. Hence Z_k=(2^k+1)Z_(k-1).

For uniform M and independently uniform nonzero p, the reduced M is
uniform among Lagrangians of p-perp/<p>. Indeed each symplectic map of
that quotient lifts, by extending a symplectic basis, to a map fixing p;
the lifted map permutes the original uniform M's and commutes with
reduction. The quotient action is transitive. The reduced L is fixed
conditional on p. Consequently the distance law D_k/Z_k reduces to
D_(k-1)/Z_(k-1). This also follows by substituting the three displayed
N_k coefficients into the Gaussian-binomial formula.

Use the deficit j=k-r. Let pi_k(j)=D_k(k-j)/Z_k for 0<=j<=k.
In deficit coordinates the coherence identity is pi_k P_k=pi_(k-1).
For fixed j,

```
pi_k(j) = w_j * product_(i=k-j+1)^k(1-2^-i)
                 / product_(i=1)^k(1+2^-i),
w_0=1,  w_j=1/product_(i=1)^j(2^i-1).
```

Since pi_k(j)<=w_j, and w_j<=3^(-(j-1)) for j>=1, dominated
convergence on this countable set proves total-variation convergence
pi_k -> pi, where pi(j)=w_j/sum_h w_h. It also proves that
sum_h w_h=product_(i=1)^infinity(1+2^-i). No infinite numerical product
is needed to evaluate L_b.

## 3. A homogeneous comparison chain

Put M=2^k and z=2^j. The deficit transition from j has probabilities

```
u_k(j) = (M^2/(2z)-3M/2+z)/(M^2-1),  to j+1,
d_k(j) = (z-1+M^2-M^2/z)/(M^2-1),    to j-1,
1-u_k(j)-d_k(j),                     to j.
```

At j=k the transition is deterministically to k-1; the same formulas
apply. Define the homogeneous chain Q on nonnegative integers by

```
u(j)=2^(-j-1),  d(j)=1-2^-j,  stay(j)=2^(-j-1).
```

Detailed balance holds because w_(j+1)/w_j=1/(2^(j+1)-1), so pi is
stationary for Q. Its expected deficit is at most 9/8: the unnormalized
first moment is at most sum_(j>=1) j/3^(j-1)=9/4 and the normalizer
is at least w_0+w_1=2.

Q is monotone. Adjacent states can cross in an ordered coupling only
if u(j)+d(j+1)>1; here their sum equals 1. Use inverse distribution
functions driven by one uniform random number to preserve order.
Couple a chain starting at 0 below a stationary chain starting with pi.
When the upper chain first reaches 0 they coalesce.

From j>=1 the upper chain's mean increment is
3*2^(-j-1)-1<=-1/4. Stopping at 0 and at a deterministic time n gives
E[min(tau,n)]<=4j by summing this drift and using nonnegativity of the
stopped state. Letting n increase gives E[tau|j]<=4j. Thus the coupling
time has mean at most 9/2, and Markov's inequality proves, for n>=1,

```
TV(delta_0 Q^n, pi) <= 9/(2n).                        (3)
```

This argument supplies recurrence and convergence directly; it invokes
no unproved mixing assumption.

For 0<=j<=k, direct subtraction gives

```
u_k(j)-u(j) = (-3M/2+z+1/(2z))/(M^2-1) <= 0,
d_k(j)-d(j) = (z-1/z)/(M^2-1) >= 0.
```

The total variation of the three-entry rows is the maximum of these
two absolute differences. The first is <=2/M and the second <=4/(3M)
for M>=2. Extend P_k to j>k by using Q there. Therefore

```
sup_j TV(P_k(j,.),Q(j,.)) <= 2^(1-k).                (4)
```

## 4. Convergence down to the fixed seed block

Let A_(m,K)=delta_0 P_m ... P_(K+1). The starting deficit is 0.
Stochastic kernels contract total variation. Telescoping (4), with
sum_(k=K+1)^m 2^(1-k)<=2^(1-K), and (3) give

```
TV(A_(m,K),pi) <= 9/(2(m-K)) + 2^(1-K).
```

Apply the same comparison with starting distribution pi_m. Coherence
gives pi_m P_m ... P_(K+1)=pi_K, while stationarity gives
pi Q^(m-K)=pi. Since pi_m -> pi, taking m to infinity yields
TV(pi_K,pi)<=2^(1-K). Hence

```
TV(A_(m,K),pi_K) <= 9/(2(m-K)) + 2^(2-K).
```

Propagate both laws from K to b. Coherence and contraction show that
the same upper bound holds for TV(A_(m,b),pi_b). In distance coordinates
pi_b has probabilities D_b(r)/Z_b. Since 0<=f<=F, the expectation
difference is at most F times this total variation bound. Combine this
with (2) and G_(m,b)<=C_b/2 to obtain (1) and the asserted limit.

## Limits of the conclusion

The hook values are premises, including the two lower bounds whose stored
rank certificates #4643 leaves open. The result is unconditional as a theorem
about the stated recurrence, and conditional when interpreted as an engine
bound. It certifies no engine implementation, new paid construction, physical
cost, selected frontier, or complete multiplication theorem. The optional
triangle strengthening is outside the theorem. No infimum over finite m,
monotonicity theorem, or formal proof-kernel review is asserted.
