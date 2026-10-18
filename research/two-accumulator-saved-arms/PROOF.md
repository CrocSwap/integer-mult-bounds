# Complete cost of the eight saved-arm recipes

## 1. Declared method and free choices

Fix the source word and the eight gate recipes in this package. A call can
use any subset of the recipes. Different calls can use different subsets.
There are nine calls and 896 live data families per replica. Let `T` be any
positive integer number of replicas. Whole helpers can use any owner map
with the retained capacity stock. Helpers cannot be split. The stock per
replica is

| Capacity | Number of bins |
| --- | ---: |
| 8 | 672 |
| 16 | 448 |
| 32 | 448 |
| 48 | 448 |

The proof below even removes owner chronology, coordinate matching, and
per-call restrictions. Thus it gives a lower cost bound for all owners that
satisfy those additional restrictions. The method does not add physical
families, change the nine-stage schedule, or change the unpaid-coordinate
and centre law. The bit supplier and the outer recipe stay fixed.

The claim is an optimum for use of these eight completed recipes, including
the zero-recipe choice. It does not optimize arbitrary rational gates,
partitions, frame choices, or schedules. No finite synthesis search is used
as evidence for an all-order impossibility statement.

## 2. Local construction and exact finite bill

The old hub helpers are 448 through 455. Each has one entrance direction
and a rank-eight final frame, so its width is 7. In recipe `g`, helper
`448+g` keeps one pair sum until the full packet can be formed. The recipe
routes the old hub uses through their original source and uses the saved
pair to complete the packet in the other accumulator. It keeps the later
packet copy. It does not reduce the total count of 480 helpers.

The complete recipe includes 19 ordered core gates with explicit frames,
removal of two old entrance corrections, two changed cleanup operands, and
four final full-frame corrections. The new saved-pair helper starts at
frame zero and ends at the full rank-nine frame. It therefore has width 9.
Its arbitrary initial value is not assumed to be zero. The four final
corrections remove its dirt from the affected packet and later helper
columns. The normal frame-zero compensation also uses this helper. This
explains why retaining its former low endpoint is not a free option.

The recipes have explicit pins to every replaced source gate. Their changed
gate sites and cleanup sites are disjoint. The check replays every one of
the 256 subsets with exact rational arithmetic. It checks the complete
704-column forward and inverse-transpose maps, source reads, monotone
frame paths, centre levels, helper entrances, and both low-end cones. The
native check separately verifies the emitted all-eight word, wrappers, and
Clifford phases. These are finite construction checks, not a formal proof
of the full multiplication theorem.

Write `H_r` for one rank-`r` child. The exact local changes are

```text
even g in {0,2,4,6}:  -2 H1 + 2 H2,
odd  g in {1,3,5,7}:           H2.
```

Every recipe adds two local rank units and changes one width 7 to width 9.
The baseline local profile is
`{1:2412,2:418,3:432,4:142,5:82,8:8}`. Its rank mass is 5586. Its width
inventory, in width order `(4,5,7,8,9)`, is `(56,32,30,122,240)`.

Let `E` and `O` now count individual even and odd recipe uses over all
`9T` calls, and put `Z=E+O`. These counts need not be uniform across calls.
The complete residual rank mass is

```text
M = 14814 T - 2 Z.
```

The complete mass remains `73*896*T - 320*T`. This includes the eight
rank-eight centre paths per call. The saving cannot come from a new deficit.

## 3. A necessary inequality for every owner

Use the signed prices from the PR1129 whole-helper proof, which credits
PR795 and the PR890/PR942 proof chain:

```text
width price at (4,5,7,8,9): (-1,-20,-8,-2,4),
capacity bonus at (8,16,32,48): (2,4,8,-13).
```

For residual rank `r`, let `u(r)` be the largest bonus plus price of any
legal bin pattern with that residual. There are 1,163 legal patterns.
Enumeration and an independent unbounded-fill recurrence give the same
table. In particular,

```text
u(0)=0, u(1)=19, u(48)=-13.
```

The baseline total signed price is `-1084 T`. A width-7 to width-9 change
adds 12, so the changed total is `S=-1084 T+12 Z`. If `n_r` counts residual
bins, every whole-helper assignment satisfies

```text
sum r*n_r = 14814 T - 2 Z,
sum u(r)*n_r >= -1084 T + 12 Z.
```

Set `v(r)=48*u(r)+13*r`. Then `v(0)=v(48)=0`, `v(1)=925`, and

```text
sum_(0<r<48) v(r)*n_r >= 140550 T + 550 Z.       (1)
```

