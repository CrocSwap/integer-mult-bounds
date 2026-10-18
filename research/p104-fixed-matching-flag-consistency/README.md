# PR3019's fixed P104 matching has a monotone relay obstruction

**Scoped negative result:** the exact 208-edge matching in Nick Petalas's
[PR3019](https://github.com/CrocSwap/integer-mult-bounds/pull/3019), commit
`44d12bdeb8ade4066645bd968bebd4756b06200a`, cannot deliver the required
correction shear `Y <- Y + (I-G/2)X` under its fixed X-only monotone
common-frame contract, with rational linear mixing and a data-independent
frame program. Requiring
only helper 91 to choose one nested flag already leaves at least 45 required
coefficients missing at Y40. The other 207 helpers retain the favorable
independent-contact relaxation.

The required added coefficient at `(Y40,X1)` is `1/2`; the relay contract forces
it to zero. This concerns the **added correction** `I-G/2`. The original
channel's existing `G/2` target response is not available as a source when Y
is unread.

This closes one fixed matching's contact-consistency handoff. Other matchings,
changed covers, extra lifetimes and changed source/target access remain open.
No new lifetime minimum, supplier admission, recursive-cost improvement or
kappa is claimed. PR3019 correctly describes its support test as necessary;
this result does not allege an error in that certificate.

## Why the relaxed paths do not compose

Only helpers 17 and 83 can write Y40. Outside source information must travel
`139 -> 91 -> 83` before that write. Receiving from 139 forces vector `113`
into helper 91's frame. A subsequent delivery to 83 requires its frame to lie
inside arrival plane B80, which excludes `113`. A nested flag cannot do both.
The late dimension-eight contact into 91 cannot feed its earlier exits.

[PROOF.md](PROOF.md) gives the complete local contact boundary, the arbitrary
independent dirty-input argument, exact correction coefficient and model limits.
[INDEPENDENT.json](INDEPENDENT.json) is reconstructed directly from raw frozen
JSON by a second implementation, without importing the predecessor or primary
checker and without using the interval-contact formula.

The primary checker also enumerates every full flag in the five-dimensional
quotient B8/A91:

| Relaxation | Passing choices | Missing required pairs |
| --- | ---: | ---: |
| PR3019's independent contacts | passes all 4,992 dependencies | 0 |
| One full flag for helper 91: 477 choices | 0 | 45 |
| One full flag for helper 91: 9,288 choices | 0 | 46 |

All 9,765 full flags are covered; [RESULT.json](RESULT.json) records both exact
support classes and representative bases. This finite exhaustive computation
corroborates the written finite-instance proof. Neither is a formal-kernel
proof or an all-parameter multiplication theorem. The independent proof needs
only the small contact boundary and separating vector, not the flag census.

## Connection to the recursive cost

The changed interface was motivated by 208 unit-step helper flags and an
inherited favorable channel/transport/ideal-idle budget. All 1,872 helper
transports remain charged. PR2920's reported screen is about `0.99889624` at
its selected-saving input, before unknown native ADD, chronology, owner,
routing, restoration, precision, tape and consumer costs. This package does
not recertify that screen or set unknown charges to zero. It rejects this
exact attempted realization before further scalar/native investment.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/p104-fixed-matching-flag-consistency
```

Direct optimized checks work from a source export without Git or network:

```sh
python3.14 -I -O -Werror -B research/p104-fixed-matching-flag-consistency/verify.py
python3.14 -I -O -Werror -B research/p104-fixed-matching-flag-consistency/independent.py
python3.14 -I -O -Werror -B research/p104-fixed-matching-flag-consistency/test_verify.py
```

Copy the three external JSON inputs at their declared repository-relative
paths as well as this package. `--emit` prints either regenerated receipt to
stdout. Neither checker writes artifacts during replay. Explicit acceptance
checks remain enabled with `-O`. The registered launcher binds the originating
catalogue and selected-record provenance; each checker authenticates all three
input files and the exported PR3019 witness before processing them.

The primary's bitmap interval/contact and quotient primitives are adapted
from Nick Petalas's credited PR3019/3013/2996 lineage. The second checker uses
literal point sets and subspace extension/deduplication. Both use the same
fixed input data and mathematical contract; they are internal AI-assisted
checks, not independent human review. Behavioral controls test the lost
nestedness, altered source/contact premises, malformed flags, source and
receipt corruption, actual CLIs and read-only Git-free export. Local check
receipts and hosted CI are separate evidence.

## Open next questions

A different explicit matching should first pass a joint relay-consistency test.
Reconstruct its endpoint intervals and inspect every source-to-target relay
for a departure space that cannot fit inside a later delivery boundary.
This can change the decision because complete paths in the independent-contact
graph do not make an executable program. This package does not search other
matchings. Any survivor must still implement coefficients chronologically,
restore arbitrary helper dirt and fit a complete physical/consumer bill.
[TASK.json](TASK.json) records the structured handoff and stopping rule.

## Sources, credit and license

Exact main/base pins, Git blobs, SHA256 values and the byte-identical PR3019
witness export are in [SOURCES.json](SOURCES.json). The canonical investigation
is [Discussion2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18981114).

Credit Nick Petalas/PR3019/3013/2996/2981/2920/2909/2896 for the fixed pairing,
endpoint covers and optimistic contact model. Credit Arham Tahir/PR2997 for
the complementary fixed-full-flag audit, Sudarsh Chaturvedi/PR2924 and Sagar
Thakrar for the lifetime-floor handoff, Hiroki Kumazaki/PR2889/2353,
ywz65/PR2614, Arham Tahir/PR2675/2682, Philippe Van Velzen, Rohan Arun/PR1972,
Chafik Boukhalfa/PR1991, Adam Gall/PR1940/2090, Jeremy Diviney/PR2113,
Josie Elliston/PR1071, Ali Romman/PR1125 and the retained geometry/native/compiler
contributors. These historical results retain their original premises.

New analysis and package by Ross Richardson with substantial OpenAI Codex
assistance, including internal frame-scheduling and observation-kernel
specialists. Apache-2.0. No independent human or formal-kernel review claimed.
Frozen predecessor packages and the selected frontier are unchanged.
