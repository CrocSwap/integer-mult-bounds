# Independent H6 budget and Walsh audit

The pinned H6 invoice reproduces, and its Walsh identity holds for every
pair of the 30,960 ports. Two errors in the block summary are corrected
below. These results do not yet supply a paid compensation
circuit. The next construction question is a legal loading, scattering and
dirty-restoration schedule, followed by an invoice of its actual frame paths.

This audit uses CrocSwap base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
and DreamingOfClouds's H6 package at
`b496aed769dd724cd1ff6b921cade626562be27b`, linked from
[discussion 1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167).
The imported predecessor package and PR606 inputs are preserved unchanged.
There is no new supplier or exponent claim.

The independently certified largest integer helper counts are:

| Comparison target | 3 stages | 5 stages | 7 stages |
| --- | ---: | ---: | ---: |
| Historical PR890, either quoted form | 80,558 | 89,683 | 80,753 |
| Selected PR1094, κ = 0.001672660197076918 | 79,880 | 88,765 | 79,778 |
| Pinned pending PR1424 title | 79,617 | 88,409 | 79,399 |

These are limits in the nominal H6 invoice: data path `[16]`, ordinary
helper path `[1,7,8,1]`, width histogram `{17:256,15:560}` and no virtual
entrances. The independent oracle builds the rank masses and bounds logs
and exponentials with rational series. It proves strict pass/fail at each
adjacent integer and monotonicity for this fixed invoice. Source float and
exact comparison modes agree. The selected record is a numerical comparison
only; its full supplier was not replayed. PR1424's larger title remains a
pending parent-admission claim in the pinned maintainer review.

Charging the proposed PR606 encoders reduces the remaining compensation
budget. At five stages, for the same helper path:

| Conditional baseline | Encoder roles already charged | Additional helpers versus selected PR1094 |
| --- | ---: | ---: |
| H6 headline invoice | 0 | 88,765 |
| PR606 conservative encoder, data `[1,15]` | 44,976 | 41,810 |
| PR606 full-center fallback, source `[16]`, target `[1,7,8]` | 816 | 66,313 |

These are necessary arithmetic screens of proposed paths, including their
bank stock and padding. They do not admit the encoder or a compensation DAG.
Extra private descents, altered chronology and other omitted work need an
additional bill. The ratio **1.538281** is correctly reproduced from the
zero-helper COSTS screens. Its E8 reference relaxes one idle rank from eight
to nine; it is not a ratio of fully paid banked constructions.

The exact structural check covers **958,521,600 ordered pairs**, establishes
the binary rank-16 alternating form using a unimodular E8 basis, and
reproduces the saved port-array hash. It finds 14,670 Walsh labels with
multiplicities two or eight, 480,337,920 compensation support entries, and
3,363,840 exceptional `|t|=3` pairs (0.70030698% of that support). For
`T = (P/2)(P/2)^T`, the identity is

`I − K = (T ∘ B)/16 − sign(t) [|t|=3]/2`.

Substituting `B = (J − W)/2` gives Walsh coefficient `1/32`. The full
65,536-dimensional Walsh matrix is normalized by 256; restriction to the
duplicated port labels does not preserve that orthogonality. Binary rank,
real matrix rank, transform size and physical helper count are separate
quantities.

The block audit found two errors in the predecessor's structural summary:
the canonical root-pair domain has **14,280 ordered off-diagonal blocks**,
plus 120 diagonal blocks, rather than 28,560 off-diagonal blocks; and
off-diagonal compensation blocks are **−f(s+S)**. The six-term polynomial
Kronecker identity for K survives with the correct canonical restriction.
These corrections do not alter the checked Walsh identity or invoice
thresholds. The separate [spectral check](spectral/README.md) reproduces
kernel rank 816 and real compensation rank 30,960 under the retained
moment/feature decomposition, with exact finite witnesses and trace checks.

An exact frame experiment identifies a restricted obstruction: each
isolated character decoder column has a coordinate support spanning all
17 address dimensions. Its common target frame is therefore zero. A final
Walsh output bucket behaves differently: a positive control has common
target frame of dimension 16. This excludes treating isolated character
columns as cheaply scattered aggregates; it does not exclude shared Walsh
transforms, cancellation between channels or low-frame routing.

The missing construction must restore every arbitrary helper dirt column,
respect common-frame additions and target chronology, work in both required
orientations, and charge loading, cleanup, repeated lane use, private
descents and spectators. A scalar identity and a favorable helper allowance
do not prove these clauses.

A [finite lifecycle probe](lifecycle/README.md) supplies an explicit
one-helper word for the actual compensation submatrix
`[−1,1;1,−1]/16` on sources 0,3 and targets 287,288. It has local transition
mass 81 and exact dirty scalar replay in both orientations, with controls for omitted cleanup,
uncompensated dirt and illegal helper reuse. It is a local example; its
transition profile is not a complete controller invoice or compiler replay.

For details, see [invoice](invoice/README.md), [Walsh](walsh/README.md), and
[helper admission](helper/README.md). Independent [charged accounting
review](review/charged-review.md) and [provenance](provenance/README.md)
retain their scopes. `TASK.json`, `SOURCES.json`, the replay
receipts and `VALIDATION.json` retain exact premises, pins and check scope.
The selected-record binding check passed separately. Full cold supplier
replay, hosted CI, a helper-loading theorem and the full multiplication
theorem are outside this audit.

## Reproduce

From this checkout, with Python and NumPy:

```sh
python3 -I -O -B research/h6-independent-audit/verify.py
make selected-record-check
```

The package checker uses explicit exceptions so its checks remain active
under `-O`. It writes only audit receipts. Frozen sources remain unchanged.

## Open next questions

1. Emit a small compensation subword on actual orthogonal source/target
   incidences and verify its complete dirty scalar map and common-frame
   chronology. This tests the loading/restoration gap before a large search.
2. Determine whether address-bucket routing or shared low-frame channels can
   avoid the isolated-character descent bill. A concrete legal word is
   needed; the support witness is not a general impossibility theorem.
3. Reprice that word's actual paths against the encoder-inclusive budgets.
   Stop the chosen target if its optimistic fully charged invoice fails.

Credit: Dominik Scholz's PR606 for geometry, factors, banked accounting and
the retained source lineage; DreamingOfClouds for H6 and PR1590; Rohan Arun,
Jeremy Kothe and the selected/pending construction lineage. Andrey Mas's
[discussion 1635](https://github.com/CrocSwap/integer-mult-bounds/discussions/1635)
independently overlaps the fixed invoice audit; this package adds a separate
rational oracle, exhaustive structural checks and scoped frame evidence.
Prepared for Ross with OpenAI Codex and delegated specialist assistance.
Apache-2.0. This is computational and written research evidence, not
independent human peer review.
