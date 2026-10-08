# Region-order selection inside the envelope-balanced compiler

The finite conditional witness gives **kappa = 10422378098629/200000000000000000 = 5.2111890493145e-05**,
**0.15200337% above the pinned envelope-balanced witness** (kappa = 5203279888519/100000000000000000
= 5.2032798885190e-05). Bit saving is 26057303141979/500000000000000000 = 5.2114606283958e-05,
against the pinned 13008876609597/250000000000000000. This is a draft candidate pending review.

The whole difference is a scheduling choice made before compilation. The pinned
witness fixes one region order per axis through
`balanced_split_graph.configuration(h)['schedule']` (axis 23 `cover-core`,
axis 25 `reverse-node`). This candidate keeps every other compiler setting
identical -- groups `[1,1,2]`, anchors, half-plane versus row coarse sums,
future-compatible completion, 0 versus 3 carry-exchange passes, exact next-use
profile costs, the coordinate-conjugated oracle pricing at h25 and the PR74
scalar-envelope reordering -- and replaces only the region order: axis 23 uses
the `node-asc` key and axis 25 the `width-node` key recorded in `scheduler.py`.
Both words are then relabelled by the recorded coordinate orders
`order-23.json` and `order-25.json`, exactly as the pinned witness does.

The compiler shipped here, `compiler.py`, is that composition: the pinned
`research/envelope-balanced/compiler.py` and `flag_engine.py` copied into this
directory, with the region order read from `scheduler.MODES` instead of
`balanced_split_graph.configuration(h)['schedule']`. Nothing in
`research/envelope-balanced/` is modified. The hook's `cover-core` key
generates the pinned axis-23 order, so the hook itself is not a second degree
of freedom; measured on the pinned source, `B82_MODE=cover-core` regenerates
`research/envelope-balanced/original-23.json.gz` byte for byte (verified with
the shared driver before this candidate's words were frozen).
`verify.py --regenerate` recompiles both axes through `compiler.py` and asserts
the words shipped here are byte-identical to its output. The only harness
difference from the pinned compiler is that the oracle subprocess is awaited
with a generous timeout instead of ten seconds: under parallel load the pinned
ten-second wait aborts a *completed* compilation at the shutdown step, before
the word is written. It cannot change the word, which is fully determined
before that step.

| Quantity | Pinned witness | This candidate |
|---|---:|---:|
| h23 auxiliary roles | 27075 | 27032 |
| h25 auxiliary roles | 35500 | 35431 |
| Physical width W | 133289600 | 133068501 |
| Total recursive rank | 76639673100 | 76512541175 |
| Deficit | 1846900 | 1846900 |
| Bit saving (1e-18 grid) | 5.2035506438388e-05 | 5.2114606283958e-05 |
| kappa (1e-18 grid) | 5.2032798885190e-05 | 5.2111890493145e-05 |

The candidate has *fewer* auxiliary roles and a *smaller* physical width than
the pinned witness, so the gain is not a width effect. It comes from the shape
of the child-multiplicity profile: the region order changes which rank-one
blocks the profiler extracts from the same physical path, and the moment
inequality

    sum_t count_t (t/m)^(1-s) / W < 1

is decided by that profile, not by W alone. A relabelled axis whose role count
and width are unchanged can move kappa by roughly 1e-7 in either direction, so
the two orders above were selected by scoring recompiled axes against the
unchanged PR65 moment and assembly arithmetic, not by any change to it.

## What is verified

`verify.py` replays both shipped words (XOR word, dirty basis, frame
incidence), rebuilds the transition and fixed-basis profile receipts, and
recomputes the profile of each axis exactly, asserting the shipped
`profiles-23.json` and `profiles-25.json`. It then rebuilds the complete
child-multiplicity profile, the 1e-18 grid saving by the inherited rational
binary search, both moment enclosures, the independent log-enclosure audit
bound, the fixed-width bridge and the balanced assembly. It asserts all 47
strict inequalities and seven margins, that the next grid value of kappa is
rejected, that the independent bounds separate (upper below one for the
accepted saving, lower above one for the next), and that the candidate kappa
strictly exceeds the pinned kappa. As a grid-robustness control it also
re-derives kappa after flooring the saving to the coarser 1e-11 grid and
requires it still to exceed the pinned kappa.

    python3 verify.py --record     # regenerate certificate.json
    python3 verify.py              # replay and compare against the record
    python3 verify.py --regenerate # also recompile both words and compare bytes
    python3 -m unittest test_controls -v   # coordinate, word, schedule and bridge controls

The recorded `--regenerate` run is in `regen.log`: it recompiles axis 23 with
region order `node-asc` and axis 25 with `width-node` through `compiler.py`,
reports the role counts 27032 and 35431, and asserts both regenerated words are
byte-identical to the shipped ones before rerunning every arithmetic check
above. `test_controls.py` adds the negative controls: a duplicated coordinate,
an inconsistent mapping, unrelabelled source values or outputs, a missing
terminal synthesis and an aliased terminal are all rejected; an unknown region
order and a region order that breaks the topological or carrier constraints are
rejected; a stale bridge field is rejected; and the recorded next kappa grid
value is rejected while the recorded value is accepted.

Region-order selection and verification with Codebuff (Buffy) assistance;
inherited sources, notices and licenses are unchanged.

## Selection of the region orders

Region orders were scored by recompiling axes and evaluating the unchanged
exact arithmetic: 12 h23 orders (9 keys plus 4 hash-seeded random orders, with
`cover-core` reproducing the pinned word exactly) crossed with 10 h25 orders,
120 pairs in total, at 8-20 minutes of compilation per axis. The best pair is
`node-asc` at h23 with `width-node` at h25; at h25 the `node-asc` and
`width-node` keys happened to produce the same order. Coordinate relabelling
was also searched separately: more than 500 hill-climbing and random relabel
draws on the pinned words never beat the identity relabel, so the coordinate
orders `order-23.json` and `order-25.json` are retained unchanged.

## Scope and limits

The arithmetic downstream of the words is inherited unchanged: the PR48
rational logarithm enclosures, the PR65 moment, assembly and audit code, the
fixed-tape transfer, the routing and recovery interfaces, the prime selection
and the all-size compiler argument. The region-order substitution is confined
to the scheduling hook documented in `scheduler.py`; it reorders independent
regions under the same topological and carrier-candidate assertions, so an
order that would break the schedule raises instead of compiling. It changes
only heuristic selection among legal choices. No global optimality over region
orders, and no measured practical speedup, is claimed.
