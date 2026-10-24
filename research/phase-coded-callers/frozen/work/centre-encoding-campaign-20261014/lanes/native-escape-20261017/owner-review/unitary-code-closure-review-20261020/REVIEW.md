# Common-input proof for the actual unitary-code routes

The representation gap has an exact repair. The logical path operators
are linearly independent at every tensor width f at least 2. The
physical affine paths have the same property at every f at least 3.
These statements use one common spatial basis input for all paths.
They do not assume a faithful regular action on a separate owner set.

There is also an exact Q-commutator result at every f at least 3.
For the three invertible scalar codes in the stated current charts,

```text
Q K = K Q    if and only if    C0, C1, and C2 are diagonal.
```

In particular, every row of all eight actual C/C* triples has a
nonzero commutator. The checker supplies 896 exact witnesses.
No commutator claim is made for f=1 or f=2. None of these results
is a lower bound on a general native decoder.

The producer packet was not frozen when this review began. This
packet binds the source matrices and route data. A separate
binding must identify the final corrected producer text and receipt.

## Sources and conventions

The review reads the actual D25 view source, SHA256
`125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473`,
and the actual unitary-completion payload, decompressed SHA256
`fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428`.
`SOURCE-MANIFEST.json` gives their exact paths. No producer module
is imported.

All 112 q_p are distinct nonzero vectors in the root nine axes.
The unitary source and all three route stages use the same
physical port order.
The checker verifies every route's orthogonality, involution,
own-line condition, and fresh-block identities. It verifies the
stored adjoint and both unitary product orders. The native word
is not replayed.

Use the position convention `P_A |x> = |A x>`. Define the
unnormalized Fourier character

```text
|chi> = sum_x (-1)^(chi dot x) |x>.
```

Then `P_A |chi> = |A^(-T) chi>`. Every path matrix A here is
orthogonal, so `A^(-T)=A`. Thus the same matrix A acts on
position coordinates and on Fourier-character labels. A physical
translation after the route gives

```text
T_t P_A |chi> = (-1)^(t dot A chi) |A chi>.
```

The intrinsic positive line operator has

```text
Q_p |chi> = i^parity(q_p dot chi) |chi>.
```

On f columns its exponent is the sum of the f parities. These
conventions fix the operator order in the proof below.

## One common input separates the logical paths

Let Omega be the sum of the nine root axes. Let e1 and e2 be
the sums of fresh blocks 1 and 2. The actual route identities are

```text
rho_(1,p) e1 = Omega+q_p,
rho_(2,p) e2 = Omega+q_p.
```

Each route fixes the other fresh block pointwise. The ordered
path from input k through r and j to output p is

```text
M_(p,j,r) = rho_(2,p) rho_(2,j) rho_(1,j) rho_(1,r).
```

Fix p. Remove its known invertible left factor rho_(2,p) and
write the remaining product as N_(j,r). Then

```text
N_(j,r) e2 = Omega+q_j,
N_(j,r) e1 = rho_(2,j) rho_(1,j) (Omega+q_r).
```

The first image gives j. Application of
`rho_(1,j) rho_(2,j)` to the second image gives `Omega+q_r`,
which gives r. The checker reconstructs both indices from all
12,544 actual image pairs.

Now apply every logical path to the SAME position basis input
with columns `(e2,e1)`. Their output pairs are distinct. A linear
combination of these path operators, applied to that one input,
is therefore a linear combination of distinct basis vectors.
It can vanish only when every coefficient vanishes. This proves
linear independence in the actual width-two spatial representation.
It is stronger than matrix distinctness alone. Zero columns extend
the witness to every f at least 2.

## Physical affine paths

Let a physical path be the affine map `x -> M x+t`, applied in
each column. Its linear part is the actual M above. Apply every
path to the SAME three-column position input

```text
(0,e2,e1).
```

The output is

```text
(t, M e2+t, M e1+t).
```

The first output gives t. Its differences from the other two
give M e2 and M e1. Thus no two paths have the same output.
This proves physical affine path independence for f at least 3,
for any literal translations t. A nonzero scalar phase on a path
does not change this conclusion.

This review does not duplicate the producer's affine-translation
enumeration. The argument needs only its stated affine form and
the verified linear parts. The actual FULL-view identities are
separately checked in the frozen phase-coded triple review.

## Monomial closure

