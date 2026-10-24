# Complete native clean services for sixteen signed-metric centres

This packet implements three related codes on the actual native
providers. Each code has a forward I-entry word, a forward Q-entry
word, a literal inverse-adjoint, a selected-bank conjugate, and a
metric-converted selected conjugate. All 30 complete words pass on
640 independent complex fields. The 416 auxiliary fields are the
identity.

The service forms the sixteen centre coordinates in productive
selected outputs. It retains each arbitrary selected target
baseline in the other selected bank. It needs no zero field,
private field, CLEAR, or odd division.

The codes describe the rank-16 reflection part of `E=P R`.
They do not compress `E-I` to rank sixteen. This packet does not
complete a routed caller or improve the full supplier bound.

## Code sources

The first code `C` is fixed by the
[signed-code freeze](../signed-sixteen-20261020/FREEZE.json),
SHA256 `8739b5dbba6a5422c9b68035683876931fbf8f6599a43375d10e73eee55b2de2`.
Its selected rows are the sixteen individual reflection readers.
It has physical diagonal metrics

```text
C K C^T = G,
C^-T = G^-1 C K.
```

The pair-closed code `Cbar` and its transpose are fixed by the
[companion freeze](../signed-sixteen-20261020/PAIRED-FREEZE.json),
SHA256 `810508791ea43aecaaf894c3cb50a8170d3e6f1f8e52684e274cda16c2c2db57`.
The extra selected-pair inverse costs 80 scalar primitives.
It gives `Cbar=H^-1 C_m H`.

The original `C^T` does not fit the old vertex grammar: 32 of its
ordinary mode rows cross vertices. The packet does not emit it.
Both `Cbar` and `Cbar^T` have exact ordinary block support and zero
ordinary diagonal. Their scalar words and metrics are separate
records.

## Physical contract

Let P select the sixteen fields, and let R be its complement.
Here the symbol R in a subscript means the ordinary field set;
the reflection matrix does not occur in the local map below.
Write `x=(a,u)` and `y=(z,v)`. For each code A in
`{C,Cbar,Cbar^T}`, the two forward entry types are

```text
I entry: X=Q x; Y_P=z;     Y_R=v.
Q entry: X=Q x; Y_P=Q_Pz; Y_R=v.
```

The output frames are FULL on all X and selected Y fields.
The ordinary Y fields have `F9 q_R`.
The forward content map is

```text
w = A x;
X'_P=-z,       X'_R=w_R,
Y'_P=w_P,      Y'_R=v+w_R.
```

All four input parts are arbitrary. In particular, the selected
baseline z is retained as `-z`; it is not erased or assumed zero.

## Literal native construction

The emitter starts from the pinned dense cyclic/clique provider.
For each provider it removes exactly 250 events whose target is
one of the sixteen selected Y fields. These events include
128 H1 children. No retained event reads a removed target.

Every remaining ordinary transfer is bound to its original event
index and actual mode source and target. Its coefficient is
retuned to the appropriate ordinary row of A. A zero coefficient
omits that ADD. All retained native events, ordered frames,
recipes, and ordinary output adapters remain exact source records.

Each selected target then advances to FULL. The I-entry word uses
the reviewed direct F9 recipe with identity side wrappers. The
Q-entry word uses the sixteen reviewed `capture-line:p` H8
recipes. Their input adapters are copied from the same-port
source adapters and bound to the selected target fields.

After the complete retained sweep, all source X fields have FULL.
The word applies the complete paid A code to those sources.
Each selected pair then uses the three ADDs

```text
Y_P += X_P;
X_P -= Y_P;
Y_P += X_P.
```

This maps `(w_P,z)` to `(-z,w_P)` at cost 24 real scalar
primitives per pair. The ordinary Y content already equals
`v+(A x)_R`. These facts prove the stated forward endpoint.

The construction emits the changed response `A_R` directly.
It does not use `C_R R=C_R` to reinterpret the old E provider.
No unpriced physical P operation is inserted.

## Literal dual and metric conversion

For each Q-entry word, the emitter takes the inverse-adjoint of
each gate in the same chronological order. A real ADD exchanges
its source and target and changes its coefficient's sign. A
scale becomes its reciprocal. A native gate is unitary, so its
inverse-adjoint is that same exact gate.

Every changed scalar event has a legal common frame. The emitter
checks this fact in the complete chronology. The result is the
physical inverse-adjoint of the complete forward word, including
its exact spatial phases.

