# A complete local-ring fallback with fresh child fields

This note makes the bad-class construction in the pinned
`research/five-stage-source527-banks/proof/three-stage-cover-bit.tex`, lines
161–195, explicit. The elimination argument, diagonal covariance and child
allowance are inherited mathematics. The contribution is their full
chronological specification, field-dependency boundary and exact nonunit
witness for the accompanying checker. The source's numerical example has
dimension 67. Only its generic construction is used below; the selected
dimension 64 is a separate instantiation.

## 1. Contract and covered domain

Fix an odd prime q, an integer w >= 1, and R = Z/q^w Z. Fix m >= 1 and
N = 2m. A parent has f >= 1 atoms in each of N complete coarse fields,
ordered by their physical position, 0 through N-1. There may be arbitrary
complete intervening, preceding and following spectator fields. The matrices
and coefficients below are ADDRESS maps over R, not additions of stored BIT
values.

For each atom column j, let M_j(a) be an invertible N by N matrix over R,
where a contains only exposed parent/ancestor fields and fixed program
parameters. Assume det(M_j(a)) = delta in {1,-1}, with delta fixed across
columns at this parent. The supplier application has delta = (-1)^r.
No matrix coefficient, pivot choice or instruction list may read unused
descendant stock u, the active head/data address values x, or the stored
VALUE payload v. The required record-address map is

```
(a, u, (x_j)_(0 <= j < f), v)
    -> (a, u, (M_j(a) x_j)_(0 <= j < f), v).
```

Every input factor is arbitrary. In particular, this is a permutation
transporting arbitrary stored values, not a zero-input computation. Its
inverse uses M_j(a)^-1 and fixes the same spectator factors.

For a common instruction skeleton across columns, assume

```
M_j = B_j M_0 B_j^-1,
```

where B_j is diagonal with unit entries and M_0 is independent of j. This
is the retained weighted-residual form. More generally the pivot argument
below works for independent left and right diagonal unit multipliers. The
matrix M_0 may depend on the parent's full current chart; its reduction
modulo q depends only on that chart's low residue. The parent chart has
become an ancestor at every child boundary.

For the cost statement retain these abstract operations:

* A later-target shear on complete fields, with an ancestor-controlled
  coefficient descriptor, is a paid ordered-affine adapter.
* A completed weighted reversed child of k atoms implements
  `F_A(H,D) = (A C_k D, C_k A^-1 H)`, preserves complete spectators and
  restores its supplied row. Here A is diagonal with unit entries and
  C_k reverses atom positions, not digits within atoms.
* A fixed sign on an address field is a paid nonrecursive adapter.

These are explicit inherited interfaces. This note proves their algebraic
composition and counts their calls. It does not implement their tapes,
controllers, physical routing, or internal row borrowing.

## 2. Low-only pivot plan, full-width elimination

Let E_ik(c) denote the elementary matrix adding c times row k to row i,
for i != k. Maintain a full matrix T over R, initially M_j. At stage k:

1. In rows k through N-1 choose the least p with T[p,k] nonzero modulo q.
2. If p != k, interchange rows p and k.
3. Let d = T[k,k]. For every i != k, in a fixed order, compute
   `c = -T[i,k] * inverse(d)` in R, and replace T by E_ik(c) T.

A pivot always exists. After the previous stages, T has a diagonal unit
block in its first k columns and an invertible trailing block. The latter
is invertible modulo q, so its first column contains a nonzero residue.
That entry is a unit in R. Clearing the whole column preserves invertibility
and leaves an invertible smaller trailing block. Induction therefore ends
at a diagonal matrix D with unit entries d_0,...,d_(N-1).

This uses at most N swaps and N(N-1) row additions. An implementation may
omit an addition only when its full coefficient is zero in R. Keeping every
addition, including zero coefficients, gives a fixed skeleton once the pivot
rows are known. A coefficient zero modulo q must not be treated as zero in R.
No nonunit is ever inverted. Nonunits may occur freely in shear coefficients.
The complete slot skeleton is needed when batching all high lifts of one low
class: a coefficient that is exactly zero on one lift can be a nonzero
multiple of q on another. A sparse numerical trace may suppress its zero
slots, but that optimization alone is not a common high-lift program.

### Diagonal covariance

Run the same stage on T and `T' = L T U`, with L and U diagonal and all
diagonal entries units. Write their entries as l_i and u_i. A row swap S
updates this relation to

```
S T' = (S L S^-1) (S T) U.
```

Thus the left diagonal is merely permuted. The low zero pattern is unchanged,
so both runs choose the same first unit pivot. For an elimination at (i,k),

