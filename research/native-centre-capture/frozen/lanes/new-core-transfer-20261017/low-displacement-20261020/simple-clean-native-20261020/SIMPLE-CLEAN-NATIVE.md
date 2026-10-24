# Direct native self-transfer with clean selected centres

This packet gives two complete local words. The first has the content
map

```text
Fsimple(a,u,z,v) = (-z, u, a+Bu, v+u).
```

The second has the content map

```text
Bcustom(a,u,z,v) = (z, u-B^Tz-v, -a, v).
```

Here P is the same set of 16 selected ports as in the frozen clean
exchange. U contains the other 96 ports. The exact row code is
C(a,u)=(a+Bu,u). Both words use the physical types

```text
input:    X=Q(a,u),       Y_P=Q_P z,       Y_U=v;
output:   X in F9,       Y_P in F9,       Y_U in F9 q_U.
```

The invoice for either complete word is

```text
native profile                96 H1 + 128 H8 + 96 H9
native mass                   1984
native children               320
real scalar primitives        2912
native side-map upper bound   448
boundary adapters             0
extra owned or private fields 0
odd divisions                 0
```

This is a direct local implementation. It does not give a closed routed
caller, a new recursive host, or a complete supplier bound.

## Physical construction

Write q_p=Q_p^-1. All 112 source fields have physical value Q_p x_p.
Apply the exact native operator F9 q_p to each source. Each operator has
rank eight and gives F9 x_p. Apply the same operator to each of the 16
selected target fields. These fields now contain F9 z_p.

Apply F9 to each of the 96 ordinary target fields. This has rank nine.
Both fields at each ordinary port now have the same FULL type. Execute
the literal scalar ADD

```text
Y_p += X_p.
```

Then apply q_p to that ordinary target. The complete physical result is
F9 q_p(v_p+u_p). This use of q_p is valid because Q_p and F9 commute.
The checker verifies the complete operator and its global phase at
every actual port. It does not infer the identity from a frame name.

All source fields still have the same FULL type. Execute the pinned
1,760-unit code C on X. At each selected port execute

```text
Y_p += X_p;
X_p -= Y_p;
Y_p += X_p.
```

The three ADDs send (L_p x,z_p) to (-z_p,L_p x), where L=[I,B].
They cost 24 real scalar primitives per port. The ordinary source
fields do not change. This proves the stated Fsimple endpoint.

The full rank-nine kernel has identity left and right wrappers. It is
the nine positive coordinate C gates that define F9. The rank-eight and
rank-one kernels retain both emitted wrappers in the invoice.

## Literal inverse-adjoint

Let M denote the real content matrix of Fsimple. The physical word is

```text
W = A_out M A_in^-1,
```

where A_in and A_out are the unitary block diagonal input and output
operators listed above. Thus

```text
W^-* = A_out M^-T A_in^-1.
```

To emit this operation, keep the original chronological instruction
order. Keep every native operator unchanged, with its exact phase.
For every scalar ADD, exchange source and target and negate the
coefficient. Replace a scalar scale by its reciprocal.

Let S exchange X_p with Y_p at each selected port. The selected input
types are Q_p on both banks. The selected output types are FULL on both
banks. Thus S commutes with both boundary operators. Replace every
selected field label in the inverse-adjoint word by its partner label.
This emits S W^-* S. It requires no extra runtime exchanges.

Direct block inversion gives

```text
S M^-T S (a,u,z,v) = (z, u-B^T z-v, -a, v).
```

The checker executes the complete changed word. It checks both orders
of the content inverse identity. It does not treat the desired block
formula as a substitute for the native instruction sequence.

## Verification and tensor scope

The direct source uses the common port list and row code of the two
pinned providers. It replaces their old native paths. Thus there is one
common direct word, rather than two copies of the same word.

Each complete word passes all 640 independent input columns. The 416
auxiliary fields are arbitrary and unchanged. The checker verifies
every native edge, every scalar operand type, every final type, and
every scalar cost. It replays the serialized payload. It rejects a
missing ordinary self-response ADD and a missing reader ADD in both
words.

There are 209 exact physical kernel checks: one full kernel, 112
line-to-FULL kernels, and 96 negative-line exit kernels. The check uses
the exact Pauli action and one complete 512-entry Gaussian state. The
Pauli action determines the Clifford up to scalar phase. The state
comparison determines that scalar phase.

These one-alphabet operator equalities lift to every tensor width f.
Each native kernel is replaced by its tensor power. Each scalar ADD
uses two fields in the same current physical type. The number of
emitted scalar instructions and native calls is independent of f.
No polynomial expansion of a tensor-power line operator is used.

At scalar instruction boundaries, the content row one-norm reaches
22 for Fsimple and four for Bcustom. The additional binary denominator
height is one in both words. These are local content bounds. The
internal precision of a recursive child remains separate.

Run the two checks in new output directories:

```text
python3 emit_simple.py --out <new-directory>
python3 -O emit_simple.py --out <another-new-directory>
```

The normal and optimized payloads and receipts are byte-identical.

## Cost consequence and source credit

The direct ordinary self-transfer adds two native ranks per ordinary
port relative to the frozen clean word. The full mass is therefore
1,984 instead of 1,792. The 320 larger children also have a different
recursive moment from the 1,520 children of the clean word. A full
budget comparison must use the complete profile above.

This packet uses the row code from the controller's frozen row-capture
packet and the clean selected exchange from this lane. It also uses
the direct-FULL kernel established in the row-capture refinement and
its independent review. The source hashes and paths are in the
payload. The compiler and exact phase interpreter have separate
pinned source records.

The construction removes the ordinary D(a+Bu) response by a different
native word. It does not claim that one can remove a final Bv ADD from
the old clean dual. Independent review of this new direct word is a
separate step. AI assistance was used for the construction, code,
proof, and checks.
