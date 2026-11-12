# Geometry and restoration for a paid carrier loan

For an owned role h let m be its old paid MOVE A→B.
The candidate injects h into a distinct existing carrier f while
both are at A. It clears h at A and reconstructs it at B.
Let v be the original normalized row of f at its earlier MOVE
clock u. Immediately after f reaches B, its normalized row is
v+h. In the tested restoration, the unchanged donor bank must
supply v so that a fresh owned h can receive f−v and then
f can be restored by subtracting h. Donor banks exclude h
and f. The two tests retain every other original role path,
scalar event, coefficient and ownership lifetime.

## Same endpoints with deferred restoration

The same-endpoint test keeps the original paid carrier A→B.
It holds the temporary carrier value until just before the
owner's first original use, at m+1. Both owner and carrier
must therefore have no intervening original contact while
the loan is live. Reads through ADD or COPY count as contacts.

All 47 owner anchors have an exact first use at m+1. There
is one earlier same-endpoint MOVE after the owner's last old
contact. It is public f988 at clock 36647, chart 260→1091,
for owner h1540 at clock 45647. Clock 36648 reads f988 into
role 862 with coefficient +1 at chart 1091. It precedes the
specified restoration and excludes the route. The opposite
chronology walks agree on all anchors and zero eligible
carriers. The next test removes the deferred timing condition.

## Same endpoints with immediate restoration

Keep f988's original paid MOVE at 36647. Inject h1540 in chart
260, then CLEAR h1540. Freshly INIT it in chart 1091 and restore
both rows before the original ADD at 36648. The owner has no
original contact after clock 35146 and before its old paid MOVE
at 45647. Its first later use is ADD 756←1540 at 45648.
The immediate test preserves every other scalar and paid route.

At pre-event 36647 both moving roles are in chart 260. The exact
chart-1091 bank has 14 public and three owned live donors. All
17 are granted as read-only sources. Both engines agree on the
137 nonzero coordinates of the original carrier row. The
forward donor matrix has rank 15. Independent reverse covectors
and exact elimination derive the same separator.

```text
x397 − x382 − 3(x2+x230)/2
```

It evaluates to zero on every allowed donor and −2 on f988.
This excludes the sole immediate exact-route case even with
arbitrary signed rational donor combinations. No donor with a
changed trajectory is granted.

## Strict nested carrier with immediate restoration

For an ascending owner MOVE A→B, the earlier carrier originally
moves A→C with strict GF(2) spans A ⊊ B ⊊ C. The proposed
carrier split A→B→C restores both rows at B before the
second leg and the next old event at u. The owner must have
no literal contact from u to its old MOVE. The carrier needs
no later contact restriction after it is restored.

Both chronology walks agree on each of the 47 previous-owner
contact clocks and the exact nested key. The forward walk
counts six same-source incidences at ascending owner anchors.
The reverse walk counts those six and four incidences at
descending owner anchors, three at 35434 and one at 39811.
The latter four fail A ⊊ B by dimension. Five of the six
ascending-source incidences fail the second strict inclusion.

The remaining route is h1550 at m=44235 and public f1161 at
u=40226, with chart chain 541→543→127 and ranks 1+1.
The last previous h1550 contact is clock 39172. The next
original h1550 contact after its MOVE is the outward ADD at
44236. The pre-event chart-543 bank at 40226 contains exactly
public roles 628 and 630 and no owned role.

The exact forward row and independent reverse covectors agree
on the required row v. Its input-4 coefficient is −1/2.
Input coordinate 4 annihilates both donor rows. No rational
combination restores the carrier under the tested contract.
No geometry or support key remains unvisited or unresolved.

## Complete directed quote

Write H_r = r^(1−κ). An exact same-route loan would delete 17
paid rank-r positions across the signed caller while keeping
22,461 productive fields. Its highest one-edit gross upper
at the old crossing is 101.33571240164612 raw. The sole
immediate exact-route candidate would retain f988's paid MOVE
and delete only the owner's rank-one MOVE, for ideal gross 17
raw and 110,502 paid positions. Its realized saving is zero.

In the nested test the old pair has ranks r and r+s and the
new pair has ranks r and s. Its exact signed paid delta is
P_{r+s} −17 and P_s +17. The paid count stays 110,519 and
the productive count stays 22,461. Signed surplus becomes
1424+17r. Its directed raw gain is 17(H_{r+s}−H_s).
Concavity bounds it strictly by the corresponding owner
deletion gain 17H_r. The predecode all-47 relaxation gives a
gross upper of 1,896.702946936210 raw at the old crossing,
before compatibility or restoration. That relaxation grants
each owner debit only once.

The best quoted nested one-edit upper is 101.15855820113319
raw at the old crossing and its complete fixed-target upper
is −38.69131601905544, both rounded upward. The sole exact
geometry has gross upper 16.91416786145965 and complete
fixed-target upper −122.86124079250860. An additional paid
rank-one position alone would exceed its gross credit. The
literal obstruction leaves zero feasible saving. Any changed
construction would still need physical signed maps and their
adjoints, exact phase, ownership and restoration, and charged
source access, compiler, precision and tape obligations.
