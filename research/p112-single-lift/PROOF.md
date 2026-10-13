# One additional total cannot lower the coordinate P112 copy-rank cost

This is a theorem about the precise finite algebraic model below. Its finite
premises have exact executable certificates. The all-real-parameter argument
is written mathematics, not a proof-assistant formalization.

## Model and result

Use DreamingOfClouds' PR717 P112 model, pinned in `SOURCES.json`: the 120 real
E8 root lines with the eight mutually orthogonal frame lines
`e_(2j) +/- e_(2j+1)` removed. Roots have squared norm 2. Let `G` be their
112 by 112 Gram matrix, and let `X_ij = <r_i,f_j>` for the deleted frame.
Then `X X^T = 2G`, `rank_R X = 8`, and every entry of X is 0 or +/-1.
Write x_j for column j of X.

Labels l_i belong to F2^9, with a nondegenerate symmetric bilinear form S
such that `l_i S l_t^T = 1 + G_it (mod 2)`. The code stores the labels and
their duals `v_i = l_i S` as nine-bit integers. For a real column d let
`V(d) = span_F2 {v_i : d_i != 0}`. Define

    beta(d,t) = rank_F2 (l_i S l_u^T)_{i in supp(d), u in supp(t)}.

This is the inherited per-total pairing-rank copy cost. The eight coordinate
terms `x_j x_j^T` each have beta 8, for total 64. Priority for this value
belongs to PR620 and its construction predecessors.

**Theorem.** For every `a in R^8` and **every** `z in R^112`,

    sum_(j=0)^7 beta(x_j, x_j - a_j z) + beta(Xa, z) >= 64.       (1)

These terms always give the exact identity

    X X^T = sum_j x_j (x_j-a_j z)^T + (Xa) z^T.                 (2)

Thus an added total with an arbitrary source vector cannot improve the copy
rank while the eight coordinate reader columns are retained. The class
allows asymmetric factors, arbitrary real magnitudes, negative coefficients,
source vectors outside col(X), and terms of pairing rank below 8.
Equality is attained by z=0. The transposed statement follows from the
symmetry of beta and X X^T.

This includes every exact nine-term factorization retaining those eight
reader columns: if the ninth source z is nonzero, reducing the identity
modulo col(X) forces its reader d into col(X), so d=Xa. Since X has full
column rank, the remaining source matrix must be X-za^T. Independent
nonzero rescaling of the original reader columns can be absorbed into their
source columns. A zero ninth source is harmless.

This last characterization requires exact equality to 2G on **all** entries.
It does not cover a masked completion corrected by additional zero-cost
terms, simultaneous changes of the original reader columns, two or more
additional totals, or interacting copy programs outside this cost model.

## Finite geometry lemma

For each j, the space `V_j = V(x_j)` has dimension 8, and
`beta(x_j,x_j)=8`. If a has at least two nonzero coordinates, `V(Xa)=F2^9`.

Here is a short exact certificate for the second claim. For every nonzero
binary functional q on the dual-label space, form

    I_q = {i : q dot v_i = 1}.

Of the 511 matrices `X[I_q,:]`, 503 have rational rank 8. The other eight
have rank 7; each has one identically zero column, and these columns run
through all eight coordinates exactly once. `RESULTS.json` provides
independent row indices for every matrix. The second checker verifies the
511 nonzero integer minors by fraction-free Bareiss elimination. In the
rank-7 cases it also checks the zero column on the entire support, proving
that the real kernel is exactly the associated coordinate axis.

If V(Xa) were proper, a nonzero q would annihilate it, whence
`X[I_q,:] a=0`. The census forces a=0 or a on a coordinate axis. This is
impossible when a has at least two nonzero coordinates. Rational rank equals
real rank for these integer matrices, so this reasoning covers all real a,
not only a finite coefficient search.

## Annihilators convert cost into a dimension bound

