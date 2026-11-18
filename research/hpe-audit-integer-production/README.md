# Production integer-row HPE audit and transport

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code/hpe_audit_and_transport.py`
still stored every scalar row as a dictionary of `Fraction` values. Wronskode’s
opt-in adapter `research/hpe-audit-fast-seed93/` already proved shared-denominator
integer rows with identical layer-end control receipts. This package wires that
equivalent rewrite into the **production** PR635 auditor used by frontier1042
layer-end controls.

Other vendored `hpe_audit_and_transport.py` copies outside this PR635 path are
intentionally left pairwise.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/hpe-audit-integer-production/verify.py
python3.12 -I -O -B research/hpe-audit-integer-production/verify.py
python3.12 -B scripts/research_package.py --package research/hpe-audit-integer-production
taskset -c 0 python3.12 -I -B research/hpe-audit-integer-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_HPE_AUDIT_INTEGER_PRODUCTION assertions=… honest=5 fuzz=40 corruption=… certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/hpe-audit-integer-production outcome=completed
PASS_IDENTICAL_HPE_AUDIT_INTEGER_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy apply-noop foil rejects via outcome
divergence or runtime failure. Package gates under `-O` still launch asserting
checker paths. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs timing the five honest FULL-WORD audits gave median wall time **6.304 → 2.528 s (2.494×)**. Details are in
[`RESULT.json`](RESULT.json). Timing is host-descriptive and is not a
correctness gate. Every honest and seeded-fuzz outcome matches the pairwise
baseline fieldwise (elapsed `seconds` excluded).

## Why the integer rows are equivalent

Each row stores integer numerators over one positive shared denominator.
Scale and ADD updates keep the same zero-free sparse support and the same
`Fraction` endpoint equality checks. Structural gate copies never share nested
lists; non-JSON-scalar shapes fall back to `deepcopy`. Memoized `basis` and
shared immutable `Fraction` coefficient objects do not change values. See
`research/hpe-audit-fast-seed93/README.md`.

## Overlap and credit

Closest priors (different delivery):

- `research/hpe-audit-fast-seed93/` — opt-in integer rows; this is the production wiring.
- `research/frontier1042-lec-parallel/` / `research/layer-end-controls-parallel/` —
  parallel call scheduling without changing the audit kernel.
- `research/emitted-local-integer-production/` / [#2357](https://github.com/CrocSwap/integer-mult-bounds/pull/2357) —
  integer rows for `hpe_audit_local.py` (different object).
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.

Leave-alone tooling on other objects was not reopened.

Credit Wronskode, icekylinx, DreamingOfClouds, and the retained PR635 lineage.
Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should other vendored `hpe_audit_and_transport.py` copies adopt
   the same integer-row rewrite?
   **Why it matters:** Historical trees still pin pairwise-era digests.
   **First step:** Diff each copy against the production transform site.
   **Blocked by:** One-object stop rule.

2. **Question:** Should `make frontier1042-verify` document the production
   integer-row auditor as the default LEC kernel?
   **Why it matters:** Operators may still export `PR635_CODE` to pairwise trees.
   **First step:** Grep driver docs for `PR635_CODE` overrides.
   **Blocked by:** Maintainer doc preference.
