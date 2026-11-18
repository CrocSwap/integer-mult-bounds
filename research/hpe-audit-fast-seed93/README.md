# Fast exact HPE transport audit for the layer-end controls


**Production wiring:** `research/hpe-audit-integer-production/` promotes this adapter into the PR635 production path. Pairwise bytes are retained here as `baseline.py` for differential checks.


**Status: tooling improvement (verification engineering). No new κ. No check is changed, removed or weakened; the selected result is unchanged.**

After `research/hpe-transport-integer-production/`, production k492 `hpe_audit_and_transport.py` ships the integer-row rewrite; this opt-in package still pins and compares against the pairwise PR635 vendor copy.

- **Track and seed:** track 85–94 (verification engineering), assignment seed **93** from the OS CSPRNG (Python `secrets`).
- **Base commit:** `ba82555c64e1879e4b7decce28186f208fcb8262`.
- **Adds:** this directory and two Makefile targets. No existing file is modified.

## What is slow

In the selected #1042 replay, the `chain` stage takes 711 s. Of that, 530 s is spent in its five layer-end control steps (`lec-p6n`, `lec-promo`, `lec-jx`, `lec-hyb`, `lec-frames`).

Each step runs the pinned `layer_end_controls_leaver.py`. That script calls PR635's
`hpe_audit_and_transport.run` about 96 times: once on the honest word, then on each of
95 mutants, every one of which must be rejected at its pinned reason. After
`research/hpe-audit-integer-production/`, the live PR635 path ships integer rows; the
pairwise Fraction-dict bytes used for differential checks live in this package's
`baseline.py` (sha256 `c9a05ff2…0aa3`).

The cost is in exact arithmetic. On one audit, profiling shows:

| Share | Where |
|---|---|
| ~63% | `Fraction` operations in the pairwise row updates (endpoint replay in both orientations, plus the P and P⁻¹ state maps) |
| ~22% | `copy.deepcopy` of gates |

## What changes

`hpe_audit_fast.py` is the pinned file with four local changes. Its control flow, every assertion, every message and every output are kept.

1. **Integer rows.** Each scalar row is stored as integer numerators over one positive row denominator, instead of a dict of `Fraction`s.
   - Each gate coefficient is still built as `Fraction(a, b)`, in the same order as before. So the `assert target != source`, `assert q` and any `ZeroDivisionError` or `TypeError` are raised exactly as in the pinned file.
   - Zero entries are never stored. That makes every truth test (`if x`, `P[g].get(h)`) and every zero-pattern unchanged.
   - Rows are reduced by their content gcd only when a denominator exceeds 128 bits.
   - The dirty-compensation table is still built from normalized `Fraction`s, sorted as before.
   - The endpoint equality is evaluated entry by entry against the pinned expected `Fraction` matrix.
2. **Structural copies.** Gates are copied structurally instead of with `deepcopy`, and nested lists are never shared. Any shape other than a list of JSON scalars and integer lists falls back to `deepcopy`.
3. **Memoized frame bases.** `basis()` is memoized for tuples of integers, which is a pure function. Any other input takes the original uncached path.
4. **Shared coefficients.** `Fraction(a, b)` objects are shared for pairs of integers with b ≠ 0. They are immutable, so sharing cannot change any value.

### How it is used

`shim/hpe_audit_and_transport.py` stands in for the module. The **unchanged** controls script picks it up when `PR635_CODE` points at `shim/`, which is what `run_lec.py` sets.

`run_lec.py` repeats the chain's invocation exactly: same portable wrapper, routing word, reason-pin file and environment. It hash-pins the controls script, the wrapper, the routing word, both pin files and the reference audit. It has three modes:

- **`reference`:** the pinned audit, unchanged.
- **`fast`:** the fast audit only.
- **`crosscheck`:** every trial word is audited by **both** implementations. Any difference in outcome raises `RuntimeError`: exception type and arguments, output bytes, receipt without `seconds`, or printed output. It never raises `AssertionError`, so no `trial()` can absorb the mismatch. The reference result is what is returned, and each outcome is logged.

This is opt-in. Nothing in `make frontier1042-verify` changes. It composes with #1059, which parallelises the calls without changing the audit. This package makes each call cheaper.

## Evidence

All measurements were taken on one machine (macOS arm64, Python 3.12.3), with the same inputs, extracted from the committed `selected-replay.tar.gz`.

