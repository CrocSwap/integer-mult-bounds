# The pair-consistent certificate

Put `p=4984891121/5000000000` and `f(r)=r^p`, with `f(0)=0`.
All objects below refer to the authenticated forward graph from #4994.
The predecessor's graph/realization and complete marginal-interval theorems
are cited premises. No native endpoint or physical phase theorem is reproved.

## 1. A relaxation containing every legal frame assignment

A vertex v carries a binary subspace U_v. Each mapped edge e:u->v imposes
`G_e U_u contained in U_v`. Its paid rank is `dim U_v-dim U_u` because G_e
is invertible. Repeated identical edges retain their multiplicity. Fixed
vertices and eight rank-eight center jobs retain the source charges.

The predecessor interval theorem gives the least and greatest feasible
subspaces L_v,H_v and proves that every subspace between them is an attainable
single-vertex marginal. Enumerate each complete interval D_v by enumerating
all subspaces of H_v/L_v. This does not assume that arbitrary simultaneous
marginal choices are feasible.

Introduce nonnegative x_(v,a), for a in D_v, with sum_a x_(v,a)=1.
For every edge with two flexible ends, introduce nonnegative
z_(e,a,b) only for pairs satisfying `G_e a contained in b`. Impose

```text
sum_b z_(e,a,b) = x_(u,a) for every a in D_u
sum_a z_(e,a,b) = x_(v,b) for every b in D_v.
```

When an end is fixed, charge its edge price directly to the remaining
x variable. When both ends are fixed, add its price to the constant.
For a two-flexible-end edge, charge z_(e,a,b) by its multiplicity times
`f(dim b-dim a)`. Include all eight center jobs in the constant.

Every legal integral frame assignment induces a feasible point by choosing
its one node marginal and compatible edge pair. It has exactly the same bill.
No assumption that every fractional point has a global frame realization is
needed. Therefore the LP minimum is a lower bound on the legal minimum.

The deterministic builder gives A x=b, x>=0, objective c^T x+c0, with
24,788 columns and 15,524 rows. It retains all 29,790 mapped edges and all
4,684 subspace choices across all 1,339 flexible contacts. This includes the
large component as well as the previously settled small components.

## 2. Symbolic weak duality

The certificate gives one vector d_i in Z^5 for every equality row. Set

```text
y_i = d_i1*f(1) + ... + d_i5*f(5).
```

All variable costs use ranks zero through five; the verifier checks that
condition explicitly. The remaining fixed costs are in c0. For each column j
it computes the coefficient vector

```text
s_j = c_j - sum_i A_ij*y_i.
```

Here c_j and s_j denote exact linear combinations of the five prices.
For every distinct nonzero s_j the directed bounds in section 3 prove
`s_j>0` at the stated p. The zero vector evaluates exactly to zero.
Consequently A^T y<=c, so for every feasible x,

```text
c^T x + c0 >= y^T A x + c0 = y^T b + c0.
```

This uses only nonnegativity of x and the explicitly checked equalities.
It does not rely on a solver's status or on LP strong duality.

The certificate also gives the indices of an integral feasible x. Every row
and index bound is checked exactly, and the associated node assignment passes
every original mapped containment and fixed vertex. Its objective, the dual
objective and the source objective are equal coefficient by coefficient to

```text
2201*f(1) + 412*f(2) + 510*f(3) + 127*f(4) + 40*f(5) + 8*f(8).
```

Thus the LP and legal integral problems both attain this exact minimum.
The attained frame labels need not be unique. This proof says nothing about
other tariffs, the backward graph or different native words/boundaries.

## 3. Exact directed power bounds

Let S=2^192. First write r=2^k a with 1<=a<2, and use

```text
log(a) = 2*sum_(j>=0) t^(2j+1)/(2j+1), t=(a-1)/(a+1).
```

The first 128 summands, each rounded down in units 1/S, give a lower bound.
Their total rounding loss is below 128/S. The remaining positive tail is at
most `2*t^257/[257*(1-t^2)]`, which the checker proves is less than 1/S.
Thus adding 129 units gives a rigorous upper bound. The same construction
bounds log(2); combine it with k and multiply by the exact rational p,
rounding the lower product down and the upper product up.

The resulting interval [l/S,u/S] for p log r lies in [0,3]. Expand its
exponential through degree 256. Recur on integer lower terms with floor
multiplication by l/(S*j), and upper terms with ceiling multiplication by
u/(S*j). Each recurrence encloses the corresponding exact Taylor term.
Their sums therefore enclose the partial series. The positive remaining
series is at most

```text
(3^257/257!) / (1-3/258) < 1/S,
```

which is checked exactly as a rational inequality. Add one unit to the upper
sum. For r=1 use the exact interval [S,S]. This proves every returned power
interval contains S*f(r).

Evaluate each signed reduced-cost polynomial by using the lower endpoint
for positive coefficients and the upper endpoint for negative coefficients.
All 383 distinct nonzero coefficient vectors have strictly positive lower
bounds. The arithmetic uses integers and Fraction throughout. Finite bound
widths and Taylor remainders are checked, not assumed from decimal precision.

## 4. What the certificate establishes

This is a finite exact optimization certificate for a specified source-bound
frame contract. Its consequences for any native schedule use #4994's inherited
graph contract. No predecessor scientific verifier runs. No independent human
review, formal proof kernel, physical implementation, complete supplier invoice
or multiplication theorem is claimed. The current selected frontier is unchanged.
