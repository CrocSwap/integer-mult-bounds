# Faster mixed-point Circuit.verify supports with identical receipts

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, merged
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984)
sped up mixed-point `scalar_check` digests but left the general
`Circuit.verify` path on `scripts/experiments/mixed_point_circuit.py` on the
historical set-intersection genexpr

```text
sum(1<<i for i,source in enumerate(inputs) if len(set(source)&set(target))==r)
```

Profiling on `build(30,3,3,1)` shows that genexpr dominates `Circuit.verify`
wall time (seconds per call; tens of seconds at h≈40). Open SharedPoint
construction PRs (#2039/#2054) and DisjointTensor `frame_data` (#2117) leave
this object free.

This change replaces the genexpr with an equivalent closed-form point-incidence
mask: precompute `vertex[p]`, then for each r-subset `U` of the target keep
inputs that contain every point of `U` and avoid every other target point. Every
output support still matches the historical checker, `verify` still returns
`True`, and support admission uses `require` so it stays enforced under `-O`.
Only the source pin for `scripts/experiments/mixed_point_circuit.py` changes
inside the two certificates that bind that file.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/mixed-point-verify-masks/verify.py
python3.12 -I -O -B research/mixed-point-verify-masks/verify.py
python3.12 -B scripts/research_package.py --package research/mixed-point-verify-masks
python3.12 -I -B research/mixed-point-verify-masks/benchmark.py --rounds 5
```

Expected:

```text
PASS_MIXED_POINT_VERIFY_MASKS verify_cases=11 mask_cases=3994 certs=2 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/mixed-point-verify-masks outcome=completed
PASS_IDENTICAL_MIXED_POINT_VERIFY_MASK_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `Circuit.verify` on the fixed
fixture set `build(20,3,3,{0,1})`, `build(26,3,3,{0,1})`, `build(30,3,3,1)`
(construction excluded) gave median wall time
**8.331 → 0.121 seconds (69.03×)**.
Timing is host-descriptive and is not a correctness gate; all samples and
environment pins are in [RESULT.json](RESULT.json). Every verify receipt matches
the baseline checker (`True` return and identical output-support fingerprints).

## Equivalence

For inputs indexed `0..p-1` and target point set `T` with `|T|=l`,

- historical: bits of inputs `S` with `|S ∩ T| = r`
- closed form: `OR_{U ⊆ T, |U|=r} ( (AND_{p in U} vertex[p]) & (AND_{p in T\U} (full ^ vertex[p])) )`

where `vertex[p] = OR {1<<i : input i contains point p}` and
`full = (1<<len(inputs))-1`. An XOR-of-vertex mutant (r=0) or OR-of-vertex
mutant (r>0) differs and is rejected by the package controls. Topology of the
constructed DAG is untouched; only the expected-support check is rewritten.

## Open next questions

1. **Question:** Is mixed-point `Circuit.add` / `build` construction worth a
   separate identical-structure rewrite after this verify-path change?
   **Why it matters:** On `build(50,3,3,1)`, `add()` is ~37% of wall time via
   huge-int dict lookups; local binding alone was only ~1.09× in this session.
   **First step:** Profile `Circuit.add` on the hybrid h=50 build with a
   structure-identity oracle and prototype a faster intern path only if ≥~1.5×
   with identical DAGs.
   **Blocked by:** Out of this session’s stop rule.

2. **Question:** Should `DisjointTensor.verify`'s `dag_sha256` `json.dumps` path
   still get a hand-rolled formatter after #2117 `frame_data` lands?
   **Why it matters:** Post-mask verify residual is mostly json/sha of huge
   support strings; a streaming hand-roll was only ~1.22× on full verify here.
   **First step:** Re-profile on a tip that includes #2117.
   **Blocked by:** Micro-opt under the session bar; pin conflict with open #2117.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861)
(open; primary pin `binary_phase_frames.py` — same `parity-side.json` file,
different key),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984)
(mixed-point `scalar_check` digests; this package answers the remaining general
`Circuit.verify` support-genexpr object),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001),
[CrocSwap/integer-mult-bounds#2117](https://github.com/CrocSwap/integer-mult-bounds/pull/2117)
(DisjointTensor `frame_data`; different file). No competing open PR on
`Circuit.verify` at refresh.

Douglas R. Colkitt authored the mixed-point and early-sharing screens and
original checkers. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
