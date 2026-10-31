# Independent helper splits and the complete cost

This proof changes the helper input and output contract of the exact PR5580
word. It retains every main endpoint, paid Gaussian call and owned lifetime.
All scalar identities below are over the rationals. The native check supplies
exact phases and the rule for every positive tensor width.

## 1. A split criterion

Let a group of helpers have the same initial chart U and final chart V.
The complete source word returns each of these helpers unchanged in normalized
coordinates and has no helper contribution to any other output.
Let F be a strict intermediate chart, with U contained in F and F contained
in V. At one chronological cut, let P be the scalar prefix matrix and S the
scalar suffix matrix. The matrices include every public input and output.
Owned fields follow the source initialization and erasure contract.

Suppose a row a and a column b use only fields at chart F. Suppose c and d
use only the specified helper group, and

```math
aP=c,\qquad Sb=d,\qquad ab=cd=1.
```

Choose a helper role p at F. There are invertible scalar matrices G and J
with

```math
e_p^T G=c,\quad Gd=e_p,\qquad e_p^T J=a,\quad Jb=e_p.
```

Here G acts only on helpers with boundary charts U and V. J acts only on
fields at F. The construction emits these matrices as ADD and dyadic-unit
SCALE operations. Its row and column elimination uses the unit pairings.
The emitted program and its inverse are explicit; no dense matrix operation
is assigned zero implementation cost.

Apply G inverse at the input. At the cut, apply J. Role p then contains the
independent coordinate t=c h. Retain p as an output at F. Introduce one new
independent input z at F. Use its new role in place of p in J inverse and in
the complete suffix. Finally apply G at V, with the same role substitution.
The suffix state changes by b(z-a P h), so its helper output is

```math
h+d(z-ch).
```

The final change of basis gives

```math
G[h+d(z-ch)]=Gh+e_p(z-t).
```

Thus the former p coordinate is replaced by the independent z coordinate;
all other helper coordinates and every main output retain their required
values. The old t coordinate has already been returned at F. This replaces
one U-to-V target by a U-to-F target and an F-to-V target.

This uses a new input, not two outputs computed from one input. It does not
assume a helper is zero. The early output is a public field and stays live
until the caller returns. The successor input is public from the start and
is first used at the cut. No new COPY, CLEAR or owned lifetime is introduced.
The source's owned erasures remain charged under the inherited contract.

All three basis changes use common physical charts. They therefore commute
with the relevant chart operator. Native normalization gives ranks
`dim(F)-dim(U)` and `dim(V)-dim(F)` with their exact phases. Scalar coefficients
stay outside the tensor substitution. The frame induction applies at every
positive width; it is not a test at width one alone.

## 2. The first explicit split

The source is PR5580 at `6efa248cf456d6101d757e9d09ba29711d18a13a`.
Use the cut after zero-based event 13778, chart 120 of dimension five, and
pivot 648. The boundary group has initial chart 3 (dimension zero) and final
chart 127 (dimension nine). With e_r the coordinate at role r, the exact
vectors are

```math
a=e_{651}^T+(e_{648}^T+e_{649}^T)/2,\quad
b=e_{648}+e_{649}-e_{650}-e_{652},
```

```math
c=(e_{648}^T+e_{649}^T)/2,\quad
d=e_{648}+e_{649}-e_{650}-e_{652}+2e_{205}.
```

The complete prefix gives aP=c; the complete suffix gives Sb=d.
Both pairings are one. The first basis change uses five ADDs, the local
basis uses five ADDs, and their two inverses use ten more ADDs. The first
split therefore adds 20 scalar events and replaces H9 by H5 and H4.
A later split divides this particular H5 target further. The full sequence,
including each updated event index, is in `SPLITS.json`.

`check_cut` reconstructs each prefix functional and propagates each suffix
column. It checks that all other input and output coefficients are zero.
The verifier then checks every public and owned row after each complete
split. A separate dense-integer transpose replay checks all 574,564 entries
of the final 758 by 758 interface.

## 3. The complete target change

The fifteen splits are

- six H9 to H4 + H5;
- five H9 to H2 + H7;
- three H9 to H1 + H8;
- one H5 to H1 + H4.

