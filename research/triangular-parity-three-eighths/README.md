# One odd-heavy n=8 prefix stays at 3/2

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4702 records the symbol `(1, 1/4, 1/4, 0, 0, 0, 0, 0)`. Its largest proper
prefix is `3/2`, and the right shear alone is `85/64`. Its open question asks
whether `(1, 3/8, 1/8, 0, 0, 0, 0, 0)` keeps every proper prefix at most `3/2`.

## Record

The tail `l1` is `3/8 + 1/8 = 1/2`. The schedule is the same nested order:
right shear, even child, Schur child, left shear, repeated inside every
child. There are 22 factors in the top even/odd basis and 21 proper prefixes.

The right shear alone has infinity norm `731/512`. That is the first proper
prefix, and it is strictly below `3/2`. The quotient is

```text
k = (3/8, -3/64, 3/512, -3/4096).
```

The bottom row carries the tail of `z k`:

```text
1 + 3/8 + 3/64 + 3/512 = 731/512.
```

The next nontrivial factor is the even child's right shear, with a single
entry `1/8`. From that prefix onward, all 20 remaining proper prefixes have
infinity norm `3/2`. The largest proper-prefix infinity norm is `3/2`, so
every proper prefix is at most `3/2`.

The product of the 22 factors equals the even/odd reordering of the Toeplitz
matrix, whose infinity norm is also `3/2`. Nine factors differ from `I`. The
top left shear is the last of them, so eight nontrivial factors sit in the
proper prefixes.

`731/512 < 3/2 < 9/4`. Moving mass from the even coefficient onto the odd
coefficient raises the first shear from `85/64` to `731/512` and still leaves
it under the one-level cap. No later proper prefix passes that cap.

The even child is `(1, 1/8, 0, 0)`. The Schur child is
`(1, -1/64, 9/512, -9/4096)`.

## Not covered

- Any other `n = 8` symbol, including `(1, 3/8, -1/8, 0, 0, 0, 0, 0)`.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-three-eighths --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-three-eighths
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream fetches at 2026-10-22T16:50:09Z and 2026-10-22T16:52:53Z were that
commit. The pinned input blobs were unchanged. The selection is κ =
`60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T16:51:47Z (471 records) and
discussions fetched 2026-10-22T16:52:37Z (3625 records). Terms
`triangular-parity-three-eighths` and `731/512` reported 2 matches, this
README and this TASK. A second search of the same cache, offline, for
`triangular-parity-quarters` and `3/8, 1/8` returned this README, this TASK,
and #4702. That note leaves this odd-heavy symbol open. No matches is not a
novelty certificate.

## Open next questions

1. **Does the `n = 8` symbol `(1, 3/8, -1/8, 0, 0, 0, 0, 0)` keep every proper
   prefix at most `3/2`?** The positive odd-heavy symbol stays at `3/2`, and
   its right shear alone is `731/512`. A negative even coefficient changes
   the quotient signs. Do not treat `p^100` as already spent.

## Credit

- The equal-quarters record, and this question, are #4702's.
- The one-half `n = 8` record is #4701's.
- The one-split `3/2` cap is #4699's.
- The triangular parity split is #4100's `SHALLOW-TOEPLITZ.md`.
- The shifted-interior citation of that compiler is #4100's `GAUSSIAN.md`.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