```
c  = -T[i,k] / T[k,k],
c' = -(l_i T[i,k] u_k)/(l_k T[k,k] u_k) = (l_i/l_k)c,
E_ik(c') L = L E_ik(c).
```

After clearing, the relation `T' = L T U` still holds. Induction proves
that the whole pivot itinerary is unchanged by diagonal unit multipliers.
Reducing the unweighted elimination modulo q also commutes with every step,
because all divisors are units. Consequently the pivot itinerary depends
only on the unweighted low residue, uniformly over all high lifts and all
diagonal weights B_j. Its coefficients, in contrast, must be evaluated on
the full weighted matrix in R.

This distinction gives the required common skeleton across the f columns.
The swap list and final determinant sign depend only on the parent's low
class. Each coefficient array c(j) depends on the parent's full fields and
weight descriptors. Neither may depend on any child's fresh role packet.
For fixed M_0, multiplication by the unit l_i/l_k also preserves the exact
zero pattern across diagonal weights. It does not imply that pattern is
constant across distinct high lifts. Similarly, a diagonal entry's equality
to one is not invariant under the row permutations of the weighted reduction;
retain all N-1 paired-diagonal slots for a uniform batched program.

## 3. Exact reconstruction and inverse chronology

Let O_1,...,O_t be the elimination operations in chronological order. Thus

```
D = O_t ... O_1 M,
M = O_1^-1 ... O_t^-1 D.
```

To apply M to a column of address values, execute D first, then

```
O_t^-1, O_(t-1)^-1, ..., O_1^-1.
```

The inverse of E_ik(c) is E_ik(-c); a row interchange is its own inverse.
Reversing the elimination list without inverting additions, or executing
the inverse list in its original order, need not reconstruct M. The complete
inverse word is obtained by reversing the compiled word and inverting each
instruction. This is an algebraic identity for every address vector.

Suppose s row interchanges occurred. Row additions have determinant one,
so

```
epsilon = product_i d_i = (-1)^s delta.
```

For i < N-1 define B_i to multiply coordinate i by d_i and coordinate N-1
by d_i^-1. Let S_epsilon multiply only the last coordinate by epsilon.
Then

```
D = S_epsilon * product_(i=0)^(N-2) B_i.
```

Indeed the first N-1 diagonal entries are d_i, while the last is
`epsilon / product_(i < N-1) d_i = d_(N-1)`. These diagonal factors commute.
The residual sign epsilon is fixed on the low class, rather than an arbitrary
uncosted unit scaling.

For two equally oriented coarse fields define

```
J_A(H,D) = (A D, A^-1 H).
```

The pair B_i is `J_(d_i) J_1`: its chronological order is **J_1 first,
then J_(d_i)**. This order yields `(d_i H, d_i^-1 D)`.

## 4. Physical field order, atom reversal and the child bill

The word “lower” refers to physical field position: E_ik(c) is a
later-target shear exactly when i > k. It is not a statement about the
numerical order of coefficient values, role indices, or matrix entries.
An upper shear with i < k obeys

```
E_ik(c) = J_1 E_ki(c) J_1
```

on the two fields, so chronologically it is a swap, a paid later-target
shear, and the same swap. Reindex c if one field has reversed atom
orientation, as specified below.

Let R_tail reverse the later f-atom field. Direct substitution gives

```
J_A = R_tail F_A R_tail.
```

For h = floor(f/2), R_tail is one unweighted reversed child on the first
and last h atoms of that field. A possible central atom is a spectator.
When h = 0, omit this operation. Therefore an ordinary weighted swap uses
at most three children, of widths f,h,h. It requires no free reversal.

The source's bank pairing reverses tail atom columns. This is accounted
for without inserting an uncharged normalization. Give each physical
coarse field i an orientation map sigma_i(j), either j or f-1-j, and write
its logical column as `x_i(j) = physical_i[sigma_i(j)]`. The parent head
fields have the first orientation and tail fields the second. A logical
weighted swap of fields i,k is:

* If sigma_i = sigma_k, the ordinary J_A above.
* If sigma_i != sigma_k, one reversed F_A directly.

In both cases the first-field physical descriptor is
`A[t] = a(sigma_i(t))`. For opposite orientations, the other output is
exactly `C_f A^-1` times the first input, as required. An analogous
substitution reindexes each shear coefficient and source atom index. Its
target still lies wholly in the later physical field when i > k, so it is
a later-target atom shear regardless of the two orientations. This proves
that the uniform three-child swap allowance is conservative for both
intrabank and cross-bank operations.

