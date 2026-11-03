# Exact pruned correction and the standalone Newton-W cost boundary

## Exact source and input contract

PR5815 at f0fcda576df410dc15cd5b8183d4f74d284eba2b supplies the spectral
construction and valuation proof. This package implements that separate
algorithm, rather than the Smith circuit in PR5821. It reuses only PR5821's
frozen Gaussian integer arithmetic and retains both sets of source notices.
No headline claim about ETH is an assumption of this result.

Let pi=1+i, n>=1, N=2^n, 0<=R<n, 0<=a<=n-R and p>=0. The source x is an
arbitrary Gaussian-integer cube. Let W=(nI-sum X_j)/2 and

```
g(j) = i^a sum_(h=0)^R (i-1)^h binom(j-a,h),
d_j = i^j-g(j), e_j=d_j/pi^(R+1), Q=p+2n-R-1, m=n-R-1.
```

Generalized binomial coefficients include negative j-a. The source proves
e_j is integral. The checker constructs every coefficient and performs the
exact division; it does not accept a floating valuation estimate.

The output is the integral numerator `G_T x = pi^n (A_n-g(W))x` modulo
pi^(p+n), with final denominator header n. Source x stays unchanged. Owned
work has explicit initialization and reset counts. This is an indexed array
contract with owned reset, not a physical reversible-tape implementation.

## Emitted gather and delivery

For each Walsh label lambda, let beta_lambda=v_pi(e_|lambda|), with infinity
for zero. A leaf is live only if beta_lambda<Q. Its required precision is
q_lambda=Q-beta_lambda. At every prefix v, use q_v=max of its live descendant
precisions. The compiler emits a literal sum/difference child array at q_v.
It does not replace that source read by a rank oracle. The exact gather mass is

```
M = sum_(nonempty prefixes v) 2^(n-|v|) q_v.
```

This is computed once from the tree and once from the executed operations.
At a live leaf, remove pi^beta from e and apply its remaining Gaussian
coefficient by a literal binary doubling/addition word. This coefficient is
a pi-adic unit; it need not be a Gaussian unit of magnitude one. Its actual
bits determine the multiplication additions. No unit-cost dense multiplier
is inserted into the invoice.

For synthesis, each child has already removed its minimum beta. Restore the
nonnegative difference between child and parent factors, then emit both
sum/difference halves. An absent child requires copies or signs, not a free
full-vector delivery. The root factor is restored at Q. The resulting z is
`H diag(e) Hx` modulo pi^Q. The source identity is

```
G_T x = i^n z/pi^m.
```

The exact integral numerator implies z is divisible by pi^m. A representative
modulo pi^Q has the same divisibility, since Q>=m. Exact division therefore
gives the required modulus pi^(Q-m)=pi^(p+n). The interpreter checks every
quotient. It records phases, scales, copies, coefficient work, output writes
and reset counts in addition to ADD precision mass. Preparation records all
n+1 coefficients, binomial terms, coefficient heights and exact divisions.
These are positive operation counts, not a complete binary-time tariff.

## Source-bound sharing

A shared bank uses one immutable snapshot of x. Each leaf is created at the
maximum demand of all named consumers. Each prefix then uses the maximum of
those leaf demands. The same induction proves every consumer receives enough
precision. Each delivery still performs its own coefficient word, full
synthesis, quotient and output write. The API checks the actual source value
at delivery and charges N version reads. Insufficient creation precision,
changed input and a retired bank are rejected. Retirement removes the stored
snapshot and coefficients from the live bank and has explicit reset charges.

A positive fixture uses n=8 and four distinct (a,R,p) tuples:
(0,2,1), (2,3,2), (4,2,3), (1,5,1). The separate gather mass is84867; the shared
mass is31862. Including every synthesis and coefficient ADD, the mass falls
from169623 to116618, a31.25% reduction. All scale, phase, source, copy, prepare,
quotient and cleanup counts remain separate in RESULT.json. This is a fixed
component comparison, not a runtime ratio, a complete P104 invoice or proof
that this is the best algorithm for the four responses. In particular, a
shared full transform plus separate polynomial responses is another baseline.

