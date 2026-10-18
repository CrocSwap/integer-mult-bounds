# The saturated rank-7 pattern direction preserves every rank tariff

This independent check concerns PR #2979 at commit
`be191346391661f4d35fc0d1508d0a6029572576`, specifically its frozen
`construction/allocation/T37-FACE-MIX.json`, `certificates/RELAX-CAP.json`
and `allocation/PROFILE.json`. It proves finite bin-pattern arithmetic and
a written identity for arbitrary rank tariffs. It does not certify the
source supplier, cap root, all-size recurrence or a new exponent saving.

The construction and pattern direction are due to Marius-Paul Dumitrean's
PR #2979, building on the source's credited PR2917 chronology, PR2930 flow
fill, PR2857 model, and themilkman216's cap/integrality observation. This
independent derivation was prepared by Ross's Codex automation with
OpenAI GPT-6.1 Sol assistance. Source credit and Apache-2.0 notices remain
in `sources/CREDITS.md` and `sources/NOTICE`.

## Contract and exact identity

A bin has capacity c in {8,16,32,48}; its pattern is a multiset of helper
widths in {4,5,6,7,8,9}, with sum at most c. Under the source model a bin
pays one residual child of rank c minus its used width, with rank zero
omitted. Helpers are whole roles in one bin. The local supplier profile
and inventory per call are held fixed. Scheduling windows, same-call
physical-family collisions, routing, native operators, arbitrary dirty
inputs and exact restoration remain separate source obligations.

Write A=[7,8,8,9]@32, B=[7,9]@16, C=[8,8]@16 and D=[7,7,9,9]@32.
The move is A+B -> C+D. Both sides have one capacity-16 and one
capacity-32 bin, and inventory {7:2,8:2,9:2}. All four bins are saturated.
Consequently both sides have exactly one zero residual at each capacity,
with no positive residual. This proves equality of the *complete*
residual histogram separately at every capacity, even if zero residuals
are retained.

For any function H on the ranks, the sum of residual tariffs H(r) is
therefore identical before and after the move. The usual source tariff
H_b(r)=r(73/r)^b for r>0, H_b(0)=0 is one example; the statement does not
rely on a root, a parameter interval, concavity or equality of rank mass.
Adding the same fully paid local profile preserves the whole moment at
every b. This is a cost identity for a legal pattern replacement; it
does not supply the chronological replacement or price any new routing.

The source's ten-column fractional basis contains A, B and C. Its
constraint columns satisfy a_D=a_A+a_B-a_C, with the same identity for
their zero residual costs. Every dual which is tight on those basis
columns is also tight on D. Thus D is a zero reduced-cost direction
whenever that basis is optimal. The independent checker also inverts
the rational basis and obtains identically zero reduced cost as a
formal linear combination of tariff values, without invoking an LP,
certifying signs of other reduced costs, or recomputing a root.

## The exact integral family

Reversing 1,063 moves from the shipped T37 mix defines k=0. Applying k
forward moves gives the following counts; omitted zero counts are allowed.

| capacity | helper widths | count |
| --- | --- | ---: |
| 8 | [8] | 24864 |
| 16 | [7,9] | 16253-k |
| 16 | [8,8] | 323+k |
| 32 | [7,8,8,9] | 1063-k |
| 32 | [7,7,9,9] | k |
| 32 | [9,9,9] | 864 |
| 32 | [6,8,9,9] | 5328 |
| 32 | [5,9,9,9] | 666 |
| 32 | [4,9,9,9] | 8655 |
| 48 | [] | 14095 |
| 48 | [9,9,9,9,9] | 2478 |
| 48 | [4,8,9,9,9,9] | 3 |

All pattern multiplicities are nonnegative integers exactly when
0<=k<=1063. Necessity follows from D having multiplicity k and A having
multiplicity 1063-k; sufficiency follows directly from the table.
The source is exactly k=1063. This is the maximal interval for this
particular one-dimensional affine family, not the full feasible set of
integral packings.

