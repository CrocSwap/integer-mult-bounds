# Production integer RREF for the R420 exact checker

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, production
`research/e8-bit-r420/code/xcheck.py:rref` still paid a Fraction-per-entry
elimination on every frame. The opt-in adapter
`research/r420-rref-performance/` already proved an equivalent
primitive-integer RREF with identical receipts and explicitly deferred
production adoption. This package wires that equivalent check into the
**production** `rref` used by `research/e8-bit-r420/verify.sh` step 2 and
`mutants.py`.

Only `research/e8-bit-r420/code/xcheck.py` and its
`research/e8-bit-r420/MANIFEST.sha256` digest line change outside this
directory. Label validation, HNF, determinant, F2 replay, H1–H5/dirty
restoration, and every mutation control remain the historical implementations.
Selected frontier untouched. Prior research packages that still pin the
Fraction `xcheck.py` digest (including `research/r420-rref-performance/SOURCES.json`
and other R420 follow-ons) are left as historical provenance, same pattern as
earlier production promotions.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/r420-rref-production/verify.py
python3.12 -I -O -B research/r420-rref-production/verify.py
python3.12 -B scripts/research_package.py --package research/r420-rref-production
python3.12 -I -B research/r420-rref-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_R420_RREF_PRODUCTION frames=672 matrices=677 corruption=… certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/r420-rref-production outcome=completed
PASS_IDENTICAL_R420_RREF_PRODUCTION_RECEIPTS
```

Default verify is read-only. Timing is host-descriptive and is not a
correctness gate. On Linux / CPython 3.12.3 (this host), five alternating
fresh-process pairs gave:

- check median **1.064 → 0.362 s (2.94×)**
- mutants harness median **11.090 → 3.457 s (3.21×)**
- stage-median sum **12.155 → 3.819 s (3.18×)**

Retained samples are in [`RESULT.json`](RESULT.json).

## Why the integer RREF is equivalent

Aman’s primitive-integer elimination (`exact_rows._eliminate(..., reduced=True)`)
computes a content-primitive integer row echelon form with the same pivot
columns as the historical Fraction RREF. Scaling each pivot row by the
reciprocal of its pivot entry returns lists of `Fraction` equal to the
historical basis rows. The unchanged `nullspace_int` therefore emits the same
integer annihilators. Finite evidence compares all **672** shipped frames plus
five supplemental matrices, and byte-identical complete `xcheck` /
`mutants` stdout. This supports the scoped kernel argument; it is not a formal
proof of the multiplication theorem.

## Overlap and credit

Closest priors (different delivery):

- `research/r420-rref-performance/` — opt-in integer RREF adapter; this package
  is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #2194
  production verify_factor, #2210 production leech_minor, #2231 production
  sparse-fusion orbits, #2239 joint-dual replay, #2257 bit-frame
  `frameopt.close`, #1861 parity-side, #1076 quadratic-affine) was not reopened.

Credit **eumemic** (PR543 checker/harness/word), **Aman** (PR367 integer rows),
and the authors of `research/r420-rref-performance/`. Prepared by **Wentao Li**
with substantial AI assistance; see [NOTICE.md](NOTICE.md) and
[TASK.json](TASK.json). Apache-2.0.

## Open next questions

1. **Should `research/r420-rref-performance/` note that production now ships the
   same integer `rref`?** Its `SOURCES.json` still pins the historical Fraction
   `xcheck.py` bytes. First step: one-line status note and pin refresh or relax.
   Blocked on: maintainer preference for touching incorporated packages.
2. **Should other packages that pin `research/e8-bit-r420/code/xcheck.py` refresh
   that single digest?** Leaving old pins keeps this tooling change focused.
   Blocked on: a dedicated provenance follow-up.
