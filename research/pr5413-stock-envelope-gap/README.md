# The selected PR5413 caller publishes no stock coefficient

**Missing-lemma result. No new κ.** The selected record is not edited.

The selected PR5413 caller publishes kappa 605457647/200000000000 and does not publish a parent-reserve or depth coefficient; its stated gain 1/200000000000 is compiler headroom over 605457646/200000000000.

## Scope and evidence

Chooser seed `412404f28272cbf9b9347e60215fd911` drew `adversarial-audit` on canonical main `1a3ced60b2f7a46bc70280a04f2eeb8ca027c700`. Suggestions 1 and 2 are not taken: `research/mixed-provider-admission` already maps the four-provider dispatch, and `research/f7-weight-parity-census-correction` already reconstructs `01021323`. This package is suggestion 3, `selected-stock-envelope`, scope **refined** to the caller promoted today.

The selected record names PR #5413 first, with κ = `605457647/200000000000` and previous κ = `15108879/5000000000`. The caller claims in `research/coupled-helper-neutral-completion/CLAIMS.json` carry the same five assumption ids (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`). Their candidate decimal is the selected kappa. Their comparison decimal is one gain below it, and the recorded gain is exactly `1/200000000000`, typed as compiler headroom with the raw signed profile unchanged.

Those claims have no stock, reserve, depth, envelope or `actual_stock_coefficient` field. The pinned literal invoice leaves `full_ordinary_budget` null. A forged claims object that stores the gain as `actual_stock_coefficient` is rejected. The older stock-margin chain still says `coefficient=unresolved` and reads `research/selected-bootstrap-stock-audit/RESULT.json`; it does not name `605457647` or PR5413. Its cutoff arithmetic is not rerun.

## What this does not establish

This does not search every file under the caller capsule. It binds the selected record, the caller claims, the literal invoice and the older stock-margin note. It does not derive a parent reserve, choose a coefficient, or run `make frontier5413-verify`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/pr5413-stock-envelope-gap/verify.py
python3.12 -B scripts/research_package.py --package research/pr5413-stock-envelope-gap
```

Expected first line: `PASS_PR5413_STOCK_ENVELOPE_GAP kappa=605457647/200000000000 gain=1/200000000000 coefficient=absent older_receipt=bootstrap`.

Pins are in [SOURCES.json](SOURCES.json).

## Open next questions

Which source object in the PR5413 caller, if any, is the parent reserve and depth coefficient of one named stage? These four pinned records do not contain it. The first step is to name that stage and its source table before treating a bootstrap cutoff as the selected envelope. No such table is identified here.

## Credit

Chris R / Clear1nsight, PR #5413, published the neutral caller and the compiler-headroom gain. The stock-margin chain and PR #2931 remain the bootstrap-receipt audits. Riquelme Soares (@hevlyo), with substantial AI assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
