# Fixed-word gauge theorem and its limits

All finite graph claims in this proof use the two source members in
`data/`, from historical commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The complete scalar program and
all native event positions remain fixed. A gauge is an invertible operator
on the full array. Native rank means the binary relative-frame rank used
by this source. This proof gives no new kappa value.

## 1. Exact boundary condition

Write the physical value on wire segment `v` as `T_v z_v`. Replace its
frame by `T_v G_v`. Use the same `G_v` for both live values of each scalar
ADD or COPY. A CLEAR starts a new zero value and gives no relation to the
old target gauge. Replace a native transition from `u` to `v` by

```text
T_v G_v G_u^-1 T_u^-1.
```

The scalar coefficients commute with these operators. Induction over the
program gives the new physical endpoint

```text
diag(T_out) diag(G_out) P diag(G_in)^-1 diag(T_in)^-1,
```

where `P` is the old scalar endpoint. The outer frames are invertible.
Thus the endpoint equals the old physical endpoint if and only if

```text
diag(G_out) P = P diag(G_in).
```

No commutation of a gauge with an old frame is assumed. This identity
includes global phases and holds for the full operators at every tensor
power.

Exact rational replay on all 712 input columns gives

```text
forward:  (x,y,h,c) -> (x,y+x,h,0)
backward: (x,y,h,c) -> (x-y,y,h,0).
```

There are 112 rows in each data bank, 480 arbitrary helpers, and eight
private values. The three nonzero blocks for each data pair force one
gauge at its four boundary points. Each helper forces one gauge at its
input and output. The private rows and columns of `P` are zero. They give
no boundary relation. The actual scalar accesses still give relations.
The full residual on a helper remains
`T_out G (T_in G)^-1 = T_out T_in^-1`.

## 2. Source graph and rank rule

Split each wire at every native event. Join only scalar ADD/COPY operands
and the boundary pairs from Section 1. The source gives 5,784 segments,
1,979 components, and 5,064 native events. Eight components are final
cleared private values with no native event. The other 1,971 components
meet native events. There is no fixed external gauge.

The native profile, including rank zero, is

```text
{0:1570, 1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}.
```

Its rank mass is 5,586. The events are 3,486 climbs, eight centres, 1,090
adapters, and 480 residual adapters. Thus a change at an old rank-zero
wrapper is charged.

For a frame subspace `U` in `F_2^9`, its inverse-image diagonal Pauli space is

```text
L_U = {(u,u+v): u in U, v in U-perp}.
```

It is a nine-dimensional Lagrangian. Two such labels have relative rank
`dim(L_U + L_V)-9`. Equivalently, the rank is the rank of their 9 by 9
symplectic pairing matrix. The two independent checkers use these two
formulas. Both check each old source rank. Left monomial wrappers preserve
this label.

A translation-line gauge has binary action

```text
S_a(x,z) = (x+a(a dot z),z).
```

This is a symplectic involution. Therefore a binary crossing has the same
rank at either end of an edge. Equal gauge bits leave the rank unchanged.
This statement is about ranks; Section 1 gives the separate exact endpoint
condition.

The forward and backward scalar partitions and undirected native graphs
are isomorphic. In backward coordinates the frame is `D_U=T_U F^-1`.
The line gauges commute with `F`, so the same line gauges have the same
ranks in both orientations. A general forward gauge `G` instead requires
backward gauge `F G F^-1` for this correspondence.

## 3. All 511 fixed lines

Fix one nonzero line vector `a` for the whole word. Each component may
choose `I` or `C_a`. The line cannot vary between components. After each
native event is priced, combine parallel edges. The rank change is

```text
E(epsilon) = sum_e w_e [epsilon_u != epsilon_v].
```

For each odd line, the exact certificates route every negative demand
`d=-w_(u,v)` from `u` to `v` through positive edges. Route amounts are
positive integers. They cover every demand exactly and use no positive
edge beyond its capacity. If a cut separates the endpoints, each route
crosses that cut at least once. Sum this inequality over the routes.
The capacity condition gives `E(epsilon)>=0` for every cut. A constant
assignment attains zero.

The two path certificates cover all 256 odd lines exactly once. They
contain 10,488 paths. The independent pairing checker verifies all
1,609,650 distinct-pair ranks over all 511 nonzero lines. The separate
span checker also verifies the full line family. For each of the 255 even
lines, every changed native edge has rank at least its old rank. Thus an
even line also cannot reduce any sum of nondecreasing native rank costs.

For the odd lines outside the common family below, the total-rank theorem
does not settle all child moments or the profiles of all zero-rank cuts.

## 4. Common lines and concave costs

The common intersection of the eight centre frames has basis

```text
30, 45, 75, 128, 256.
```

Its 16 odd vectors are

```text
128,158,173,179,203,213,230,248,
256,286,301,307,331,341,358,376.
```

For each line, an exact signed-cut certificate has minimum rank change
zero. If at least one centre edge is crossed, the minimum is 13. The
latter means at least one centre, not all eight centres simultaneously.
There are 3,384 exact flow/cut cases across these tests.

Here is the finite certificate argument. Choose a vertex cover of the
negative edges and enumerate every assignment to it. All remaining edges
between free vertices have nonnegative weights. A fixed/free edge gives
a unary cost. Subtract the smaller unary value into a constant and use
the difference as a source or sink capacity. Every case supplies an
integer feasible flow and a cut of equal value. Capacity, conservation,
branch coverage, cut value, and the original signed objective are checked
exactly. Their equality proves that branch's minimum. Enumeration proves
the global minimum.

