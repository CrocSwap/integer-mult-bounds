# Independent review of the six-full-block obstruction

**Verdict: PASS, with the stated characteristic, rank-defect, square-zero-query,
and commuting-idempotent hypotheses. No new κ.**

Reviewer: OpenAI GPT-6 Astra Pro research subagent A, for @CubeJerry,
2026-11-07. The source Hall and no-idle packages remain unchanged. I read the
following final author files and independently reconstructed their proof:

- `PAIRED-DEFECT-ADDENDUM.md`, SHA256
  `b4849cc8f7ee3803722636022077a08a29ab97ac5ecc76f3c293a59250139032`.
- `verify_paired_defect.py`, SHA256
  `f4952a62fa92e65b20774d8e461e0b54b827b87c482ce5add5a7f64736f55afa`.

The two reviewed author files are retained unchanged at this package root. I did not import
or execute the author's verifier. The separate exact controls below use my own
implementation and do not establish the universal claim by finite search.

## 1. The full-block gauge and rank requirement are valid

The root identity gives `H=A−G` of rank two, including every other query.
Write `H=UV`; at a selected rank-two block, `U_iV_i=I_2` implies that both
matrices are invertible and `V_iU_i=I_2`. The query gauge
`X_i→X_iU_i`, `Y_i→U_i^{-1}Y_i` changes neither the physical query nor its
supporting projector. It makes every selected off-diagonal Gram block
`sign(i−j)I_2`, regardless of intervening thin blocks.

Six selected blocks therefore have Gram `S_6⊗I_2`. The displayed integral
inverse of `S_6` multiplies to the identity, so the Gram has rank twelve over
any field. Its twelve columns must lie in a stage union of dimension at least
twelve. No reflection classification, two-thin census, prefix condition, or
scalar-full-call theorem is used in this step.

Commuting idempotents simultaneously diagonalize by successive image/kernel
splittings over the original field. Their rank-four images therefore become
four-element supports. Since the query factors have full rank, supporting
`R_i` on both sides is equivalent to fixing `X_i` and `Y_i` on the appropriate
side. The invertible cross-Gram factors through the intersection of two
supports, forcing every pairwise intersection to have size at least two.

## 2. The no-common-pair union argument withstands the boundary cases

If all pair intersections have size at least three, every set adds at most one
coordinate outside any fixed first set, giving union at most `m+3`.
Otherwise normalize two supports to `A∪B` and `A∪C`, with three disjoint pairs.
If their common pair `A` is not contained in every support, take a witness `E`
missing an element of `A`. To meet both original supports twice, `E` must take
at least three of their six coordinates. Their triple union `T` thus has size
at most seven, while their triple intersection has size less than two.

A further four-set adding at least two coordinates outside `T` has at most two
coordinates inside `T`. Those coordinates must meet each of the three witness
sets twice, hence would form a pair in their triple intersection. This is
impossible. Each later support adds at most one coordinate, proving union at
most `m+4`. This reasoning explicitly permits repeated supports and does not
assume that all six supports are distinct.

I checked the normalized finite boundary independently: 17 possible witness
sets and 671 compatible extensions obey the claimed inequalities. A six-set
family with triple-core variants reaches union ten with no common pair, so the
combinatorial bound is not artificially strengthened.

## 3. The common-pair case needs—and has—the ordered sign constraint

If every support contains a pair `A`, its two remaining coordinates are an
outside edge. Three disjoint outside edges would make the three pairwise
stage intersections exactly `A`. The associated two-by-two column and row
factors `α_i,β_i` are invertible because their cross-products are `±I_2`.
For chronological `i<j<k`,

\[
\beta_i\alpha_j=\beta_i\alpha_k=-I_2,\qquad
\beta_j\alpha_i=\beta_k\alpha_i=I_2
\]

imply `α_j=α_k` and `β_j=β_k`. Consequently `β_jα_k=β_kα_j`, contradicting the
required values `−I_2` and `I_2` when the characteristic is not two. No scalar
commutativity of those matrices was assumed; only invertibility was used.

Thus the outside graph has matching number at most two. It has at most two
edge-bearing components, and its incident vertex count satisfies `v≤e+c`.
With at most `m` distinct edges, its union together with `A` has size at most
`m+4`. Parallel edges arising from repeated supports only decrease `e`, so
multiplicity causes no gap.

Pairwise two-intersection alone would be insufficient: six disjoint outside
pairs form a fourteen-coordinate sunflower. My controls explicitly preserve
this counterexample to the falsely stronger bare set-family statement. The
ordered sign equations, not an unstated set theorem, exclude that sunflower
in characteristic other than two.

## 4. Exact independent checks actually executed

```sh
python3.12 -B research/noidle-root-defect/six_full_check.py
```

Output: `PASS_INDEPENDENT_SIX_FULL_BOUNDARY_CONTROLS`.
The standard-library script checks the integer sign-matrix inverse, the
17 normalized witness sets and 671 compatible extensions, both ten-coordinate
extremal union patterns, and the fourteen-coordinate sunflower that would be
allowed without the sign obstruction. It independently constructs the
characteristic-two sunflower Gram and verifies its rank twelve by binary
elimination, while showing that its self-Gram equals `2I` over characteristic
zero. This confirms the precise role of the field assumption; it is not a
native caller in characteristic two.

The packaged checker differs from the original review script only in report
handling: it compares the retained `SIX-FULL-RESULT.json` instead of overwriting
it. Its independent matrix and set-family algorithms are unchanged.

For `m=6`, the stage union has dimension at most ten but the selected Gram
requires twelve. The contradiction proves the at-most-five theorem. The
claim does not establish that five is attainable, does not exclude higher
rank defect or paid larger stages, and does not apply to noncommuting
productive outputs or non-square-zero aggregates of shared-body calls.
