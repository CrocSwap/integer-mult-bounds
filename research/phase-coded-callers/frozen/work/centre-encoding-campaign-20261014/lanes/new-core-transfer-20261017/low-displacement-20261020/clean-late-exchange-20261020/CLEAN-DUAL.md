# A native inverse-adjoint for the clean centre exchange

The Q-entry clean word has a literal inverse-adjoint with the same
native profile and scalar price. Its selected-bank conjugate has the
same price too. The conjugate is emitted by changing the field labels
of every instruction. It does not need extra physical swap instructions.

Both providers pass all 640 arbitrary input columns and restore all 416
auxiliary fields. Each word costs 8,600 real scalar primitives and has
native mass 1,792. This packet supplies a local physical operation.
The routed two-call construction and the full supplier bill are
separate.

## The actual content blocks

Use the selected ports P, the other ports U, and the normalized reader
L=[I,B] from `CLEAN-LATE-EXCHANGE.md`. Put D=E_UP. Exact multiplication
on the source matrices gives

```text
D = -B^T,        E_U x = u + D(a+Bu),        x=(a,u).
```

These are identities of the actual response. They are not assumptions
about an arbitrary row code.

Let the selected target content be z and the ordinary target content
be v. The clean word has content map

```text
alpha = a+Bu,
M(a,u,z,v) = (-z, u, alpha, v+u+D alpha).
```

Its inverse is obtained directly from its output:

```text
a = third - B second,
u = second,
z = -first,
v = fourth - second - D third.
```

Thus its inverse-transpose is

```text
M^(-T)(a,u,z,v) = (-z, u+Da-v, a+Bv, v).
```

Let S exchange only the selected X and Y coordinates. Then

```text
Bswapclean = S M^(-T) S,
Bswapclean(a,u,z,v) = (z+Bv, u+Dz-v, -a, v).
```

The checker derives M^(-T) from the complete stored inverse of M.
It compares the result with these block equations and checks both
inverse product orders. No inverse of E or odd division is used.

## Physical operator and exact order

Let A_in and A_out denote the block diagonal physical entry and exit
operators. For the Q-entry clean word, they are unitary:

```text
A_in  = diag(Q_X, Q_P on selected Y, I_U on ordinary Y),
A_out = diag(F9_X, F9_P on selected Y, F9 q_U on ordinary Y).
```

The actual operation is W=A_out M A_in^-1. Therefore

```text
W^(-*) = A_out M^(-T) A_in^-1.
```

All content coefficients here are real. The notation * denotes the
Hilbert adjoint of the complete physical operator, including phases.
This statement does not replace an adjoint with a transpose for a
general complex response.

Suppose the original chronological gates are G1,...,Gn. The physical
operator is Gn...G1. Its inverse-adjoint is

```text
Gn^(-*) ... G1^(-*).
```

The chronological order is unchanged. Every native gate and endpoint
view is unitary, so its inverse-adjoint is exactly the same operator,
including its global phase. For the scalar instructions:

```text
target += c source   becomes   source -= c target,
target *= c          becomes   target *= 1/c.
```

The emitter applies these rules to every scalar instruction. All scalar
reads still use two fields in the same current frame. Native frame
progress is unchanged. The full column replay checks the resulting
word, including every borrowed helper.

## Selected-bank conjugation without added swaps

At each selected port, both input fields have the same Q frame and
both output fields have the same FULL frame. Their exact input
monomial records are also equal. Consequently S commutes with A_in
and A_out.

The conjugated physical operator can be written

```text
S W^(-*) S
  = (S Gn^(-*) S) ... (S G1^(-*) S).
```

Each adjacent pair S S cancels. To emit this circuit, replace every
selected field index p with 112+p, and vice versa, in every instruction
and boundary binding. This is a different, explicit circuit on the
same physical fields. It is not an unpriced swap of live data.

The emitter stores this field permutation. It checks all input records
by their physical target, frame, port, and complete monomial recipe.
The ninety-six ordinary output records keep their fields. The native
recipes and frame lists are unchanged byte for byte. The entry and exit
frame arrays are invariant under the selected permutation.

The exact physical Bswapclean result is

```text
input:
  X = Q(a,u),        Y_P = Q_P z,        Y_U = v;

output:
  X_P = F9(z+Bv),    X_U = F9(u+Dz-v),
  Y_P = -F9 a,       Y_U = F9 q_U v.
```

The unpermuted inverse-adjoint is also stored as a separate complete
word. It has content (-z,u+Da-v,a+Bv,v) with the same physical exit
frames.

## Invoice and checks

For both variants and both providers, the complete local invoice is

```text
scalar primitives              8600
native profile                 1392 H1 + 64 H2 + 48 H3 + 16 H8
native mass                    1792
native children                1520
input monomial views           128
output monomial views           96
native side-map upper bound    3040
extra boundary swap steps         0
extra owned or private fields     0
odd divisions                    0
```

Inverting the real power-of-two scales keeps their price. Transposing
and negating the ADDs also keeps their price. The H8 wrappers remain
charged.

The exact content prefix row one-norm is 12. The additional binary
denominator height is two. These are bounds at the emitted operation
boundaries. They do not include recursive child precision or primitive
internal roundoff.

The normal and optimized runs produce identical payloads and receipts.
The serialized programs are replayed. A wrong code ADD sign and a wrong
exchange ADD sign are rejected in all four complete words.

```text
python3 emit_dual.py --out <new-directory>
python3 -O emit_dual.py --out <another-new-directory>
```

Both commands refuse an existing output directory.

This construction uses the frozen clean exchange and its reviewed
native dependencies. The independent clean-exchange review is
`new-native-recipes-20261017/clean-centre-exchange-review-20261020`,
with freeze SHA256
`6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d`.
The cover-algebra lane supplied the useful selected-bank formulation.
AI agents prepared this literal circuit and its checks.

The matching input types make this local conjugation legal. They do
not by themselves establish the next routed service, its scalar code,
its output decoder, or a complete multiplication bound.