Only the constant cover branches reach zero. In each such branch,
residual source or sink reachability forces every free native component
to the same side as the cover. Thus every rank-zero cut is constant on
all 1,971 native components. The eight isolated cleared values may vary.
The full native profile is unchanged at equality.

The separate capped-cost certificate proves minimum zero for
`f_k(r)=min(r,k)`, for `k=1,...,8`, on all 16 lines. It has 800 exact
flow/cut cases. All ranks in this family lie between zero and eight.
For `f(0)=0`, set `d_j=f(j)-f(j-1)`. If
`d_1 >= ... >= d_8 >= 0`, then

```text
f(r) = d_8 min(r,8)
       + sum_(k=1)^7 (d_k-d_(k+1)) min(r,k).
```

All coefficients are nonnegative. Hence every increasing concave rank
cost is nondecreasing. This includes `sum r^(1-b)` for `0<=b<1`. At `b=1`,
use zero at rank zero and one at every positive rank. That is the paid
child count `min(r,1)`.

## 5. Common products and the four-state family

For the binary family `I,G` with `G=C_128 C_256`, the changed edge ranks
are computed directly from the two commuting transvections. The exact
rank minimum is zero, and all rank-zero cuts have the same rigidity.
Capped-cost certificates through cap nine give minimum zero. The
nonnegative decomposition in Section 4 therefore applies through rank
nine.

For the four states `I,C_128,C_256,C_128 C_256`, every native rank table
depends only on the XOR of the endpoint states. The exact rank objective
has a pointwise lower bound which separates the two bits. Both signed
lower graphs have minimum zero and the same zero-cut rigidity. A constant
state attains zero in the true problem. Thus every zero-rank state choice
is constant on all native components.

For each cap, let `d_1,d_2,d_3` be the changes at XOR states `01,10,11`.
Put `m=max(0,d_1+d_2-d_3)`. The weights `2d_1-m` and `2d_2-m` give a
separable lower bound for twice the true edge cost. At states `01` and
`10`, this follows from `m>=0`. At state `11`, it follows from
`m>=d_1+d_2-d_3`. The check also verifies each actual table entry.
Both signed lower graphs have minimum zero at every cap from one to nine.
Thus the four-state family cannot reduce any increasing concave rank cost.
The solver status and exploratory saved state are not used in this proof.

## 6. Full-frame counterexample and its limited moment bound

The binary family `I,T_415` has rank minimum zero and rank-zero rigidity,
but its cap-one minimum is minus one. A cut which differs from a constant
only at component 608 removes one rank-eight centre child. Seven incoming
edges retain rank four; seven outgoing rank-one edges become rank nine.
The rank change is 48, and the profile is

```text
{0:1571, 1:2405, 2:418, 3:432, 4:142, 5:82, 8:7, 9:7}.
```

The child-moment change for this cut is
`7*9^(1-b)-7-8^(1-b)`. Thus a no-gain claim for every increasing concave
cost on this full-frame family would be false.

The exact cap minima for caps one through nine are `-1,0,0,0,0,0,0,0,0`.
Every native rank increment is even. Rank-zero rigidity therefore makes
every changed native cut have total-rank increase at least two. With
`a=1-b`, the threshold decomposition gives

```text
Delta sum r^a >= 2*(9^a-8^a) - (2-2^a).
```

For `3/5<=a<=1`, the first term is greater than `24/49`, and the
subtracted term is less than `97/200`. The exact integer checks
`49^5>81*20^5` and `303^5<8*200^5` establish these strict bounds.
Consequently every changed native cut has moment increase greater than
`47/9800` for `0<=b<=2/5`. Constant native gauges retain the profile.

`T_415` does not commute with `F`. This forward certificate applies to
`F T_415 F^-1` in backward coordinates. It gives no identical-`T_415`
claim there.

## 7. Local rank bound for arbitrary common-line products

Let `A subset U subset F_2^n`, let `e=dim(U)`, and let `s` be the rank of
the standard dot product restricted to `A`. Permit arbitrary products of
`C_a`, with `a in A`, at both ends of a native descent from `T_U` to the
identity. Their relative binary action has the form

```text
S_B(x,z) = (x+Bz,z),   B = sum_j a_j a_j^T.
```

Here `im(B) subset A`, and `B` kills `U-perp`. An intersection point of
`L_U` and `S_B L_0` has a unique form

```text
z=w+u,  w in U-perp,  u in U,  Bu=u.
```

A fixed vector of `B` in `U-perp` is zero. The intersection dimension is
`n-e+dim Fix(B|U)`, so the exact relative rank is
`e-dim Fix(B|U)`. Every fixed vector lies in `A` and in the image of
`B|A`. The map `B|A` factors through the dot-product map on `A`, whose
rank is `s`. Therefore

```text
native rank = e-dim Fix(B|U) >= e-s.
```

Applying a common symplectic map to both labels reduces two arbitrary
endpoint products to their relative product. Thus the same bound holds
with arbitrary common-line product gauges at both endpoints.

For the actual common basis, the Gram rows are `0,0,0,8,16`. The Gram
rank is two, and each centre has dimension eight. Hence each descent has
rank at least six. Direct pairing checks show that `C_128 C_256` attains
six at each of the eight centres. This local bound does not price the
rest of the scalar graph or exclude a complete-cost gain.

## Verification boundary

The replay checks the complete finite source words, exact rank tables,
integer path certificates, flow/cut witnesses, and 13 damage controls
under optimized Python. It does not emit a changed physical supplier.
The all-size compiler, hosting, precision, and analytic obligations of a
multiplication theorem are outside this package. Its graph-specific
conclusions do not transfer to a changed current construction without a
new source-bound proof.