| Step | Reference | Fast | Speedup | Cross-check (96 trials) |
|---|---:|---:|---:|---|
| `lec-p6n` | 75.2 s | 30.3 s | 2.48× | identical (99.9 s) |
| `lec-promo` | 76.2 s | 30.3 s | 2.51× | identical (101.0 s) |
| `lec-jx` | 76.0 s | 29.9 s | 2.54× | identical (99.9 s) |
| `lec-hyb` | 75.4 s | 29.7 s | 2.54× | identical (99.5 s) |
| `lec-frames` | 76.4 s | 29.8 s | 2.56× | identical (101.1 s) |
| **total** | **379.2 s** | **150.0 s** | **2.53×** | **480/480 identical** |

Each `crosscheck` row means:

- all trial words gave identical outcomes and identical outputs under both audits;
- the resulting `COLD-END-CONTROLS.json` is byte-identical to the `reference` run's;
- it equals the maintainer's archived receipt for that step, apart from the word path.

**Differential fuzz** (`verify.py`):

- The five honest words give byte-identical canonical and full words, receipts and printed output.
- The recorded run `FUZZ-300-SEED93.json` has 300 mutants with seed 93, and all 300 are identical under both audits. Their outcomes:

  | Outcome | Count |
  |---|---:|
  | rejected at the arbitrary-dirt endpoint | 168 |
  | accepted (the audit passes) | 53 |
  | rejected because the compensation reads an entering helper | 27 |
  | rejected because the precondition or compensation touches a cold helper | 23 |
  | `TypeError` from a non-integer coefficient | 12 |
  | rejected as `nonmonotone` | 10 |
  | empty `assert q` | 6 |
  | other | 1 |

  The total time was 135.0 s for the reference and 44.9 s for the fast audit.

The mutations are:

- coefficient changes, including non-dyadic values;
- edge values: 0, 3⁶⁰, −5⁵⁰, 2³⁰⁰, `'x'`, 1.5 and `None`. These exercise `ZeroDivisionError`, `TypeError`, the empty `assert q` and the 128-bit normalization;
- gate drops, swaps and duplicates;
- register changes;
- frame-vector bit flips.

**Unit tests:**

- 300 random gate programs give integer rows equal to the pinned `Fraction` rows;
- zero entries are dropped;
- `apply` raises the same errors on bad gates as the reference;
- copies never share nested lists;
- a deliberately wrong fast audit makes `crosscheck` raise `RuntimeError` (control).

## Reproduce

```sh
make hpe-audit-fast-verify            # about 1-2 min: 5 honest words, 40 seeded mutants, 7 unit tests
make hpe-audit-fast-crosscheck-lec    # about 2 min: all 96 lec-p6n trials under both audits
```

The first target prints:

```
PASS_HPE_AUDIT_FAST_EQUIVALENCE | honest 5/5 identical | fuzz 40 seed 93 identical | reference …s fast …s
```

Any single step can also be run directly:

```sh
python3 -B research/hpe-audit-fast-seed93/run_lec.py --archived hyb --pins LEC-REASON-PINS-STACK --out /tmp/x/lec-hyb --mode fast
```

For `lec-frames`, pass `--pins LEC-REASON-PINS`.

## Scope

- **What the evidence is.** Equivalence is shown by:
  - a line-by-line argument (the changes are local, and they preserve values, zero patterns and exception order);
  - finite differential evidence: every trial of the five selected steps, plus a seeded fuzz.

  It is not a formal proof of equivalence for every possible input. That is why `crosscheck` exists: anyone who wants the pinned semantics on new words can run both audits.
- **What it does not change.** No pinned file, reason pin, receipt or selected record is changed.
- **About the timings.** They describe one machine. They are not measurements of multiplication performance.

## Credit

- **Audited code:** `hpe_audit_and_transport.py` was prepared for icekylinx with GPT-6 Astra assistance. It was adapted from icekylinx's PR425/433, DreamingOfClouds' PR484 `audit_gk.py` and Round19's transport, and shipped in PR635. Its Apache-2.0 header is kept in the derived file.
- **Controls:** the layer-end controls are DreamingOfClouds' and LayerReviewer's. The leaver variant and its not-applicable handling come from LeaverSAT and Q6Reviewer, in Jeremy Kothe's #1004/#1005 chain.
- **Related work:** #1059 (thakrarsagar) parallelises the T37 layer-end controls; this package is complementary to it.
- **Precedents:** #367 applied the same `Fraction`-to-integer technique to PR364's frame verifier, and #824 to the stage-pair audit. Neither touches this audit.

Prepared by Wronskode (@Wronskode) with substantial AI assistance from Claude (Anthropic) via Claude Code. New material is Apache-2.0.