The coefficient from input port k to output port p is

```text
sum_(j,r) C2[p,j] C1[j,r] C0[r,k] P_(M_(p,j,r)).
```

For fixed k, distinct paths have distinct outputs on the common
input above. For different k, the sources are different input
coordinates. Hence the exact nonzero term count in row p is

```text
sum_(j in supp C2[p,:]) sum_(r in supp C1[j,:]) |supp C0[r,:]|.
```

This counts paths after all allowed cancellations, not only
formal matrix products. A monomial operator must have one
nonzero source and one nonzero output basis position in a row.
The common-input test rules out even a new monomial output view
that is not in the listed path set.

Since all three matrices are invertible, each row is nonzero.
One term in every output row first forces C2 to be monomial.
Its permutation reaches every row of C1, so C1 must be monomial.
The same argument then forces C0 to be monomial. The converse
holds by composition.

The resulting criterion is valid in logical coordinates for
f at least 2, and for the literal physical affine maps for f
at least 3. The argument does not establish a width-one result.

## A common character witness for the Q commutator

Fix p, k and a nonzero path coefficient
`c=C2[p,j] C1[j,r] C0[r,k]`. Put `A=M_(p,j,r)`. On character
columns `(chi_1,...,chi_f)`, the contribution to `QK-KQ` is

```text
c * [i^L - i^R] |A chi_1,...,A chi_f>,

L = sum_l parity(q_p dot A chi_l),
R = sum_l parity(q_k dot chi_l).
```

For a physical affine path, multiply this coefficient by the
nonzero sign `(-1)^sum_l(t dot A chi_l)`. The sign is the same
on both sides of the commutator. Thus translations cannot remove
a nonzero phase difference.

Use e2 and e1 as the first two character columns. Their output
labels separate all paths in this p,k matrix entry, by the
previous certificate. Suppose the chosen path breaks the line:

```text
A^T q_p != q_k.
```

Compute the exponent difference d on those first two columns
modulo 4. If d is nonzero, use 0 as the third column. If d is
zero, choose a unit vector w on which `A^T q_p` and q_k differ.
The third-column parity difference is then 1 or -1. In both
cases, the three-column phase difference is nonzero.

The chosen path has a unique output character tuple. No other
path can cancel its coefficient. Therefore `QK-KQ` is nonzero
in the actual width-three representation. Zero character
columns preserve the phase difference and give the result for
every greater width.

This argument checks a common input for the complete path sum.
It does not infer independence merely because two Clifford
operators or two route matrices are unequal.

## Which paths preserve the line

The pulled output line is

```text
M_(p,j,r)^T q_p = rho_(1,r) rho_(1,j) rho_(2,j) q_p.
```

If j differs from p, `rho_(2,j) q_p` has a nonzero fresh2
component. Both stage-1 factors preserve that component.
The result cannot equal any root line q_k.

If j=p, the expression reduces to `rho_(1,r) q_p`. If r
differs from p, it has a nonzero fresh1 component and again
cannot equal a root line. If j=r=p, the path is the identity,
and distinctness of the port lines gives equality only for k=p.
Consequently

```text
M_(p,j,r)^T q_p = q_k    if and only if    j=r=k=p.
```

The checker verifies all 12,544 fresh2 tests and all 12,544
fresh1 tests from the literal route matrices.

If Q commutes with K at f at least 3, every nonzero path must
preserve the line by the common-character argument. Every row
of C1 and C0 is nonzero, so any nonzero C2[p,j] has a nonzero
continuation. It follows that j=p, and C2 is diagonal.
Invertibility gives nonzero diagonal entries. The same argument
then forces C1 and C0 to be diagonal. Conversely, all three
diagonal scalar matrices commute with the routes and with Q.
This proves the stated criterion.

## Actual unitary-code witnesses and scope

The actual C and C* have zero diagonal and nonempty rows. For
each of the eight stage choices, the checker selects one
nonzero path in every output row. All 896 paths have j different
from p and hence break the line. `COMMUTATOR-WITNESSES.json`
stores the input port, intermediate ports, nonzero Gaussian
coefficient, three input characters, output characters, and
the two distinct powers of i.

All normal and optimized outputs are byte-identical. Source
hashes are checked before and after each run. No frozen source
is changed. This packet supplies no native word, owner host,
recursive interface, cost saving, or numerical-grid proof.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
