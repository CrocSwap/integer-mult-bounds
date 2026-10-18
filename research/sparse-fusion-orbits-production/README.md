# Production spectator orbits for the sparse-fusion screen

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`scripts/audit_sparse_fusion.py:central_gate_screen` still summed exact binary
ranks over every weight-three indicator. ToikY's opt-in adapter
`research/sparse-fusion-orbits/` already proved an exact spectator-orbit
reduction with identical receipts. This package wires that equivalent check
into the **production** source used by `make verify`.

`certificates/sparse-fusion-audit.json` stays **byte-identical** (this audit has
no `source_sha256` map). Every screen field, all 4,096 joint-frame inequalities,
finite phase identities, candidate budgets and the retained historical language
are unchanged. Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/sparse-fusion-orbits-production/verify.py
python3.12 -I -O -B research/sparse-fusion-orbits-production/verify.py
python3.12 -B scripts/research_package.py --package research/sparse-fusion-orbits-production
python3.12 -I -B research/sparse-fusion-orbits-production/benchmark.py --rounds 5
```

Expected:

```text
PASS_SPARSE_FUSION_ORBITS_PRODUCTION screen_heights=[22, 25, 28] screen_cases=3 certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/sparse-fusion-orbits-production outcome=completed
PASS_IDENTICAL_SPARSE_FUSION_ORBITS_PRODUCTION_RECEIPTS
```

Default verify is read-only. Use `--write-certificate` only after editing the
production source if regeneration is ever needed; the mathematical certificate
must still match the base bytes. Timing is host-descriptive and is not a
correctness gate.

On Linux / CPython 3.12.3, five alternating fresh-process pairs gave median
**screen-only 0.661 → 0.044 s (15.05×)** and **complete certificate 0.608 →
0.060 s (10.07×)**. Retained samples are in [`RESULT.json`](RESULT.json).

## Why the orbits are equivalent

For each of the 64 symmetric three-coordinate blocks `S`, the screen builds
`Q = diag(S, I_(h-3))`. Permutations fixing coordinates 0,1,2 satisfy
`P Q P^T = Q`, so

```text
rank(Q + t t^T) = rank(Q + (P t)(P t)^T).
```

Weight-three indicators with the same low three bits form one orbit of size
`C(h-3, 3-wt(low))`. Summing the eight weighted representatives therefore equals
the historical sum over all `C(h,3)` triples. At `h=25`, unary ranks fall from
147,200 to 512; the 128 frame ranks and 4,096 joint-pair ranks stay unchanged.
This is the same argument as `research/sparse-fusion-orbits/PROOF.md`.

## Overlap and credit

Closest priors:

- [ToikY / sparse-fusion-orbits](../sparse-fusion-orbits/) — opt-in orbit
  adapter; this package is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2054/#2150
  shared/mixed-point, #2100 ternary, #2117 DisjointTensor.frame_data, #2194
  production verify_factor, #2210 production leech_minor, #1861 parity-side)
  was not reopened. Fresh overlap refresh over 464 open PRs found no competing
  production rewrite of `central_gate_screen`.

Douglas R. Colkitt authored the sparse/fusion screen and original checker.
ToikY authored the orbit algorithm. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should `research/sparse-fusion-orbits/` note that production
   now ships the same orbit reduction?
   **Why it matters:** That package's source-admission pins expect the
   historical pairwise enumeration block.
   **First step:** Add a one-line status note without editing pinned evidence.
   **Blocked by:** Maintainer preference on touching incorporated historical
   packages.

2. **Question:** After orbit wiring, is the remaining joint-pair double loop
   the next productive production pass?
   **Why it matters:** With unary ranks reduced, joint pairs dominate residual
   screen time.
   **First step:** Profile production `central_gate_screen` with orbits merged.
   **Blocked by:** No open identical-receipt adapter yet for the joint-pair
   stage.
