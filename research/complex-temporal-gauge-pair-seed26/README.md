# Exact composition of the L248 and L253 temporal gauges

**Finite complex-word construction and fixed-pair optimality result; no new κ.**
This package composes two individually verified time-varying gauges on the
selected PR1094 complex word, then checks the merged source word, all formal
columns and its complete scalar invoice in both orientations.

## Result

The frozen baseline is the simultaneous constant-gauge word of PR1263, pinned
at `5fbaca13028846bddbb001e8e07addc2ab8e5816`. PR1353 supplies a changing
absolute gauge for L248; its 71 incident ADDs save 90 complex primitives per
orientation over that baseline. PR1350 supplies a time-varying offset on top
of L253's retained static gauge; its 96 incident ADDs save 182 complex
primitives per orientation.

The schedule indices use different event streams: PR1353 indexes the original
word, while PR1350 indexes PR1263's word after static entry scales have been
inserted. The verifier maps both schedules onto the ordered source ADD stream
and checks that their incidence sets are disjoint in each orientation. Each
ADD is therefore priced by at most one changing coordinate. The two exact
one-coordinate objectives separate, so their pinned global minima give the
global minimum for this fixed two-coordinate class with all other PR1263
gauges frozen. This is not a search over other pairs or over the full gauge
vector.

The composed word costs **135,730 forward** and **135,746 backward** complex
primitives, 272 fewer per orientation than PR1263's 136,002 / 136,018. It
replays all 712 formal columns, restores all 480 dirty helpers and erases all
eight private center columns. The paid recursive profile stays
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`; the inherited local 192-bit charge
still passes. Relative to the original PR1094 scalar word, the total saving is
13,272 complex primitives per orientation. The selected κ remains
`836330098538459/500000000000000000` (`0.001672660197076918`).

## Reproduce

From the repository root, with Python 3.11 or later and only the standard
library:

```sh
python3 -I -O -B research/complex-temporal-gauge-pair-seed26/verify.py
python3 -I -O -B research/complex-temporal-gauge-pair-seed26/test_package.py
python3 scripts/research_package.py --package research/complex-temporal-gauge-pair-seed26 --check-only
```

The verifier prints:

```text
PASS_COMPLEX_L248_L253_TEMPORAL_COMPOSITION
forward shared_add_ids 0 complex_primitives 135730 columns 712 no_new_kappa
backward shared_add_ids 0 complex_primitives 135746 columns 712 no_new_kappa
```

The repository's registered Python 3.12 replay is declared in `VERIFY.json`.
The local direct replay and tests were run on CPython 3.14.7. `SOURCES.json`
pins the base inputs, predecessor commits, copied schedule receipts and the
minimal PR1263/PR1161 source needed to rebuild the event word. The optimized
PR1350 and PR1353 verifiers were also run at their pinned heads before
composition; their exact one-coordinate optimality arguments remain inherited
from those packages.

The four mutation controls reject a shared ADD ID, duplicate schedule entry,
omitted incident ADD, and incorrect combined invoice.

## Scope and limits

This is a composed scalar word and an exact global optimum only for the fixed
pair (L248,L253), conditional on the pinned one-coordinate DP certificates in
PR1353 and PR1350. Those PRs are open research submissions, not accepted
selected-supplier results. This package does not independently re-prove their
one-coordinate DP domains, does not change the selected record, and claims no
new κ. Native supplier emission, whole-call hosting/controller admission,
precision/tape transfer beyond the inherited local check, all-size compilation,
analytic transfer, and the multiplication theorem remain open.

The task card records three candidates and why this pair was selected. The
closest open result PR1350 specifically defers the neighboring L253/L254
temporal pair; this package instead composes the distinct L248/L253 schedules.
The final overlap refresh also found PR1369 (head
`f28e1c460cd910886f9b06835abd6b1c96d2992f`), which scans single-coordinate
temporal schedules on the 19 zero-static helpers and explicitly does not
compose schedules. This package instead certifies a fixed pair of nonzero-static
coordinates and its exact combined invoice; the scope and evidence are
distinct.

## Open next questions

**Does the same separability certificate extend to a third time-varying gauge?**
That would matter because a new pairwise composition can reduce scalar cost
without changing the paid profile, while additional coordinates may interact
through shared ADDs. The first step is to choose one pinned third-coordinate
schedule and compare its canonical source ADD set with the L248/L253 union.
The blocker is that any shared ADD couples the exact gate-price objective and
needs a separately priced joint schedule; no third coordinate is searched
here.

## Credit and disclosure

Credit Philipp (@mightyOil) and the PR1263 authors for the frozen 218-helper
word; credit the retained PR1161 scalar replay and PR696 lowerer lineage; and
credit PR1350 and PR1353 for the individually optimized L253 and L248 schedules
composed here. Original source notices are retained in the vendored files.
Prepared by Cinna Davis (@1337isnot1337) with substantial OpenAI Codex
assistance in task triage, exact cost reasoning, implementation, verification
and writing. No independent human review is claimed. New material is
Apache-2.0.