There are at most N(N-1) reconstructed shears, N swaps and N-1 diagonal
pairs. Charging every shear as upper gives at most

```
6N(N-1) + 3N + 6(N-1)
    = 24m^2 + 6m - 6 < 32m^2
```

completed reversed children. Every child has at most f atoms. For a
parent with n = mf atoms per bank, this is ratio at most 1/m. The result
also applies after peeling a remainder and setting f = floor(n/m).

The later-target additions are still paid. They require at most
N(N-1)f atom shear passes, hence O(Vn) work for fixed m under the retained
ordered-affine contract; the fixed sign and descriptor preparation are
additional nonrecursive work. The displayed child count is neither a
scalar-operation count nor a complete machine-time bound. For m=64 the
inherited allowance is 98,682, below 32*64^2 = 131,072. This arithmetic is
not a new saving or a replacement of the selected paid histogram.

## 5. Fresh-field and restoration implication

Fix a complete parent ancestor prefix a. The deterministic low pivot plan,
full-width coefficients, inverse chronology and diagonal descriptors are
then fixed, independently of the child's fresh packet and unused suffix.
Every algebraic instruction is the identity on those factors. If unused
stock is `[W_child] x [U]`, every value of W_child remains present with the
same multiplicity before any child begins. The new parent-dependent
coefficient can be placed in that child's ancestor-only weight descriptor.

Each completed child restores its supplied row and preserves the exposed
parent fields by the retained child contract. Therefore the next sequential
child may reuse the same unused stock. This uses arbitrary values of the
stock and spectators; no clean initialization is assumed. It is exactly
the field-dependency implication required in the row note, lines 11–15.
It does not by itself construct the child's physical row split, prove its
complete invocation domain, or validate its own restored endpoint.

The elimination evaluator uses only a fixed number of ring operations for
fixed m. Unit inverses and arithmetic on O(w)-digit residues have polynomial
cost in w. Uniform descriptors through an entire recursive supplier still
require the inherited descriptor and scheduler arguments; they are not
established by the one-parent algebraic word.

## 6. A full-width nonunit witness

For every odd prime q and w >= 2, work modulo q^w and set

```
g = [[q, q-1], [1, 1]],       det(g) = 1,
u = [q,1]^T,                 v = [1,1-q]^T,
P = u v^T = g diag(1,0) g^-1.
```

Since v^T u = 1, P is a rank-one split idempotent. Its entry P[0,0] = q
is nonzero in R and zero modulo q. At q=3,w=2, for example,

```
P = [[3,3], [1,7]]  (mod 9).
```

With the source's reversed cross block P C_2, the first northeast pivot
is P[0,0] = q, so this is a bad generic-residue class. Nevertheless the
full residual

```
M = [[I-P, P C_2], [C_2 P, I-C_2 P C_2]]
```

is an involution, is invertible over R, has split rank one relative to I,
and has determinant -1. The full unit-pivot elimination above therefore
applies. Treating a zero low residue as an exact zero loses a nonzero
nilpotent term. The lifted term can be observed on an ordinary coordinate
basis vector; low-residue correctness cannot certify the full operator.

For the selected-size model, begin with P_0 = diag(I_42,0_22) in dimension
64 and embed g on axes 0 and 42, leaving all other axes fixed. Put
`P = g P_0 g^-1`. This projector has split rank 42 and again P[0,0]=q.
Its 128-coordinate residual has determinant +1 and lies in a GL64
conjugacy orbit of split rank-42 projectors. This is an explicit witness
inside the assumed full-cover rank-42 model. It is **not** an assertion
that the checker emitted an actual selected finite physical residual, nor
that every selected hosting or common-label obligation has been solved.

## 7. Scope of the conclusion

The written proof covers every indicated q,w,m,f, every admissible diagonal
unit weight array, every complete spectator value, and every invertible
residual of fixed determinant sign satisfying the stated dependence rules.
The executable's finitely many fixtures are separate evidence about its
implementation, not the basis of the universal statement. No formal-kernel
proof is claimed.

Binding all selected physical residuals to this local-ring contract, matching
their common labels and hosting layouts, realizing ordered-affine passes and
completed children on fixed tapes, proving their restoration with internal
borrowing, and completing the outer time/precision/transfer obligations all
remain outside this result. PR2084/PR2120's stock implications, PR2097's
fresh-fiber counting theorem and PR2140's one-port carry route retain those
premises. This note neither changes the selected frontier nor proves a new
multiplication exponent.
