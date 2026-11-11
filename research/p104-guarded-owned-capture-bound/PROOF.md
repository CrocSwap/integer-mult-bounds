# Guarded capture and fixed first-read exclusion

A lifetime begins with literal INIT and ends with its matching CLEAR.
The immediately following event must be a nonzero ADD into that owner
from a distinct cocharted source. Fresh zero ownership makes this a
scaled capture. The owner must have at least one paid MOVE and at least
one source-only ADD read. Later owned contacts may be paid MOVEs or
source-only ADDs, and every read must be on a single literal chart.
The two stationary lifetimes on protected role 1568 are excluded.
The proposed public donor must already be live on the exact chart,
have arrived by a paid MOVE, and be distinct from all read destinations.

The forward engine uses exact binary elimination for chart nesting.
The reverse engine enumerates exact GF(2) spans, restores the initial
public chart map and matches CLEAR to INIT. The comparator verifies all
72 literal lifetime IDs, their boundary charts, all 516 ordered contact
clocks and access directions, every paid MOVE rank, every original
source ADD, and every disposition.

| First disposition | Lifetimes |
| --- | ---: |
| Protected role | 2 |
| No paid MOVE | 32 |
| No immediate nonzero ADD capture | 28 |
| Other owned contact | 4 |
| Common read chart strictly lower than birth | 6 |
| Equal or higher common read chart | 0 |
| Unresolved | 0 |

The unique COPY capture lifetime has no paid MOVE. Each of the six
strictly lower cases has one paid descent and its first source ADD is
the next literal event. Those six were priced separately before support.

| Owned role | MOVE clock | First read clock | Chart | Separating input | Owned coefficient |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1514 | 33133 | 33134 | 260 | 2 | 1 |
| 1518 | 34519 | 34520 | 431 | 2 | 1 |
| 1519 | 35434 | 35435 | 600 | 2 | 1/4 |
| 1516 | 36319 | 36320 | 394 | 1 | −1 |
| 1517 | 36327 | 36328 | 598 | 1 | −1/4 |
| 1515 | 39844 | 39845 | 599 | 0 | 1/4 |

The exact direct projection propagates the three selected public basis
inputs through the original signed rational ADD, COPY and SCALE actions.
INIT/CLEAR manage zero ownership and MOVE preserves normalized rows.
For each first read the chosen input has nonzero coefficient on the owned
source and zero coefficient on every other live role in that chart.
The check covers 28 other-role incidences, including all 19 public donor
incidences, even before applying the paid-arrival and alias restrictions.
No scalar multiple or combination of the other rows can match the owned
row. Since every proposed donor must match the first read, checking
later uses is unnecessary. The separation is in normalized rows and
therefore gives a necessary physical obstruction under the unchanged
source contract.

## Complete directed price

The signed #7314 invoice has 17 native copies, 110,536 paid positions,
22,461 productive fields, rank surplus 1,424 and no empty-root credit.
Use the exact crossing upper
`36462214364462343366888845568981/10000000000000000000000000000000000`.
Deleting one lifetime with m[r] paid rank-r MOVEs changes P[r] by
`−17*m[r]` and keeps T fixed. The optimistic raw credit is
`17*sum(m[r]*r^(1−κ))` before any added physical or ordinary costs.

The relaxation prices all 47 owned MOVEs once using histogram
`{1:20,2:9,3:2,4:13,5:2,6:1}`, for a directed gross upper of about
1896.7038062781314 raw. The actual scope permits one lifetime.
The higher-chart site price is zero after complete empty stock.
The lower-chart best one-lifetime relaxed upper is about 33.91417798
raw, for rank two. After all six first-read exclusions the compatible
upper is zero. The census and separators require no changed native or
caller replay and yield no verified κ gain.
