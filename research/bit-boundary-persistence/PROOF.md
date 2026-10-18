# Source boundary and complete cost

All gate indices and original register identifiers below are zero-based.
The object is the exact PR589 word pinned in `SOURCES.json`.

## 1. The legal late read

Let `x` be source77, `q` helper470, and `r` receiver444. In A, the only two
uses of q are:

```text
A[230]  at frame79: q += x
A[1993] at frame79: r += q
```

There is no B use of q. The copied totals do not include q. Before the second
operation, exact replay on all independent initial columns gives
`x = x_in` and `q = q_in + x_in` over F2. In particular, a borrowed helper is
not treated as initially zero.

Source77 begins at frame79, the line `[77]`. A[426] reads it at frame186,
whose lines are `[33,77]` and whose rational dimension is two. Receiver444
is still at frame0 before A[1993]. Its next gate is A[1994] at frame509,
which contains frame186 and has dimension four. The next source77 read is
B[35] at frame186. Thus the new gate

```text
at frame186: r += x
```

has valid entry frames, common-frame operands, and valid next frames for both
operands. The original frame79 read of x at this time would be a descent
from frame186 and is invalid. The new gate does not move x early.

Delete A[230], replace A[1993] as above, and remove q from the physical stock.
Subtract one from every old identifier greater than 470. Keep the E8 geometry,
all other A gates, B, scatter and all copied totals, subject to that renaming.

The rational frame check and the native legality checker give these paths:

| Old register | Old path | New path |
|---|---|---|
| 77 | `[79,186,509,386,560,1]` | same |
| 444 | `[0,79,509,392,513,1]` | `[0,186,509,392,513,1]` |
| 470 | `[0,79,1]` | removed |

Every other surviving register path is equal under the renaming. The complete
lists are in `FRAME-PATHS.json`. All 636 original frames remain in the catalogue.

## 2. Dirty state and literal restoration

The removed read used to add both `x_in` and `q_in` to r. The new read adds
`x_in`. Thus deletion changes a dirty-helper column; it is not a free scalar
substitution inside the old compensated word.

Rebuild D from the exact map of A, scatter and B. D contains only frame-zero
helper-to-target operations. In this case the rebuilt D is exactly the old D
with its 55 q operands deleted and all other identifiers renamed. It changes
from 18,085 to 18,030 scalar ADDs. Every remaining helper contribution is paid.

Rebuild C as the literal reversed list of all A/B operations that write a
source or helper, at the full frame. Reuse of the old C would not restore the
changed basis. C has 2,573 gates instead of 2,574. The original interleaved
checker verifies H1-H5 and the conclusions `U_block_form`, `J_identity`,
`C_is_U_inverse`, and `K_equals_D` on the changed word.

The complete order is D, A, nine COPY/scatter/ERASE episodes, B, C, then all
required final MOVEs. Exact F2 replay returns every source and helper to its
initial value and maps each target `y_i` to `y_i + x_i` for every dirty column.
The source checker also verifies the punctured-line geometry and rank-seven
copied totals. No decoder change is used.

Removing A[230] and its C inverse saves two ADDs. The compensation change saves
55 more. The total is 57. The independent literal emitter and the unchanged
native exporter produce the same record list for each complete word.

The signed native inverse uses negated ADDs and the original unchanged center
for reverse COPY/ERASE blocks. The existing native checkers and parent checker
replay this inverse. The cancellation-free forward and reverse bounds remain
49,347 and 1,113,070. Their charged precision bounds remain 93 local bits and
177 nine-stage bits, within the inherited 104/192 allowances.

## 3. Local recursive charges

Deletion of q removes rank-one and rank-seven MOVEs. Moving r first to the
rank-two frame changes its first two increments from `(1,3)` to `(2,2)`.
No other path changes. Therefore the exact profile difference is

```text
rank 1: -2; rank 2: +2; rank 3: -1; rank 7: -1.
```

The complete profiles are:

| Child rank | R439 | R438 |
|---|---:|---:|
| 1 | 1323 | 1321 |
| 2 | 1342 | 1344 |
| 3 | 79 | 78 |
| 4 | 44 | 44 |
| 5 | 102 | 102 |
| 6 | 11 | 11 |
| 7 | 19 | 18 |

The paid rank mass falls from 5,129 to 5,121. It still satisfies
`8R + 63 + 14v`, with `R=438` and `v=111`. Each local call saves two children.
This local result alone is insufficient: the removed helper occupied an idle
window, whose remaining child must grow.

## 4. Hosting and returned idle rank

Use the same nine-stage parent, four DATA pairs and 32 replicas. Expand the
original frozen hosting plan. For each stage remove the width-eight slot for
old helper index `470 - 222 = 248`. Group the remaining widths by idle window
and copy, rebuild the integer pattern counts, and run the original deterministic
expander for R438. No search or objective improvement is used.

These are the nine deleted slots per replica. The last column is the old
idle remainder before the eight units are returned.

| Idle window | DATA copy | Offset | Stage | Old remainder |
|---|---:|---:|---:|---:|
| 2 | 82 | 16 | 0 | 4 |
| 2 | 155 | 0 | 1 | 4 |
| 4 | 47 | 24 | 2 | 2 |
| 4 | 135 | 16 | 4 | 2 |
| 4 | 185 | 32 | 5 | 2 |
| 6 | 49 | 24 | 3 | 2 |
| 6 | 174 | 32 | 7 | 2 |
| 7 | 86 | 0 | 6 | 4 |
| 8 | 31 | 0 | 8 | 6 |

The expander can rename or reorder retained helper placements when it groups
patterns. The emitted candidate, rather than the old placement names, is the
object of the full hosting audit. That audit checks all 126,144 residual roles,
actual source-owner windows, disjoint offsets, call orientation and restoration.
There are no banks. Live DATA and physical stock do not increase.

Per replica, the old remainder histogram is
`{2:435, 4:444, 6:444, 7:666, 42:9}`. The new histogram is
`{2:430, 4:441, 6:443, 7:666, 10:5, 12:3, 14:1, 42:9}`.
The new idle children carry exactly 72 more rank units per replica. Across
32 replicas this returns all 2,304 units removed by the 288 local words.
The complete hosted rank mass is therefore unchanged at 1,808,352.

The final paid child profile is:

```text
{1:380448, 2:400832, 3:22464, 4:26784, 5:29376,
 6:17344, 7:26496, 10:160, 12:96, 14:32, 42:288}
```

It contains 904,320 children, including idle remainders, instead of 904,896.
The deficit remains `64*28416 - 1808352 = 10272`. The maximum child is 42.
The two-level condition remains `2*42^2 = 3528 < 4096 = 64^2`.

## 5. Exact supplier invoice

The unchanged inherited invoice charges the emitted ADDs, bridges, COPY/ERASE
operations, selectors, data access, restored helper stock, every recursive
child, and the signed prefix bound. Its precision fields are:

```text
prefix:                 177 bits, charged 192
coefficient:            177 bits
two-level coefficient:  393 bits, charged 512
row coefficient:        18355
```

Two independent exact moment engines accept

```text
c = 433544072119966441673 / 250000000000000000000000
```

and reject the next `10^-24` grid point

```text
1734176288479865766693 / 1000000000000000000000000.
```

These checks use the complete profile above and the inherited surcharge. They
do not infer a supplier gain from the local ADD reduction. The smaller selected
complex value still binds. The full-theorem assumptions listed in the README
remain open; this is a finite conditional supplier construction.
