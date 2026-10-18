# One rank-7 group pays only when all four helpers drop

**Partial. No new exponent.**

Group V45 in the #2979 frame record lowers helpers 249, 251, 265 and 267 onto
one rank-7 subspace. Each recorded end frame drops from rank 8 to rank 7. The
pinned prices charge one idle-width unit per helper. One, two, or three helpers
lose that charge. All four pay by 22,972. The claimed exponent is not replayed.

## What was executed

The shared subspace has GF(2) rank 7. Each of the four new end frames equals
that subspace and is a hyperplane of its old end frame. The same relation holds
for every helper end frame in the file: all 22 go from rank 8 to rank 7. All
139 gate frames are hyperplanes too. Their rank drops are 6 of 5→4, 22 of 6→5,
32 of 7→6 and 79 of 8→7. The note's parenthetical "7 → 6" on the entering
helpers is not the rank of those helper end frames.

The break-even constant is 2,091,300. A subset price `delta` with `k` helpers
has margin `-delta - k * 2,091,300`. The four single lowerings are each
-53,141. The six pairs are -27,770. The four triples are -2,399. The full group
has local price -8,388,172, idle charge 8,365,200 and margin +22,972. The five
group prices sum to the recorded stage-1 price -46,150,994.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this one
group. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the price table, the frame record and the
task catalogue. No selected frontier file changes. Child counts, cleanup
buffers and both supplier caps are not recomputed.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/rank7-v45-single-lowering/verify.py
python3.12 -B research/rank7-v45-single-lowering/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-v45-single-lowering
```

Both commands finish in under a second.

## Open next questions

The complete invoice still has to carry this group's child changes, cleanup
buffers and idle widths into both supplier caps. The pinned admission does
that, and this check does not replay it.

## Credit

Dugongue supplied the joint rank-7 frame record and the stage prices. Jeremy
Kothe's rewrites and the PR2942 words are the predecessors named there. This
package recomputes the V45 ranks and margins from those two records.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
