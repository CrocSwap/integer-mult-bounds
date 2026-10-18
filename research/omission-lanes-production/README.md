# Production packed lanes for the R439 omission atlas

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`,
`research/r439-omission-atlas-seed81/verify.py` still replayed every single-ADD
omission with a fresh 661-bit row map. Sagar Thakrar’s opt-in adapter
`research/omission-lanes-seed92/` (incorporated
[#1433](https://github.com/CrocSwap/integer-mult-bounds/pull/1433)) already
proved sixteen independent omissions in integer bit lanes with identical
complete certificates. This package wires that equivalent rewrite into the
**production** PR1017 atlas used by R439 omission tooling.

The historical per-omission `replay(gates,k)` helper is retained for baseline
and witness checks. Dependent packages that live-pinned the pairwise-era atlas
digest are demoted or refreshed: opt-in `omission-lanes-seed92` vendors
pairwise `baseline.py`; `r439-three-omission-distance` demotes its atlas
`verify.py` pin to provenance (it has its own independent replay).

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/omission-lanes-production/verify.py
python3.12 -I -O -B research/omission-lanes-production/verify.py
python3.12 -B scripts/research_package.py --package research/omission-lanes-production
taskset -c 0 python3.12 -I -B research/omission-lanes-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_OMISSION_LANES_PRODUCTION honest=1 matrices=5563 short_checks=… corruption=1 certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/omission-lanes-production outcome=completed
PASS_IDENTICAL_OMISSION_LANES_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy packed-mutant bit-flip foil rejects via
audit failure. Package gates under `-O` still load checkers with
`compile(..., optimize=0)`. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs over the complete 5,563-mutant atlas gave the median wall time recorded
in [`RESULT.json`](RESULT.json). Timing is host-descriptive and is not a
correctness gate. Every honest receipt matches
`research/r439-omission-atlas-seed81/CERTIFICATE.json`.

## Why the packed lanes are equivalent

Pack a batch of `B` omissions as width-`N` lanes inside one Python integer.
Lane `j` occupies bits `[jN, (j+1)N)`. An ADD is an XOR of source into
destination; XOR cannot carry across lanes. Suppressing lane `j` at omitted
gate `k` is exactly the historical `if k != omit` guard for that lane. See
`research/omission-lanes-seed92/`.

## Open next questions

- Should other historical copies of the same literal omission loop adopt packed
  lanes with coordinated digest refresh?
- Should `research/omission-lanes-seed92` be marked superseded as an opt-in
  monkey-patch now that production ships packed lanes?

## Overlap and credit

Closest priors (different delivery):

- `research/omission-lanes-seed92/` / [#1433](https://github.com/CrocSwap/integer-mult-bounds/pull/1433)
  — opt-in packed lanes; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Leave-alone tooling through [#2412](https://github.com/CrocSwap/integer-mult-bounds/pull/2412)
  and pending `cursor/scalar-fused-dyadic-production-60b9` / deferred
  `cursor/ck-dyadic-replay-production-60b9` were not reopened.

Credit woklerx and Sagar Thakrar. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0.