Let J be the support of a, of size k>=2, and put

    H_j = {q in V_j : q dot l_i = 0 whenever x_ij-a_j z_i != 0},
    H_0 = {q in F2^9 : q dot l_i = 0 whenever z_i != 0}.

Rank-nullity gives

    beta(x_j,x_j-a_j z) = 8 - dim H_j,
    beta(Xa,z) = 9 - dim H_0.

We prove that the addition map from the **external** direct sum
`(direct_sum_(j in J) H_j) direct_sum H_0` into F2^9 is injective. This gives
`sum dim H_j + dim H_0 <= 9`, so the k changed terms and the extra term
cost at least 8k. The remaining 8-k terms cost 8 each, proving (1).

Suppose `(q_j,q_0)` is in the kernel of this addition map. At a port i
write `b_ij = q_j dot l_i`. If b_ij=1, the definition of H_j forces

    x_ij = a_j z_i.                                           (3)

If z_i!=0, membership in H_0 gives `q_0 dot l_i=0`. Hence an even number
of the b_ij are 1, and all their nonzero values `x_ij sign(a_j)` have the
same sign, namely sign(z_i). If z_i=0, every selected x_ij is zero.
In either case, for each sign epsilon=+1,-1 we have the binary equation

    sum_{j in J : x_ij sign(a_j)=epsilon} b_ij = 0.              (4)

These equations are necessary for every real a and z, regardless of the
magnitudes of a_j. They form a binary matrix on the 8k coefficients of
the q_j in the certified bases of V_j. A common sign reversal only exchanges
the two equations at each port. It therefore suffices to enumerate sign
vectors in {-1,0,1}^8 with at least two nonzero entries and first nonzero
entry positive. There are exactly 3,272, all checked (seed 40 changes the
traversal order only).

| k | sign cases | rank of (4) |
|---:|---:|---:|
| 2 | 56 | 16 |
| 3 | 224 | 24 |
| 4 | 560 | 32 |
| 5 | 896 | 40 |
| 6 | 896 | 48 |
| 7 | 512 | 56 |
| 8 | 128 | 63 |

For k<=7 the full column rank forces every q_j=0, and then q_0=0.

**The k=8 case needs an additional check.** For every one of its 128 sign
patterns the one-dimensional kernel of (4) is explicitly recorded. At
exactly 56 ports its nonzero vector selects j's with at least two distinct
values in `{x_ij sign(a_j)}` (values 0,+1,-1 are distinguished). These demand
incompatible signs or zero/nonzero values of z_i in (3). Consequently that
nonzero vector cannot belong to the actual direct-sum kernel. The zero
vector is again the only possibility. The checkers regenerate every such
conflict, not only the first witness. The linear system alone does **not**
prove the k=8 case, and a negative control rejects that mistaken argument.

This proves injectivity in all cases k>=2 and completes the main argument.

## Boundary cases and proof boundary

If a=0, the original eight terms are unchanged and the ninth reader is zero.
If only a_j is nonzero, the two affected reader spaces are both V_j.
The support of x_j is contained in the union of the supports of
`x_j-a_j z` and z. The rank of a union of column sets is at most the sum
of their ranks, so these two terms cost at least `beta(x_j,x_j)=8`.
Thus (1) also holds at k=0 and k=1.

The finite checks certify the stated P112 geometry and the necessary
linear/conflict facts. The written rank-nullity argument, not sampled
vectors or a solver's failure to find a candidate, proves the quantified
result. No SAT/CP-SAT solver, floating-point rank, proof assistant, physical
circuit compilation, or new multiplication exponent is claimed.

Under PR446 Theorem C's inherited separate-total copy-tree assumptions,
the result blocks a decrease in this copied-information charge. Additional
preparation, source access, frame changes, cleanup/restoration, and recursive
children were optimistically granted zero extra cost before construction.
Even that relaxation cannot make the **copy-rank sum** smaller than 64.
It does not rule out benefits in helper work, scheduling, hosting, or the
distribution of recursive ranks at the same sum. No complete cost recurrence
or physical realization is offered for an allegedly improved supplier.
