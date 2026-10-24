# An explicit no-idle border controller

The ambitious question was whether the controller can eliminate its entire
whole-idle invoice, which the contemporaneous #4602 planning screen identifies
as roughly 56–59% of the paid moment. Deleting those calls and retaining their
productive credit is invalid. The actual controller below loses precisely the
corresponding productive rank mass. It nevertheless has an explicit diagonal
border with a better *formal* moment. This is a changed interface, not another
frame-lattice search. Its conversion to a paid exact supplier is a separate
obligation; the calculations here do not establish a new multiplication bound.

The construction uses the no-idle event word of
`research/kappa-rebuild/bit/complex_controller_factor.py`, followed by the
query thinning in `research/query-thinned-controllers/controller.py`. The local
native contract remains the source one. The formal variables commute; they
are not evaluated at Fourier characters or treated as involutions over Q.
The source authors are zxv and Cinna Davis with the controller and native
predecessor chain retained in those packages.

## Exact all-pairs formula

Take p >= 2 pairs `(X_j,Y_j)`, indexed 0 through p-1. Retain full native stages
`0,1,3,...,2p-1,2p`; replace every other local stage by the credited paid query
shear. Delete every whole IDLE event. Keep every bridge and final signed swap.
There are p+2 full native calls and p-1 queries per port. Define commuting units

```
d_0 = D_0 D_1,
d_j = D_(2j+1)                 (0 < j < p-1),
d_(p-1) = D_(2p-1) D_(2p).
```

The resulting matrix A has no mixed X/Y blocks. Its X block is `Q^-1 U` and
its Y block is `Q V`, where

```
U_ii = d_i,
U_ij = (-1)^(j-i-1) (1-d_j)                         (i < j),
U_ij = 0                                            (i > j),

V_ii = d_i,
V_ij = (-1)^(i-j-1) (product(k=j..i-1) d_k) (1-d_i) (i > j),
V_ij = 0                                            (i < j).
```

For p=1, the original F/B/F triple is already diagonal with
`d_0=D_0 D_1 D_2`. All these formulas have integral coefficients and therefore
reduce coefficientwise modulo two. That reduction checks the formal algebra;
it does not supply the physical BIT scalar-extension implementation.

### Derivation from the actual chronology

Let x_j,y_j denote the original input values. After a pair's backward stage,
its two bridges and its forward stage, but before the reverse chain of bridges,
write the pair values as a_j,b_j. Direct substitution of the source shear
formulas gives

```
a_j = -Q d_j y_j - d_j a_(j-1),       a_-1=0,
b_j = Q^-1 (d_j x_j + x_(j+1))       (j < p-1),
b_(p-1) = Q^-1 d_(p-1) x_(p-1).
```

For j=0 the initial forward stage makes the backward-stage X value
`-Q D_0 D_1 y_0`. For an interior pair, the preceding two bridges present
`Y_j = y_j + Q^-1 x_j + Q^-1 a_(j-1)` to its backward stage; this gives the
recurrence for a_j. The same pair's thin forward shear and bridge update give
the displayed b_j and prepare the next Y input. At the final pair, the last
full forward stage multiplies both outputs by D_(2p), giving the last d_j.
This proves the recurrence by induction through the source events.

The reverse bridge chain, in decreasing j, changes the X values to
`a_j+a_(j-1)` and the Y values to
`b_j-b_(j+1)+b_(j+2)-...`. The final signed swap therefore returns

```
X'_j = sum(k=j..p-1) (-1)^(k-j) b_k,
Y'_j = -(a_j+a_(j-1)).
```

Substitution of the recurrence proves U and V term by term. Setting all
formal variables to one gives A(1)=I. Thus no additional constant
normalization is required in this example. In particular, a claimed control
that omits A(1)^-1 would be vacuous and is not counted as evidence.

## An explicit filtration

Put `w(X_j)=j` and `w(Y_j)=p-1-j`, and let E(epsilon) be the diagonal matrix
with entries `epsilon^w`. In

```
B(epsilon) = E(epsilon)^-1 A E(epsilon),
```

an entry at row i, column j acquires exponent `w(j)-w(i)`. Every diagonal
entry has exponent zero; every nonzero off-diagonal entry has positive exponent.
Consequently B is a polynomial in epsilon of degree exactly p-1, and

```
B(0) = diag(Q^-1 d_0, Q d_0, ..., Q^-1 d_(p-1), Q d_(p-1)).
```

All local helper outputs remain the source's separate diagonal productive
operators when the epsilon wrappers act only on main fields. This statement
uses the full arbitrary-input native endpoint contract. It does not grant
productive credit to owned interpolation copies or fresh scratch.

`border_algebra.py` independently builds this closed formula and compares every
Laurent coefficient with the literal source emitter for p=1,...,8. The source
emitter is loaded by extracting only its three pure polynomial functions;
source imports, unrelated verification code and external files are not executed.
The checker also verifies A(1)=I, the exact border degree, integral coefficients,
wrong-backward-sign rejection, and rejection of reversed scaling weights.

