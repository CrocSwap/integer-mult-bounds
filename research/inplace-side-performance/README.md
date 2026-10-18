# Faster historical inplace-side prefix replay

**Tooling improvement; no new kappa.** The historical
`scripts/experiments/inplace_side.py:verify_prefix` check rejects a specified
n-role Gauss–Jordan side family using three pinned witnesses (`h = 42, 46, 50`).
Each elimination column previously rebuilt `sorted(unused)` to locate the least
unused row with the pivot bit set. The production checker now scans an unused
flag array from index 0 and tests bits with a column mask. The lexicographic
rule, XOR updates, switch witnesses, deficit arithmetic and every receipt field
are unchanged.

The selected frontier, `upstream/` and the mathematical rejection in
[docs/research/inplace-side.md](../../docs/research/inplace-side.md) are not
reopened. Only the source pin for `scripts/experiments/inplace_side.py` changes
inside `certificates/inplace-side.json`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/inplace-side-performance/verify.py
python3.12 -I -O -B research/inplace-side-performance/verify.py
python3.12 -I -B -m unittest tests.test_inplace_side tests.test_inplace_side_performance -v
python3.12 -B scripts/research_package.py --package research/inplace-side-performance --check-only
python3.12 -B scripts/research_package.py --package research/inplace-side-performance
```

Expected verifier line:

```text
PASS_INPLACE_SIDE_PREFIX_FAST witnesses=3 h=[42, 46, 50] paths=[151, 415, 767] ... no_new_kappa
```

Expected registered replay:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/inplace-side-performance outcome=completed
```

Normal verification is read-only. To regenerate the certificate after editing the
production source:

```sh
python3.12 -I -B research/inplace-side-performance/verify.py --write-certificate
```

Before/after wall times (descriptive; not a pass gate):

```sh
python3.12 -I -B research/inplace-side-performance/benchmark.py --rounds 5
```

Expected: `PASS_IDENTICAL_INPLACE_PREFIX_RECEIPTS`. Samples are retained in
[RESULT.json](RESULT.json). On this Linux host / CPython 3.12.3, five alternating
fresh-process pairs gave median **17.061 s → 5.466 s (3.12×)** for the three
pinned witnesses. Timing is descriptive, not a correctness gate.

## Why the receipts stay identical

For each column `col`, the original code selected

```text
min{ i in unused : rows[i] has bit col }
```

by materializing `sorted(unused)` and taking the first hit. Scanning
`i = 0, 1, …` over a boolean unused table and stopping at the first hit yields
the same index, because the integers are totally ordered. Column tests
`rows[i] & (1 << col)` equal `rows[i] >> col & 1` on these nonnegative row
masks. The subsequent row-XOR updates therefore run on the same pivot sequence
and produce the same residual matrix, the same certified nonorthogonal path
list and the same deficit upper bound.

[baseline.py](baseline.py) is a byte-identical copy of
`scripts/experiments/inplace_side.py` at base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea` (blob
`db3de6f1d962ccc3a4eae31f83c72bba995ba44e`). The verifier compares every field
of every witness receipt against that baseline, checks shared rejection
behavior, rejects a greatest-unused mutant on all three witnesses, and requires
the working certificate to differ from the base certificate only in the single
`inplace_side.py` source pin.

## Task card, overlap and limits

Chooser seed `1cd1f71746c2d200dd617bc3dd17d8a6` drew `bit-mechanisms`; live
helper-contract and register-model surfaces were saturated. Expertise override
to `replay-runtime` (verifier-engineering). Scope **refined** to this fixed
historical screen inside `make verify-certificates`.

Closest priors (different objects; no code reused here):

- [CrocSwap #756](https://github.com/CrocSwap/integer-mult-bounds/pull/756) —
  packed-column balanced-Fano replay (2.91×) on a different checker.
- [CrocSwap #1584](https://github.com/CrocSwap/integer-mult-bounds/pull/1584) —
  finite-bit block-core frame interning.
- [CrocSwap #1076](https://github.com/CrocSwap/integer-mult-bounds/pull/1076) /
  [#1075](https://github.com/CrocSwap/integer-mult-bounds/pull/1075) —
  quadratic-affine / quadratic-code tooling.
- Local `find_overlap.py` for `inplace side` / `inplace_side` / `verify_prefix`
  reported no competing open PR on this object at refresh time.

Limits: timing is host-descriptive; OS caches were not flushed. Full
`make verify`, selected-supplier cold replay, Lean and multiplication-theorem
obligations were not rerun for this isolated historical-checker change.

## Open next questions

- Can the same least-unused scan replace `sorted(unused)` inside `compile_side`
  without changing gate lists on `h = 6, 10` and, if identical, on `h = 50`?
- Should CI grow a soft regression timer for this screen, or keep RESULT.json
  descriptive only?

## Credit

Douglas R. Colkitt authored the inplace-side rejection, witnesses and original
checker. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor), wentaol4@illinois.edu)
with substantial AI assistance, under Apache-2.0. No independent human
peer-review or formal proof-assistant claim.
