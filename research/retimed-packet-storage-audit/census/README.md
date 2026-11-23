# Gaussian owner census supplement

The source-specific result is [OWNER-CENSUS.md](OWNER-CENSUS.md). It proves
an explicit per-context bound of 115,058 owned fields and the calendar cover
`sum_e count[e] * (Q*delay[e]+1)`. With the existing mass enclosure this gives
fewer than `2B` historical Gaussian slots in each positive native arena.
The proof keeps zeros, hidden graph fields, all simultaneous output copies,
both half-column subjobs and suspended parents in the count.

From the repository root, use the enclosing driver for a fresh offline
restoration and all author/review checks:

```sh
python3 -B research/retimed-packet-storage-audit/verify_supplements.py \
  --output /tmp/retimed-owner-byte-results
```

To use a runtime already restored by the packet package's retained bootstrap,
run `verify_census.py --runtime RESTORED_RUNTIME --output RESULT_DIRECTORY`
from this directory. That driver rejects any change in the eleven resolved
source modules used here. It expects `PASS_GAUSSIAN_OWNER_CENSUS` and writes
`RESULT.json` plus individual receipts in the chosen output directory.

`census_raw.py` executes the actual two-copy raw and adapted-cut control code,
abstracting payload operations by a proved one-replacement-field envelope.
It retains all 105,216 productive tokens and visits all 564,144 adapted cuts.
`census_primitives.py` checks the replacement envelope separately on actual
small tapes, including zero-valued owners. `census_schedule.py` runs the
actual calendar and decoder with explicit custody tokens, including real
interior loans, incomplete last groups and incomplete cycles.

The tests reject missing graph, zero and replacement retirement, plus an
inadmissible flattened delay table. They do not execute the astronomical
production calendar or verify a new all-size byte constant. The retained
integral enclosure is a named input to the final exponent consequence.
Ordinary role bytes, repair-tag sizes and private control data remain outside
this owner-count supplement.

`sources/` contains stable resolved source copies and pinned proof context.
`SOURCE-BINDINGS.json` gives their byte digests and the canonical graph/layout
digests. The large derived `graph.json` and `layout.json` are local inspection
artifacts; verification reconstructs and checks them from the pinned archive.
They need not be included when integrating this supplement into a repository.
