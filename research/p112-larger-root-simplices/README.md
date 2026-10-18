# Larger root simplices exclude three P112 weight shapes

For `b=6,7,8`, independent P112 pieces of weights bounded by `2,5^3,6^b`
cannot have code-intersection dimension at least `b`. This excludes one
named shape in each pinned TWOSIDE cell `(6,4),(7,4),(8,4)`.

The proof extends PR3164's six-vertex root-simplex argument to seven, eight
and nine vertices. Each coordinate meets at most `12,16,20` edge supports.
The three incidence contradictions have exact margins **9, 4 and 12**.
The original source's relevant survivor counts are `69,154,251`; this package
does not claim to close those entire cells.

[PROOF.md](PROOF.md) gives the characteristic-zero argument and its exact
hypotheses. [RESULT.json](RESULT.json) contains the replayed geometric
quantities, three literal simplex controls, original 24-cell survivor table,
three exclusion receipts and overlap audit. This is author-checked evidence,
not independent human or proof-kernel review. No full C5, `C(P112)>=64`,
decoder, supplier admission or new kappa is established. Selected frontier
files are unchanged.

## Reproduce

From the repository root, with Python 3.12+ and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p112-larger-root-simplices --check-only
python3.12 -B scripts/research_package.py --package research/p112-larger-root-simplices
```

The registered replay enumerates all 4,097,782 five-/six-flat kernels, checks
7,140 root planes and 960 simple reflections, reruns the original survivor
program and runs fifteen behavioral groups. It compares exact proof-relevant
JSON fields rather than timing or compressed-container bytes. Set `TMPDIR`
to an external session directory if your workspace policy requires it.
A direct replay writes nothing in the checkout:

```sh
python3.12 -W error -B research/p112-larger-root-simplices/verify.py
python3.12 -O -W error -B research/p112-larger-root-simplices/test_verify.py
```

`verify.py --output /NEW/EXTERNAL/RESULT.json` creates a fresh receipt and
refuses an existing path or an output inside the checkout. A Git-free export
needs only this package and its one declared data input. [CHECKS.json](CHECKS.json)
records the environment, checks and verification limits.

## Scope and source credit

Nick Petalas. Apache-2.0. The original reduction, TWOSIDE piece hypotheses,
weight filters and survivor program are DreamingOfClouds's PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d`, with the retained E8/P112 decoder
lineage. The root-simplex predecessor is Nick Petalas's PR3164 at
`857384079ab640a949fb7618b7909664d3e737e5`. Its geometry implementation and
proof are copied unchanged into `vendor/`; the new work is the larger-simplex
lemma, these three applications and their checks. The original notice and
license are retained. [SOURCES.json](SOURCES.json) pins every retained file by
source commit, Git blob and SHA256. Source equality is checked at replay;
origin-byte equality was separately checked against those Git objects.
Pending-PR Git history is not required for replay. The generic metadata pins
resolve only at main; the vendored originals have their own explicit byte
inventory, checked by `verify.py`.

PR3167 at `c2c7508f2d731feea550f1628601aebd35c6e147` is an overlap control,
not a new dependency of the theorem. Every weight-certified four-piece
quotient cover here needs at least fourteen separate deletions, with no
nonbasis rank-four anchor. Thus the earlier eight-/ten-deletion and
rank-four/twelve-deletion bounds do not supply these exclusions by that
weight-only route. Other geometric covers or proofs are not ruled out.
Concurrent [PR3169](https://github.com/CrocSwap/integer-mult-bounds/pull/3169)
at `b859f7791a6d2dad68652d5a54e266cb020a1302` reports five ten-piece
`(5,5)` exclusions using a stronger six-vertex coordinate budget. Its PR
was read at submission, not cold-replayed. Its scope is distinct from these
seven-/eight-/nine-vertex results.

The canonical investigation is [Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-18999460).
[Task, handoff choice and expansion decision](TASK.json). Development and local
checking used substantial automated assistance.

## Open next questions

Pin one actual remaining TWOSIDE shape and check whether its small pieces
again leave a one-dimensional quotient with all edge supports below 70.
A positive complete incidence margin could justify another exclusion;
a nonpositive margin is a stop test, not a construction. Refresh the live
ledger first. The present package does not establish a complete remaining
cell or authorize further supplier construction. Structured next steps and
blockers are in [TASK.json](TASK.json).
