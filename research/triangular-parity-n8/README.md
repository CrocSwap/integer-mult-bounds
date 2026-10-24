# One n=8 parity prefix stays at 3/2

**Claim type:** an infinity-norm record for one nested triangular circuit.
**No new κ.** The selected record is `60403/20000000`. Every other tail, the
full shifted-interior stage, and the dyadic `p^100` normalizer stay hypotheses.

## Question

#4699 bounds one parity split by `3/2` when the tail `l1` is at most `1/2`.
Its open question asks whether nested splits keep every proper prefix inside
the product of those one-level caps. The named first step is one `n = 8`
symbol.

## Record

Let the symbol be `(1, 1/2, 0, 0, 0, 0, 0, 0)`. Its tail `l1` is `1/2`.
Expand every parity split down to `1×1` factors. At a block, apply the right
shear, then the even child, then the Schur child, then the left shear. Each
factor is an `8×8` matrix in the top even/odd basis. A child factor is
converted from that child's even/odd basis into its power basis before it is
written into the parent block.

This schedule has 22 factors, 5 of them different from `I`:

- the top right shear, infinity norm `3/2`;
- the Schur child's right shear, infinity norm `5/4`;
- the next Schur left shear, infinity norm `17/16`;
- the size-4 Schur left shear, infinity norm `5/4`;
- the top left shear, infinity norm `3/2`.

The top left shear is the last factor, so it is not part of a proper prefix.
The other four are. All 21 proper prefixes have infinity norm exactly `3/2`.
The product of the 22 factors equals the even/odd reordering of the Toeplitz
matrix, whose infinity norm is also `3/2`.

The product of two one-level caps is `9/4`, and the product of the four caps
already present in the proper prefixes is `81/16`. Both are larger than `3/2`.
On this symbol, nesting does not lift a proper prefix above the one-level cap.

The Schur child is `(1, -1/4, 0, 0)`, and its Schur child is `(1, -1/16)`.
Those are the only places a nested factor is not the identity.

## Not covered

- Any other `n = 8` symbol, including tails with two nonzero entries.
- A bound for every tail of `l1` at most `1/2`.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the prefix.
- The row gap after truncation, alias removal and rounding.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-n8 --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-n8
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream fetches at 2026-10-22T16:35:02Z and 2026-10-22T16:42:39Z were that
commit. The pinned input blobs were unchanged. The selection is κ =
`60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T16:41:33Z (468 records) and
discussions fetched 2026-10-22T16:42:23Z (3623 records). Terms
`triangular-parity-n8`, `proper-prefix infinity`, `nested parity`, and
`n=8 symbol` reported 2 matches, this README and this TASK. A second search
of the same cache, offline, for `triangular-parity-prefix` and
`parity-split prefix` returned #4699, its DONE note, and this TASK. That
note leaves the nested depth outside its claim. No matches is not a novelty
certificate.

## Open next questions

1. **Does every `n = 8` symbol with tail `l1` at most `1/2` keep every proper
   prefix at most `3/2`?** This symbol stays at `3/2` after four nontrivial
   factors. The first step is the symbol `(1, 1/4, 1/4, 0, 0, 0, 0, 0)`:
   record its largest proper-prefix infinity norm. Do not treat `p^100` as
   already spent.

## Credit

- The one-split `3/2` cap, and this question, are #4699's.
- The one-factor ledger is `research/one-factor-of-t`'s.
- The triangular parity split is #4100's `SHALLOW-TOEPLITZ.md`.
- The shifted-interior citation of that compiler is #4100's `GAUSSIAN.md`.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