## Exact degree-zero cost at every width

For R=0, d_j=i^j-i^a. If j-a is0 modulo4, it is zero. If j-a is odd, its
valuation is1. If j-a is2 modulo4, its valuation is2. Thus e has valuation0
or1 on live leaves. For n>=2, all such leaves remain live for every p>=0.

Every proper prefix has at least one unprocessed bit. Its possible completion
weights include two consecutive integers, one of which differs oddly from a.
That descendant has beta=0. Consequently **every prefix through depth n-1
exists at the full Q=p+2n-1 precision**, despite exact valuation pruning.

Put c_b=sum binom(n,j) over j-a congruent to b modulo4. Then the exact gather
precision mass is

```
M_0 = N(n-1)Q + (N-c_0)Q - c_2
    >= N(n-1)(p+2n-1).
```

The first term is forced by the complete proper-prefix tree. The second is
the leaf sum. The checker reconstructs189 complete trees and compares this
closed formula. This all-width statement covers the degree-zero residual
compiler itself, without an assumption about the bulk implementation.

## All-interval boundary for the stated standalone circuit

For positive degree, fix the literal Newton-W bulk graph used by the
independent polynomial oracle: each of its R steps applies W to the current
full array before the next falling-factor update. One W pass computes
`n*v[r]-sum_j v[r xor 2^j]` at every r. It executes nN neighbor additions.
The checker counts exactly R*n*N such additions in every endpoint case.

Consider the **uniform bulk precision contract** that each such addition is
assigned at least p Gaussian digits. This is an explicit metered circuit
contract, not a lower bound inferred from a big-O upper bound. It includes
the usual uniform-modulus Newton-W implementation. A fused, shared or
heterogeneous-precision bulk is outside this clause.

If R>=1, its ADD precision mass is at least nNp. If R=0, the preceding exact
residual theorem gives at least N(n-1)(p+2n-1). Hence for n>=2, every interval
and degree in this standalone bulk-plus-correction circuit costs at least

```
(n/2) N p.
```

This lower bound already grants every other operation for free. At p=Theta(n)
it is Omega(N*n^2), while the integer source has Theta(N*n) bits. In the stated
precision-work model this emitted route cannot give a positive log-exponent
saving. A new representation, shared bank, changed bulk graph or different
precision contract is required to escape the statement. It is not a barrier
to all Gaussian or spectral algorithms, native queries or finite networks.

The source already warns that its Smith word retains this asymptotic scale.
The new cost result closes the degree-zero exception and states an exact
all-interval obstruction for the named standalone Newton-W route. The generic
source's upper-bound formula alone would not have proved this lower bound.

## Independent checks and result

The oracle computes g(W)x through falling factorials over exact rational
Gaussian pairs, then subtracts it from the original C-tensor numerator. It
uses no Walsh transform, coefficient valuation or pruned circuit. The actual
residual agrees for all336 parameter choices through n=7, including all a,R
and p in{0,1,3}, plus98 basis columns. Normalized p=0 remains a nontrivial
fractional-grid task. There is no input parity or symmetry promise.

Across that complete bounded census, exact valuation/zero pruning reduces
uniform interval-mask gather mass from1265104 to1251298, about1.09%. The shared
fixture is a larger component improvement, but no current physical caller
has been supplied. These data are not asymptotic measurements. The construction
and the scope of the cost boundary determine the released next task.

Credit Dugongue/PR5815 for the residual and sharing construction, PR5813 for its
spectral predecessor, and all frozen native/precision/ownership/compiler
notices. New implementation, exact census, source-version controls and scoped
cost proof: Ali Romman with substantial OpenAI Codex assistance; no subagents.
All five framework assumptions remain. No new kappa or frontier change is claimed.
