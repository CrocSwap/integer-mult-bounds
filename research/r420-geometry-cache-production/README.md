# Production geometry reuse for the PR543 R420 mutation harness

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/e8-bit-r420/code/mutants.py` still rebuilt `Word.__init__` / `labels()`
on every gate-only mutation control. The opt-in adapter
`research/r420-geometry-cache/` already proved an exact geometry cache with
identical mutation receipts. This package wires that equivalent reuse into the
**production** harness used by `research/e8-bit-r420/verify.sh`.

Every mutation stdout field, the JSON control receipt, and the
`PASS mutation controls: 9/9` marker are unchanged. `full()` and `interface()`
still run on a fresh `Word` after every geometry hit. Selected frontier
untouched. Production `xcheck.py:rref` is left alone (open #2263).

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/r420-geometry-cache-production/verify.py
python3.12 -I -O -B research/r420-geometry-cache-production/verify.py
python3.12 -B scripts/research_package.py --package research/r420-geometry-cache-production
python3.12 -I -B research/r420-geometry-cache-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_R420_GEOMETRY_CACHE_PRODUCTION controls=10 corruption=... mutants_sha=8c2738b3258e certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/r420-geometry-cache-production outcome=completed
PASS_IDENTICAL_R420_GEOMETRY_CACHE_PRODUCTION_RECEIPTS
```

Default verify is read-only. Timing is host-descriptive and is not a
correctness gate. On Linux / CPython 3.12.3, five alternating fresh-process
pairs gave median harness wall time about **9.66 → 1.49 s (≈6.46×)** in the
authoring screen; committed samples are retained in [`RESULT.json`](RESULT.json)
after `--write-result`.

## Why the geometry cache is equivalent

Gate-only mutations in this harness keep `h`, `v`, `R`, `form`, `lines` and
`frames` byte-identical. `Word.__init__` and `labels()` read only those fields.
Equal JSON serializations of those fields therefore have equal derived geometry
(`lines`, `fdim`, `fperp`, `FULL`, `ZERO`, label receipt). On a hit the harness
builds a fresh `Word`, copies immutable geometry into fresh mutable containers,
clears per-word nesting memoization, and always reruns `full()` and
`interface()` against the current gates. Failures during construction/labels
never populate the cache. Details match `research/r420-geometry-cache/`.

## Overlap and credit

Closest priors:

- [`research/r420-geometry-cache/`](../r420-geometry-cache/) — opt-in adapter;
  this package is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #2194
  production verify_factor, #2210 production leech_minor, #2231 sparse-fusion
  orbits, #2239 joint-dual replay, #1861 parity-side, #2257 frameopt.close,
  #2263 xcheck.rref) was not reopened. Fresh overlap refresh found no competing
  production rewrite of `mutants.py` geometry reuse.

**eumemic** authored the PR543 checker/harness/word. **mtpsl** authored the
opt-in geometry cache. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should other packages that pin live `mutants.py` bytes refresh
   those SHA-256 entries after this equivalence-preserving rewrite?
   **Why it matters:** Leaving old pins keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up after confirming receipt
   identity.
   **Blocked by:** Pin repair outside registered VERIFY live inputs is outside
   this change.

2. **Answered in-tree:** `research/r420-geometry-cache/` demotes its
   `mutants.py` execution pin to provenance in the same tip so its local
   verify no longer fails working-source drift.
