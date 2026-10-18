# Review handoff

Status: **finite complex-supplier construction; no new kappa**.

Base: `007664306fff84fbb1c9a1b4053b69f439764034`.
Published branch: `zewelor/integer-mult-bounds:research/jp8-direct-small-integers-seed29`.
Scope: only `research/jp8-direct-small-integers/`.

The completed result replaces all historical PR626 JP8 coefficients ±2/±3
with direct target accumulation and a paid work clear. Counts fall by 2,848
real primitives in each orientation, with exact scalar boundary, dirty-input,
prefix, grid, source-access and unchanged-paid-profile evidence.

Clone the published contribution and record the reviewed head:

```sh
git clone --single-branch --branch research/jp8-direct-small-integers-seed29 https://github.com/zewelor/integer-mult-bounds.git jp8-review
cd jp8-review
git rev-parse HEAD
python3 -I -O -B research/jp8-direct-small-integers/verify.py
python3 -I -O -B research/jp8-direct-small-integers/test_package.py
python3 -I -O -B research/jp8-direct-small-integers/recheck_fraction.py
```

Expected: `PASS_JP8_DIRECT_SMALL_INTEGERS macros=1424+1424 saved=2848/2848 columns=725 no_new_kappa`, six passing tests, and
`PASS_JP8_FRACTION_RECHECK all_program_receipt_fields=equal no_new_kappa`.

Original patch validation: a fresh temporary Git index based at the exact base
accepted the initial patch and produced the same tree as that contribution. A minimal
export from that Git tree (this package plus its six pinned inputs) passed the
optimized isolated verifier without Git or network access. Python syntax,
JSON parsing and staged whitespace checks also passed.

Suggested PR title:
**Finite complex construction: direct JP8 integer updates save 2,848 primitives per orientation (no new kappa)**.

The patch is ready for an independently scoped review; production adoption is
separate. Read `README.md` for the proof, complete cost/access comparisons,
predecessor credit and unresolved physical/compiler/analytic obligations.
`EXPECTED.json` is the exact finite certificate; `SOURCES.json` pins all six
consumed inputs; `VALIDATION.md` records executed checks.

Publication resumed after the contributor created `zewelor/integer-mult-bounds`.
The result is published on `research/jp8-direct-small-integers-seed29` in that
writable fork, preserving the exact research base. The contributor opened
[PR1223](https://github.com/CrocSwap/integer-mult-bounds/pull/1223) after the
integration's create-PR attempt returned HTTP 403. The former patch-only handoff
is superseded by the published branch and PR.
No pinned coordination issue existed, so the claim is recorded locally.
Refreshed upstream main is `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`; all six
consumed inputs are unchanged. Related PR999/1036/1064 are credited and the
additional JP8 scope is explained in `README.md` and `OVERLAP.json`.

A requested second audit checked the published head
`86381e9adf3c9d1e958cca4d53fec15254190434` (tree
`0166b06587244338e81d81635892e5cff7ecd12e`) and added the complete Fraction
interpreter. The original lowering and `EXPECTED.json` are unchanged.
All six source payloads also match refreshed main
`49b3157d1d89adcef16df8be98445451672be5ba`. Repeated validation is recorded in
`VALIDATION.md`; hosted workflows were awaiting maintainer action at that audit.

Prepared by Michał Ciemięga (@zewelor), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review, full multiplication proof, global
invoice/assembly run, or new kappa is claimed.