## The actual formal invoice

For p>=2, per port the diagonal has four rank `1+2b` fields and `2(p-2)` rank
`1+b` fields, with b=8 for the complex source and b=7 for BIT. It has p+2 copies
of the source's local productive helpers and local paid jobs, plus p-1 paid
rank-one queries per port. There are no whole-idle paid jobs. The rank-one
surplus is still `48(p+2)-ports`: deleting idle work also deletes its productive
rank mass. No new rank mass has been created by a singular limit.

For complex p16, the resulting *formal border* profiles are

```
T = {4:504, 7:126, 8:846, 9:9004, 17:448},
P = {1:41946, 2:6984, 3:8892, 4:2646, 5:648, 8:144}.
```

Their rank masses are 98,318 and 97,566, leaving surplus 752. The original
#4470 main target mass was 177,408; the removed idle mass was 141,568; the new
main target mass is 35,840. Keeping the old 177,408 would be an unearned credit.

Exploratory floating-point moment roots (not certified endpoints) are:

| p | Complex formal border root | BIT formal border root |
|---|---:|---:|
| 2 | 0.002118505300 | 0.002463371003 |
| 4 | 0.003220993919 | 0.003716919894 |
| 8 | 0.004162555165 | 0.004785768721 |
| 16 | 0.004822180518 | 0.005533618177 |
| 32 | 0.005222843492 | 0.005987486573 |
| 64 | 0.005445483624 | 0.006239566631 |

The checker recomputes every p=1,...,64 and also a favorable relaxation that
balances the same main target mass across all 2p ports. At p16 that relaxation
has complex root approximately 0.004855075634, so this topology cannot plausibly
supply the original >0.01 ambition merely by balancing these main ranks.
That explicit limitation is part of the outcome. If exactification can preserve
the formal moment asymptotically, removing the idle requirement would still be
a qualitative new compiler interface. We do not rebrand its roughly 60% p16
formal headroom as the more ambitious factor-three target.

## Costs that must be paid before using the border

The inverse epsilon powers in the input/output wrappers prevent executing the
limit by setting epsilon to zero. A valid conversion must construct a finite
exact algorithm, count every evaluation of the native word, retain all separate
arbitrary productive inputs, and charge copying, combination, scalar coefficients,
owned storage and eventual erasure. Conditioning and bit precision must follow
the actual interpolation nodes and tensor power.

Over characteristic two, evaluation may require a finite extension or another
coefficient-extraction representation. Its coordinate expansion, copies, scalar
linear maps, and return to ordinary BIT must be explicit. A characteristic-zero
argument is not a proof of that conversion. Any tensor amplification must use
an allowed product of the actual operator word rather than silently replacing a
product of sums by a tensor of a chosen endpoint. Native matching, the mixed
compiler, ordinary BIT conversion and every outer cost row remain obligations.

## Open next questions

Can one prove a fully charged border-to-exact theorem for these mixed-target
native words, with only subexponential overhead under a legal amplification?
The first test is exact coefficient extraction for the p2 polynomial, including
all borrowed/owned fields and both orientations. A positive algebraic identity
alone does not close that question. A negative moment after charging extraction
must stop a dependent construction round or force a genuinely different
interface or topology.

### The chronological-product obstacle

The source moment-product theorem is not the ordinary tensor product of the
whole endpoint matrix. It pauses parallel U copies at every paid position and
runs V on their current requested fields. Its proof uses the exact diagonal
endpoint of V before resuming U. Replacing V by a polynomial with off-diagonal
errors inserts new cross-copy errors at every such position. Correctness modulo
epsilon can survive, while polynomial degree may grow with the expanded
chronological program rather than linearly in the number of product levels.
Therefore the familiar linear-degree interpolation argument for a tensor power
is not available merely from the degree-p-1 raw border.

One possible invariant would use a compatible global filtration on every
suspended field and owned bank. It must prove that errors cannot move down in
an outer role while moving up in an inner role. Without such compatibility,
lexicographic weights can grow exponentially and erase the hoped-for moment
gain. No such invariant is proved here.

There is also a simple losing exact-correction route. Let S be strictly upper
triangular with `S_ij=(-1)^(j-i-1)` for i<j. Then

```
U = (I-S) diag(d) + S.
```

Retaining raw inputs, subtracting `Q^-1 Sx` and multiplying by `(I-S)^-1`
recovers the X diagonal exactly. The literal direct implementation needs p-1
independent Q applications per port because S has rank p-1. For p16 it adds
1,680 rank-one jobs to a formal surplus of 752, before any Y correction.
That implementation already loses at rank one. This is not a universal lower
bound for every physical decoder: the existing paid thin queries could
conceivably expose reusable central-Q data. Such reuse needs an actual
chronological ownership/restoration proof and its complete bill.
