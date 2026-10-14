# Faster parity-side basis/contains with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, the historical parity-side audit
(`scripts/audit_parity_side.py`) rejects a specified even-`h` signed
intersection-parity DAG and prices its deterministic frame-safe coarsening for
`h = 8, 10, 26`. Profiling shows most time in
`scripts/binary_phase_frames.py`: `basis` and `contains` are called millions of
times from `parity_phase_repair.coarsen`, and `contains` previously rebuilt
`basis(space)` twice per membership test.

This change memoizes `basis` on the row tuple and implements `contains` by
reducing the vector against one basis of the space. The highest-bit pivot rule,
elimination order, classify/nullspace/residual APIs and every Boolean result are
unchanged. Only the source pin for `scripts/binary_phase_frames.py` changes
inside the three certificates that bind that file.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/parity-side-basis-cache/verify.py
python3.12 -I -O -B research/parity-side-basis-cache/verify.py
python3.12 -B scripts/research_package.py --package research/parity-side-basis-cache
python3.12 -I -B research/parity-side-basis-cache/benchmark.py --rounds 5
```

Expected:

```text
PASS_PARITY_SIDE_BASIS_CACHE h=[8, 10, 26] roles=[724, 2271, 82720] repaired=[938, 3283, 308336] ... no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/parity-side-basis-cache outcome=completed
PASS_IDENTICAL_PARITY_SIDE_RECEIPTS
```

Default verify is read-only. Use `--write-certificate` only after editing the
production source. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3, five alternating fresh-process pairs of the full
`h=8,10,26` parity-side experiment stream gave median wall time
**27.349 → 13.463 seconds (2.03×)**. Timing is host-descriptive and is not a
correctness gate; all samples and environment pins are in
[RESULT.json](RESULT.json). Every experiment receipt matches the baseline
checker fieldwise (`roles`, `repaired_roles`, `dag_sha256`, nested-edge counts
and obstruction fields). Restoring the old `binary_phase_frames.py` pin
recovers each base certificate byte-for-byte after that single substitution.

## Equivalence

- `basis` still inserts highest-bit pivots first and returns
  `tuple(pivots[p] for p in sorted(pivots, reverse=True))`.
- Memoization keys the exact row tuple; list/generator inputs are converted with
  `tuple(rows)` before the cache, matching the previous materialization.
- `contains(space, v)` is true iff reducing `v` against `basis(space)` yields
  zero, which holds exactly when
  `len(basis((*space, v))) == len(basis(space))`.
- `classify` still calls `basis` twice (once on the generators, once on the Gram
  rows); only the cost of those calls changes.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
packed balanced-Fano replay;
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793)
inplace-side prefix scan;
[CrocSwap/integer-mult-bounds#1217](https://github.com/CrocSwap/integer-mult-bounds/pull/1217)
ternary frame-pair memoization (h=8/9 frames only; not `binary_phase_frames`).
No competing open PR on this parity-side/`binary_phase_frames` object at refresh.

Douglas R. Colkitt authored the parity-side obstruction, repair and original
binary phase-frame checkers. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

Structured entries are in [TASK.json](TASK.json).
