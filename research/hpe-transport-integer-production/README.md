# Production integer-row HPE transport audit

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/complex-k492-owner-repair/code/hpe_audit_and_transport.py` still stored every
scalar row as a dictionary of `Fraction` values. Wronskode’s opt-in adapter
`research/hpe-audit-fast-seed93/` (incorporated
[#1137](https://github.com/CrocSwap/integer-mult-bounds/pull/1137)) already
proved shared-denominator sparse integer rows with identical complete transport
receipts. This package wires that equivalent rewrite into the **production**
k492 transport auditor used by changed-word tooling.

SELECTED-SOURCE-bound
`research/complex-sw4-frame8/local/hpe_audit_and_transport.py` copies are intentionally
left pairwise so the selected inventory stays untouched. Dependent packages that
previously live-pinned the k492 path retarget **pin inventory and execution** to that
sw4 transport (including coded-helper / global-screen / factory5 loaders).

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/hpe-transport-integer-production/verify.py
python3.12 -I -O -B research/hpe-transport-integer-production/verify.py
python3.12 -B scripts/research_package.py --package research/hpe-transport-integer-production
taskset -c 0 python3.12 -I -B research/hpe-transport-integer-production/benchmark.py --rounds 5 --write-result
```

Expected:

```text
PASS_HPE_TRANSPORT_INTEGER_PRODUCTION assertions=26 honest=5 fuzz=20 corruption=… certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/hpe-transport-integer-production outcome=completed
PASS_IDENTICAL_HPE_TRANSPORT_INTEGER_PRODUCTION_RECEIPTS
```

Default verify is read-only. Temp-copy ADD-drop foil rejects via audit failure
or receipt divergence. Package gates under `-O` still load checkers with
`compile(..., optimize=0)`. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated historical-checker change.

## Result

On Linux / CPython 3.12.3 with `taskset -c 0`, five alternating fresh-process
pairs over the five honest frontier1042 layer-end words gave median wall time
**6.452 → 2.816 s (2.29×)**. Details are in
[`RESULT.json`](RESULT.json). Timing is host-descriptive and is not a
correctness gate. Every honest and fuzz outcome matches the pairwise baseline.

## Why the integer rows are equivalent

Each row stores integer numerators over a shared positive denominator instead of
a dict of `Fraction`s. Scale and ADD updates rewrite that representation exactly;
zero entries are omitted just as in the original dictionaries. Gate copies are
structural list copies with `deepcopy` fallback for non-JSON-scalar shapes.
`rows_equal` admits the integer form against the Fraction oracle used by the
cone / compensation checks. See `research/hpe-audit-fast-seed93/`.

## Overlap and credit

Closest priors (different delivery):

- `research/hpe-audit-fast-seed93/` / [#1137](https://github.com/CrocSwap/integer-mult-bounds/pull/1137)
  — opt-in integer rows; this is the production wiring.
- [CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756)
  — identical-receipt tooling quality bar.
- [CrocSwap/integer-mult-bounds#2357](https://github.com/CrocSwap/integer-mult-bounds/pull/2357)
  — same production-promotion pattern for `hpe_audit_local.py` (different object).
- Open leave-alone tooling through [#2375](https://github.com/CrocSwap/integer-mult-bounds/pull/2375)
  (`frame_pair_solutions` and earlier production rewrites) was not reopened.

Credit Wronskode, icekylinx, and the retained transport-auditor lineage. Prepared by
Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

## Open next questions

1. **Question:** Should the SELECTED-SOURCE-bound sw4 `hpe_audit_and_transport.py`
   copies adopt the same integer-row rewrite with a coordinated
   `SELECTED-SOURCE.json` digest refresh?
   **Why it matters:** Selected cold-chain layer-end controls still run the pairwise
   checker.
   **First step:** Enumerate SELECTED-SOURCE paths with sha256 `c9a05ff2…` and
   dependent VERIFY binders.
   **Blocked by:** Maintainer inventory-refresh preference.

2. **Question:** Should other byte-identical vendored `hpe_audit_and_transport.py`
   copies adopt the same rewrite?
   **Why it matters:** Historical trees still pin pairwise-era digests.
   **First step:** Diff each copy against the production transform site.
   **Blocked by:** One-object stop rule.
