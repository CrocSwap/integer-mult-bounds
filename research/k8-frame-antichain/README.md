# A sharp register bound for the k8 factory interface

This package proves a scoped negative result. The retained k8 factory
interface needs at least **224 helper registers in addition to 112 source
registers**. The bound permits arbitrary rational scalar gates, new gate
orders, cancellation, undo and redo, and operations between different
blocks. It does not fix the operation multiset.

The interface has 144 face values and 48 leaver values. Their 168 distinct
binary support frames form an antichain. The proof requires two registers
at the first formation of each frame. Monotone frames prevent one register
from serving two different frames in this antichain. The 14 existing
24-register packet factories attain the bound for this interface.

This is **not** a lower bound of 480 on the complete word. It does not
require 224 dedicated factory helpers if another stage lends its helpers.
It does not bound the paid profile at a fixed helper count. A changed value
or frame interface, target borrowing, and private query descents can leave
the theorem's class. There is no new supplier or kappa claim.

The package also checks two limits on target borrowing. None of the 112
target end frames contains any of the eight complete cold-block frames.
None contains any of the eight complete center-query frames. These are
frame obstructions even when the scalar payload has been restored. The
32 cold helpers do have exact scalar restoration at the end of A, after
their low cleanup tails; the check includes all 704 arbitrary input
columns. That scalar fact does not remove the frame obstruction.

For a disjoint two-cap split of one cold block, six carriers are necessary
in six of the seven possible partitions. The last partition needs eight.
Four different caps can support four independent face carriers instead.
An exact witness for that escape is included. It is not a native circuit:
its formation, target dirt, source access, frame path, and restoration
cost still need a construction. No current admission guard was changed.

Run from a clean checkout, with Python 3.10 or newer and the standard library:

```sh
python3 -I -O -B research/k8-frame-antichain/verify.py
```

Expected output:

```text
PASS_K8_FRAME_ANTICHAIN demands=168 helpers=224 cold_caps=896 center_caps=896 split_blocks=8 controls=5
```

The command reads only this package. It replays the exact source rows,
checks the complete finite frame data, checks the cold scalar tails,
recomputes the split ranks, and compares the result with `CERTIFICATE.json`.
Five controls check distinct failure modes. Assertions are not used for
admission, so the same command works with `-O`.

An independent implementation replays one input column at a time. It
uses explicit binary span sets and integer determinants for the split
ranks. It does not import the primary checker:

```sh
python3 -I -O -B research/k8-frame-antichain/independent.py
```

`PROOF.md` gives the theorem, the free choices in its class, and a limited
cost screen for descent between local formation jobs. `SOURCES.json` pins
the inputs and predecessor commits. `RESEARCH-NOTES.md` records the failed
construction attempts and the stopping decision. `BASELINE-REPLAY.md`
records the separate native rebuild. That rebuild is evidence for the
input word; the package check is not a new full supplier audit.

The experiment base is
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. Its selected result was PR942,
with kappa `1661960547713947/10^18`. During this work, main advanced to
`ba82555c64e1879e4b7decce28186f208fcb8262` and selected PR1042, with kappa
`1672188119205421/10^18`. Both statements are dated source context.
This package keeps the PR1074 seven-slot word fixed. The new endpoint
variant in PR1107 and the concurrent owner-packing work are outside this
fixed-interface result. The final overlap check reached PR1128. PR1124
adds an eighth slot and new endpoints. PR1126 proves a distinct ADD-count
bound for the cell cores in a positive-lift alphabet; it does not study
this arbitrary-linear factory register problem.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
The license is Apache-2.0. See `NOTICE.md` for predecessor credit.