They add 15 independent helper inputs. The source's 735 public fields become
750, of which 542 are helpers and 208 are main fields. Eight owned lifetime
roles remain; only one is live at a time. The 25,140 source events become
25,502. Every source paid occurrence remains, with the same ordered pair of
charts, rank and ownership. Some register names change to identify the
successor input. The new local helper profile is

```text
{1:4, 2:5, 4:90, 5:10, 7:5, 8:18, 9:410}.
```

For every 0<t<1 and positive a,b, strict concavity gives
`a^t+b^t>(a+b)^t`. Each split strictly increases the target moment and leaves
the paid moment fixed. The signed local target change is

```math
4H_1+5H_2+7H_4+5H_5+5H_7+3H_8-14H_9.
```

Its rank mass is zero, as required. A source-bound complete caller, not a
standalone packing relaxation, supplies the resulting exponent claim.

## 4. Native maps and the caller

The exact signed-Pauli and phase verifiers check every paid chart change,
every helper target and every main adapter. The local replay checks a strict
nested chart relation on each public move and the source's descending owned
moves. Each helper target is strictly productive.

Cinna Davis's p16/a7 controller and Ali Romman's all-forward implementation
from PR5544 remain literal inputs. All 18 full calls use the new local word
with fresh independent helpers. Sixteen backward main interfaces use the
retained signed exchanges and central-square translations. These wrappers
act only on the main pair. They do not alter a new helper output.

The physical caller check retains all 104 central ports, 7,488 boundary
contacts, 53,248 central-square column checks, 3,328 main Gaussian targets,
15 thin query sites and 3,120 whole idle jobs. It checks native routes,
spectators, exact phases and every whole target. The complete counts are

```text
paid calls:         66852
productive fields:  13084 = 18*542 + 32*104
rank mass surplus:  760
maximum target:     145
maximum paid rank:  72
```

The invoice is counted twice, once from literal events and once from the
controller path lengths. Input and output normalizers, added scalar basis
operations, routes, owned allocation and erasure, queries and idles are all
included. The new independent field count enters the completion-tail bound.
It is not left at the old 12,814 value.

## 5. Strictification, compiler and outer transfer

Two independent rational interval engines evaluate the complete moments.
The exact raw crossing is in (0.00309839352211, 0.00309839352212).
`RESULT.json` gives its rational endpoints and the strict tested margin. The claimed kappa is 0.00309839 and the tested saving is
0.0030983905. Their gap funds the finite compiler and outer parameters. An exact negative
derivative bound on [0,0.0034] makes this crossing the raw ceiling for this
fixed invoice under the retained BIT cap. It is not a global optimum.

Power 1024, cutoff 17, target floor 18 and tail offset 1/5 are retained.
The extra independent fields require a different tail bound: both charged
tail ratios are below 39/40, and `(39/40)^128 < 1/16`. Eight such blocks still
give the retained `2^-32` remainder. The fixed reserve is `10^-10`.
The complete normalized cost is strictly less than one. The old cutoff 20
fails and is retained as a control.

The compiler checks its finite integer threshold, initial range, shifted
exits, complement capacity, logarithm power 1024 and predecessor integer point. The old logarithm
power 1000 does not meet the new complement-capacity inequality.
The ordinary BIT saving remains 0.0034. All 54 strict outer conditions and
four functional conditions are checked with exact rational arithmetic.
The scalar growth bound uses fewer than 26,000 local operations and the
retained per-operation bound. The native growth bound uses the actual sum
of local paid ranks. The complete ordinary-work allowance remains below
`10^9`; the local scalar and route allowance remains below `10^7` per call.

## 6. Scope of acceptance

The five selected framework assumptions remain: native implementation at
all widths, owned erasure, uniform compiler closure, precision and tape
cost, and analytic integer recovery. The source helper-endpoint contract
also remains. This package proves the new finite interface, the chart
identities and every new numerical condition within that framework.

The enormous uniform word and complete rounded multiplier are not
materialized. These are author-side checks by the same AI-assisted author.
They are not independent human acceptance or a proof-kernel theorem.
Two greedy cut orders on PR5569 reached the same fifteen-split histogram.
That observation does not prove a maximum over bases, cuts, scalar programs,
frames, controllers or multiplication algorithms.
