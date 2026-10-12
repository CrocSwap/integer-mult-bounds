# Ordered target Schur intervals on PR470

## Result and scope

The frozen construction changes only the B target-update sequence of the pinned PR470 R715 word. It applies 17 disjoint two-ended target factors, then one additional overlapping factor after replaying the changed chronology. All helper entrances, helper endpoints, source/helper construction and cleanup, retained centres and scatter are byte-for-byte equal as JSON fields. The existing whole-residual hosting selection therefore remains applicable after local native compilation passes.

The final local paid profile is

    {1:2393, 2:1069, 3:225, 4:299, 5:87, 6:75, 8:9}.

Relative to PR470, its delta is

    {1:-10, 2:-1, 3:-3, 4:-18, 5:+15, 6:+3}.

The total rank mass is unchanged. There are 14 fewer recursive children per local invocation. There are 36 extra target-read additions. Primitive costs must count those additions; they are not free operations.

## Exact sufficient identity

Work over F2. During an interval, let donor d gain V and receiver u gain U. Require that no intermediate operation reads u, except operations explicitly handled in the transformed interval. Helpers supplying the increments remain unchanged during B. The transformation is:

1. At the interval entrance execute u += d.
2. Replace the receiver's increment sequence by a sequence summing to U+V. Whenever a donor-increment helper already appears in the receiver interval, remove one such occurrence. Otherwise add that helper to the receiver at the donor's own read frame.
3. At the interval exit execute u += d again.

For arbitrary initial values, including correlated dirty values, the receiver ends as

    u0 + d0 + U + V + (d0 + V) = u0 + U.

The donor is unchanged relative to the original program. Thus the complete interval has the same scalar endpoint. The new additions must occur at common allowed frames; this is checked separately from the identity. Recovery is placed after the actual modified paths have reached a common frame, not after a frame inferred only from unmodified history.

The 17 first-layer factors have disjoint target pairs. The second-layer factor reuses registers involved in the first layer, but has its own complete interval in the already rewritten word. It is restored before any pending outer-factor read. Composition of the exact interval identities proves preservation of the whole scalar endpoint; there is no claim that arbitrary overlapping substitutions commute.

The second layer is u=122, donor=210, interval[15,70] in the first-layer word, setup frame0, recovery frame546. It removes helper705 from gate20 and adds helper513 after gate70. Those are indices in the frozen first-layer word, not the original PR470 indices.

## Paid-moment improvement

Fourteen first-layer pairs replace ranks[1,4] by[5]. Three replace[3,4] by[1,6]. The second layer replaces[2,4] by[1,5]. For every exponent alpha in (0,1), each change strictly decreases the sum of r^alpha, by strict subadditivity or concavity at equal rank mass. Thus the improvement is exact and does not rely on the floating-point discovery score. The complete global profile changes by 88 times the local delta when all 11 stages and 8 replicas use the changed word. The independent root pricer supplies the actual certified kappa.

## Reproduction and exact evidence

Use `schur_constructor.py SOURCE SCHUR-SELECTION.json OUT1`, then `schur_constructor.py OUT1/word.json SCHUR-LAYER2.json OUT2`.

Source canonical JSON SHA256:
`2b91cf95df15d9c32d830f15cfa3f2b74b89c439f40ebbe2f04c8235cfb1b49b`.

First-layer canonical word SHA256:
`743902b972103c6b14496f233f401730ff75f4aa969fbdad37ff037c729d035f`.

Final canonical word SHA256:
`afd6333e2613a373c1078653d62667ae44b40b8ccfd9c548858b499377401f6c`.

The standalone standard-library constructor checks all 955 independent arbitrary-dirty binary columns, exact rational frame ranks, frame nesting and every integer clean-operand support. All 54 mutations omitting one setup, added correction or recovery are rejected. Those checks are a finite interface certificate; the signed/formal-column native checks, literal compilation, runtime invoice and inherited all-size analytic interfaces remain root-assembly obligations. No Lean certification was performed.

## Provenance and novelty boundary

This reuses the chronological target-label and arbitrary-dirty interfaces of the earlier target-prefix construction, and the public R715 carrier/retiming/kernel work in PR463, PR467 and PR470. The two-ended view was motivated by block elimination and exact transvection words: Mathlib `LinearAlgebra/Matrix/SchurComplement.lean`, `Matrix.fromBlocks_eq_of_invertible₁₁` (line50), and project `Mathproof/Meta/TISLTransvectionWord20260908.lean`, `commutator3` (line25). These sources were inspected; their theorem names are not substitutes for the explicit interval proof above, and no fresh kernel replay was run.

The generalized search permits symmetric-difference corrections and changed recovery frames. However, a direct control using our historical strict-prefix search also found equivalent first-layer paid profiles. We therefore do NOT claim that these gains establish an unprecedented algebraic identity or a technique absent from our previous work. The actual contribution is a new checked 18-factor construction on PR470, including a second ordered factor that gives additional saving after the disjoint first layer. Claims of mathematical priority beyond that are unwarranted.

Discovery: bounded native C++ screens, 186,065 first-pass intervals and 158,850 second-pass intervals. First pass had 77 positive nominations; second pass had 4, representing equivalent choices for one further gain. Search is frozen for this deliverable.
