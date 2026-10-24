# Close a fixed-past supplier at the outer consumer

This note states the outer contract for the fixed-past construction
family under investigation. The outer steps are explicit. The native
supplier and its recursive cost are hypotheses, not conclusions.

Use the selected parameter family and sources pinned in
[COMPLETED-PREFIX-CODES.md](COMPLETED-PREFIX-CODES.md). Let `A` be the
current active selected bits and `P` be one fixed set of completed
named bits, disjoint from `A` and from every later active selected
bit. The number `|P|` is `O(d)`. Let

```text
H0 = (1/2) [[1,1],[1,-1]],
S = diag(1,i),
h = S C S = (1+i) H0.
```

The scalar identity uses the actual complex `C` of the source.
It gives `h^2=iI` and `h^8=I`. Put `h_P=h^tensor(|P|)`.

## Required native contract

For every size admitted by the recursion, the proposed whole-layer
procedure must compute

```text
h_P tensor H0_A
```

on every productive row, in the same physical named coordinates.
It must satisfy its stated contract on all other arbitrary fields.
The past block must be the same in every common outer round. The
procedure must include its preparation, coordinate maps, phases,
storage, restoration, children, and finite guard. Its recursive
invoice must already be proved.

For a procedure that returns `C_P tensor C_A`, the ordinary phase
conversion gives the required map: apply `S` on all selected bits
before and after it, and use scalar `b^|A|`, where `b=(1-i)/2`.
Do not use `b^(|P|+|A|)`. The latter would normalize the past factor
to `H0_P` and introduce an unnecessary repeated scale. The ratio
between the two choices is

```text
(1+i)^|P| = 2^floor(|P|/2) i^floor(|P|/2) (1+i)^(|P| mod 2).
```

It is one exact power-of-two scaling and at most one fixed complex
scaling. Its width and prefix effect must be included in the guard.
This identity changes no native child dimension.

The contract does not follow merely by projecting an old child
rank onto the active coordinates. In particular, all old rank-zero
routes must still have legal and priced transitions after a past
frame is omitted. A row-dependent change of chart is not a proof
of that condition.

## Exact outer endpoint

In the forward procedure, select the completed bits after the initial
one or two rounds. In the changed opposite procedure from the cited
note, select them after its first common round. In both cases every
remaining common round has butterfly and twiddle supported outside
`P`. Therefore `h_P` commutes with each such exact round.

If `n` common rounds use the native contract, the resulting operator
is exactly

```text
h_P^n T,
```

where `T` is the required unencoded transform, including the retained
record layout. The initial preparation rounds are included in `T`.
In the opposite direction, evaluate the final long-only round
individually. Its selected slots are disjoint from `P`, so it commutes
with the carried code too. This costs `O(Vd)`.

Decode `h_P^n` once before each forward pointwise product and once
after the opposite procedure. Because `h_P^2=i^|P| I`, an even power
needs only a scalar fourth-root phase. An odd power needs one past
Walsh tensor and a scalar phase. Individual selected-bit kernels,
with the two `S` phases, implement that tensor in `O(V|P|)` time.
Every underlying bit has its complete two-element range. Thus the
decoder works on arbitrary productive rows, not on a special input
subspace.

After decoding, the source's pointwise polynomial product and its
normalization are used unchanged. No nonmonomial code is passed
directly to that product. The opposite procedure consumes the exact
stored order described in the cited note.

## Error and precision

The past tensor is not a contraction in the coefficient maximum
norm. For every integer `j`, however,

```text
||h_P^j||_infinity <= 2^(|P|/2).
```

For even `j`, it is a scalar phase times the identity. For odd `j`,
each row has `2^|P|` entries of modulus `2^(-|P|/2)`. This proves
the displayed bound, independently of the number of rounds.

Suppose each implemented complete round has additive error at most
`eta` in that norm. The remaining exact active rounds are
contractions and commute with `h_P`. After the final exact decoder,
the error injected in round `j` is multiplied by a past power
`h_P^-j` and an active contraction. Consequently the total decoded
error from the `n` rounds is at most

```text
n 2^(|P|/2) eta.
```

An `O(d)` extra fractional-bit reserve therefore covers the code's
condition number. The factor `n` is the usual transform round count.
The encoded values need `O(d)` extra integer bits. An exact odd-power
decoder adds at most `|P|` dyadic denominator levels, so its exact
temporary width also increases by `O(d)`. Since `d=o(p)`, all these
widths remain `Theta(p)`.

The native procedure must supply its own prefix and approximation
bound for inputs of this guarded magnitude. That is a material
hypothesis. Once that bound is supplied, the displayed calculation
propagates its error to the unchanged outer consumer. It does not
reuse the old finite guard without a check.

## Layout and time

The initial individual rounds and the terminal decoder cost
`O(Vd)`. The selected exact margin `1-epsilon-kappa>0` admits this
term. The opposite procedure has the same named-slot order and
asymptotic layer/layout invoice as before; its changed monomial is
an exact signed coefficient shift.

If row-role codes must use completed coordinates too, a separate
completed whole axis supplies all recursive row digits at cost
`O(V ell)`, with `ell=Theta(p/d)`. Its precision allowance is stated
in the cited note. Exclude that axis from the active and past
payload coordinates; no bit serves both roles. The selected
inequality `epsilon-kappa>0` admits this additional term.

[PAST-CATALYST-LAYOUT.md](PAST-CATALYST-LAYOUT.md) gives a physical
common-offset wrapper when the fixed-past native word fixes the
required spectator block. For the proposed active/past ratio
`64:9`, it uses no extra address bits or complex children. It adds
a fixed number of admitted bit interchanges per invocation and
`O(d)` single-bit placements per complete transform. The updated
finite compact-engine and hosting invoice is still required.

Thus a supplier meeting the native contract has an explicit outer
path through both transform directions, the product, and final
decoding. Its extra top-level work has the already admitted orders
`O(Vd)` and `O(V ell)`. There is no additional factor of the number
of rounds multiplying the `O(Vd)` decoder term.

This is a conditional closure theorem for an actual construction
family. It resolves the outer consumer, offset, and opposite-order
questions. It does not prove that the retained cover preserves a
proper past subspace, that an active child profile improves, or that
an encoded child composes recursively. The campaign's fixed-past
lane is checking those remaining requirements. No supplier or
kappa improvement is claimed here.

Prepared with OpenAI Codex assistance.
