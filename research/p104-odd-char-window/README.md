# Odd-character window of the P120 odd graph (no new κ)

**No new κ.** The selected record stays `781451/250000000`. This package
upper-bounds the port-window of `P120` and of every nonempty subset, including
`P104` and both copies of `P112`. It does not build a word or a paid profile.

The proof is in [PROOF.md](PROOF.md). The finite census, the rank checks and
the failure controls are in [verify.py](verify.py).

## Result

Let the odd graph have an edge when two weight-3-or-7 vectors in `F_2^9` have
odd dot product. `P120` is all 120 of those vectors. `P104` is the 104-vector
subset in `data/ports_p104.json`, byte-identical to the port list of PR #6933
at `a967c521074c2c7450255ae237fda9c439ee1b35`.

1. The odd graph on `P120` is connected and strongly regular with parameters
   `(120, 63, 30, 36)`. The degree count is written out. The parameters `λ = 30`
   and `μ = 36` are the exhaustive pair census.
2. `H = 3I - A` has rank 36 over `Q`, nonzero diagonal in every characteristic
   other than 3, and zeros on non-edges. So `w(S; F) ≤ 36` for every nonempty
   `S ⊆ P120` and every field of characteristic not 3.
3. In characteristic 3 that matrix has zero diagonal. A degree-at-most-2
   factorisation produces a 1-block pattern of rank 38, so `w(S; F_3) ≤ 38`.

Accepting the lower bounds in #6933, Theorem 4, without replaying them:

| field | P104 | P112 | P120 |
|---|---|---|---|
| char ≠ 2, 3 | [13, 36] | [14, 36] | [15, 36] |
| char 3 | [13, 38] | [14, 38] | [15, 38] |

Characteristic 2 is unchanged: #6933 already has `w(P104; F_2) ∈ [53/6, 9]` and
`w = 9` on `P112` and `P120`. The reduction of `H` is a legal pattern there of
rank at most 36, which does not beat the Gram pattern of rank 9.

## Scope

Original card: `complex-rank-shape-decoder`. Scope status: **changed**. The
card asks whether a decoder or coframe change improves the signed moment. This
package does not change a word, a coframe, or a moment. It answers the odd-character
half of the window question left open by #6933: an odd-character decoder mask
of this type cannot inherit the characteristic-2 window 9, and the best
explicit pattern here has ratio 36, or 38 in characteristic 3.

The lower ends 13, 14 and 15 are #6933's. They are not reproved. The upper
ends are proved here. Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B research/p104-odd-char-window/verify.py
python3 -I -O -B research/p104-odd-char-window/verify.py
python3 -B scripts/research_package.py --package research/p104-odd-char-window
```

Expected final line: `PASS_ODD_CHAR_WINDOW rank36=36 char3_rank=38`, then
`PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `partial`.

The verifier enumerates all `C(120,2)` pairs, reduces `3I-A` modulo four odd
primes, solves the 120 characteristic-3 linear systems, and rejects a planted
orthogonal entry, the characteristic-3 reduction of `3I-A`, the all-ones
matrix, and the linear-only feature map on eight sampled columns. No Lean,
Docker, selected-baseline replay, or solver certificate was run.

## Open next questions

1. Is `w(P104; F)` equal to 13 for some odd characteristic, or is 36 (38 in
   characteristic 3) the wrong shape of construction? The E8 argument of #6933
   is the matching lower bound. A first step is one explicit factorisation of
   width 13 over `F_5`. Nothing in this package exhibits one, and the
   Bose-Mesner pattern `3I-A` cannot, because its rank is 36.
2. Does characteristic 3 admit a pattern of rank 36? The matrix that works for
   every other odd characteristic is illegal there. The degree-2 factorisation
   has rank 38. Closing the gap of 2 needs a different column space.

## Credit

DreamingOfClouds, PR #6933, for the window definition, the port list, the
characteristic-2 Gram rank, and Theorem 4's lower bounds `n/8`. The strongly
regular census and both upper bounds are new. Prepared by unpaidmoon with
substantial Cursor Grok assistance. New work is Apache-2.0.
