# Production containment masks for joint-dual word replay

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`scripts/experiments/binary_frame_replay.py:replay` still scanned every
weight-three triple for each paid output. Aaron Wang's opt-in adapter
`research/joint-dual-replay-fast/` already proved an exact containment-mask
reduction with identical receipts. This package wires that equivalent check
into the **production** source used by `make joint-dual-verify`.

Compiler replay receipts in `certificates/joint-dual-compiler.json` stay
**byte-identical**. Only the source digests for
`scripts/experiments/binary_frame_replay.py` change inside
`research/joint-dual/SOURCE.json`, `certificates/joint-dual-kappa.json` and
`certificates/skip-frame-kappa.json`. Every assertion, `check_word` control
(including the PR64 scatter multiset), both full-basis orientations and the
histogram/rank-mass fields are unchanged. Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/joint-dual-replay-production/verify.py
python3.12 -I -O -B research/joint-dual-replay-production/verify.py
python3.12 -B scripts/research_package.py --package research/joint-dual-replay-production
python3.12 -I -B research/joint-dual-replay-production/benchmark.py --rounds 5
```

Expected:

```text
PASS_JOINT_DUAL_REPLAY_PRODUCTION words=[23, 25] outputs=12261 receipts=2 no_new_kappa
PASS_JOINT_DUAL_REPLAY_PRODUCTION_O_POLICY refused_by_assert_gate=2 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/joint-dual-replay-production outcome=completed
PASS_IDENTICAL_JOINT_DUAL_REPLAY_PRODUCTION_RECEIPTS
```

Default verify is read-only. Timing is host-descriptive and is not a
correctness gate.

On Linux / CPython 3.12.3, five alternating fresh-process pairs replaying both
pinned words (`h=23` and `h=25`) gave median wall time **5.873 → 3.120 s
(1.882×)**. Retained samples are in [`RESULT.json`](RESULT.json).

## Why the masks are equivalent

For `triples = list(combinations(range(h), 3))`, bit `i` of `center[c]` is set
iff `c in triples[i]`, and bit `i` of `pair[c][x]` is set iff
`{c, x} ⊆ triples[i]`. Then

```text
expected(common, triple) = center[common]
    & ~pair[common][x] for each x in set(triple) - {common}
```

equals the historical scan

```text
sum(1 << i for i, t in enumerate(triples)
    if common in t and not (set(t) & (set(triple) - {common})))
```

Destination lists for copied centres are the same index lists as
`[i for i, t in enumerate(triples) if common in t]`. Frame lookup preserves
first-match `F.index` semantics. This is the same argument as
`research/joint-dual-replay-fast/README.md`.

## Overlap and credit

Closest priors:

- [Aaron Wang / joint-dual-replay-fast](../joint-dual-replay-fast/) — opt-in
  containment-mask adapter; this package is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #2194
  production verify_factor, #2210 production leech_minor, #2231 production
  sparse-fusion orbits, #1861 parity-side) was not reopened. Fresh overlap
  refresh over open PRs found no competing production rewrite of
  `binary_frame_replay.replay`.

Chafik Boukhalfa authored the joint-dual verifier and certificates.
Aaron Wang authored the containment-mask algorithm. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should `research/joint-dual-replay-fast/` note that production
   now ships the same containment-mask scan?
   **Why it matters:** That package's source-admission pins expect the
   historical pairwise enumeration block.
   **First step:** Add a one-line status note without editing pinned evidence.
   **Blocked by:** Maintainer preference on touching incorporated historical
   packages.

2. **Question:** After mask wiring, is the remaining full-basis word simulation
   the next productive production pass?
   **Why it matters:** With the per-output scans reduced, dual-orientation XOR
   simulation dominates residual replay time.
   **First step:** Profile production `replay` with masks merged.
   **Blocked by:** No open identical-receipt adapter yet for that stage.
