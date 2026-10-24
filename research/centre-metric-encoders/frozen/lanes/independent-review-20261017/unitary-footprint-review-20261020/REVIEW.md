# Independent review of the 24-coordinate unitary code

The finite-field lower bound and the actual 24-coordinate matrix
pass this review. The complete common-frame scalar words also pass.
The proof applies to Gaussian dyadic unitary codes, and more generally
to real dyadic orthogonal codes. It does not give a lower bound for
all encodings or for native implementation cost.

The reviewed root proof is
`root/UNITARY-CENTRE-FOOTPRINT-20261020.md`, digest
`464628f0966138a9f95c34d26abeed214ab38720916fb1214820dd62e998f0a0`.
The actual 24-coordinate source is
`lanes/new-core-transfer-20261017/low-displacement-20261020/metric-completion-20261020/TWENTY-FOUR-FREEZE.json`,
digest
`3fda436c0390fb8ef2ee72b4d9fe6ccbfc0ea994208f4d962bb9f43960af7a82`.
The source proof has digest
`420e5d4eb13c43bfbd41614c7a686db49e1091bf06ed26039f231323208461a6`.
The decompressed matrix and word payload has digest
`9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c`.

The checker in this review imports no root or producer arithmetic,
matrix code, or interpreter. It reads the frozen matrices, geometry,
and literal component instructions. All source digests are checked
before and after the computation.

## The lower bound

Let A have entries in Z[1/2]. Suppose A has row rank r modulo an
odd prime p, and A A^T has rank s modulo p. Let U be orthogonal
over Z[1/2]. Suppose the exact required vector A x can be recovered
from m coordinates of U x, for every x.

Set y=U x. Every y is possible. The required vector is A U^T y.
If recovery ignores a coordinate of y, the corresponding column
of A U^T must be zero. This argument also applies to a recovery
routine that was not declared linear.

Reduce T=A U^T to its m used columns and then reduce modulo p.
It has row rank r because U remains invertible. Its Gram matrix
is A A^T and has rank s. The row space W therefore has radical
R of dimension r-s. The ambient coordinate pairing is
nondegenerate, so R-perpendicular has dimension m-r+s. Since
W is contained in R-perpendicular,

```text
r <= m-r+s, and hence m >= 2r-s.
```

This argument does not assume that the pairing on W is
nondegenerate. Its radical is the reason for the extra coordinates.

Appending arbitrary borrowed inputs appends zero columns to A.
It changes neither rank. Orthogonality of the extended U still
makes every encoded y possible. Thus arbitrary borrowed inputs
cannot defeat this bound. A promised zero input is a different
hypothesis; it is not covered.

The review reconstructs all 16 actual centre rows from the signed
mode blocks and the actual pair matrix. It obtains

```text
V V* = diag(12 I8,8 I8),
rank_F3(V)=16.
```

The real form A has rank 32 modulo 3. Its Gram has rank 16.
The bound is therefore 48 real coordinates, or 24 complete
complex fields. These ranks were computed directly with exact
modular elimination, in addition to the block derivation.

For Gaussian dyadic unitary codes, realification gives a real
dyadic orthogonal code. The same proof also permits arbitrary
real dyadic orthogonal mixing of real and imaginary components;
complex linearity is not required for that stronger statement.

## Arrays and physical frames

For N complex entries in each field, use the reader V tensor I_N.
The real ranks modulo 3 are 32N and 16N. This proves a bound of
48N real coordinates, or 24 arrays of N complex entries. The code
may mix ports, spatial entries, and owner indices. For arrays of
different sizes, the bound concerns total coordinate capacity.

Let A be this real reader, and replace it by L A U. If U is dyadic
orthogonal and both L and L^-1 are dyadic, then

```text
(L A U)(L A U)^T = L (A A^T) L^T.
```

Both relevant ranks modulo 3 are unchanged. The complex statement
requires a Gaussian dyadic unitary U and a Gaussian dyadic L whose
inverse is also Gaussian dyadic. Merely being invertible over
the rational numbers is insufficient: L=3I illustrates the
difference. This condition must be kept explicit in any use of
the frame extension.

These are exact finite-dimensional statements. They do not bound
approximate recovery, odd-denominator codes, nonunitary codes,
native calls, or the complete recursive cost.

## Independent reconstruction of the 24-coordinate code

The large 48-port block is identical to the pinned 32-coordinate
code. The review does not infer that an unnormalized pair matrix
is unitary. It checks its inverse explicitly and verifies both
unitary products of the resulting full physical code.

For each actual small clique, the review builds the stated eight
Haar rows independently. Their squared norms are
`8,8,4,4,2,2,2,2`. The factors `(1+i)/4`, `1/2`, and `(1+i)/2`
give unit rows with zero pairwise inner products.

For v=(1,1,-1,0,-1,0,0,0), the matrix
`R=I-v v^T/2` is an orthogonal involution because v^T v=4.
It fixes the sum because v^T 1=0. After multiplication by R,
the output assignment `(0,1,5,3,2,7,6,4)` makes each of the
seven contrast rows omit its assigned input coordinate.

This independently constructed matrix agrees entry by entry
with the saved physical matrix. The direct checks establish:

* Both unitary product orders and the saved adjoint.
* The full decoder T=V C*, its exact support of 24 fields, and T C=V.
* All 88 ordinary identities `(C E)_R=C_R`.
* Every ordinary diagonal in the physical and native mode bases.
* Exactly eight nonzero code diagonals, all at selected small ports.
* Every mode transfer remaining inside its original vertex or clique.
* Gaussian dyadic coefficients throughout these matrices.

The selected set has 16 physical large ports and one port from
each of the eight small cliques. The large reader supports overlap;
counting four physical coordinates per large row would double-count
their common selected set.

The construction attains the coordinate bound. Its eight selected
diagonals still need the proposed selected FULL paths. It does not
give an all-hole zero-diagonal code.

## Literal scalar words

The review pulls every active real output covector backwards
through the literal component word. This differs from the
producer's forward sparse-row computation. It obtains the exact
real matrix of C or C* on all 224 active real coordinates.

No instruction reads or writes any of the other 1,056 real
coordinates. This proves the full 1,280-column map with arbitrary
outside inputs. No zero field is assumed.

A second forward computation checks every instruction prefix.
Each word has 2,418 instructions and costs 8,052 real scalar
primitives under the source tariff. The code has prefix
one-norm bound 16 and binary denominator height 3. The adjoint
has bounds 28 and 2. The saved adjoint word is exactly the
reverse sequence of inverse component operations.

A deleted ADD is rejected separately in each direction. Both
normal and optimized runs give
`PASS_UNITARY_FOOTPRINT_AND_24_CODE_REVIEW` with identical receipts.
The commands and file digests are recorded in this review's freeze.

## Scope of acceptance

There is no material defect in the reviewed matrix, common-frame
word, or finite-field theorem. The array and frame extension is
accepted with the explicit inverse-in-the-dyadic-ring condition
stated above.

The target-path removal census, replacement native service,
phases inside new native calls, source access at unequal hole
types, inverse-adjoint service, routed caller, helper host, and
full precision proof are outside this review. The native review
worker has those implementation obligations. Neither the
footprint bound nor a scalar code invoice pays them.

The source bytes were preserved. AI assistance was used. No PR,
commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
