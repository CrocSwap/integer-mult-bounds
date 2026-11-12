# Temporal obstruction for owner 1531

The owned role has original lifetime 32607–44247. Its paid MOVEs
are at u=41996 and v=44242, in strict chart chain 594⊊117⊊534 of
dimensions 1, 5 and 6. The only intervening owner contacts are
the incoming ADDs at 41997 and 44241. They read role 1291 with
coefficient −2 and role 732 with coefficient −1. Neither changes
any source trajectory. The required aggregate a on normalized
arbitrary inputs is

```text
a = −2 R1291(41997) − R732(44241).
```

Replace the two paid MOVEs by a direct rank-five chart 594→534
MOVE at either u or v. Let d be the unchanged owner row at
pre-event u. The two original writes are removed, so the old
late owner row is never available as a donor. The target
at the corridor exit is d+a.

For the early switch, chart 594 is available immediately before
the replacement at u. Chart 534 is available immediately after
it at u and throughout the later cuts. For the late switch,
chart 594 is available throughout the corridor and immediately
before the replacement at v. Chart 534 is available immediately
after it at v. The within-clock cuts share the same untouched
donor rows because the replacement moves only the owner.
Every old donor row remains read-only, with its own trajectory
and lifetime. The test grants all live cocharted rows, including
owned donors, and arbitrary rational coefficients. Combining
donors and scaling the owner at different legal times can
therefore only generate a row in the span of d and the legal
union for that switch. The proof permits the union across both
switches as an additional relaxation.

## Exact input-coordinate witness

On input e244, the old pre-u owner diagonal is zero. The exact
old source values are R1291(41997)=0 and R732(44241)=1/2.
The required aggregate has response −1/2. The chronological
sweep visits both literal outer banks at every pre-event cut
in [41996,44242], inclusive. Each pre-event key denotes the
unchanged donor bank on either side of a replacement MOVE at
that same clock when the corresponding schedule allows it.

The following table records all nine exact aliases. An alias
is contiguous and ends at an incident donor event, ingress,
lifetime change or a switch boundary. The receipt includes
schedule tags and the birth clock for the only owned donor.

| Chart | Inclusive cuts | Live donors |
|---:|---|---|
| 594 | 41996 | 575, 1231, 1502 |
| 594 | 41997–42014 | 575, 1231, 1502 |
| 594 | 42015–43333 | 1231, 1502 |
| 594 | 43334–44241 | 1231 |
| 594 | 44242 | 1231 |
| 534 | 41996 | 995, 1489 |
| 534 | 41997–43307 | 995, 1489 |
| 534 | 43308–44241 | 995 |
| 534 | 44242 | 995 |

All 7,163 donor incidences are zero on e244. The old diagonal
is also zero, so no sequence of legal unchanged donor writes
can supply the aggregate under either schedule. There is no
unvisited cut. This covers temporal donor selection within
both specified fixed-switch schedules, including any number
of such unchanged donor reads. Changed donor trajectories,
switch clocks and producer or recovery contracts remain open.

## Directed price

Both schedules spend the same two old paid anchors. The complete
17-copy delta is P1 −17, P4 −17 and P5 +17. Paid count is
110,502, productive count 22,461 and signed rank surplus 1,424.
The optimistic complete one-edit gross is at most
0.154513811062998 raw at the old crossing. The complete
fixed-target margin upper is below −139.59718548090816 at
κ = 0.0040075385047236. One additional paid rank-one position
would defeat the positive probe. The exact scope realizes zero
saving before any new physical proof, signed compiler, ordinary
work, ownership, precision or tape checks.
