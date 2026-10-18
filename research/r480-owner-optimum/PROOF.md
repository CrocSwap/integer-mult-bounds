# The fixed R480 owner optimum

This note fixes the seven-slot k8 word from Jeremy Kothe's PR1074 at
`052afc128954f7b6a2b3c409eb4d72248e4020f2`. Its source package is
`research/gauge44-slots-t16`. PR1018 applies the seven-slot construction,
which credits Rohan Arun's PR987 search, to the R480 k8 leaver word.
This note changes the owner assignment. It does not change that local word.

The result is conditional on the same local supplier and physical interfaces.
It is not a formal proof of integer multiplication, an unconditional bound,
or a measured runtime gain. The selected result is not changed by this package.

## 1. Fixed inventory

Each replica has nine complete calls and 896 live data families. Each call has
480 whole helpers. Their widths are

```
width:     4   5   7    8    9
count:    56  32  30  122  240
```

The paid local child profile is

```
{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}.
```

Each replica has 672 bins of capacity 8 and 448 bins of each capacity 16, 32,
and 48. Thus the helper width per call is 3730. The local paid rank mass is
5586. The residual rank mass per replica is

```
M = 8*672 + (16+32+48)*448 - 9*3730 = 14814.
```

The complete deficit remains `73*896 - 9*5586 - 14814 = 320` per replica.
The gain comes from the child-rank distribution. It does not come from a new
rank deficit. PR1069 independently describes this distinction for recent claims.

The inputs retain the full PR1074 SPEC and PLAN. The checker compares the
provider width list, local profile, complete call set, and per-replica capacity
stock. Source files and arithmetic engines have SHA256 pins. These comparisons
bind a declared cost contract; they do not replace the local scalar proof.

## 2. A necessary inequality for every positive replica count

Use the signed width prices from Chafik Boukhalfa's PR795 and the retained
PR890/PR942 proof:

```
width price at (4,5,7,8,9): (-1,-20,-8,-2,4)
capacity bonus at (8,16,32,48): (2,4,8,-13).
```

For a residual rank `r`, let `u(r)` be the maximum capacity bonus plus signed
width price over all legal patterns that leave `r`. The checker enumerates all
1,163 patterns. A separate fill recurrence gives the same table. In particular,
`u(0)=0`, `u(1)=19`, and `u(48)=-13`.

For `T` replicas, let `n_r` be the number of bins with residual rank `r`. All
helper roles occur exactly once. Therefore their total actual signed price is

```
S*T = [672*2 + 448*(4+8-13)
       + 9*(-56-20*32-8*30-2*122+4*240)]*T = -1084*T.
```

Each bin's actual price is at most `u(r)`. Thus

```
sum r*n_r = 14814*T,
sum u(r)*n_r >= -1084*T.
```

Eliminate `n_48` and use `u(0)=0`. With

```
v(r) = 48*u(r)+13*r,
v(1) = 925,
```

we obtain the necessary inequality

```
sum_(0<r<48) v(r)*n_r >= 140550*T.                 (1)
```

The PR942 U8 theorem has different right-hand sides. It cannot be reused by
keeping its U8 profile or its demand 150. Equation (1) is for this R480 inventory.
The prior PR1034 mixed-catalogue theorem also excludes this new inventory.

## 3. Supporting moment inequality

Let

```
I = [0.001676905273619680861300,
     0.001676905273619680861301],
phi_b(r) = r*(73/r)^b,
c_b(r) = 48*phi_b(r)-r*phi_b(48),
lambda_b = c_b(1)/925.
```

For every `b` in `I`, both retained exact rational engines certify

```
lambda_b > 0,
c_b(r) > lambda_b*v(r)   for every attainable 0<r<48, r != 1.
```

At rank one there is equality by definition. The certificate encloses `phi`
over the complete interval `I`. It uses the lower endpoint for a positive
lower bound and the upper endpoint for a positive upper bound. It reverses the
chosen endpoint when it multiplies by a negative integer. No floating-point
sign decision is used.

Multiply (1) by `lambda_b`. The residual moment then satisfies

```
sum phi_b(r)*n_r / T
  >= (5622/37)*phi_b(1) + (11302/37)*phi_b(48).    (2)
```

This follows by writing the left side as
`(14814/48)*phi_b(48) + sum_(r<48) c_b(r)*n_r/(48*T)`.
The arithmetic is `140550/925 = 5622/37` and
`(14814-5622/37)/48 = 11302/37`.

The bound permits all positive integer replica counts. It removes chronology,
per-call matching, coordinate charts, and finite precision constraints. These
relaxations can only lower the possible moment. The strict supporting margins
imply that equality has no nonzero residual rank other than 1 and 48. Equality
also requires (1) to be tight. Both normalized counts then force `37 | T`.
This is a necessary equality condition, not a uniqueness claim for owners.

## 4. An exact bin construction

The following bin pattern counts attain (2) at `T=37`. The width-count vector
uses the order `(4,5,7,8,9)`.

