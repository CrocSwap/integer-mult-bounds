# Replay the current mixed-norm finite certificate

The main frontier release retains payload 2048. This supplemental checker proves the finite premises of the source-specific magnitude envelope, with 121 actual bits and 179 bits using local reserve 128. It does not run or certify a payload 256 release, reduce denominator charges, change the paid moment, or establish κ independently of the enclosing release.

Use Python 3.13 or later and the standard library. No additional packages, persistent service, network call or Lean compiler is needed for this supplemental check. Run it only against a completed fresh native cache and the literal allocation outputs. The checker reads all inherited inputs and writes only a fresh output directory.

## Inputs from the enclosing full pipeline

Supply these paths explicitly; none is tied to a particular drive:

- `--source`: immutable derived PR 2833 source with exactly 541 manifest entries plus `MANIFEST.json`. Its manifest SHA-256 must be `c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f`.
- `--native-root`: the completed native producer directory containing `NATIVE-RECEIPT.json` and `native-cache`. Both current providers must have completed all five stages. The complete cache inventories and canonical-provider bindings are authenticated. Fresh native computation belongs to the enclosing full replay; it is not replaced by this norm checker.
- `--plan`: the actual T372 rebound `PLAN.json`.
- `--parent`: its dedicated source-parent `GLOBAL-TEMPLATE.json.gz`, with the 32-event prototype controller. This is the source prototype, not the emitted hosted controller.
- `--owners`: the actual T372 `OWNERS.json.gz`. The checker streams all 1,365,984 records instead of loading them together.
- `--data-phases`: the enclosing replay's `DATA-PHASES.json`, whose hash must match the source parent's exact phase binding.

The emitted hosted controller and its all-operator, phase, window and full release audits remain required in the enclosing admission. This supplemental pre-emission checker independently certifies static source-chart and native-interface premises; it does not silently treat the source-parent prototype as the hosted output.

## Portable invocation

Run from this metric directory. Replace the example directory names with the enclosing replay's actual fresh outputs. The manifest output and checker output must not exist already.

```powershell
python -X utf8 -B prepare_metric_inputs.py `
  --source ../vendor/frontier-source `
  --native-root ../work/native `
  --plan ../work/rebound/PLAN.json `
  --parent ../work/parent-data/GLOBAL-TEMPLATE.json.gz `
  --owners ../work/owners/OWNERS.json.gz `
  --data-phases ../work/global/base/work/complex-nine-native/DATA-PHASES.json `
  --out ../work/metric-inputs.json

python -X utf8 -B mixed_fibre_certificate.py `
  --manifest ../work/metric-inputs.json `
  --out ../work/metric-check
```

The preparer computes a machine-local manifest and selects provider paths from the authenticated native receipt. Do not publish that generated manifest as portable evidence: it contains the local paths supplied by the caller. The selected `CURRENT-RESULT.json` has no local machine paths. Its source-manifest hash identifies the exact recorded run, whose original machine-local manifest is preserved in the research archive.

## Checks and controls

The checker authenticates all 541 source files, the completed native cache, selected primary preprint sources and every explicit input before and after computation. Imported predicates are compiled from the exact authenticated source bytes into fresh module namespaces; timestamp-valid stale bytecode is never loaded. A negative control supplies such stale bytecode and verifies that authenticated source wins.

Both orientations undergo exact free-warp arbitrary-dirty endpoint replay and private first-clear/terminal-zero checks. The fail-closed opcode inventory classifies all native scalar, monomial, child, wrapper, marker and zero-buffer events. Exact dyadic Horner recurrences reproduce the current local peaks. All owner roles are checked for fixed integer chart data, exact widths, orthogonal basis permutations, disjoint families and literal call order. Thirteen negative controls cover cover-mixing kernels, unknown numerical phases, singular charts, address-dependent descriptors, undercharged factors, incorrect roles, a cross-replica bridge, stale bytecode and forged dirty-helper response.

A PASS establishes the sufficient magnitude envelope stated in the two proof documents. It preserves the enclosing denominator, mass, C0, precision, bootstrap and complete admission obligations. It does not advertise a newly admitted payload.
