# Involutions with a diagonal sign metric

The actual sixteen-block response admits a Gaussian dyadic replacement
with correction rank sixteen and twenty-four diagonal exceptions.
Its inverse equals itself. Its adjoint equals its conjugate by a diagonal
sign matrix. This removes the odd diagonal scales from the adjoint-to-
inverse conversion at the matrix level.

This packet gives the exact actual response and its factorization. It
does not give a native word, a complete caller, or a recursive invoice.
In particular, the new complex transfer coefficients need literal scalar
programs and costs.

## Construction

Let D be a diagonal matrix with entries in {1,-1}. Choose a column w
over the Gaussian dyadic ring such that w* D w=2, where * is the
conjugate transpose. Then

```text
S = I - w w* D
S^2 = I
S* = D S D
S* D S = D.
```

These identities follow by direct multiplication. No division occurs.
The correction has rank one. Its -1 eigenspace is spanned by w.

For each signed six-mode block, select two coordinates. Set w=d,
where d is the old sign vector. Give the two selected coordinates sign
-1 in D, and give the other four sign +1. Then w* D w=4-2=2.
The diagonal of S is two at the selected coordinates and zero elsewhere.
All coefficients are real integers.

For each eight-mode block, select one coordinate p. Set w_j=d_j on
the other seven coordinates, and set w_p=(1+2i)d_p. Give p sign -1
in D and give the other coordinates sign +1. Then

```text
w* D w = 7 - |1+2i|^2 = 7-5 = 2.
```

The selected diagonal entry of S is six; the other diagonal entries
are zero. Its coefficients are Gaussian integers. The identity uses
the norm of 1+2i. It does not divide by 1+2i or by five.

Take the direct sum over the eight blocks of each size. The result has
correction rank sixteen, determinant one, and trace eighty.

## Actual physical ports

Start with the sixteen pivots from the row-capture construction. Add

```text
2,25,13,51,11,63,42,105.
```

The new large pivots form four complete pair-code blocks:

```text
(2,25), (13,51), (11,63), (42,105).
```

Together with the four old selected pairs, they give exactly two
selected coordinates in each six-mode block. The eight small pivots
remain unchanged. Thus the selected set has twenty-four ports and is
closed under every physical pair code.

Let H be the actual pair code. It commutes with D. On the large
component H*H=2I; on the small component H=I. The two components do
not mix. Therefore the physical response

```text
A = H^-1 S H
```

satisfies A^2=I and A*=D A D with the same physical diagonal D.
Its diagonal support is exactly the twenty-four selected ports.
The ordinary mode rows keep the old off-diagonal support. Their
coefficients between two ordinary coordinates also remain unchanged.
Their selected-column coefficients change and must be retuned.

This last point differs from the sixteen-row completion. The present
construction changes selected columns in ordinary rows. The sixteen-
row lower bound for row replacement does not apply to it.

## Why a sign metric helps the mixed phase

Let Z be any diagonal unitary field operator that commutes with D.
The line-entry interface has Z=diag(Q_P,I_R). Put E_eff=Z A. Then

```text
E_eff* = A* Z^-1
       = D A Z^-1 D
       = D E_eff^-1 D.
```

Thus conjugating the dual cross response by D converts its adjoint
to its inverse. The conversion uses only field signs. It introduces
no odd denominator and no new spatial transform.

For a literal upper shear B(E*) with cross term -E*, pre- and
post-conjugation by diag(D,D) gives B(E^-1). Each D scale must still
appear in the scalar ledger. All other progress must commute with D;
this condition holds for fieldwise diagonal progress. It must be
checked for any coupled code or bank reset in a complete caller.
This identity does not remove stage dependence or a final phase.

## A limit of one exception in the six-mode block

Within a rank-one sign-metric reflection, suppose all but one diagonal
entries are zero. Normalize one ordinary coordinate to one. The zero
diagonal equations give norm one and the same metric sign on all
ordinary coordinates. After an overall sign change of the metric,
the selected coordinate must have Gaussian rational norm k-3.

For k=6 this would require a^2+b^2=3 for rational a,b. This is
impossible. Write a=A/C and b=B/C in lowest common integer terms.
Modulo three, A^2+B^2=3C^2 forces both A and B to be divisible by
three. The equation then forces C to be divisible by three, a
contradiction.

For k=8 the required norm is five, and 1+2i supplies it. Thus the
construction uses the minimum number of diagonal exceptions in
each independent rank-one sign-metric block: two for size six and
one for size eight. This is not a bound for coupled blocks, higher
correction rank, non-diagonal metrics, or general native circuits.

## Validation and scope

The checker uses exact pairs of rational numbers for Gaussian values.
It checks the pinned actual pair codes, the selected pair closure,
both physical identities, the complete 112-column matrices, and the
rank-sixteen contraction VU=-2I. It also checks ordinary support and
all dyadic denominators.

Run the checker normally and with optimized Python into separate
directories. The payloads and receipts must be byte-identical.
Independent proof review and a native emission are separate steps.

This result builds on the campaign's actual signed-clique response,
row-replacement mechanism, normalized pivots, and mixed-phase dual.
AI assistance was used. No publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
