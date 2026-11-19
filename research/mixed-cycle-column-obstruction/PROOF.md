# The mixed-cycle input does not exist

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Let q >= 5 be prime, b >= 1, n = q+3 and m = 3q^b. There is no
n-by-(n-1) matrix A with entries in the mth roots of unity and A* A = nI.
In particular, there is no eight-by-seven partial Butson matrix over the
fifteenth roots. This resolves the released input in
[PR #7744](https://github.com/CrocSwap/integer-mult-bounds/pull/7744).
It does not follow from failure to find a matrix.

The proof first shows that any such partial matrix would complete in the
original alphabet. It then rules out that square completion. The two steps
are necessary: nonexistence of a square Butson matrix alone does not exclude
a partial matrix whose completion needs a larger alphabet.

## 1. Projected Gram rigidity

Write omega for a primitive third root and eta for a primitive q^bth root.
Every mth root is uniquely omega^x eta^y. Let pi discard eta, and put
B = pi(A), entry by entry. This is a map on the root group, not a
characteristic-zero ring homomorphism.

Each inner product of distinct columns of A is a vanishing sum of n roots.
The two-prime cycle theorem of Lam and Leung decomposes it into rotated
3-cycles and q-cycles. The equation 3r+qs=q+3 has only the nonnegative
solution r=s=1: s is zero or one, and s=0 would require 3 to divide q.
Projection kills the 3-cycle and sends the q-cycle to q times a third root.
Thus B has diagonal column Gram entries n and off-diagonal entries q omega^a.
[Lam and Leung, Theorem 3.3 and Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=7)

For any three columns, the determinant of their Gram matrix is

```text
n^3 - 3nq^2 + 2q^3 Re(omega^t),
```

where omega^t is the product of the three directed off-diagonal phases.
For t=0 this is 27(q+1). For t=1 or 2 it is

```text
-3q^3 + 27q + 27 < 0,                 q >= 5.
```

For example, q^3 >= 25q makes the expression at most -48q+27.
A Gram matrix is positive semidefinite, so every triangle has t=0.
Scale the columns by third roots to make all off-diagonal Gram entries q.
Then scale rows by third roots to make the first column all ones. These
operations preserve the original alphabet and orthogonality of A.

Each other projected column has sum q. Its three symbol counts therefore
satisfy c0-c2=q, c1-c2=0 and c0+c1+c2=q+3. Hence they are (q+1,1,1).
Each column is now the all-one column with omega at one row a and omega^2
at a different row b. Represent it by the directed edge (a,b).

Two different edges have projected inner product q exactly when they share
their first endpoint, share their second endpoint, or are reverses. This
follows by subtracting their two exponent vectors: the difference must
again have one 1 and one 2, with all other entries zero. A reverse pair
cannot have a third compatible edge. If two non-reverse edges have the
same first endpoint, every other compatible edge has that first endpoint;
the same argument applies to a common second endpoint. Thus a compatible
family of at least three edges is a directed star.

For n-1 columns there are n-2 edges. Their distinct leaves and common
centre occupy n-1 rows, so exactly one row is unused. For n columns there
are n-1 edges, and the star occupies every row. Both orientations occur in
this necessary projected classification; it does not supply the q-part
of an actual orthogonal matrix.

## 2. The partial input would complete without a negative sign

Use the unused row u as the normalization row. The formula from
[PR #5865](https://github.com/CrocSwap/integer-mult-bounds/pull/5865) gives

```text
w = (nI - AA*) e_u,        w_u = 1,        H = [A w].
```

It proves H*H=nI and w_i in the 2mth roots. In particular each w_i is
eps omega^x eta^y with eps in {1,-1}. That theorem uses the rank-one
complement, integrality of the displayed formula and Kronecker's theorem;
we retain its proof as a dependency.

Reduce in the ring R = F_q[X]/(X^2+X+1), with omega sent to X and eta
sent to 1. This is a ring map from Z[omega,eta], since the q^bth
cyclotomic polynomial takes the value q at 1. It commutes with inversion
of roots. R is nonzero and has odd characteristic. The powers of X have
odd order, so their coset and its negative are disjoint. This remains true
when R has zero divisors.

The unused row of B is all ones. If the star has exponent s in {1,2}
at its centre and -s at each leaf, the projected row sums are

| Row | Sum across the n-1 supplied columns | Negative sum modulo q |
| --- | --- | --- |
| Centre | 1 + (q+1) omega^s | omega^(-s) |
| Leaf | q+1 + omega^(-s) | omega^s |
| Unused | q+2 | The diagonal term makes w_u=1 |

The completion formula therefore reduces each w_i to a positive power
of X. Disjoint sign cosets force eps=1 for every i. Thus H uses only
mth roots. Undoing the row and column phases preserves this property.
A different normalization row changes w by an mth root, so the conclusion
does not depend on which row was originally first.

## 3. No square completion can have these parameters

Apply Section 1 to a hypothetical n-by-n H. Its projected star has n-1
leaves. Multiply its centre row by omega^(-s), and order rows and columns
so the constant column is first and each leaf matches its edge column.
The projected matrix then has omega^(-s) on the diagonal and 1 elsewhere.
Scale rows by q^bth roots to make the q-part of every diagonal entry 1.
Consequently

```text
H = Q + (omega^(-s) - 1) I,
```

where Q has entries in the q^bth roots and Q_ii=1.

For columns i and j, the two nontrivial third-root terms in their inner
product occur at rows i and j. In the unique one-3-cycle/one-q-cycle
decomposition, they must belong to the same 3-cycle, with the same q-part.
Their q-parts are Q_ij and conjugate(Q_ji). Thus Q is Hermitian.
Since omega+omega^2=-1, full orthogonality gives

```text
HH* = Q^2 - 3Q + 3I = (q+3)I,
Q^2 - 3Q - qI = 0.
```

The two possible eigenvalues of Q are (3 +/- sqrt(9+4q))/2. If the first
has integer multiplicity k, the trace condition trace(Q)=n gives

```text
(2k-n) sqrt(9+4q) = -n.
```

For odd q, 9+4q is 5 modulo 8 and cannot be a square. Its square root is
irrational. If 2k-n is nonzero, the displayed equation would make it
rational; if 2k-n is zero, it would give n=0. Both are impossible.
Thus no square H exists. Section 2 now excludes the partial A as well.

## Evidence and limits

The checker examines all 319,770 multisets of eight fifteenth roots in an
integer basis modulo Phi_15. Exactly 15 vanish, and these are exactly the
one-3-cycle/one-5-cycle multisets. This separately checks the source cycle
conclusion in the requested small case.

It examines all 6,561 ternary words of length eight and all 1,540 pairs of
the resulting 56 edge words. A maximal-clique search gives exactly 16
stars and 28 reverse pairs. A separate fixed-size search finds all 112
six-edge configurations and compares them with the star subsets. Every
configuration passes the missing-column sign check in both orientations.

For all 24 primes from 5 through 101 it checks 648 Gram phase assignments,
2,408 completion row residues and every possible spectral multiplicity.
Exact Eisenstein arithmetic checks the Hermitian matrix identity and
rejects missing conjugation, missing diagonal shift and a wrong linear
coefficient. Reverse-pair, nontrivial-phase, opposite-sign, nonorthogonal
projection and excluded-q controls mark the other boundaries. The pinned
PR7744 verifier runs unchanged in both registered modes.

The theorem for arbitrary q and b is the written proof, not a conclusion
from finite sampling. The checker constructs no valid mixed-case input:
the theorem proves that none exists. No global literature priority is
claimed. Other row counts, more than two prime factors, larger powers of
three, noisy inputs and physical recovery remain outside scope. This
does not improve kappa or discharge any of the five framework assumptions.
No selected cold replay, Lean, Docker or formal proof kernel was run.
