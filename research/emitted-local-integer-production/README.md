# Production integer-row emitted local audit

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/complex-k492-owner-repair/code/hpe_audit_local.py` still stored every
scalar row as a dictionary of `Fraction` values. woklerx’s opt-in adapter
`research/emitted-local-integer-replay-seed90/` (incorporated
[#1184](https://github.com/CrocSwap/integer-mult-bounds/pull/1184)) already
proved shared-denominator sparse integer rows with identical complete local-audit
receipts. This package wires that equivalent rewrite into the **production**
k492 checker used by emitted-local tooling.

SELECTED-SOURCE-bound
`research/complex-sw4-frame8/local/hpe_audit_local.py` copies are intentionally
left pairwise so the selected inventory stays untouched. Dependent VERIFY
packages that previously live-pinned the k492 path retarget to that sw4 checker.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/emitted-local-integer-production/verify.py
python3.12 -I -O -B research/emitted-local-integer-production/verify.py
python3.12 -B scripts/research_package.py --package research/emitted-local-integer-production
taskset -c 0 python3.12 -I -B research/emitted-local-integer-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_EMITTED_LOCAL_INTEGER_PRODUCTION assertions=… controls=25 corruption=… certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/emitted-local-integer-production outcome=completed
PASS_IDENTICAL_EMITTED_LOCAL_INTEGER_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy ADD-drop foil rejects via audit failure
or receipt divergence. Package gates under `-O` still launch asserting checker
children (`python -B` with `PYTHONOPTIMIZE` cleared). Full `make verify`,
selected cold replay, Lean, and multiplication-theorem obligations were not
rerun for this isolated historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs gave median complete selected-R480 local-audit wall time **7.080 → 3.131 s (2.26×)**. Details are in
[`RESULT.json`](RESULT.json). Timing is host-descriptive and is not a
correctness gate. Every receipt matches digest
`13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17`
(25 retained negative controls).

## Why the integer rows are equivalent

Each row stores integer numerators over a shared power-of-two denominator
(`2**exponent`). Scale and ADD updates shift exponents exactly when the
coefficient is dyadic, matching `Fraction` arithmetic on this dyadic scalar
macro language. Zero entries are omitted just as in the original dictionaries.
JSON mutation fixtures are decoded once and reloaded per control, preserving
the original deepcopy isolation. See
`research/emitted-local-integer-replay-seed90/PROOF.md`.

## Overlap and credit

Closest priors (different delivery):

- `research/emitted-local-integer-replay-seed90/` / [#1184](https://github.com/CrocSwap/integer-mult-bounds/pull/1184)
  — opt-in integer rows; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- Open leave-alone tooling on other objects (#1922 joint frames, #2039/#2054
  shared-point, #2100 ternary, #2117 DisjointTensor, #2150 mixed-point,
  #2194/#2210/#2231/#2239/#2257/#2263/#2276/#2320/#2329/#2348 production
  rewrites; #1076 quadratic-affine) was not reopened.

Credit woklerx, icekylinx, and the retained local-checker lineage. Prepared by
Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should the SELECTED-SOURCE-bound sw4 `hpe_audit_local.py`
   copies adopt the same integer-row rewrite with a coordinated
   `SELECTED-SOURCE.json` digest refresh?
   **Why it matters:** Selected cold-chain local-replay still runs the pairwise
   checker.
   **First step:** Enumerate SELECTED-SOURCE paths with sha256 `6bd9a1e2…` and
   dependent VERIFY binders.
   **Blocked by:** Maintainer inventory-refresh preference.

2. **Question:** Should other byte-identical vendored `hpe_audit_local.py`
   copies adopt the same rewrite?
   **Why it matters:** Historical trees still pin pairwise-era digests.
   **First step:** Diff each copy against the production transform site.
   **Blocked by:** One-object stop rule.