The additional demand is `48*12-13*2=550` for each recipe use. The sign is
positive. A model that consumes arbitrary rank-one idle mass misses this
new packing restriction.

## 4. Supporting inequality at the baseline optimum

For a complex saving `b`, let

```text
f_b(r) = (r/73)^(1-b),
c_b(r) = 48*f_b(r) - r*f_b(48),
lambda_b = c_b(1)/925.
```

The baseline whole-helper optimum has its root in

```text
I = [0.001676905273619680861300,
     0.001676905273619680861301].
```

The exact interval checker proves, for every `b` in `I`,

```text
lambda_b > 0,
c_b(r) > lambda_b*v(r)
  for each attainable 0<r<48 other than r=1.      (2)
```

At ranks 0, 1, and 48 the required non-strict inequality is exact. The
checker encloses each exponential with rational atanh and Taylor bounds.
It uses interval endpoints according to each coefficient's sign. There
is no floating-point sign test. Since `r<73`, each `f_b(r)` increases with
`b`, which justifies the endpoint choices.

Use (1) and (2), and eliminate the residual mass term. They give

```text
sum f_b(r)*n_r >=
 T*((5622/37)*f_b(1) + (11302/37)*f_b(48))
 + Z*((22/37)*f_b(1) - (2/37)*f_b(48)).          (3)
```

For example, the coefficient of `f_b(1)` is
`(140550*T+550*Z)/925 = (5622*T+22*Z)/37`. The coefficient of `f_b(48)`
is the remaining mass divided by 48. This proves the claimed residual
increment without assuming that the fractional counts can be attained.

## 5. Every nonempty use has a larger complete moment

Combine (3) with the exact local changes. The complete increment for one
even recipe is

```text
Delta_even = (2/37)*(37*f_b(2)-26*f_b(1)-f_b(48)).
```

The complete increment for one odd recipe is

```text
Delta_odd = (1/37)*(22*f_b(1)+37*f_b(2)-2*f_b(48)).
```

Both are strictly positive for every `0<b<1`. Here is a proof that does
not use numerical samples. For `s=1-b`, the function `x^s` is strictly
concave on nonnegative real numbers. In decreasing order, the vectors

```text
(48, 1 repeated 26 times, 0 repeated 10 times)
(2 repeated 37 times)
```

have the same length and sum. Each initial partial sum of the first vector
is at least the corresponding sum of the second. The vectors differ.
Strict concavity therefore gives
`48^s+26 < 37*2^s`. This proves `Delta_even>0` after multiplication by
the positive factor `73^(-s)`.

The same argument applies to

```text
(48, 48, 0 repeated 57 times)
(2 repeated 37 times, 1 repeated 22 times).
```

Their common sum is 96. It gives `2*48^s < 37*2^s+22`, which proves
`Delta_odd>0`. The checker verifies every integer partial-sum inequality.
Strict concavity supplies the theorem for the whole open interval.

At the baseline optimum root `b0` in `I`, the unchanged complete moment is
`896*T`. Every changed owner with `Z>0` has moment at least

```text
896*T + E*Delta_even + O*Delta_odd > 896*T.
```

All complete moments increase with `b`. Thus every nonempty finite mixture
has a complex root strictly smaller than `b0`. The argument permits all
positive replica counts and all per-call subsets. The 256 finite checks
establish the recipe bills; they are not the reason that the number of
replicas can be unbounded.

## 6. Attainment and kappa

The zero-recipe choice retains the PR1129 local word and owner inventory.
PR1129 supplies an exact attaining whole-helper pattern table and a
literal time-compatible T37 owner map. Its root is `b0`. This package
rechecks the pattern counts and the root bracket. The existing native
global and independent owner receipts remain predecessor evidence with
explicit pins. The global owner construction is not rerun here.

The retained bit endpoint is `0.001733427039589844234749`, above `b0`.
The retained outer recipe is monotone in the complex endpoint in this
range. Its seven updates have the form `a_next=s*(1-s+a_old)` with fixed
strict reserves. PR1129 checks all 47 inequalities and both endpoints
of `I` give the same outer grid value,

```text
kappa = 0.001674097969905390.
```

It follows that no member of this method family improves that value.
The zero-recipe choice attains the family optimum under the inherited
admission contract. A very sparse nonempty mixture can tie the same rounded
grid value; the strict statement concerns the complex root, not every
rounded display value. There is no claim of a new kappa.

This argument uses the actual changed helper widths and all residual mass.
It remains valid if a changed word has further owner or physical-admission
restrictions. Those restrictions cannot lower the cost below this relaxed
bound. It gives no obstruction for a new local bill outside these recipes.
