# Independent invoice review and an all-rank extension

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This review addresses the scalar pair-placement invoice. A separate exact
implementation reviews the geometry. It is author-side parallel review,
not external human acceptance.

## Literal invoice audit

I independently rebuilt native helper/paid histograms, every binary-node
auxiliary target and idle, every thin query, the eight main targets, and
both paid fragment replacements. The resulting reference invoice matches
the exact retained #6726 receipt at allocation (4,4,1,1,4,4). Every coefficient
of the package's candidate target and paid histograms also matches its RESULT.json.
There are 13,670 productive fields and 66,956 paid requests. Its signed delta
from the reference is exactly

    104 H(41)-104 H(40)-104 H(1).

The third whole C idle is paid. The three root thin queries are paid. Both
fragment splits pay for both pieces. No native helper or binary auxiliary
is counted twice. The signed linear rank-mass surplus remains 760.

The check covers four independent allocations and all four choices of
fragment orientation, comparing the exact signed histogram difference
104[H(8C+1)-H(8C)-H(1)]. The universal formula follows from the explicit
term cancellation, not from these 16 fixtures.

Reproduce the portable independent audit with
`python -I -B independent_invoice.py`. It reads the package's reported histogram
only after constructing its own, and checks `INDEPENDENT-INVOICE.json`.
The explicit `--write` mode authors that receipt. The portable adaptation changes
only input paths and receipt-writing behavior, preserving the independent
counting and inventory implementation.

## Higher second-pair ranks need no new search in this fragment model

Retain the package's universal geometric premises: P has rank 4 at sites (1,2), Q
commutes with P and is compatible with both actual prefixes at sites (5,6),
and Q(I-P)=I-P. Commuting endpoint projectors L,N have rank 2 and satisfy
L<=P,N<=Q. Their query pairing factors through LN and is nonzero, so
rank(LN)>=1. This section grants exactly one fragment from a pure B target
and one from a pure C target, as in the package's stated economic comparison.

Use bits A=L,B=P,C=Q,D=N. The nesting and P union Q=I leave only
the eight sectors B,AB,C,BC,ABC,CD,BCD,ABCD. There are eight scalar
coordinates; the A,B,D marginals are 2,4,2. The ABCD sector has dimension
at least 1. The pure B and pure C sectors each have dimension at least 1.
An exact count-vector enumeration gives just eight inventories:

| rank Q | Inventory |
|---:|---|
| 5 | B², AB, C³, CD, ABCD |
| 6 | B², C⁴, (ABCD)² |
| 6 | B², C³, ABC, CD, ABCD |
| 6 | B, AB, C⁴, BCD, ABCD |
| 6 | B, AB, C³, BC, CD, ABCD |
| 7 | B, C⁴, BC, (ABCD)² |
| 7 | B, C⁴, ABC, BCD, ABCD |
| 7 | B, C³, BC, ABC, CD, ABCD |

No rank 8 inventory has a pure B target. This is a complete finite necessary
inventory census, not an assertion that all eight inventories are geometrically
attainable. Its conditions follow from the premises above at every rank.

Let T_X=H(1+8 times the total body size of X), J_C=H(8C), and let
R5 be the first row. Every rank 6 row pays one more whole C idle than R5.
All native, binary, root-query and granted-fragment terms are otherwise
unchanged. In the displayed row order, the exact differences from R5 are

| Rank 6 row | Difference |
|---:|---|
| 1 | T_ABCD+T_C-T_AB-T_CD-J_C |
| 2 | T_ABC-T_AB-J_C |
| 3 | T_C+T_BCD-T_B-T_CD-J_C |
| 4 | T_BC-T_B-J_C |

Rows 2 and 4 are strictly negative by H(x+y)-H(x)<H(y).
For row 1, diminishing increments give
T_ABCD-T_AB <= T_CD-1, so its difference is at most i(C)-1<0.
For row 3, T_BCD-T_CD <= T_B-1 gives the same bound.
These inequalities hold for every positive body allocation and every 0<k<1.

Each rank 7 inventory permits deletion of one C incidence to a listed rank 6
inventory while retaining both pure groups. Deleting that incidence saves
J_C and loses a target increment smaller than J_C, so it strictly improves
the complete invoice. The census checker verifies an explicit deletion
for each row. Thus every rank 7 invoice is strictly worse than a rank 6 one.

Consequently every higher-rank second projector in this declared model
with one pure fragment per bank is strictly dominated by R5, which A already
proved strictly dominated by an orientation-matched #6726 allocation. This
closes the rank 6+ cost branch without assuming an unattained projector or
running additional endpoint searches. It does not cover extra retirements,
fragments from nonpure target groups, two fragments in the same bank,
larger first-pair rank, or changed native schedules.
