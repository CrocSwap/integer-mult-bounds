# Swap-free route for the helper-462 matcher

**Partial route-schedule result. No new κ.** The selected record stays
`781451/250000000`.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status: **refined**.

Discussion #1166 comment 19137812 leaves one concrete next task after the
conditional A0→A1 API in `research/bit-completed-backend-api`: a literal
stock/role/route generator for one fixed invocation. This package does not
build that generator. It prices one letter of it, the already published
helper-462 matcher.

The pinned matcher `S` is the `matcher` field of
`research/bit-completed-backend-api/science/RESULT.json`. Its published
elimination is 5 axis swaps, 5 scales and 14 shears. Under that package's own
high-row rule, the pair ledger is 80 ordinary chunk interchanges, 80 unit
scalings and 224 linear ordered shifts.

In the same alphabet the following holds.

- `det(S) = -16`.
- For any word of axis swaps, single-coordinate scales and shears,
  `(product of the scale coefficients) * (-1)^{number of swaps} = det(S)`.
  A word with no scale letter would have determinant `±1`, so every
  factorization uses at least one scale.
- Elimination without axis swaps produces an explicit word with **0 swaps,
  7 scales and 27 shears**. Its scale coefficients multiply to `-16`, and
  the word multiplies to `S`.
- The same high-row rule assigns this word the pair bill **0 ordinary chunk
  interchanges, 112 unit scalings and 432 linear ordered shifts**.

The published five swaps are therefore one Gaussian schedule, not a lower
bound on ordinary chunk interchanges for this matrix. Seven scales and
twenty-seven shears are not claimed to be minimal. No comparison of a
completed interchange against a linear shift is made, so this is not a
signed-moment improvement.

Checked controls: the pinned 24-factor word still multiplies to `S`; dropping
the last shear, or adding 1 to its coefficient, misses `S`; the identity needs
no scale. The predecessor multiplier `16` per letter reproduces the pinned
ledger before it is applied to the new word.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/helper462-swap-free-route/verify.py
python3 -I -B research/helper462-swap-free-route/verify.py
python3 -B scripts/research_package.py --package research/helper462-swap-free-route
```

Expected first-line token: `PASS_HELPER462_SWAP_FREE_ROUTE`.

## Open next questions

1. Once a chunk interchange and a shear have their inherited P2 tariffs, does
   any legal word beat the published pair on the completed ordinary bill?
   The zero-swap schedule removes 80 interchanges and adds 32 scales and 208
   shifts. Those tariffs are not in this package.
2. Is there a zero-swap word with one scale, or with fewer than 27 shears?
   The determinant identity makes one scale necessary. The constructive count
   is only an upper bound.

## Credit

The matcher, the five-swap elimination and the high-row ledger are from
`research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957), using
the helper-462 witness of ai-nanachi #4760/#4814 and the retained ordinary
lineage named there. Prepared by unpaidmoon with substantial Cursor Grok
assistance. Apache-2.0.
