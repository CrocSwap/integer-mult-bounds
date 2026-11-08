# Production one-basis closure for the PR886 bit-frame checker

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/bit589-frame-optimum/frameopt.py:close` still rebuilt a modular
elimination for every candidate live line. Ross Richardson's opt-in adapter
`research/bit-frame-closure-basis/` (merged [#1666](https://github.com/CrocSwap/integer-mult-bounds/pull/1666))
already proved an exact one-basis reduction with identical receipts. This
package wires that equivalent `close` into the **production** source used by
`research/bit589-frame-optimum/verify.sh`.

Every receipt field, all three stdout digests in
`research/bit-frame-closure-basis/EXPECTED.json`, the degraded positive control
and the `PASS_BIT589_FRAME_OPTIMUM` marker are unchanged. Selected frontier
untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/bit-frame-closure-production/verify.py
python3.12 -I -O -B research/bit-frame-closure-production/verify.py
python3.12 -B scripts/research_package.py --package research/bit-frame-closure-production
python3.12 -I -B research/bit-frame-closure-production/benchmark.py --rounds 5
```

Expected:

```text
PASS_BIT_FRAME_CLOSURE_PRODUCTION cases=['pr589', 'pr555', 'degraded'] corruption=... certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-frame-closure-production outcome=completed
PASS_IDENTICAL_BIT_FRAME_CLOSURE_PRODUCTION_RECEIPTS
```

Default verify is read-only. Timing is host-descriptive and is not a
correctness gate. On Linux / CPython 3.12.3, five alternating fresh-process
pairs gave median **pr589 17.298 → 3.213 s (5.383×)** and **complete three-case
suite 47.744 → 8.904 s (5.362×)**. Samples are retained in
[`RESULT.json`](RESULT.json).

## Why the one-basis close is equivalent

For a nonempty mask `M` and live lines `L_i`, the historical checker returns

```text
({i : rank_p(S ∪ {L_i}) = rank_p(S)}, rank_p(S))  where S = {L_i : i ∈ M}.
```

The production path builds one increasing-pivot echelon basis of `span_p(S)`
and admits each remaining live line exactly when its residual is zero. That is
the same membership predicate over the fixed prime field
`p = 2147483647`. The module-level Hadamard guard
`B^d < p^2` still justifies that modular rank equals rational rank on this
line table. The empty-mask result remains `(0, 0)`. Full details are in
`research/bit-frame-closure-basis/PROOF.md`.

## Overlap and credit

Closest priors:

- [Ross Richardson / bit-frame-closure-basis](../bit-frame-closure-basis/) —
  opt-in one-basis adapter (#1666); this package is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #2194
  production verify_factor, #2210 production leech_minor, #2231 sparse-fusion
  orbits, #2239 joint-dual replay, #1861 parity-side) was not reopened. Fresh
  overlap refresh over 475 open PRs found no competing production rewrite of
  `frameopt.close`.

Seth Burkart authored the PR886 frame-only optimum checker. Ross Richardson
authored the one-basis algorithm. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should `research/bit-frame-closure-basis/` note that production
   now ships the same one-basis close?
   **Why it matters:** That package's source-admission pins expect the
   historical pairwise `frameopt.py` bytes.
   **First step:** Add a one-line status note without editing pinned evidence.
   **Blocked by:** Maintainer preference on touching incorporated historical
   packages.

2. **Question:** Should `research/r439-resynth-frame-seed10` refresh its
   `frameopt.py` SHA-256 after this equivalence-preserving rewrite?
   **Why it matters:** That package binds working-tree bytes; leaving the old
   pin keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up after confirming receipt
   identity.
   **Blocked by:** Pin repair outside this tooling change.
