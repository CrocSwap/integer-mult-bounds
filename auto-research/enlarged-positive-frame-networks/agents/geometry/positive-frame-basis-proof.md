# Actual signed positive-frame profiles in a fixed basis

This branch profiles the actual enlarged frames and retained use matching. It
does not relabel a positive construction by the smaller original envelope.
The complete scalar and dirty-state compiler remains a required premise.

## Projector identity

Let the forced coordinate set be F, with f=|F| in {1,2}, and put s=3-f.
The free signed classes are disjoint vectors a_c with entries in {0,1,-1},
sizes k_c and coordinate sums sigma_c. The actual integer basis has columns
B_c=s a_c+sigma_c 1_F. For H=I-J/9,

    B^T H B = s^2 diag(k_c)+(f-1) sigma sigma^T.

This matrix is positive definite. Define

    D = sum_c a_c a_c^T/k_c,
    u = sum_c sigma_c a_c/k_c,
    v = sum_c sigma_c^2/k_c,
    d = s^2+(f-1)v.

The Sherman-Morrison identity and conjugation by L give

    L P_H L^-1 = D+(s u z^T+s w u^T+v w z^T-(f-1)u u^T)/d.

For L=I-4J/[3(h+3)], w=1_F-4 1/[h+3] and z=1_F+1. For L=I+J,
w=1_F+3 1 and z=1_F-10 1/[3(h+1)]. The first identity is checked directly
against rational Gram inversion on actual signed frames by
[positive_negative_projector_review.py](code/positive_negative_projector_review.py).
The scout independently derived the identity from the Gram matrix.

Source triples have their separate rank-one projector: at the negative
parameter its numerator is ((h+3)1_T-4 1)(1_T+1)^T with denominator 2(h+3).
The source and copied-center nonzero-coordinate proof is unchanged by internal
frame enlargement. The complete both-negative data-corner certificate can
therefore be reused when the source triples and physical permutations stay
fixed.

## Integer clearing and exact ordered ranks

Let K=lcm(k_c), U=K u, V=K v, and dnum=K d. A clearing denominator is
(h+3)K dnum at the negative parameter and 3(h+1)K dnum at I+J. The native
code writes every numerator explicitly, then divides numerator entries and
denominator by their common gcd. This signed block diagonal D is not the
zero-one diagonal used by the earlier original-envelope minor bound.

For a physical transition P_B-P_A, use the lcm of the two reduced frame
denominators. Let Z be the maximum absolute entry of that exact integer
matrix. Every minor of order e has absolute value at most e^(e/2) Z^e by
Hadamard's inequality.

The rank cutoff r=dim(B)-dim(A) has an independent mathematical premise:
the full positive-space compiler validates A subset B and nondegeneracy of
both spaces. Their H-orthogonal projectors satisfy P_A P_B=P_B P_A=P_A.
Thus P_B-P_A is an idempotent of rank r. In particular every NE submatrix
has rank at most r. Conjugation by the common invertible L preserves this
identity. It is insufficient to check only numerical ranks or scalar masks.

For r>=2, the integer bound

    r^ceil(r/2) Z^r

covers every potentially nonzero NE minor. The native code uses enough
distinct trial-division-proven 31-bit primes so their product is strictly
larger than this bound. Denominators are nonzero modulo every selected prime.
An integer minor vanishing modulo all primes must then vanish over Q.
The maximum modular NE rank table is therefore the exact rational rank
table. Mixed second differences recover the rook pivots; contiguous runs
in both row and column indices give the recursive child widths. A union
of individual modular pivot patterns would not justify that step.

Rank-one children use singleton calls. Rank-zero transitions are checked
by exact cleared integer equality. The identity transition has its exact
width-h profile. Each remaining transition's rank, integer denominator,
entry maximum, minor bound, prime count and final pivots are recorded in
the external complete transition audit.

## Accounting and scope

The finite driver reconstructs every unoptimized addition, source and terminal
transition, then applies each retained positive selected-use continuation once.
It checks unique donors and physical use identities, actual positive ranks,
lexicographic dependency order, the original rank histogram and full rank mass
hR+2*loss. Copied totals replace h width-h calls by h singleton calls, leaving
rank mass hR+loss. Every data correction, exterior role charge, shared-bank
restriction and inverse chronology remains in the coordinator's assembly.

The native histogram is conditional on the independently audited actual
nested spaces. A candidate is promoted only after that audit and the full
47-constraint multiplication assembly. This written derivation and finite
native verification are not a formal proof of the infinite multiplication
theorem. Reproduction requires the pinned scalar DAG, positive labels,
selected-use map and authored source; the driver retains their hashes.
