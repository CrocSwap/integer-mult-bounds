# Precise obligations and independent finite evidence

Let F = F₂ⁿ with the standard symmetric bilinear form B. The endpoint frames
A ⊆ U must both be nondegenerate. Define R = U ∩ A⊥. The source obligations are
`residual`, `classify`, and `orthonormal_basis` in `scripts/binary_phase_frames.py`,
and `characteristic` and its membership test in
`scripts/experiments/parity_phase_repair.py`. The retained manuscript supplies
the orthonormal absorption and signed weight-phase arguments in
`upstream/build/sections/03-motifs.tex`. Exact source bytes are in SOURCES.json.

## Orthogonal residual and characteristic test

Nondegeneracy of A gives U = A ⊥ R, and nondegeneracy of U implies that R is
nondegenerate. Thus dim R = dim U − dim A. The map d(v) = B(v,v) is F₂-linear:
the two cross terms in d(v+w) cancel. Nondegeneracy identifies U with its dual,
so there is a unique w_U ∈ U satisfying B(w_U,v) = d(v) for every v ∈ U.

The orthogonal decomposition gives w_U = w_A + w_R. Therefore R is alternating
exactly when d restricted to R vanishes, equivalently w_R = 0, equivalently
**w_U ∈ A**. This includes R = 0: the zero form is alternating and nondegenerate,
and its empty orthonormal basis is admissible. The compiler rejects only
**nonzero** alternating residuals. It cannot replace the criterion with a test
of B(w_U,w_U): in full F₂², w_U = 3 is isotropic but the space is nonalternating.

The oracle computes R by filtering every vector of U against every vector of A.
It computes the radical directly and searches all w ∈ U for the characteristic
equations. These calculations do not use the subject's Gram elimination.

## Orthonormal basis obligation

An orthonormal basis has identity Gram matrix, so a nonzero space admitting one
is nondegenerate and nonalternating. Conversely, split off unit lines until the
remaining nondegenerate space is alternating. Such a remainder splits into
hyperbolic planes with B(a,a)=B(b,b)=0 and B(a,b)=1. One prior unit line w,
orthogonal to a plane, absorbs it via

    w+a, w+b, w+a+b.

These vectors are independent and have Gram matrix I₃. Retain one of them to
absorb the next plane. This proves sufficiency in every finite dimension. The
checker independently validates each returned vector, the complete output span
and every Gram entry; it does not regard a reported dimension as enough.

## Signed phase obligation

For q(y) = wt(y) modulo four, binary addition satisfies

    wt(z+w) = wt(z) + wt(w) − 2|supp(z) ∩ supp(w)|.

If B(z,w)=0, the intersection size is even, hence q is additive on that
orthogonal sum. Orthogonal projection exists and is unique for a nondegenerate
space, including an alternating endpoint. If v_i is an orthonormal basis of R,

    P_U x = P_A x + P_R x,
    P_R x = sum_i [B(v_i,x)] v_i,
    q(P_U x) − q(P_A x) = sum_i wt(v_i)[B(v_i,x)] mod 4.

The reverse edge negates the last expression. Each wt(v_i) is odd; its residue
may be 1 or 3, so replacing every coefficient with +1 is incorrect. The oracle
finds P_U x and P_A x by testing all candidate projected vectors for the required
pairings, independently of the subject's returned orthonormal basis.

Concrete controls: U=F₂³, A=span(7) has rejected residual span(3,5).
The opposite pair A=span(3,5), U=F₂³ has admissible residual span(7).
At U=span(7), A=0, x=1, the phase is 3; substituting +1 or reversing the edge
incorrectly gives 1. The independent unit basis (1,2,7) of F₂³ is not mutually
orthogonal and gives an incorrect phase at x=1. Equal alternating endpoints
have a valid zero residual. Degenerate and nonnested endpoints violate explicit
preconditions and are tested separately.

## Completeness of the declared domain

Begin at {0}. For each enumerated space S and each v outside it, enumerate the
full extension S ∪ (v+S), then deduplicate by vector-set equality. Every
(k+1)-space has a k-dimensional subspace and an outside vector, so induction
covers every subspace, without relying on row-reduction correctness. Counting
by dimension is checked against the independent recurrence

    [n,k]₂ = [n−1,k−1]₂ + 2^k [n−1,k]₂.

Every pair of enumerated nondegenerate spaces is inspected for A ⊆ U. Every
admissible residual is checked at all 2ⁿ ambient inputs, in both directions.
The cap is six and the stopping rule is completion of this domain once; no
sampling or larger-domain exclusion is claimed. The seed changes input
presentation, not which subspaces or endpoint pairs are covered.

The written arguments above explain the encoded obligations. The finite
certificate checks their implementation through n=6; it is not formal proof of
the all-size compiler, physical hosting, scalar circuits, tape/precision bounds,
analytic transfer or complete multiplication theorem. Later interfaces that
permit alternating kernels have a different scope. No new κ is inferred.
