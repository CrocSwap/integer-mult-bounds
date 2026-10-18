# Exact scope of the archived free asymmetric sink exclusion

This certifies only `free_relax()` in Joel Pulikkan's archived PR620
`s2-decoder/asym.py`. The original observation and feasibility criterion are
his, building on DreamingOfClouds' PR595. The contribution here replaces
floating-rank evidence with portable exact witnesses and states the boundary.

## Geometry, labels and complete enumeration

Let L contain the 120 Hamming-coordinate E8 root lines in the pinned source
order, with eight coordinate lines first. Every row has squared norm 4.
The live set is T={8,...,119}. Let G=LL^t/2 and B=(J+G) modulo 2. The source
uses a rank-nine factorization B=UU^t, giving each line its nine-bit label u_t.
Our exact row elimination independently checks rank_F2 B=9. Since U has
full column rank, the map w -> U w from F2^9 is injective and its image is
column(B)=row(B), using symmetry. Consequently the 512 words in row(B)
are exactly all source-label sink functionals, regardless of label basis
or the source's reversed bit convention. No assumed label correspondence
is needed. For the same-label sink w=u_t the word is B's row t.

The verifier enumerates all 511 nonzero words p. For each target t in T,
the admissibility condition is p_t=1, and alternatives exclude p=B_t.
Since B_tt=1, u_t is nonzero and exactly 256 functionals have p_t=1;
exactly one is the same-label sink. Thus the complete alternative domain
contains 112*255=28,560 cases. Both replay implementations check this
cardinality and coverage. Zero is correctly excluded because p_t=0.

## Rational span criterion and exact certificates

For an alternative (t,p), let Z={s in T: p_s=1 and s != t}. With no
additional total, a frame-decoder relaxation would require a linear
functional c on the eight coordinates satisfying L_s c=0 for s in Z and
L_t c !=0. Such c exists if and only if L_t is outside span{L_s:s in Z}.
Equivalently rank(L_Z with L_t appended)>rank(L_Z). This is precisely the
archived `free_relax()` test. Matrix entries are integral, so the exact
rank conclusion is unchanged on extending Q to R or C.

Every one of the 28,560 alternatives has equal ranks:

| Exact rank before and after appending target | Cases |
|---|---:|
| 7 | 448 |
| 8 | 28,112 |

Each case has a nonsingular square integer minor using source rows in Z.
The 4,030 distinct minors are stored explicitly, with their determinants.
The producer selects rows modulo 101 and checks the resulting determinant
using integer Bareiss elimination; the independent checker uses Fraction
Gaussian elimination. A modular nonzero minor alone would prove the
rational lower bound, but both executions additionally compute its integer
determinant. The finite minor inventory is not a sampling experiment.

For rank eight the ambient eight columns give the matching upper bound.
Each rank-seven pattern is exactly B_a for one omitted coordinate line
a in {0,...,7}. All its live source rows, including t, have coordinate a
equal to zero. The minor on the other seven columns proves the matching
lower bound. This explicit upper bound is essential: these 448 cases
must not be inaccurately described as full-rank eight.

The certificate stores each pattern's base minor and replacement minors
when deleting a target used in that base. The independent verifier rebuilds
the entire code by set closure, verifies the exact pattern and repair
inventories, and checks that every target-deleted source set contains its
certified minor. All stored minors must be used. Thus sharing a minor
between cases does not omit their individual coverage checks.

## Positive control and boundary

For each of the 112 excluded same-label sinks, Z consists of the live lines
orthogonal to L_t. Its rank is exactly seven; L_t is not in that hyperplane
because L_t.L_t=4. Appending t raises rank to eight. The original sink is
therefore a positive control, not a counterexample to the restricted
alternative exclusion. All 112 controls pass.

This establishes no-free-alternative sinks for this fixed P112 live set
and eight coordinate totals. It does not exclude PR595's paid extra total,
PR620's `feasible_pairs(Q,g)` augmented rows, changed frames/ports, nonlinear
decoders, or interacting delivery programs. In particular the historical
search for the maximum number of sinks per paid rank-one total remains
open here; its pricing discussion is not certified by this package.
PR620 remains partially reviewed. No supplier, kappa improvement, or full
multiplication theorem is claimed.

Contributor @woklerx with substantial OpenAI Codex assistance in proof,
implementation, checking and writing. Apache-2.0.
