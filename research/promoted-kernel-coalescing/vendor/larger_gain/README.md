# Larger-gain research after PR564

The new direction is to create residual helpers of width seven, which can
share a rank-sixteen owner with a width-nine helper. The current width-eight
helpers cannot make that exact pair. Thirty-two coordinated entrance-frame
promotions per selected call create this option while preserving the scalar
program. This changes the available packing patterns, rather than extending
the already saturated width-five-to-four promotion family.

The frozen literal nomination uses 63 width-seven providers and nine ordinary
four-cold providers. Its complete profile has native rate
`b = 0.001602631813774414678548` and nominal grid value
`kappa = 0.001600067494703216`, about 0.4352% above PR564. Full global admission
passes: physical chronology and all sixteen owner mutations, the complete
finite invoice, both exact moment engines, all 47 outer constraints for each
model, and rejection of all 89 invalid assembly variants. The conservative
model also passes at `kappa = 0.001600067491919801`. See the
[frozen result and artifact bindings](global/width7/RESULT.json).

The separately completed four-cold fallback is already fully admitted at
`kappa = 0.001593675235313849`, a 0.03396% gain. See its
[result and artifact bindings](global/fourcold/RESULT.json) and the
[independent adapter review](geometry/FOUR-COLD-SEAM-REVIEW.md).

## Latest state and scope

Research ran in an isolated checkout based on PR564. Publication is based on
main and includes only this package; PR564 is an explicit external dependency. The
repository has an `origin` remote; its main branch and PRs through 566 were
fetched. The [state record](STATE.json) pins every inspected head:

- `origin/main`: `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`.
- [PR564](https://github.com/CrocSwap/integer-mult-bounds/pull/564):
  `c18417b02b80594b2ca1c8c21185d28befafc935`, numerical baseline
  `kappa = 0.001593134158181640`.
- [PR565](https://github.com/CrocSwap/integer-mult-bounds/pull/565) and
  [PR566](https://github.com/CrocSwap/integer-mult-bounds/pull/566) add formal
  compact counting and input preparation. PR566 reports a concrete six-tape
  composition with bound `22n+17`. These are not a higher kappa or a general
  worst-case constant-time indexing theorem.

The complete unchanged PR564 verifier was freshly run: all 36 stages passed,
including its providers, phases, physical owners, finite invoice, two moment
engines and outer assembly. Source hashes, receipts and the stage log are
retained in [baseline564](baseline564/BASELINE.json).

Every new numerical result here has the same conditional finite-construction
boundary as the inherited package. All-size compilation, common labels and
mutable bases, normalized residual realization, correlated whole-call
hosting, precision/tape and analytic transfer remain assumptions. No
unconditional multiplication theorem, complete Lean proof, or general O(1)
indexing theorem is claimed.

## What changed locally

Three additional exact suffix relations reduce three width-nine helpers to
width eight in each zero-, four- and eight-promotion provider. Their combined
paid change is `3 H1 + 6 H2 - 6 H3`. The relations were reconstructed for each
provider: copying the same insertion cuts blindly was invalid. The actual
words, all-column scalar checks, dirty-helper restoration, omitted-kernel
controls and phase recipes are retained under [providers](providers/README.md).

Next, 32 entrance-frame promotions create width-seven helpers. Their combined
paid change is `32 H1 + 160 H2 - 128 H3`. The fully checked eight-promotion
provider therefore has local profile

```text
H = {1:2352, 2:592, 3:328, 4:192, 5:56, 6:56, 8:8}
helper widths = {4:8, 5:48, 7:32, 8:128, 9:288}
```

All three versions passed 728 columns in both orientations, exact restoration,
native frames, eleven local negative controls, 3005 phase edges and 224
endpoint adapters. Their source-bound bundles are in
[providers/width7](providers/width7/).

The packing search must respect complete helper ownership. A width-count
solution initially failed literal expansion because it demanded incompatible
shared owners from the same invocation. Additional subset constraints excluded
that solution. The retained nominee checks actual invocation windows, whole
owners, distinct roles and disjoint prefixes.

## Exact bounds that keep the search focused

The strongest negative result is an exact dual certificate for the current
PR564 providers. Within its present capacities and live stock, no repacking,
provider remix or finite cloning can reach the next `10^-18` kappa grid point.
The proof enumerates every 4/5/8/9 pattern in capacities 8/16/32/48, relaxes
integrality and chronology, and checks the resulting 548 dual inequalities
with two independent rational engines. See
[the proof and scope](patterns/PROOF.md).

Additional width-five-to-four promotions are affine continuations of the
existing cost/inventory family. Forty more pass local checks but do not
improve the four-cold capacity ceiling. Width-seven promotions change that
conclusion by introducing new bin patterns. The exact upper bound for the
32-promotion family is approximately `0.001600564129863655`. Combining it
with forty more width-four promotions raises the relaxed upper bound only to
`0.001600616266460206`. Neither is an admitted result: these deliberately
ignore physical conflicts. All sixty available width-seven promotions also
passed local checks, but their additional cost yields no further relaxed gain.

The larger alphabet was also tested at five, seven, nine and eleven stages,
allowing arbitrary fractional provider mixtures, all mixed-width auxiliary
banks, and no chronology conflicts. Exact upper bounds are approximately:

| Stages | Dimension | Kappa upper bound |
| --- | ---: | ---: |
| 5 | 41 | 0.001395406 |
| 7 | 57 | 0.001577285 |
| 9 | 73 | 0.001600617 |
| 11 | 89 | 0.001554605 |

These are rounded upward for display. The nine-stage optimum uses no banks.
The other stage counts remain below PR564 even in this enlarged model.
The [stage proof, exact receipts and reproduction commands](geometry/README.md)
describe the padding and provider assumptions; these are not universal bounds
over every possible local construction.

## Where a materially larger gain could come from

The next useful target is the local packet factory, especially expensive
helper paths. An exact sensitivity experiment removes each candidate's actual
paid frame path and residual demand, with all other costs retained. Under the
optimistic assumption that a new word replaces that work for free, saving six
selected helper paths per call crosses a 1% target; saving 32 crosses 5%.
This identifies the cost budget a new construction must beat. It does not
show that the existing helpers are removable. See the measured paths and
adjacent exact threshold checks in [HELPER-TARGETS.md](geometry/HELPER-TARGETS.md).

The 5% target would also outgrow the currently composed PR543 bit supplier.
[PR555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) already reports
bit rate `0.001733052823330162099157`, enough headroom in principle; its
source-bound replay and new composition were not performed here.

Several structural shortcuts were checked and failed within explicit scopes:
lossless binary dimension reduction, hyperplane puncturing, seven-center
decoding with too few deletions, retaining 120 ports at the old center bill,
literal tensor lifts, direct clone-free ordinary packet reads, and a full
tetrahedron Walsh output basis with unchanged packets. The geometry and
provider notes retain exact receipts and explain what each test leaves open.
In particular, a joint packet refactorization, a sparse mixed output basis,
or joint reselection of entrance kernel/gauge bases remains a substantive
direction beyond the affine local promotions tried here.

## Verification and attribution

The full provider and global reproduction uses an explicit immutable PR564
source package. The output directory must be new:

```sh
python3 -B research/larger-gain/global/reproduce.py \
  --source /path/to/pinned-PR564/research/complex-allcold \
  --work /tmp/width7-reproduction
```

The exact capacity exclusions can be replayed without SciPy. Set the same
source package for the supplementary model screens:

```sh
GAIN_PR564_SOURCE=/path/to/pinned-PR564/research/complex-allcold \
  python3 -B research/larger-gain/patterns/verify_ceiling_controls.py
```

This checks every retained capacity dual and rejects deliberately corrupted
source pins, potentials, dimensions, rates and signs. The stage receipts have
their separate standard-library verifier. SciPy nominates solutions only;
exact rational checks establish the stated exclusions.

The new providers preserve their source credits and immutable input hashes.
Modified global adapters retain the complete invoice and all inherited
guards; the patch and source/adapted hashes are included. See [NOTICE](NOTICE).
Prepared with substantial OpenAI Codex assistance. The publication adds only
this research package; its PR564 dependency is external and pinned. No
upstream scientific package was modified.
