# Production gate-table `zero_state` for the multicold Clifford evaluator

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py`
still evaluated every amplitude with the historical per-basis loop. Charles
Bethin's opt-in adapter `research/clifford-state-performance/` already proved
exact permutation/phase tables with identical helper-interface receipts. This
package wires that equivalent evaluator into the **production** multicold source
used by `scripts/verify_cold617_interface.py`.

Historical inventories under `research/complex-multicold/**/MANIFEST.json` and
`SOURCE-PINS.json` without a registered VERIFY matrix are left as provenance.
`research/clifford-state-performance/` vendors pairwise-era bytes as
`baseline.py`. `research/clifford-reciprocal-basis-obstruction/` demotes its
`clifford_exact.py` pin to provenance (and drops it from VERIFY inputs).
Selected frontier untouched.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/clifford-state-production/verify.py
python3.12 -I -O -B research/clifford-state-production/verify.py
python3.12 -B scripts/research_package.py --package research/clifford-state-production
python3.12 -I -B research/clifford-state-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_CLIFFORD_STATE_PRODUCTION states=… instances=2 corruption=… certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/clifford-state-production outcome=completed
PASS_IDENTICAL_CLIFFORD_STATE_PRODUCTION_RECEIPTS
```

Helper-interface receipt and benchmark runs briefly **swap the live**
production `clifford_exact.py` under `try`/`finally` restore: `scripts/verify_cold617_interface.py`
overwrites `MULTICOLD_SOURCE` to the repository multicold tree, so temporary
overlay paths are ignored. The working tree is restored after every run.
Permutation-foil rejects via receipt mismatch or subprocess failure. Package
gates under `-O` still launch asserting helper-interface children (`python -B`
with `PYTHONOPTIMIZE` cleared; this host's CPython `-I` omits the script
directory from `sys.path`). Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-evaluator change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs gave median wall time **1.202 → 0.382 s
(3.15×)**. Timing is host-descriptive and is not a correctness gate; all
samples and environment pins are in [`RESULT.json`](RESULT.json). Every
helper-interface receipt matches digest
`8e775e5927b2f05c1671902680e25995adba6a2d2236f5dc116683b18ac4a42c`.

## Why the gate tables are equivalent

For a permutation gate, `Gx = G(x xor lowbit(x)) xor G(lowbit(x))` evaluates the
same binary matrix product as the historical `mv` loop. For a diagonal gate, the
upper-triangular quadratic formula with the lowest bit removed matches
`qvalue`. Translations, global phases and C gates retain the original
Gaussian-integer formulas and dyadic normalization. See
`research/clifford-state-performance/README.md`.

## Overlap and credit

Closest priors (different delivery):

- `research/clifford-state-performance/` — opt-in gate tables; this is the
  production wiring.
- [CrocSwap/integer-mult-bounds#662](https://github.com/CrocSwap/integer-mult-bounds/pull/662)
  — incorporated opt-in adapter.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2039/#2054
  shared-point, #2100 ternary, #2117 DisjointTensor, #2150 mixed-point,
  #2194/#2210/#2231/#2239/#2257/#2263/#2276/#2320 production rewrites; #1076
  quadratic-affine) was not reopened. Soft note: #2263/#2276 touch
  `e8-bit-r420/MANIFEST.sha256`; this tip does not.

Credit Charles Bethin and the multicold Clifford lineage. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should the other byte-identical vendored `clifford_exact.py`
   copies under `research/*/vendor/` adopt the same gate-table `zero_state` in a
   follow-up tip?
   **Why it matters:** Those trees still pin pairwise-era digests; a coordinated
   refresh would remove stale inventory digests without changing receipts.
   **First step:** Diff each copy against the production transform site and list
   which SOURCE inventories would need provenance demotion or honest refresh.
   **Blocked by:** Out of this session’s one-object stop rule.

2. **Question:** Should `scripts/verify_frontier617.py` /
   `verify_frontier626.py` grow a microbenchmark gate for the helper-interface
   stage?
   **Why it matters:** A future edit could restore the pairwise evaluator without
   failing equivalence tests.
   **First step:** Decide whether RESULT.json medians belong in CI or remain
   descriptive.
   **Blocked by:** Maintainer CI-budget preference.
