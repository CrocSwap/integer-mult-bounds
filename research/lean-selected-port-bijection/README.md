# [Lean] Exact selected 1320-port labels and table-backed reindexing

This standalone Lean 4.21.0 package certifies a concrete interface of the retained selected construction at commit `3b6b66891c0ac888521cf591fe306c6286601d4f`.

## Completed claims

- `CurrentMain.CurrentComplexPortLabels.canonical_labels` proves that the ordered list `(List.range 1320).map inputMask` is exactly `PairedCubeSourceLabels.labels 11`.
- `CurrentMain.CurrentComplexPortBijection.toLabel` and `fromLabel` use the actual packaged `inputMask` and `inverseTable`. Both inverse laws are proved; the inverse is a table lookup, not a choice function.
- Whole-row gather/scatter and complete two-bank gather/scatter are inverse reindexings for arbitrary vertex and payload types. The entire arbitrary helper/spectator value is preserved.

The contribution is the exact selected accessor/table binding and its verified interface. Generic list identities, bijections and reindexing laws are not claimed as new mathematics. The package has 74 local modules and 1,183,511 bytes of Lean source. The smaller ordered-label entry point has 39 modules. The only external source import is the Lean distribution itself; no Mathlib checkout is required by the source import graph.

## Scope and source version

The proposed PR is additive to upstream commit `12a4934d15006e8c10f9b2264f13f8f341be802b`, but the packaged selected data remain pinned to `3b6b66891c0ac888521cf591fe306c6286601d4f`. Equality to any changed selected data at the newer base is not asserted.

This package proves a finite interface, not a physical invocation provider, a three-stage implementation, a dirty-helper/frame chart equation, a cost bound or a multiplication theorem. It contains neither the separately developed word-reversal primitive nor the separate coordinate/input-preparation work. No generic PR397 or PR430 chain/physical-provider proof is copied here.

## Explicit retained kappa and author check

The retained source's `certificates/selected-result.json` records

`kappa = 330942774629799 / 500000000000000000 = 0.000661885549259598`.

The rational/decimal agreement, selected certificate identity and source attribution have been checked against the pinned source, as have the precise three theorem claims above. The original selected-result source has SHA-256 `434456fb153101c31aa69fe5abb67a33f2cfbcb083dbae7ee0f8ff0872d2b20d` and Git blob `cc52499459c604cedbf6ddd0e6da5a4e5425a694`. See `PROVENANCE.json` and the preserved source excerpts in `evidence/`.

This is the selected source's conditional parameter, not an exponent theorem established by this port package. For comparison, upstream README at the proposed newer base records `90446448750933 / 125000000000000000 = 0.000723571590007464`; it is a separate target and is not substituted into these files.

The retained supplier is attributed as “Shared-edge supplier and completed entrance banks, 2026,” developed with OpenAI model assistance, under Apache-2.0. The preserved notice adds no personal byline.

## Reproduce

For the resource-audited reproduction, use Linux with `/proc` and the official Lean 4.21.0 distribution selected by `lean-toolchain`. The Lean sources are portable, but this POSIX runner and its virtual-memory review measurements are supported only on Linux. From this directory run:

```
python3 check.py --lean /path/to/lean-4.21.0/bin/lean --build-dir .build
```

The checker first validates every source hash, import and topological order in `MANIFEST.json`. It then builds the exact 74 sources into a fresh output directory, with no old objects or Mathlib paths. Each compiler process has a 60-second and 4-GiB hard bound. It stops for review above 45 seconds or 3.5 GiB. Logs, source/object hashes, queue/compile times and axiom output are recorded separately for every module. A stopped check is not reported as package completion. No package installation or network access is performed.

Historical source-matched checks for all 74 modules passed. The ordered-label and final bijection statements print only standard axioms (`propext` and, for the latter, `Quot.sound`). Historical receipts used an established library-path environment; the fresh isolated package replay is recorded separately when complete.

`MANIFEST.json` preserves the historical receipt hashes and exact source bytes. Build products and private workspace paths are excluded from the publication payload.
