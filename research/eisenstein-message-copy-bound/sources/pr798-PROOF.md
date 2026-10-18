# Eisenstein E8: copy charge at least 22, and a sharp limit of clique certificates

This is a theorem about a specified finite decoder model. It is not a new
supplier, a proof of decoder optimality, or a new multiplication exponent.
The weighted-clique argument follows the distinct Hurwitz and Gaussian
geometries of [PR703](https://github.com/CrocSwap/integer-mult-bounds/pull/703)
and [PR738](https://github.com/CrocSwap/integer-mult-bounds/pull/738).
The new result is the exact primal/dual certificate for the **40-line
Eisenstein geometry**, including a bound on *all* clique-weight certificates.

## Model and geometry

Start with the 240 E8 roots in doubled coordinates: vectors with two entries
equal to ±2 and all other entries zero, and the vectors in {±1}^8 with an even
number of minus signs. Each root has squared norm eight.

Following Joel Pulikkan / GamingPuzzled's archived PR620, choose four mutually
orthogonal A2 planes, with roots (a,b) satisfying a·b = -4, and let J be the
product of their rotations s_a s_b. The literal pairs are in the certificate.
The independent implementation uses the same root order and greedy choices
as the pinned predecessor, so it defines the same rational action, not merely
a configuration with similar counts. The reflection formula is

    s_a(x) = x - (x·a)a/4.

The exact checks establish J^3 = I, J^2 + J + I = 0, and preservation of the
inner product and root set. Thus Q^8 is a four-dimensional vector space over
K = Q(ω), with multiplication by ω realized by J. The root orbits under ±J
partition the roots into 40 K-lines. For a line set S, let X_S be the rational
span of r_i,Jr_i for i in S. Every X_S is J-invariant.

Two distinct lines are nonorthogonal if r_i·r_j or r_i·Jr_j is nonzero. Each
line has 27 such neighbors. Let B be an arbitrary 40×40 matrix over F2 with

    B_tt = 1;
    B_ts = 0 if distinct lines t,s are nonorthogonal.

The other directed entries are unconstrained. Consider any finite decomposition

    B = Σ_j 1_(R_j) 1_(A_j)^T       over F2.

There is no symmetry, minimal-rank, or number-of-totals restriction. For any
row bases V_R,V_A of the rational spans, define the abstract copy charge

    c(R,A) = rank_Q(V_R V_A^T)/2,       C = Σ_j c(R_j,A_j).

This is a *pairing* rank; it need not equal either support's span dimension.
The rank is even: the kernel X_R ∩ X_A^⊥ is J-invariant, because J is an
isometry and X_A is J-invariant. Both domain and kernel are K-spaces.
Consequently each c is an integer. Translating this abstract charge into a
physical copy lower bound inherits PR446's premise, which the base review
ledger marks unreviewed. The finite algebraic result needs no such premise.

## General clique bound and the lower certificate

A clique Q is a set of pairwise nonorthogonal lines. The fitting rules give
B[Q,Q] = I. A binary rectangle restricted to Q×Q has rank one exactly when
both supports meet Q. Rank subadditivity gives

    |Q| ≤ Σ_j [Q∩R_j ≠ ∅ and Q∩A_j ≠ ∅].                 (1)

For each nonempty clique assign a nonnegative rational weight λ_Q. Suppose
these weights satisfy, for all supports R,A,

    Σ_Q λ_Q [Q meets R and A] ≤ c(R,A).                  (2)

Multiplying (1) by λ_Q and summing proves C ≥ Σ_Q λ_Q |Q|.

The certificate uses weight **1/40 on each singleton** and **1/960 on each
of the 2,880 seven-line cliques**, with weight zero elsewhere. The resulting
objective is exactly

    40/40 + 2,880·7/960 = 22.                            (3)

To certify (2), close R and A in the line matroid: cl(S) contains every
configuration line lying in X_S. Closure leaves X_S, hence the pairing rank,
unchanged. It can only increase the clique-hit indicators. Therefore it is
sufficient to check every pair of flats F,G. Write H_7(F,G) for the number
of seven-line cliques meeting both flats. The required integer inequality is

    24 |F∩G| + H_7(F,G) ≤ 960 c(F,G).                    (4)

The replay verifies (4) by exact rational rank on all **298,378 unordered
pairs of the 772 flats**, including the empty flat. Symmetry of the pairing
rank and hit count covers both orders. This is a complete reduction from
arbitrary supports; the theorem does not assume supports were originally
flats. Equations (1)–(4) prove **C ≥ 22** for every finite decomposition.

## Why no weighting of cliques can prove more

The following upper bound concerns the certificate method, not decoder cost.
Let P consist of the **240 unordered pairs** F,G of twelve-line, rank-three
flats with c(F,G)=2. Each such pair has |F∩G|=2 and H_7(F,G)=1,872, so (4)
is tight. Give each of these pairs dual weight 1/24; give the full/full
pair dual weight 1/2. Its cost is

    (240·2)/24 + 4/2 = 22.                              (5)

For *every literal nonempty clique* Q, the certificate verifies

    1/2 + #{(F,G) in P : Q meets F and G}/24 ≥ |Q|.      (6)

The complete incidence census is below. In particular, no unproved
transitivity assumption or orbit-averaging argument is needed.

| Clique size | Dual pairs hit | Number of cliques |
|---:|---:|---:|
| 1 | 12 | 40 |
| 2 | 48 | 540 |
| 3 | 81 | 2,880 |
| 3 | 108 | 360 |
| 4 | 106 | 6,480 |
| 4 | 123 | 2,880 |
| 4 | 192 | 90 |
| 5 | 125 | 5,184 |
| 5 | 134 | 8,640 |
| 6 | 145 | 10,080 |
| 7 | 156 | 2,880 |

Now take *any* nonnegative clique weights satisfying (2), including arbitrary
nonuniform weights on smaller cliques. Multiply (6) by λ_Q, sum over Q,
and apply (2) to the full/full pair and each pair in P. Equation (5) gives

    Σ_Q λ_Q |Q| ≤ 22.

Together with (3), this proves that the optimum of the entire weighted-clique
certificate method is exactly **22**. A stronger copy lower bound will need
an ingredient beyond inequalities (1)–(2). In particular, using more clique
weights or a different clique-weight optimizer alone cannot improve it.

## Decoder bounds and the optimistic accounting screen

Every fitting B has an abstract cost-40 decomposition: for each row t,
take R={t} and A equal to that row's nonzero positions. A contains t; every
other member of A is orthogonal to t. The rational Gram block therefore has
rank two, so this row costs one. These 40 rectangles reproduce B. Hence the
minimum charge lies in **[22,40]**. The lower endpoint is attained by a
*certificate*, and no cost-22 decoder is constructed.

For the separate Dfc stage accounting in the pinned format notes, v=40,
each line has rational rank k=2, and cst=2C. Thus, conditionally on that
accounting and the physical interpretation of the charge,

    D/T = (s-1)vk - s·cst ≤ 80(s-1) - 44s = 36s-80.

At s=3 the upper deficit is 28, which is positive. This lower bound **does
not exclude three stages**. A positive three-stage deficit would require
C < 80/3; integrality narrows the unresolved possibilities to C=22,...,26.
All helpers, source access, frame changes, copies beyond this lower bound,
restoration and recursive children would still have to be paid. None is
implemented or assumed free in an achieved construction. At the cost-40
row decomposition the deficit is -80 for every stage count, so that abstract
upper-bound witness itself cannot supply a saving under Dfc.

The selected #626/#543 composition remains complex-bound. This research
does not provide a replacement supplier or change any assembly constraint.

## Completeness and proof boundary

Flats are generated from the empty span by adding one root line and taking
exact rational span/closure. Any flat has a line basis, so induction on basis
size proves this generates every flat in four K-dimensions. The verifier
also checks all 30,880 one-line extensions remain in the enumerated set.
The flat counts by (K-rank, number of lines) are

    (0,0):1; (1,1):40; (2,2):240; (2,4):90;
    (3,5):360; (3,12):40; (4,40):1.

All nonempty cliques are generated once by successively adjoining larger
vertices adjacent to every previous vertex. This recursion exhausts every
ordered increasing clique. A separate Bron–Kerbosch maximal-clique census
corroborates the 2,880 maximum cliques and 90 smaller maximal cliques.

The committed certificate contains the literal flat generators, maximum
cliques, all 240 dual pairs, complete pair/incidence censuses, and hashes of
the regenerated root orbits and all 40,054 cliques. The replay uses no solver.
An ordinary Fraction elimination on original root generators checks 258
seeded/boundary Gram blocks independently of the integer RREF implementation.
Eight mathematical negative controls cover fitting identities, clique
admission, rank accounting, and both primal and dual weights/coverage.

The separate `crosscheck.py` imports neither implementation. It checks all
298,378 primal inequalities on original integer generators using rank modulo
101. Such a rank is a lower bound on rational rank, which is the sufficient
direction for (4). It checks all 240 dual-pair costs and the full-pair cost
by exact Fraction elimination. Geometry and enumeration completeness remain
the responsibilities of the main replay and the preceding argument.

This is a written proof with exhaustive finite premises, not a proof-assistant
formalization or a finite replay claimed to prove the full multiplication
theorem. Whole K-lines, scalar binary totals and the stated fitting pattern
are essential to the scope. Sub-line/vector-valued operations, different
decoder patterns or geometries, physical realization, all-size compilation,
hosting, precision, tape and analytic transfer remain outside it.

Prepared by Jonathan Lam (@jonathanlam) with substantial OpenAI Codex
assistance. See [SOURCES.json](SOURCES.json) for exact pins and predecessor
credit. New material is Apache-2.0 under the repository license.
