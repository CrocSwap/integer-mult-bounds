# Independent check of the backward snapshot rows

The exact row and interval check passes. No source or producer module is
imported. The checker reads the pinned clean backward event word, the
original canonical frame list, the actual R matrix, and the frozen
snapshot payload. It rebuilds every scalar row on all 712 formal input
columns.

The source snapshot payload has decompressed SHA256
`3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c`.
The full pins are in `SNAPSHOT-ROWS-REVIEW.json`.

## Coverage

The 16,687 intervals cover all 704 persistent wires at every boundary
from event 8106 through event 24913. They have no gap or overlap. The
checker verifies that no scalar target update or canonical native-frame
change occurs inside an interval. It compares 24,199 interval endpoints
with fresh full-input rows and frames.

The complete final map is `(x,y,h,c) -> (x-Jy,y,h,0)`. All 480 arbitrary
helper rows are identity in their canonical coordinates, with the
inherited native endpoints. The private fields are cleared. The check
does not replace those canonical helper identities by a physical
identity claim across different helper frames.

The fresh rows also satisfy the claimed support law after the test
substitution `x=Jy`, `h=0`, `c=0`: at frame U, a remaining Y coefficient
can use only a port whose binary label is perpendicular to U. This
checks 16,023 distinct frame/row pairs and 98,056 nonzero coefficients.
The final X and all helper/private rows vanish on this test family.
The exact query minors and the full cone theorem have a separate review
in the cover-algebra lane. This receipt is an independent source-row
check, not a second full minor review.

After event 17606, a non-FULL canonical view may need the specified
inverse exit monomial. The negative support argument can grant that
view, since a zero source row remains zero under an invertible map.
This does not make such a view free in a new capture construction.

Three controls reject an added arbitrary private coefficient, an omitted
interval, and an incorrect frame label. The native profile is unchanged:
`{1:2412,2:418,3:432,4:142,5:82}`.

## Exact private lifetime and repair cut

Event 8702 is the last original private read or write. It clears C7;
all eight private fields are zero at this cut. Phase A starts at event
8703. No later original event reads, writes, or advances any C field.
The final scalar event is 24913. At that cut, all 112 X fields and 402
helper fields have the canonical FULL frame.

Thus a new protocol that starts after event 8702 can use C0 as a serial
snapshot temporary and C1 through C7 as seven query accumulators. One
additional owned field would supply an eighth accumulator. A cleared
zero field can receive a new frame label without a physical operation,
because its exact physical value is zero. A positive construction must
check that zero state before each such label change and must emit every
nonzero completion with its complete native phase.

Suppose a supplied snapshot protocol gives eight FULL rows

```text
q = RY + L X_out + H h_full,
```

where `X_out=X-JY` is the unchanged completed core output and `h_full`
contains only the 402 available FULL helper fields. Subtract both
baseline terms from all eight q fields before changing any X field.
Then the 448 signed-quarter entries of K give

```text
X_out -= Kq = X-JY-KRY = X-Y.
```

These final additions cost 5376 real primitives, followed by the query
clears. This is a conditional exact suffix. No snapshot synthesis or
favourable native-rank total is supplied here. In particular, it does
not bypass the single-cone obstruction. A merged protocol must provide
its actual capture times, views, coefficients, completion recipes,
storage lifetimes, recursive-child hosting, and full invoice.

## Reproduction

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/circuit-interface/snapshot-audit/review_snapshot_rows.py
```

Expected status:

```text
PASS_INDEPENDENT_BACKWARD_SNAPSHOT_ROWS
```

No source file is changed. No new native phase sweep, recursive replay,
global owner admission, or supplier improvement is claimed. Before any
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