| Capacity | Width-count vector | Number of bins | Residual rank |
| --- | --- | ---: | ---: |
| 8 | (0,0,0,1,0) | 24864 | 0 |
| 16 | (0,0,0,2,0) | 3306 | 0 |
| 16 | (0,0,1,0,1) | 9394 | 0 |
| 16 | (2,0,0,1,0) | 3876 | 0 |
| 32 | (0,0,2,0,2) | 298 | 0 |
| 32 | (0,1,0,0,3) | 10656 | 0 |
| 32 | (1,0,0,0,3) | 5622 | 1 |
| 48 | (0,0,0,0,0) | 11302 | 48 |
| 48 | (1,0,0,1,4) | 5274 | 0 |

The checker sums every capacity and helper width. It requires exact equality
with the full inventories, not only with total occupied width. This table
proves attainment of the bin relaxation. The next section supplies its actual
time and physical-family assignment.

## 5. From exact pattern flow to literal owners

The call order is the source-bound PR942 T37 order. Each replica retains the
same 30 source events. A pending child can host a complete call only after its
last physical-pair touch and before its idle event. Bridge touches are included.

`PATTERN-FLOW.json` contains integer pattern counts and integer assignments of
widths to call times. It groups the two equivalent child sides, with 224 ports
per group. For each group and pattern, the certificate has `N` bins. It assigns
exactly `N*n_w` width-`w` roles, and at most `N` roles at each call time. Each
call receives the exact width inventory above. All assigned times are in the
actual source-event window.

`construct.py` converts each group and pattern to `N` literal bins. Split each
width vertex into `n_w` vertices of degree `N`. The other vertices are call
times, each with degree at most `N`. This is a bipartite multigraph. A matching
can cover every width vertex and every time vertex of degree `N`: add dummy
vertices and edges to obtain an `N`-regular bipartite graph, and take a perfect
matching. Remove it and repeat. The implementation obtains the same covering
matching directly with augmenting paths. It checks the degree invariant after
each removal.

Each matching names one physical bin. Thus no bin uses two helpers from one
call. The constructor assigns the bins to literal child/port coordinates and
assigns the local helper numbers of each width to the resulting slots. It
sets offsets to contiguous prefixes. Its output must equal the frozen owners
as a complete decoded JSON value. Compression-container bytes are not used
as mathematical equality.

The final map has 159,840 roles in 333 calls. Its residual profile is
`{1:5622,48:11302}`. The independent owner audit reconstructs source-event
windows and orthogonal 73-axis charts without importing the constructor or
flow model. The global controller audit checks the emitted program and its
phase projections. These audits are separate from the bin theorem.

The independent audit also checks that distinct pending children on one
physical family have disjoint axes. It checks all 2016 child/port bases.
A control copies one axis into a second child of the same family. It must
fail at this disjointness guard. Josie Elliston's PR1091 identified this
explicit check in the concurrent T16 audits.


## 6. Complete moment and outer recipe

The complete T37 profile is

```
{1:808818, 2:139194, 3:143856, 4:47286,
 5:27306, 8:2664, 48:11302}.
```

It has 33,152 live families, rank mass 2,408,256, and deficit 11,840. Both
rational engines accept the lower endpoint of `I` and reject the upper endpoint.
The proper-child guard is `73^2 > 2*48^2`.

Equation (2) applies throughout `I`, so it applies at the unique root of this
profile's strictly increasing moment. Every other packing has at least that
moment. The table attains it. This proves the optimum complex root in the bin
relaxation. The finite owner construction attains the same profile.

The unchanged PR589 bit endpoint is `0.001733427039589844234749`, with its
exceptional-residue surcharge. It is larger than the complex endpoint. The
retained seven-step outer recipe is monotone in this range. Each update is
`a_next=s*(1-s+a_old)`. Both relevant partial derivatives are positive here;
the final map in `a` is also increasing. The strict reserves remain fixed.
Both endpoints of `I` give the same outer grid value:

```
kappa = 0.001674097969905390.
```

All 47 inequalities are checked. The next grid value is rejected. This is a
global grid optimum for this word, whole-helper capacity inventory, and fixed
outer recipe. It is not a ceiling for another word, helper splitting, new
capacity stock, another outer reduction, or relaxed restoration rules.

## 7. Scope of physical admission

The bank envelope uses 8+8+8+8+5 lanes. Its five groups retain the inherited
504-helper dedicated banks, which provide a conservative reserve envelope.
The final hosted construction removes those banks. It uses the 480-helper
local word and has 33,642 physical families. The partial group's complement
coordinates are recomputed. They are not selected recursive children.

The finite invoice charges 1024 complex prefix bits. The local prefix is 68,
and `68+37+333+333+4=775`. The bit allowance stays 512. The independent row coefficient is 17495, below
20161. The global audit checks 1110 source events, 666 pending windows, and
11150 distinct orthogonal charts. The full invoice recounts
all helper operations, wrappers, scalar work, bridges, shifts, moves, local
adapters, recursive children, and final corrections. The seven finite bootstrap
cutoffs use the new complex allowance. `CODE-DERIVATION.patch` records every
change from the immutable PR1074 code. Verification executes normal source
files; it does not patch imported modules at runtime.

The all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, exact-recovery, analytic-transfer, and bit H1-H5 obligations
remain inherited. Passing finite checks does not discharge these assumptions.