The selected-bank conjugate replaces each selected field index
`p` by `112+p` and vice versa in every event and input adapter.
The Q-entry endpoint types are invariant under this change:
both selected inputs have the same Q frame and both selected
outputs have FULL. The ordinary output adapters are fixed.
This is a complete wire relabeling; it adds no runtime swap.

The raw selected dual has the map

```text
w = A^-T(z,u);
X'_P=w_P,      X'_R=w_R-v,
Y'_P=-a,       Y'_R=v.
```

For `A=Cbar^T`, its mixed-source code is exactly `Cbar^-1`.
This is a local inverse-code interface. It does not assert that
two different routed stage codes cancel.

For a code with `A K_A A^T=G_A`, put `J_A=K_A^-1`.
The complete unpermuted metric conversion is

```text
diag(G_A,G_A) F_A^-T diag(J_A,G_A^-1).
```

Conjugating this complete word by the selected-bank relabeling
gives the same displayed map with `w=A(z,u)`. All wrappers are
individual-field signed power-of-two scales. They commute with
each field's own complex spatial frame, including mixed input
and output frame sets.

The paired-transpose family uses the swapped metric identity
`Cbar^T Gbar^-1 Cbar=K^-1`. Its wrappers are emitted from that
identity. The raw and metric-converted variants are distinct:
the former uses the inverse-transpose code, and the latter uses
the primal code.

## Full local invoice

All numbers below come from the emitted event words. A real
coefficient acts on both complex components, and both costs are
included.

| Code family | Retuned core | Source code | Signed exchanges | Forward or raw dual | Metric-selected dual |
| --- | ---: | ---: | ---: | ---: | ---: |
| C | 4040 | 5564 | 384 | 9988 | 11252 |
| Cbar | 4040 | 5644 | 384 | 10068 | 11284 |
| Cbar transpose | 4296 | 5644 | 384 | 10324 | 11156 |

The metric wrappers cost 1264, 1216, and 832 respectively.
No wrapper fusion is assumed.

| Entry | Native profile | Children | Rank mass | Input views | Output views | Native side-map bound |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| I | 1392 H1 + 64 H2 + 48 H3 + 16 H9 | 1520 | 1808 | 112 | 96 | 3008 |
| Q | 1392 H1 + 64 H2 + 48 H3 + 16 H8 | 1520 | 1792 | 128 | 96 | 3040 |

Every dual has the Q-entry profile. The side-map column is an
upper bound from the complete native recipe records. It is not
a finite map implementation cost.

The exact event-boundary content bounds are:

| Code family | Forward norm/height | Raw dual norm/height | Metric-selected dual norm/height |
| --- | --- | --- | --- |
| C | 26 / 3 | 8 / 3 | 13 / 5 |
| Cbar | 26 / 3 | 8 / 3 | 13 / 5 |
| Cbar transpose | 18 / 3 | 22 / 3 | 40 / 2 |

The norm is the row one-norm of the exact content operator.
The height is its maximum binary denominator exponent.
These bounds exclude recursive child internals and rounding.

## Verification and source phase scope

The [emitter](emit_signed_clean.py) verifies all 640 independent
complex input columns of every complete word, every native
entrance and exit frame, every scalar common-frame condition,
and all 416 auxiliary outputs. It checks the full serialized
payload again. A wrong diagonal metric sign is rejected.

There is no fresh spatial operator in this packet. The retained
native records and endpoint adapters are exact copies from the
independently reviewed dense provider, direct FULL formation,
and selected line-entry packets. The input manifest includes
their review freezes. This inheritance includes global phase;
it is not a rank-only comparison.

The gate identities lift by tensor products. The real scalar
code commutes with its common complex spatial frame. No one-bit
polynomial is substituted for a tensor native child.

Run from the workspace root with fresh output directories:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/signed-clean-native-20261020/emit_signed_clean.py --out <new-directory>
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/signed-clean-native-20261020/emit_signed_clean.py --out <another-new-directory>
```

The expected status is `PASS_COMPLETE_SIGNED_SIXTEEN_NATIVE`.
Normal and optimized payloads and receipts match byte for byte.
Independent native review is a separate validation step.

The root lane supplied the reciprocal reflection family.
The oblique lane fixed its physical metric and placement.
The cover lane supplied the full diagonal-dual identity.
The bridge access lane requested the transpose interface.
The prior native and review lanes supplied the unchanged
spatial recipes. This lane supplied the complete retuned words,
pair-closed code, and local checks. AI assistance was used.

This packet does not allocate the 416 auxiliary roles as a
cache. It does not provide routed composition, a terminal
decoder, recursive child hosting, a finite-precision proof,
or a complete supplier improvement.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
