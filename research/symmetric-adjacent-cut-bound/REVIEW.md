# Independent mathematical review

Result: the claimed optimum is valid in the stated formal model. For every
`n>=2`, finite `R>=W`, arbitrary binary rank-one idempotent coefficients,
unit-cost adjacent labels, and free scalar `GL_R(F2)` mixing, the complete
formal diagonal endpoint has minimum paid-call count `sum_j inv(w_j)`.
No mathematical defect was found in the reviewed proof or primary checker.

The reviewer is the `math-exact-circuit-verification` specialist, using its
arbitrary-dirty-column and independent-representation obligations. The worktree
base is `94e50883325b387add6891258a986f797b09cacc`. No producer code was imported
into the independent checker, and no external actions were taken by this reviewer.

## Reviewed files

SHA-256 values at review:

| File | SHA-256 |
| --- | --- |
| `PROOF.md` | `008be68867a8e85f4e18455d206e03f20aebfc28e9f08efba576180e7e1edc50` |
| `verify.py` | `3db69c6c75436527c1580e695c65520df438aab17001a5065b2b418d1b4f74ad` |
| `EXPECTED.json` | `fa2b8c81fbab847073a1efd5a339ba75f14227e03294b753b6f6cbcbb7c2732d` |
| `independent.py` | `3752b33a8e6722d7ee2034692737e4b0ece45f3cdbe8b92845dcea247135f248` |

All filenames above are relative to
`research/symmetric-adjacent-cut-bound/` in the shared run worktree
`/Users/ross/git/math/donated-20261014-1603`.

## Mathematical review

The ordered-distinct-pair action is a group-algebra homomorphism with the stated
composition convention. Its increasing-to-decreasing block for an adjacent
transposition has a single nonzero entry. Tensoring with a rank-one coefficient
therefore gives crossing rank one, while scalar role changes have crossing rank
zero. The block product identity proves subadditivity without requiring
commutativity or invertibility. At the complete diagonal target the block ranks
add to `sum inv(w_j)`. Every dirty role is included in this block argument.

The upper bound is separate and formal: swapping adjacent descents on the right
gives `w t_1 ... t_l=e`; chronological calls `t_1,...,t_l` multiply to
`t_l ... t_1=w`. Coordinate-role factors preserve spectators exactly. The proof
and primary implementation correctly account for this order. The proof now
explicitly allows any adjacent-descent order, including the primary checker's
bubble-sort sweeps. This resolved a minor presentation mismatch, not a defect
in the theorem or its implementation.

Free-map normalization is optional for the cut argument and is valid via scalar
conjugation. Augmentation forces the residual scalar product to be identity
under the stated complete endpoint. Rank-d charges and the nonadjacent-alphabet
counterexample are correctly separated from the unit rank-one result.

Represented equality is not used as sufficient evidence for a formal endpoint.
For `S4`, the nonzero formal sum of all 24 group elements acts as zero on ordered
pairs: each fixed input/output ordered-pair entry receives exactly two terms.
The independent checker adds that norm in an off-diagonal dirty column, verifies
the entire represented operator is unchanged, then rejects the formal boundary.

The primary checker was read independently. Its group-coefficient dictionary
and packed role multiplication implement `[g][h]=[g after h]` with the correct
coefficient order. Its full endpoint comparisons include all dirty columns and
restored spectator rows. Reversing an entire paid word correctly checks the
inverse boundary. The fixed receipt is consumed by default rather than silently
regenerated.

## Independent finite evidence

Reproduction from the worktree root:

```sh
python3 -I -B research/symmetric-adjacent-cut-bound/independent.py
python3 -I -O -B research/symmetric-adjacent-cut-bound/independent.py
python3 -I -B research/symmetric-adjacent-cut-bound/verify.py
```

All three commands passed. The independent checker uses breadth-first Cayley
graph distances, complete bitsets of formal coefficients in each role entry,
and explicit complete ordered-pair matrices. It does not use the producer's
bubble sorting, coefficient dictionary, receipt, or source imports.

| Covered finite domain | Count |
| --- | ---: |
| All permutations in `S2,...,S7`: BFS distance equals exact crossing rank | 5,912 |
| Directed adjacent Cayley edges visited | 34,406 |
| All paid factors, `2<=n<=5`, `1<=R<=3`; formal involution and full represented cut | 350 |
| All scalar `GL_R(F2)` matrices, `1<=R<=3`; zero crossing rank | 175 |
| Distinct scalar conjugates of a coordinate projector, equal to the complete rank-one idempotent inventory | 35 |
| Complete formal `S4` endpoints at `R=3`, two targets and one arbitrary dirty spectator | 744 |
| Of those endpoints, all `GL_3` gauges of fixed targets, with every paid-prefix cut checked | 168 |

The 744 formal endpoints consist of all 576 target pairs under one nontrivial
scalar gauge and 168 gauges for targets of costs six and three. Counts describe
checks rather than distinct endpoints; one fixture occurs in both groups.

Six controls reject for their exact intended reason: a nonadjacent paid label,
a rank-three unit-cost coefficient, a free address-changing map, an unrestored
spectator, a dirty-to-target leak, and represented equality substituted for
formal equality. Visible-target-row and clean-spectator-column checks are shown
to miss their respective dirty-state defects.

Additional in-memory mutation checks removed, individually, the adjacent-label,
rank-one-charge, scalar-address-preservation, and full-formal-boundary detectors.
Each corresponding control then failed with the expected
`negative control unexpectedly accepted` message. No on-disk source was mutated.
The run emitted `PASS_INDEPENDENT_DETECTOR_SENSITIVITY variants=4 edits_on_disk=0`.

## Limits and remaining responsibilities

This is an independent review of a written all-parameter proof supported by
exact finite replay. It is not a formal-kernel proof, exhaustive circuit search
over arbitrary lengths, physical BIT construction, precision analysis, recursive
supplier admission, or new multiplication-exponent claim. The finite census
does not by itself quantify over unbounded `n`, role count, or word length.

The parent owns source-pin/predecessor provenance, overlap coordination, package
metadata/tests, publication, durable handoff, and worktree cleanup. The proof
specialist owns `PROOF.md`. Native address realization, physical scalar costs,
hosting, and complete recursive profiles remain unproved by this result.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
