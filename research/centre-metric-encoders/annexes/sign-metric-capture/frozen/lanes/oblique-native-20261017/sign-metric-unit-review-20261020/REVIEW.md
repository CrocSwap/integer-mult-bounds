# Independent review of the 32-field unit centre code

The frozen algebraic construction passes this review. There is no
material finding. It removes the selected-reader unit obstruction
of the 24-exception response. It does not give a native word or
inherit the response metric through the row code.

## Response and actual physical ports

In each eight-mode block, two selected entries have w_j=(1+i)d_j
and negative metric sign. The six other entries have norm one and
positive sign. Thus w*Dw=6-2-2=2. The matrix S=I-ww*D is a
rank-one reflection, and S*=DSD. The selected diagonal entries
are 3.

The six-mode blocks retain two selected norm-one entries. Their
selected diagonal entries are 2. All sixteen blocks remain
disjoint before the physical pair code. The full correction rank
is 16, the determinant is 1, and the trace is 80.

The independent checker reconstructs the full 112-port matrix
from the old pinned block signs and physical pair matrices. It
uses the preserved integer-realification engine from the earlier
independent review. No root producer or Gaussian arithmetic
helper is imported.

Both the 32 FULL ports and the original 16 centre pivots are
closed under the actual physical pair code. The checker verifies
this directly. It checks every response and correction entry,
the exact rank contraction, A^2=I, and A*=DAD. The physical
diagonal is zero outside the 32 FULL ports. It has 16 entries
equal to 2 and 16 entries equal to 3.

## Normalized reader and row code

Let P be the ordered original 16 centre pivots. The large part of
V_P is a signed pair-code matrix with a dyadic inverse. Each small
part is the scalar 1-i. Its inverse is (1+i)/2. The checker verifies
both inverse orders of the actual physical minor.

Set L=V_P^-1 V. The stored reader satisfies

```text
L_P = I16;
L A = -L.
```

The second identity follows from VA=-V, since VU=-2I. Both
identities are also checked on the complete actual matrices.

Replace rows P of the identity by L to obtain C. If N=C-I,
then N has nonzero rows only in P and nonzero columns only
outside P. Hence N^2=0, and C^-1=I-N=2I-C. The checker verifies
both inverse orders and every serialized coefficient. All
response, reader, and code coefficients are Gaussian dyadic.

This is a unit on arbitrary arrays. It does not use a promise
that a field is zero or belongs to a proper code image.

The response metric does not pass through C. This is an actual
failure, not only an unproved assertion: the checker verifies

```text
C* D C != D;
(C A)* != D (C A)^-1 D.
```

Thus a caller must distinguish ZA from ZCA. The sign-only
adjoint conversion for A cannot be assigned to the coded
response without another proof.

## Meaning of the 32-field minimum

The minimum applies to independent rank-one sign-metric blocks
with blockwise normalization. It assumes that every diagonal
exception and every pivot for an arbitrary normalized reader is
in the FULL selected coordinates. The actual pair-closed code
preserves this coordinate split.

A six-mode block needs at least two diagonal exceptions by the
rational norm-three obstruction. An eight-mode block can have
one exception, but its single selected reader coefficient has
norm five and is not a Gaussian dyadic unit. If only that field
is FULL, the reader has no right inverse there. A second FULL
field is therefore required in each eight-mode block.

These conditions give at least 8 times 2 plus 8 times 2 FULL
coordinates. The present construction reaches 32. It uses
only 16 of them as centre carriers.

This is not a general native lower bound. It does not cover
coupled blocks, a non-pair-closed mixed representation,
normalization from other frames, code-image division,
additional carriers, or a different diagonal-transfer grammar.

## An alternative with the unchanged 24-exception matrix

The checker also verifies a distinct option. Keep the entire
earlier 24-exception response and its metric unchanged. Add the
same eight small ordinary ports to the FULL read set. Use these
16 centre pivots:

```text
0,27,36,111,20,7,57,46,5,4,35,12,29,32,26,31.
```

The first eight give the same dyadic large minor. Each new small
pivot has reader coefficient -1. Both inverse orders of this
minor pass exactly. Thus the unchanged 24-exception response
also has a Gaussian dyadic normalized reader once 32 fields
are available for reading. It uses different small centre
slots. A native access word and its price remain separate.

This option does not contradict the earlier obstruction:
that obstruction restricted the reader to the original 24
selected columns.

## Reproduction and scope

Run from this directory:

```text
python3 -I -B check_review.py --out run-normal
python3 -I -O -B check_review.py --out run-optimized
```

The receipts must be byte-identical. The checker pins the root
freeze, the actual matrix inputs, and the independent integer
engine. The root's frozen files are unchanged.

The accepted result is the 32-FULL/16-centre algebraic response
and dyadic row code, with the stated blockwise minimum. Complex
scalar lowering, all 32 target paths, the actual centre access,
native and recursive invoices, and a complete caller remain open.

The root supplied the 32-field construction. It follows the
norm-five reader obstruction found during the preceding review.
The campaign's controller and cyclic packets supplied the actual
mode and pair data. This review adds an independent exact check,
the coded-metric rejection, and the unchanged-response option.
AI assistance was used.

No PR, push, commit, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
