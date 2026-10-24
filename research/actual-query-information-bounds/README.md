# Information bounds for the actual routed queries

This package gives scoped information bounds for the historical complex
nine-stage word. It combines exact proofs, finite certificates, and their
independent agent reviews. It does not change the complete kappa calculation.
It does not give a universal circuit lower bound.

The [proof](PROOF.md) states the separate models. The
[source manifest](SOURCE-MANIFEST.json) records every input and each portable
edit. The [source pins](SOURCE-PINS.md) identify the historical supplier.
[NOTICE.md](NOTICE.md) preserves contributor credit and the AI disclosure.

| Model | Result | Exact source and review |
| --- | --- | --- |
| Nine queries of one fixed arbitrary source on the full regular cover | First five moments `72,120,244,1649/3,47467/36`; dimension at least `15560/273` complete fields; at least 57 whole fields or 64 fields in whole eight-field cohorts | [Moment proof](payload/lanes/temporal-reuse/QUERY-MOMENTS.md), [independent review](payload/lanes/cover-algebra/QUERY-MOMENTS-REVIEW.md) |
| Actual query row space and actual snapshots of rank at least two | Exact source-port support distance 53; a k-query common span needs at least `k+2` birth fields | [Support proof](payload/lanes/history-encoding/QUERY-SUPPORT-DISTANCE.md), [independent review](payload/lanes/cover-algebra/QUERY-SUPPORT-DISTANCE-REVIEW.json) |
| One positive proper actual snapshot cone | No nonzero completed query in any of the 1,002 cones, with all snapshot times granted | [Cone proof](payload/lanes/history-encoding/SNAPSHOT-CONE-OBSTRUCTION.md), [full source review](payload/lanes/circuit-interface/snapshot-audit/SNAPSHOT-ROWS-REVIEW.md) |
| Same-content monotone snapshot networks, with the original core fixed | General cut lemma; global bound 42; bound `9k` for twelve specified rank-five query spaces; bound `8k` for cones 983 and 991, including direct FULL bypass edges | [Cut theorem](payload/lanes/cover-algebra/MOVABLE-SNAPSHOT-CUTS.md), [global review](payload/lanes/history-encoding/SNAPSHOT-FLAG-CUT-REVIEW.md), [rank-five review](payload/lanes/cover-algebra/RANK5-UNION-CUTS-REVIEW.md), [rank-eight review](payload/lanes/cover-algebra/MOVABLE-RANK8-CUTS-REVIEW.md) |
| One complete linear residual channel for the specified nine-stage controller | Exact residual rank `72|G|-d`; with the separate cover bound, 72 complete arrays per replica or 1,152 across 16 replicas | [Residual proof](payload/lanes/residual-syndrome/PROOF.md), [algebra review](payload/lanes/residual-syndrome/review/REVIEW.md), [cover review](payload/lanes/source-domain/COVER-REVIEW.md) |

The numbers in different rows cannot be added. The fixed-source hypothesis
does not apply automatically when a controller reads changing sources.
The snapshot field count does not price a shared network. The rank-eight
cone bounds do not give a global bound of 64. The residual channel count
does not bound peak workspace or a procedure that reads the source again.

## Reproduction

Use Python 3.11 or later with SymPy 1.14.0. All other dependencies are in
the standard library. Run from this package directory with a new output
directory outside the package:

```sh
python3 -I -O -B replay.py --output /absolute/path/to/new-query-bounds-replay
```

Expected final line:

```text
PASS_ACTUAL_QUERY_INFORMATION_BOUNDS_PACKAGE
```

The command runs 17 exact checks in sequence. It requires at least 3 GiB
of free disk space. It writes logs, all regenerated receipts, and `REPLAY.json`
under the output path. It does not need Git, network access, a workspace
checkout, or a search solver. It uses one Python process at a time.

The replay rebuilds the actual source matrix by reverse propagation. It
enumerates all 194,400 supported fifth-order triples. It rebuilds every
scalar snapshot row on all 712 formal inputs and checks all 16,687
availability intervals. It then checks the support distance, cone minors,
cut weights, exact source restrictions, and every allowed cut edge in the
specified certificates. The independent rank-five review checks the full
712-column query overlap. The independent cover review uses all 73 binary
axes. The independent residual review uses separate exact SymPy examples.

Each complete generated JSON receipt must equal its expected receipt,
including JSON types. The portable source-hash changes are explicit in
`REPLAY.json` and `SOURCE-MANIFEST.json`. The optional sixth-moment cover
extension is omitted; the replay checks the complete baseline receipt after
the five named optional extension fields are removed. No other mathematical
field is omitted from receipt comparison.

The source proofs retain their historical commands and dependency paths.
Use the package command above for the portable replay. The original versions
of changed files remain under [frozen](frozen). The mathematical checks are
unchanged. The changes replace local Git and workspace reads with the same
hash-pinned archive members and update the resulting checker hashes.

## Validation boundary

The checked supplier source is commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. This is a historical source.
At publication base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, the
[selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/b58ad9ef4d4e861b0eaa5dba41742bdc072dca51/certificates/selected-result.json)
uses [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
and kappa `60403/20000000 = 0.00302015`. This package does not prove that
the historical bounds apply to that changed construction.

The full snapshot replay checks scalar content and canonical frames.
It does not check a new capture word, chronological schedule, native phases,
owner assignment, precision, tape cost, or complete recursive price. The
local native lift and the controller endpoint normal form remain separate
inherited application dependencies for the residual theorem. Their source
proofs and receipts are included; their native checks were not rerun here.
No proof assistant or independent human review is claimed.

No LP or failed search is used as impossibility evidence. The package uses
only the accepted finite cuts. It omits the low-rank screens, movable-cut
searches, and the unreviewed sixth-moment extension.

## Related models

[PR #4700](https://github.com/CrocSwap/integer-mult-bounds/pull/4700) fixes
the later PR4610 scalar graph and proves a 64-rank floor for its eight
retained centre calls under binary monotone chart changes. It permits a
different class of edits and does not supply the global snapshot-network
bound that is open here.
[PR #4200](https://github.com/CrocSwap/integer-mult-bounds/pull/4200) treats
closed private walks for copies of one unchanged BIT total.
[PR #4267](https://github.com/CrocSwap/integer-mult-bounds/pull/4267) treats
a formal orbit query grammar, and
[PR #4269](https://github.com/CrocSwap/integer-mult-bounds/pull/4269) treats
constant-direction scalar callers over a cubic algebra. These are distinct
models. The overlap check does not claim novelty against all literature.

## Open next questions

1. Determine the global unchanged-core snapshot-network cost above the
   proved floor of 42. A first step is one exact certificate on the complete
   allowed graph. Shared edges prevent the addition of separate cone bounds.
2. Determine the actual fixed-source query rank beyond the first five
   moments. Those moments alone attain the stated continuous relaxation
   bound, so a stronger result needs additional information.
3. Test the hypotheses on a later supplier before using these bounds there.
   The source matrices, observation graph, routes, and endpoint contracts
   must be bound to that supplier. No such application is part of this package.
