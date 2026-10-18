# P112 kernel bases composed into the selected centre cut

**Exact fourteen-block consumer binding; no selected-kappa improvement is claimed.**

## Result

For each of the selected provider's fourteen P112 tetrads, the source-bound
unimodular output change `U` has four rows in the left kernel of that block's
rank-four update. Its output basis can be composed into the actual selected
gauge44 centre-cut matrix `S` with

```text
S_new = U^{-T} S
S_new^T (U y) = S^T y
```

The identity holds over exact rationals for every port vector `y`, including
arbitrary dirty values. Rebuilding the aggregate additive cut gives this
support profile:

| Tetrad | Old coefficients | New coefficients | Delta |
|---|---:|---:|---:|
| `(0, 1, 2, 3)` | 8 | 19 | +11 |
| `(0, 1, 4, 5)` | 16 | 23 | +7 |
| `(0, 1, 6, 7)` | 16 | 24 | +8 |
| `(0, 2, 4, 6)` | 8 | 19 | +11 |
| `(0, 2, 5, 7)` | 8 | 21 | +13 |
| `(0, 3, 4, 7)` | 16 | 16 | 0 |
| `(0, 3, 5, 6)` | 16 | 12 | -4 |
| `(1, 2, 4, 7)` | 16 | 23 | +7 |
| `(1, 2, 5, 6)` | 16 | 23 | +7 |
| `(1, 3, 4, 6)` | 8 | 21 | +13 |
| `(1, 3, 5, 7)` | 8 | 19 | +11 |
| `(2, 3, 4, 5)` | 16 | 23 | +7 |
| `(2, 3, 6, 7)` | 16 | 24 | +8 |
| `(4, 5, 6, 7)` | 8 | 19 | +11 |
| **Full selected cut** | **176** | **286** | **+110** |

The first three blocks—the first count that clears the inherited rank-72
complex target screen—change 176 coefficients to 202 (+26). Across all fourteen,
the added count is +110. Coefficient denominators remain in `{1, 2, 4}`. These
are exact aggregate rational maps. The one-add-per-nonzero reconstruction does
not certify native precision bounds, stage chronology, supplier implementation,
or cleanup/restoration.

## Target sensitivity

The following uses the inherited rank-72 complex relaxation, `a=3/997`,
`centre=112-4k`, and unpaid average `1+k/28`. As a sensitivity only, it adds
one rank-1 unit per **net new cut coefficient** to the rank-1 profile:

| Fused tetrads `k` | Added incidences | Moment upper | Complex-only ideal κ ceiling |
|---:|---:|---:|---:|
| 3 | 26 | 0.999414381264 | 0.005113645447 |
| 5 | 50 | 0.997363756140 | 0.012033839741 |
| 9 | 60 | 0.993200210512 | 0.025620878335 |
| 14 | 110 | 0.988057254181 | 0.038865401047 |

The fourteen-block figure is the largest ceiling in this finite sensitivity
census. It is not an achieved κ: the scalar cut has no validated conversion to
recursive rank-one charges, the rank-72 children are an ideal relaxation, and
the complete bit/complex suppliers and invoices remain unproved. The previous
bit rank-63 relaxation is unchanged. The selected kappa remains
`0.001672660197076918`.

## Obligation ledger and comparison

| Obligation | Status |
|---|---|
| Source binding of selected P112 port labels and all fourteen gauge44 centre-cut blocks | **Proved** against pinned archive hashes |
| Four integer update-kernel rows and unimodular output transform per block | **Proved** over the integers |
| Immediate cut identity on every transformed block and arbitrary dirty port inputs | **Proved** over the rationals by `S_new^T U = S^T` |
| Aggregate cut support, blockwise incidence deltas, and exact additive reconstruction | **Proved**; 176 to 286 coefficients |
| Scalar cost of the 110 net new incidences | **Unknown**; no incidence-to-rank tariff is established |
| Chronological supplier admission, precision/magnitude limits, cleanup and restoration | **Unknown** |
| Concrete rank-72 complex supplier and complete bit-side invoice | **Unknown** |
| Selected frontier update | **Not claimed**; selected kappa is unchanged |

This differs from the related [gauge44 port-syndrome encoding](../gauge44-port-syndrome-encoding/README.md),
which uses 104 row shears to concentrate the centre signal into eight anchors
while leaving a residual consumer. Here each P112 tetrad's four update-kernel
rows change the provider's output basis, and the inverse-transpose is composed
into the actual selected immediate centre cut. Neither result supplies a full
chronological caller or a complete invoice.

The next decision is whether a concrete transformed supplier and its scalar,
dirty-state, cleanup, and bit-side costs can fit the target. Stop construction
expansion if those obligations have no favorable bound.

## Sources and reproduction

The selected source archive, P112 basis witness, port binding, geometry, bit
price dependency and ceiling engine are pinned in [SOURCES.json](SOURCES.json).
The selected record and task catalogue are provenance; the other listed files
are live inputs.

From the repository root:

```sh
python3 scripts/research_package.py --package research/p112-tetrad-cut-consumer --check-only
python3.12 scripts/research_package.py --package research/p112-tetrad-cut-consumer
```

The verifier uses Python's standard library and exact `Fraction` arithmetic. It
does not replay the full native program.

## Open next questions

- Can the transformed supplier outputs reach this cut in the canonical
  chronology while preserving dirty ports and centre accumulators through
  cleanup and compensation? Bind a concrete supplier and check the full
  affected stage sequence and magnitude bounds.
- What is the native scalar cost of the 110 net new cut coefficients? Replace
  the unit-incidence sensitivity with an exact tariff, then combine a concrete
  complex supplier with an admitted bit-side profile.
- Do the four invariant combinations per tetrad correspond to unpaid recursive
  coordinates across all eight roles and 896 complex families? Derive the
  ownership and endpoint map for one block before scaling.

## Credit

Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. The local
P112 tetrad construction retains the predecessor attribution in its source
package; the selected provider and archived sources retain their original
credits. New work is Apache-2.0.
