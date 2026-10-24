# Independent review of the sign-metric response

The frozen response passes this review. There is no material finding.
The result is a matrix construction. It is not a native word or a
complete supplier.

## General reflection

Let D be a diagonal sign matrix, and let w be a Gaussian rational
column with w*Dw=2. Set S=I-ww*D. Then

```text
S^2 = I-2ww*D+w(w*Dw)w*D = I;
S* = I-Dww* = DSD;
S*DS = D.
```

The range of S-I is the line spanned by w. S acts as -1 on that line
and as +1 on the kernel of w*D. Thus its correction rank is one,
its determinant is -1, and its trace is k-2 in a block of size k.
These claims use characteristic zero.

In each actual six-mode block, w has sign entries. Two negative
metric entries and four positive entries give w*Dw=2. The two
selected diagonal entries of S are 2. All other diagonal entries
are zero.

In each actual eight-mode block, one selected entry of w is changed
from d to (1+2i)d. Its norm is 5. The other seven norms are one.
One negative metric entry gives 7-5=2. The selected diagonal entry
is 6. No division by 5 or by 1+2i is used.

The sixteen blocks have disjoint mode coordinates. Their correction
rank is therefore 16, their determinant is 1, and their trace is
8 times 4 plus 8 times 6, which is 80.

## Actual physical pair code

The independent checker reads the pinned pair matrices and the old
mode blocks. It does not import either producer. The selected large
ports are exactly these complete pairs:

```text
(0,27), (2,25), (7,57), (11,63),
(13,51), (20,46), (36,111), (42,105).
```

There are eight further selected small ports. The actual code H
therefore commutes with the physical diagonal D. Also, H*H is 2I
on the large component and I on the small component. S does not
mix those two components. It follows that

```text
A = H^-1 S H;
A^2 = I;
A* = D A D.
```

The checker uses integer realification: a complex matrix X+iY is
represented by the real integer block matrix [[X,-Y],[Y,X]], after
an explicit common factor of 2 when needed. This is distinct from
the producer's pairs of rational Gaussian coefficients.

It reconstructs every entry of A from the old block signs, the
selected ports, and the actual pair matrices. It verifies the
serialized response and adjoint, both physical identities, the
metric identity, and the correction factors. The contraction
VU=-2I proves exact complex rank 16; it is not a modular rank
estimate.

The physical diagonal has 16 entries equal to 2 and 8 entries equal
to 6. It is zero at all 88 ordinary ports. A stronger support check
also passes: every ordinary physical row has its old support, and
the entire ordinary physical principal block is unchanged. Every
selected column changes in the ordinary rows. Thus the result is
not a selected-row replacement.

## Ordered phase conversion

For any diagonal unitary field operator Z that commutes with D,

```text
(ZA)^-1 = A Z^-1;
(ZA)* = A* Z^-1 = D A Z^-1 D;
D (ZA)* D = (ZA)^-1.
```

No commutation of A and Z is used. The checker uses an explicit
noncommuting diagonal phase as a control. It also rejects the
bilinear transpose in place of the adjoint, omission of D, and
changing the metric sign on only one member of a physical pair.

The corresponding two-bank conjugation uses diag(D,D). It costs
field signs. Any progress between these signs must commute with
D, or its conjugated implementation must be supplied. The
identities do not remove stage changes, boundary code costs,
spatial phases, or a final decoder.

## Scope of the one-exception bound

The bound can be stated for every nontrivial rank-one reflection
S over the Gaussian rationals that is self-adjoint in a diagonal
sign metric. Write S=I-u v* with v*u=2. The identity S*D=DS forces
v=cDu for a nonzero real rational c. A zero ordinary diagonal
entry gives c d_j |u_j|^2=1.

Normalize by one such coordinate u_j. After an overall sign change
of D, all ordinary metric signs are positive and all ordinary
norms are one. If there is exactly one exceptional coordinate in
a block of size k>3, the metric norm equation becomes

```text
(k-1) - |w_p|^2 = 2.
```

The exceptional metric sign must be negative, and its Gaussian
rational norm must be k-3. For k=6, this requires a^2+b^2=3 over
the rationals. Clear denominators in lowest terms. Reduction
modulo 3 forces both numerators to be divisible by 3; the original
equation then forces the denominator to be divisible by 3. This
is a contradiction. For k=8, 1+2i has the required norm 5.

Zero exceptions are also impossible in these rank-one blocks,
since their trace is k-2, which is nonzero. Thus two exceptions
for each six-mode block and one for each eight-mode block are
minimal in this family.

Two counterexamples show why the hypotheses matter:

- A direct sum of three ordinary swaps on six coordinates is an
  involution with no diagonal exceptions. Its correction rank is
  three, not one.
- The real integral matrix I-u v^T with
  u=(1,1,1,1,1,1)^T and v=(1,1,1,1,1,-3)^T is a rank-one
  involution with one exception. Its diagonal is (0,0,0,0,0,4).
  Its diagonal symmetrizer has an unequal magnitude 3; it cannot
  use a diagonal sign metric.

The bound does not cover coupled blocks, higher correction rank,
non-diagonal metrics, or arbitrary native circuits.

## Reproduction and limits

Run from this directory:

```text
python3 -I -B check_review.py --out run-normal
python3 -I -O -B check_review.py --out run-optimized
```

Both runs must produce the same `CHECKS.json` bytes. The source
freeze is checked before either run. Every input file is pinned.
No producer code is imported.

The review does not price Gaussian scalar gates, emit a native
word, or prove recursive hosting or a complete caller. Those
obligations remain separate. The root supplied the sign-metric
construction; the pinned controller and cyclic packets supplied
the actual mode blocks and pair code. This review adds an
independent exact reconstruction, the physical support check,
and the stated scope controls. AI assistance was used.

No PR, push, commit, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
