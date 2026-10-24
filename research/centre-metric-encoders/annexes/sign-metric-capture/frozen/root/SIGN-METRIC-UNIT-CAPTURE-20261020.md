# A sign metric with a dyadic centre code

The twenty-four-exception response has a useful sign metric, but its
selected centre minor is not a unit over the Gaussian dyadic ring.
In each eight-mode block, its reader has coefficient 1-2i at the
only selected field. That coefficient has norm five. This prevents
an arbitrary normalized reader in those selected fields. It does
not invalidate the response or its sign-metric identity.

A thirty-two-field variant removes this centre-code obstruction.
It retains correction rank sixteen. All response coefficients, the
normalized centre reader, and its row code are Gaussian dyadic.
This is an algebraic construction. A native word and its full invoice
remain separate obligations.

## Change to the eight-mode blocks

Retain the two selected fields in each six-mode block from the
previous construction. In each eight-mode block select two fields.
Set

```text
D_j = -1 on both selected fields, +1 elsewhere;
w_j = (1+i)d_j on both selected fields, d_j elsewhere;
S = I - w w* D.
```

Then w* D w=6-2-2=2. Thus S^2=I and S*=D S D. The two selected
diagonal entries are three; the other diagonal entries are zero.
The selected reader coefficient is 1-i up to sign. Its inverse
(1+i)/2 lies in the same Gaussian dyadic ring.

In each six-mode block the old reader coefficient at a selected
field is a signed unit. Hence one selected field per block supplies
a unit sixteen-by-sixteen minor before the physical pair code.
The original sixteen pivots are closed under that code, so the
physical minor is a unit as well.

The additional small ports are

```text
5,4,35,12,29,32,26,31.
```

Together with the twenty-four-field set they give thirty-two FULL
fields. Only the original sixteen fields need carry centre rows.
The other sixteen can retain ordinary response values.

## Unit row code

Let V be the physical rank-sixteen reader and P the original sixteen
pivots. Set L=V_P^-1 V. Then

```text
L_P = I,       L A = -L.
```

Define C by C_P=L and C_R=I_R. The difference C-I has square zero,
so C^-1=2I-C. Every entry of both codes is Gaussian dyadic.
Thus the capture is a unit on arbitrary data. It needs no promise
that a target is zero or already in a special image.

The source word still requires a literal complex scalar lowering.
The changed selected-column coefficients and all thirty-two
selected target paths must be included. It is not valid to import
the old real1760 scalar tariff or the old sixteen-carrier native
profile.

The response sign metric does not automatically pass through the
new code C. In particular, the coded effective response Z C A
must not be identified with Z A. A complete forward/backward caller
must track this difference.

## Scope of the tradeoff

For independent blocks, the six-mode sign-metric rank-one family
needs at least two diagonal exceptions. The previous proof gives
this rational norm obstruction. In an eight-mode block, one
exception is possible, but its selected reader has norm five and
cannot form a unit minor. A second FULL field is therefore needed
if the centre must be normalized entirely in FULL selected fields.
The present construction reaches these blockwise counts.

This is not a lower bound for coupled blocks, code-image division,
additional fields, or a general native algorithm.

The exact checker binds the earlier Gaussian arithmetic helper and
actual matrix/pair sources. It verifies both minor inverse orders,
both code inverse orders, the centre action, actual pair closure,
the full response identities, and every coefficient denominator.
It emits the actual112-port response and the code. Normal and
optimized runs must produce identical files.

This extension follows the independent review's norm-five reader
obstruction for the twenty-four-field response. It builds on the
campaign's row-capture mechanism and actual signed blocks.
AI assistance was used. No publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