The width-7 slots outside capacity 16 number (1063-k)+2k=1063+k.
This family has at most one width-7 slot in each capacity-16 bin; the
unrestricted catalogue also permits [7,7]@16. Any Hall obstruction using
that at-most-one premise is restricted to this family (or another
explicitly restricted support), not every capacity-16 allocation.
No claim is made here that all 1,064 family members can be scheduled,
or that a necessary interval Hall condition is sufficient.

## Complete finite invoice and T74 scaling

Each point has bin counts {8:24864,16:16576,32:16576,48:16576}. There
are 333 calls. The per-call inventory is
{4:26,5:2,6:16,7:52,8:99,9:213}, summing to 408 helpers, so the complete
inventory is {4:8658,5:666,6:5328,7:17316,8:32967,9:70929}, with
135,864 helper roles.

The residual histograms, including zero, are:

| capacity | residual-rank histogram |
| --- | --- |
| 8 | {0:24864} |
| 16 | {0:16576} |
| 32 | {0:7057,1:8655,5:864} |
| 48 | {0:3,3:2478,48:14095} |

Hence there are 48,500 saturated bins and positive idle histogram
{1:8655,3:2478,5:864,48:14095}. The fully paid local per-call profile is
{1:2445,2:706,3:232,4:108,5:18,8:8}. Adding 333 copies gives exactly
{1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095}, with rank
mass 2,408,256 = 65088*37. Thus the complete source-style moment at T37 is

    [822840 H(1) + 235098 H(2) + 79734 H(3) + 35964 H(4)
     + 6858 H(5) + 2664 H(8) + 14095 H(48)] / [73*896*37].

Doubling the finite counts gives T74, 666 calls, 271,728 roles, and
{1:1645680,2:470196,3:159468,4:71928,5:13716,8:5328,48:28190}, exactly
the frozen `allocation/PROFILE.json`. The source-style moment is
unchanged because its numerator and denominator double. This arithmetic
does not independently prove that the literal interleaving preserves
windows or physical families; the owner's chronological check has that
separate obligation.

## Fractional cap and integral mixture are distinct

The source README's phrase "cap-level integer mixes" must not identify
the preceding integral family with the fractional cap profile. The
fractional basis has residual counts per replica
{1:234,3:1341/20,5:93/4,48:7619/20}. At T37, subtracting this profile
from the integral family's profile yields the exact nonzero difference

    Delta = -3 e1 - (57/20) e3 + (15/4) e5 - (3/20) e48.

Its rank mass is zero, but its histogram is different. Therefore the
identity among the integral family preserves its existing near-cap
moment; it does not close its gap to the fractional cap. The source
reports a near-cap root, and this check neither recomputes its digits
nor proves the basis optimal. Fractionality of one basis alone would
also not rule out another integral optimum on a larger face. An exact
cap-attainment claim would require its own complete optimal-face and
chronological argument.

## Verification and defect sensitivity

Run `python3 -B research/rank7-chronological-face/independent_face.py`,
also with `python3 -O -B`. Explicit exceptions, not assertions, enforce
the checks. The program independently reconstructs all finite counts,
enumerates the 1,064 family points, checks per-capacity residuals and
the T74 profile, and checks the symbolic target reduced cost.

Negative controls reject both out-of-range endpoints, a changed source
count, a capacity-preserving count transfer which changes width
inventory, and a claimed-profile change which preserves child count
and rank mass. A saturated wrong swap A+B -> A+C preserves capacities
and residuals but changes inventory. A stronger rank-mass control uses
[4,5]@16+[6,7]@16 versus [4,6]@16+[5,7]@16: both preserve inventory,
two residual children and residual rank mass 10, but their histograms
are {3:1,7:1} and {4:1,6:1}; tariff H(r)=r^2 gives 58 versus 52.
These controls show why rank mass alone does not establish the claim.

The written swap identity holds for arbitrary tariffs and all legal
applications. The exhaustive finite computation covers the stipulated
T37 family only. Neither is a formal-kernel proof or a new supplier or
recursive-complexity admission.
