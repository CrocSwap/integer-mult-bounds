# Production packed dyadic central-factor check

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, `scripts/experiments/complex_centers.py:verify_factor`
still used the historical nested entrywise loop over all scatter/gather pairs.
Ross Richardson's opt-in adapter `research/central-factor-packed/` already proved
an injective packed-row algorithm with identical receipts. This package wires
that equivalent check into the **production** source used by
`scripts/audit_complex_centers.py` / `make verify-certificates`.

Only the source pin for `scripts/experiments/complex_centers.py` changes inside
`certificates/dyadic-central-factor.json`. Every coefficient is still checked;
`circuit`/`factor` generators, side/phase obligations and the retained historical
`2^-31` language are unchanged. Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/central-factor-production/verify.py
python3.12 -I -O -B research/central-factor-production/verify.py
python3.12 -B scripts/research_package.py --package research/central-factor-production
python3.12 -I -B research/central-factor-production/benchmark.py --rounds 5
```

Expected:

```text
PASS_CENTRAL_FACTOR_PRODUCTION heights=[8, 10, 12, 18, 26] ... no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/central-factor-production outcome=completed
PASS_IDENTICAL_CENTRAL_FACTOR_PRODUCTION_RECEIPTS
```

Default verify is read-only. Use `--write-certificate` only after editing the
production source. Timing is host-descriptive and is not a correctness gate.

On Linux / CPython 3.12.3, five alternating fresh-process pairs gave median
**factor-only 2.615 → 0.059 s (44.06×)** and **complete audit 5.784 → 3.356 s
(1.72×)**. Samples are in [`RESULT.json`](RESULT.json).

## Why the packed check is equivalent

For each scatter row `u(S)` and gather column `v(T)` the historical obligation is

```text
sum_i u(S)[i] v(T)[i] = |S ∩ T| - 1.
```

Gather entries are in `{-1,0,1}` and appear at most once per column, so
`|actual - expected| <= ||u(S)||_1 + 2`. Choose
`bits = (max_S ||u(S)||_1 + 2).bit_length()` and place `B = 2**bits`. Packing
every gather/incidence column as `sum_j coeff_j B**j` and comparing packed
actual/expected rows is an injective encoding of the difference vector: the
packed equality holds if and only if every coefficient matches. This is the
same argument as `research/central-factor-packed/README.md`; structural and
scalar-charge gates are unchanged.

## Overlap and credit

Closest priors:

- [Ross Richardson / central-factor-packed](../central-factor-packed/) — opt-in
  packed adapter; this package is the production wiring of that algorithm.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #1861
  parity-side, #2155 exclusion embedding residual) was not reopened.

Douglas R. Colkitt authored the dyadic central factor and original checker.
Ross Richardson authored the packed algorithm. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** After #2117's `DisjointTensor.frame_data` lands, what is the
   residual wall time of `audit_complex_centers.py` with packed `verify_factor`
   already in production?
   **Why it matters:** `frame_data` still dominates the complete audit after the
   coefficient check shrinks.
   **First step:** Replay `benchmark.py --rounds 5` on a tree that also contains
   the merged #2117 head.
   **Blocked by:** #2117 is leave-alone / open.

2. **Question:** Should `verify-certificates` adopt a microbenchmark regression
   gate for `verify_factor(h=26)`?
   **Why it matters:** A future edit could restore the nested loop without
   failing equivalence tests.
   **First step:** Decide whether `RESULT.json` medians belong in CI or remain
   descriptive.
   **Blocked by:** Maintainer CI-budget preference.
