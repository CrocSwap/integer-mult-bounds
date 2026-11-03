# Exact backward precision for the Newton bulk

Let pi=1+i, n>=1, 1<=R<=n, 0<=a<=n-R and p>=0. The last two parameters are
integers. Put N=2^n and W=(nI-sum_j X_j)/2, where X_j flips cube coordinate j.
The fixed graph has F_0=x and

    F_h=(W-a-h+1)F_(h-1)/h,
    bulk=i^a sum_(h=0)^R (i-1)^h F_h.

For each output coordinate, the W pass starts an accumulator at n F_(h-1)
and subtracts its n neighbors, then divides by 2. This is the literal
polynomial_oracle graph in the retained PR5825 source. The subtraction of
(a+h-1)F_(h-1), division by h and bulk accumulation follow that pass.

## Error contract and exact optimum

After each of the nN neighbor ADDs in pass h, an independent error can be any
multiple of pi^q in the Gaussian integers. All other operations are exact.
The required output error is in pi^p times the localization of Z[i] at (pi).
An odd denominator is a unit in this congruence. Equivalently, for the source's
numerator pi^n bulk, the required output error has valuation at least p+n.

This is a robust residue-lift contract. It permits heterogeneous precision at
every ADD. It does not assert that deterministic rounding on an actual reachable
lattice can generate every permitted independent error. Correlated errors,
shared bulk/residual computation, altered graphs and exact lattice encodings
are different contracts.

For h=1,...,R define

    D_h = max_(h<=k<=R) [k-2h+2+2 v_2(h binom(k,h))],
    q_h = max(0,p+D_h).

**Theorem.** Every neighbor ADD in pass h has minimum nonnegative precision
q_h. These minima are simultaneously sufficient. They are sharp individually:
if q_h>0, lower any one ADD to q_h-1 and an explicit single error violates
the output congruence. Therefore the exact minimum neighbor-ADD precision mass is

    n 2^n sum_(h=1)^R q_h.

The formula has no dependence on a or n other than R<=n and the operation
multiplicity. It is an exact optimum for the declared errors and graph, not a
binary-time or physical memory optimum.

## Exact suffix map

Let an error delta enter a neighbor accumulator at coordinate r in pass h.
Later neighbor subtractions read F_(h-1), so the error persists unchanged in
that accumulator. The two divisions send delta/(2h) into F_h. Its final
linear effect is K_h(W) delta e_r, where

    K_h(W) = i^a/(2h) sum_(k=h)^R
             (i-1)^k / binom(k,h) * binom(W-a-h,k-h).

This identity follows either by the forward recurrence for F_k or by
S_R=i^a(i-1)^R I and
S_h=i^a(i-1)^h I + S_(h+1)(W-a-h)/(h+1), with K_h=S_h/(2h).
It applies to every source x and every neighbor position in the pass.

## Integral Boolean expansion

Set E_j=(I-X_j)/2. The commuting idempotents E_j sum to W. For any integer b
and d>=0, Vandermonde's identity in the Boolean quotient gives

    binom(W-b,d) = sum_(s=0)^d binom(-b,d-s)
                         sum_(|J|=s) product_(j in J) E_j.

All displayed binomial coefficients are integers. Each displacement coefficient
therefore has valuation at least -2d. The coefficient at any displacement of
Hamming weight exactly d is (-1)^d/2^d: only J equal to that displacement
contributes. In particular this valuation bound is attained whenever d<=n.

The k-th summand of K_h has every coefficient of valuation at least

    2h-k-2-2 v_2(h binom(k,h)).

Let k_* be the largest k attaining D_h. At any displacement of weight k_*-h,
all terms with smaller k vanish. The k_* term has valuation exactly -D_h.
Every term with larger k has strictly larger valuation by the choice of k_*.
Thus no cancellation removes the leading digit. Every coefficient of K_h has
valuation at least -D_h, and one has valuation exactly -D_h.

An error pi^q times any Gaussian integer has output valuation at least q-D_h.
This proves sufficiency for q=q_h. Finite sums of permitted errors retain that
valuation, so every local minimum can be used at the same time. For sharpness,
use delta=pi^(q_h-1) at the chosen ADD and zero error elsewhere. At the witness
displacement its output valuation is p-1. A zero source is sufficient for this
error-model witness. This is not a claim about deterministic rounding of zero.

## Complete high-degree consequence

The single k=R term gives

    q_h >= max(0,p+R-2h+2+2 v_2(h binom(R,h))).

In particular the first W pass alone requires at least p+R+2v_2(R) digits at
every neighbor ADD. This removes the old uniform-at-least-p premise for all
positive degrees in this error contract. More strongly, with
L=min(R,floor((p+R+1)/2)),

    mass >= n 2^n L(p+R+1-L).

If p>=R-1, this is n 2^n R(p+1). For p=n and R=n-1 it is
n 2^n (n^2-1). The bound follows from actual neighbor ADDs; it grants all other
work for free. The exact formula can be larger. At n=p=8,R=7, every offset has
q=(16,15,14,13,8,7,3), with exact mass 155648. The single-outer-shell floor is
145408. At n=p=16,R=15 the exact mass is 310378496.

PR5900's credited residual-prefix bound treats low degree under its own
max-descendant contract. Here the high-degree literal bulk remains expensive
even with heterogeneous digits. At p=Theta(n), the new high-degree bound is
Omega(2^n n^3), and the first-pass bound alone is Omega(2^n n^2). Neither is a
universal Gaussian lower bound or a selected multiplier theorem. A new graph,
shared computation or a justified dependent-error/lattice contract is needed
before further work on this route can claim an exponent gain.

## Credit

Ali Romman, with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
Credit David Ganz / Dugongue PR5813 and PR5815 for the Gaussian/Newton construction,
Ali Romman PR5825 for the named graph and uniform-precision boundary, and Nick
Petalas PR5900 for the low-degree residual theorem and explicit high-degree
question. PR5890's bulk denominator result is related endpoint context; its
quantity is not this per-ADD suffix demand. Boolean idempotents, Vandermonde's
identity and non-Archimedean valuation rules are classical. The new result is
the exact source-graph demand law, optimal error schedule and high-degree bill.
