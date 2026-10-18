# Global boundary-pair lower bound for the two-projection connector

**Exact finite-model result; no new kappa.** The earlier two-projection
connector fixed one valid pair of source-prefix boundaries for each output
mask and proved that this table has a shortest frame schedule using 10
full-row XORs. This package checks every possible choice of boundary pairs
for that same source word and readout model. The minimum remains exactly **10
full-row XORs**.

For the fixed ten-call source word `B0 B1 B0 B1 B2 B3 B4 B2 B4 B3`, sources
0, 1, 2 and 4 inject in helper direction `(1,0)` and source 3 injects in
direction `(1,1)`. Every nonzero five-bit mask must be read exactly twice,
using either the `(1,0)` or `(1,1)` projection. Paid frame changes are only
the two row shears already charged in the predecessor package. Among all
4,194,304 possible sets of boundary/projection demands, 848 cover all 31
outputs. An exact six-frame dynamic program prices every covering set;
38 attain 10 XORs and none uses fewer. The predecessor's certified schedule
is one of those minimizers.

The theorem is a scoped minimum for this fixed word, direction assignment,
pair-readout contract and generator set. It does not cover other source words,
other projections, other row operations, more helper rows or general
two-projection connectors. It counts row-XOR operations but assigns no
physical price to them. The local 180-child versus 182-child comparison in
the predecessor is therefore not an unconditional cost improvement: selected
supplier placement, helper hosting and the full row-XOR invoice remain open.

## Proof and replay

`PROOF.md` proves that same-projection prefix differences characterize paired
readouts, gives the complete node-set enumeration, and explains why the
six-frame min-plus dynamic program is exact. The independent standard-library
checker reads the predecessor's certificate as an attainment control; it
does not import or call its implementation.

```sh
python3 -I -O -B research/two-projection-boundary-optimum/verify.py
python3 scripts/research_package.py --package research/two-projection-boundary-optimum
```

Expected direct replay:

```text
PASS_TWO_PROJECTION_BOUNDARY_OPTIMUM demand_sets=4194304 covering=848 node_hist=... xor_hist=... minimum_xors=10 minimizers=38 current_xors=10
```

The complete histograms and source pins are in `RESULT.json` and
`SOURCES.json`. `VERIFY.json` registers the exact replay used by the repository.

## Research scope

This is a changed-scope follow-up to the catalog's `connector-alphabet-change`
card. The two-row connector extension was already completed in
[`two-projection-connector-seed51a5`](../two-projection-connector-seed51a5/README.md);
its explicit next question asks whether another valid boundary table can
reduce the 10-XOR schedule. This package answers that question for the pinned
ten-event word and its two projections. The refreshed overlap snapshot found
no open PR and no exact-term claim for the all-boundary optimization. It did
find the expired #1167 claim for the predecessor itself; #2221 and #2262 cover
different connector models. See `OVERLAP.json` for the query terms, distinction
and snapshot coverage.

## Remaining gap

The exact minimum of 10 rules out reducing the frame-XOR count by changing
only the boundary pairs for this fixed word. It does not establish a lower
bound across other source words or changed interfaces. More importantly, no
occurrence of this connector has been bound to the selected multiplier
supplier. A supplier-level claim still needs a literal source-bound place for
the second dirty row, legal frame changes and restoration, plus a complete
comparison of row-XOR, storage, precision and recursive-child costs.

## Credit

The two-projection construction, its source word, finite search and original
10-XOR witness remain credited to Cinna Davis with substantial OpenAI Codex
assistance in the predecessor package. This follow-up supplies the all-
boundary lower bound and its checker. It uses no selected-frontier change and
makes no literature-priority claim.

## Open next questions

- Does the 10-XOR minimum persist after varying the ten-event source word or
  which source uses direction `(1,1)`? Those paths enlarge the search beyond
  this theorem's fixed prefix tables. A next study should retain the exact
  paired-readout and two-shear model and screen each candidate with the same
  exact frame-cost recurrence. This package does not establish that larger
  search's result.
- Can a source-pinned selected-supplier boundary host the second arbitrary
  dirty row and frame changes for less than the two saved rank-one children?
  Only a complete literal placement and invoice can transfer this local
  operation-count result into the selected supplier. No such placement is
  identified here.
