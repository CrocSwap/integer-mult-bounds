# P112 kernel basis composed into the selected centre cut

**Exact three-block consumer binding; no selected-kappa improvement is claimed.**

## Result

The first three sorted P112 tetrads' unimodular output changes can be composed
into the actual `cut` stage of the selected gauge44 word. For each affected
block, the new consumer matrix is `S_new = U^{-T} S`, so for every port vector
`y` (including arbitrary dirty values),

```text
S_new^T (U y) = S^T y.
```

The center accumulator receives the same delta; this local identity does not
require a clean port workspace. The exact aggregate coefficient support and
one-add-per-nonzero cut screen change as follows:

| P112 tetrad | Old nonzero cut coefficients | New coefficients | Added |
|---|---:|---:|---:|
| `(0, 1, 2, 3)` | 8 | 19 | 11 |
| `(0, 1, 4, 5)` | 16 | 23 | 7 |
| `(0, 1, 6, 7)` | 16 | 24 | 8 |
| Full selected cut | 176 | 202 | 26 |

The new coefficients have denominators in `{1, 2, 4}`. They define an exact
rational additive cut. This does not establish native fixed-precision bounds,
instruction-order admission, supplier implementation, or cleanup/restoration.

## Budget sensitivity

For the first three blocks, the inherited rank-72 complex-side planning profile
has `{1:204, 2:44, 72:73, 56:1}`, centre charge 100 and unpaid average `31/28`.
At `a=3/997`, its moment is approximately `0.999371758109` and its complex-only
ideal ceiling is `0.005390681416`.

As a sensitivity only, adding 26 rank-1 units—one for each new nonzero cut
coefficient—raises the moment to `0.999414381264` and lowers the complex-only
ceiling to `0.005113645447`. The repository's recursive ceiling does not price
scalar cut additions, so this conversion is not an invoice or an asserted
upper bound on their cost. The rank-72 child profile is also only a relaxation.
No joint bit/complex supplier is admitted, and the selected kappa remains
`0.001672660197076918`.

## Obligation ledger and comparison

| Obligation | Status |
|---|---|
| Source binding of the selected P112 port labels and gauge44 centre cut | **Proved** in this finite verifier against pinned archive hashes |
| Three block matrices are unimodular and annihilate their four update directions | **Proved** over the integers |
| Immediate cut identity for arbitrary dirty port inputs | **Proved** over the rationals by `S_new^T U = S^T` |
| Exact support delta and aggregate additive-cut reconstruction | **Proved**; 176 to 202 nonzero coefficients |
| Scalar cost of the 26 added incidences | **Unknown**; no incidence-to-rank tariff is established |
| Chronological supplier admission, precision/magnitude limits, cleanup and restoration | **Unknown** |
| Concrete rank-72 complex supplier and complete bit-side invoice | **Unknown** |
| Selected frontier update | **Not claimed**; selected kappa is unchanged |

This differs from the related [gauge44 port-syndrome encoding](../gauge44-port-syndrome-encoding/README.md),
which uses 104 row shears to concentrate the centre signal into eight anchors
while leaving a residual consumer. Here each P112 tetrad's four update-kernel
rows change the provider's output basis, and the inverse-transpose is composed
into the selected immediate centre cut. Neither result supplies a full
chronological caller or a complete invoice.

The bounded next step is to bind this modified cut to an admitted transformed
supplier and replay its dirty endpoints, cleanup and magnitude bounds. Stop
before a larger construction search if those costs cannot fit the target.

## Sources and reproduction

The selected source archive, P112 basis witness, port binding, geometry and
ceiling engine are pinned in [SOURCES.json](SOURCES.json). The selected record
and task catalogue are provenance; the other listed files are live inputs.

From the repository root:

```sh
python3 scripts/research_package.py --package research/p112-tetrad-cut-consumer --check-only
python3.12 scripts/research_package.py --package research/p112-tetrad-cut-consumer
```

The verifier uses Python's standard library and exact `Fraction` arithmetic.
It does not replay the full native program.

## Open next questions

- Can the transformed supplier outputs be placed at the actual cut while all
  dirty ports, centre accumulators, cleanup state and magnitude guards remain
  valid? The next test needs a concrete changed supplier and full chronology.
- Can the native scalar charge for 26 added cut coefficients, plus a concrete
  complex supplier and admitted bit-side profile, leave the joint target above
  `0.003`? The current rank-72 comparison is only a sensitivity screen.

## Credit

Prepared by Gonzalo Mier with substantial OpenAI Codex assistance. The local
P112 tetrad construction retains the predecessor attribution in its source
package; the selected provider and archived sources retain their original
credits. New work is Apache-2.0.
