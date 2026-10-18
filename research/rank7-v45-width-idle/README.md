# Four V45 widths add 36 idle-rank units

**Partial. No new exponent.**

Moving only helpers 249, 251, 265 and 267 from width 8 to width 7 raises the
idle rank mass by 36 per replica, one width for each of the nine calls. The
same vertex appears at the recorded parent cap and at the recorded stage-1 cap.
The joint stage-1 histogram is a different vertex. The exact dual enclosure of
this four-width vertex is not rebuilt.

## What was executed

The packing is the fixed-capacity model: bins of capacity 8, 16, 32 and 48, and
nine copies of the per-call width inventory. A deterministic simplex locates a
vertex, and that vertex is solved in exact rationals. On the parent inventory
it reproduces the parent certificate histogram. On the stage-1 inventory it
reproduces the stage-1 certificate histogram. Pattern counts are 1,163 and
2,551, as recorded.

The four-width inventory is the parent inventory with four roles moved from
width 8 to width 7. Its vertex is

| idle rank | count per replica |
|---:|---:|
| 1 | 234 |
| 3 | 387/5 |
| 5 | 75 |
| 48 | 1853/5 |

Against the parent histogram, rank 3 falls by 9/5, rank 5 falls by 9, and rank
48 rises by 9/5. The rank mass rises by 36. Rank 1 stays 234. The local profile
stays the parent's; the objective was evaluated at both recorded caps and the
vertex did not change.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
four-width idle separation. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the stage certificate and the task catalogue.
No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/rank7-v45-width-idle/verify.py
python3.12 -B research/rank7-v45-width-idle/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-v45-width-idle
```

The search finishes in about a second.

## Open next questions

The vertex is primal feasible and it is the float optimum at both recorded
caps. An exact reduced-cost enclosure at the new root would certify it. The
local-profile change that belongs to these four helpers is still separate from
this width-only inventory.

## Credit

Dugongue supplied the stage certificate whose parent and stage-1 histograms are
the calibration. The four helpers are the V45 group in that proposal.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
