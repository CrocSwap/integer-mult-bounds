# A complete clean unitary centre interface

The actual 24-coordinate unitary code now has complete native forward,
inverse-adjoint, and selected-conjugate interfaces. The packet emits
eight words: two forward entry types and two dual words for each of
the base and extra providers.

Every word costs 16,020 real scalar primitives. The Q-entry words have
native profile

```text
1328 H1 + 64 H2 + 48 H3 + 24 H8,
```

with 1,464 children and rank mass 1,792. The I-entry forward replaces
the 24 H8 calls by 24 H9 calls, for rank mass 1,816. Each word
accepts all 640 independent complex inputs and restores the 416
arbitrary helper fields. No extra field or odd division is used.

These are complete local native interfaces. They do not establish a
routed caller, a recursive helper host, a precision bound, or a
complete supplier improvement.

## The exact forward contract

Let P be the stored set of 24 selected ports and let R be its
88-port complement. Let C be the frozen actual unitary code:

```text
C* C = C C* = I,
C^-* = C,
(C E)_R = C_R.
```

All ordinary mode diagonals of C vanish. The selected set is closed
under each physical pair code. The selected small ports contain the
eight nonzero diagonals of C.

The input is X=Qx. The target has Y_P=z for I entry and Y_P=Q_P z
for Q entry; its ordinary part is Y_R=v. All these contents and
all helper contents are arbitrary.

Put w=Cx. The forward content map is

```text
X_P = -z,       X_R = w_R,
Y_P = w_P,      Y_R = v+w_R.
```

All X fields and selected Y fields end in F9. Each ordinary Y field
ends in F9 q_p. Thus the selected code coordinates have no borrowed
target contribution. The old selected target values are retained,
with a minus sign, on selected X.

The original sixteen centre readers are recovered from w_P by the
frozen decoder V C*. The map also retains all contrast information.
It does not overwrite or discard independent input coordinates.

## The complete forward word

Start with the pinned rank-sixteen native provider. Remove every
event whose target is a selected Y field. This removes 380 events,
including 192 H1 calls. No retained event reads a selected Y field.
The retained X paths are complete and unchanged.

Retune each retained transfer slot to the corresponding ordinary
mode coefficient of C. A zero coefficient removes that scalar
transfer. Every nonzero coefficient stays in its original six-mode
vertex or small clique, so it uses an existing equal-frame transfer
slot. The ledger records the old event index, exact source and target
mode, and new Gaussian coefficient.

The resulting ordinary response is C_R x. Advance each selected Y
baseline directly to FULL. For I entry this is the existing exact
H9 kernel with identity wrappers. For Q entry it is the exact
canonical line-to-FULL H8 operator.

After the retained sweep and selected progress, all 112 X fields
are at the same FULL frame. Apply the complete scalar word for C
to X. Then, for each selected port, execute

```text
Y_p += X_p;
X_p -= Y_p;
Y_p += X_p.
```

These three complex unit ADDs map (X_p,Y_p) to (-Y_p,X_p).
They cost 24 real scalar primitives per port.

The complete scalar bill is

```text
retained and retuned core       7,392
complete source code C         8,052
24 signed exchanges              576
total                         16,020.
```

The I-entry word has 112 explicit input views, 88 explicit ordinary
output views, and at most 2,880 native side maps. Its 24 direct FULL
children have identity wrappers. Each Q-entry word has 136 input
views, 88 output views, and at most 2,928 native side maps.
These are complete local map counts; they do not make map or helper
hosting cost zero.

## Complex scalar macros

For a Gaussian coefficient a+ib, one transfer is the contiguous
real-component word

```text
target.real += a source.real
target.real -= b source.imag
target.imag += b source.real
target.imag += a source.imag.
```

Zero terms are omitted. Source and target are distinct fields.
The checker verifies the complete real matrix of this word against
the stated complex ADD, on every real input component.

An individual component ADD need not commute with a complex native
frame. Therefore the payload stores the complete Gaussian transfer
as one macro. It stores the complete source code C as a second type
of contiguous macro. No native event or address map can occur inside
either macro. The common complex frame is checked only at macro
entry and exit.

Each completed macro is complex-linear and commutes with the common
complex frame on its fields. Its implementation uses the stated
real scalar instructions; no complex multiply primitive is hidden.
The full C macro is checked on all 224 active real coordinates.

The receipt gives two different local bounds. At complete macro
endpoints, the largest content coefficient component one-norm is
10 for the forward word and 5 for the dual words. Within one macro,
the largest component one-norm relative to that macro's physical
input fields is 16 for the forward word and 7 for the dual words.
These quantities are not a complete recursive rounding bound.

## The literal inverse-adjoint

For a chronological word M=G_n ... G_1,

```text
M^-* = G_n^-* ... G_1^-*.
```

Thus the chronological order stays the same. Each native operator
and each monomial view is unitary, so its inverse-adjoint is the
same physical operator.

For a real scalar ADD, transpose its source and target and negate
its coefficient. For a real scale, use its reciprocal. For each
complete component macro, apply those rules to its component
instructions in the same order. The macro boundary is preserved.
The complete Gaussian ADD then has coefficient -conjugate(a+ib)
on the transposed source-target pair.

The complete C macro has inverse-adjoint C. The checker verifies
this at the real-component instruction level; it does not merely
replace its descriptor by the matrix identity.

The resulting inverse-adjoint content is

```text
w = Cx,
X_P = -z,       X_R = w_R-v,
Y_P = w_P,      Y_R = v.
```

Now conjugate the whole Q-entry word by the selected-bank
permutation S. At each selected port, both input fields have Q_p
and both output fields have FULL. Therefore the permutation is an
exact wire relabeling. Every event target, component index, input
view, and endpoint frame is rebound. No unpriced physical swap is
inserted.

With x=(a,u), the selected-conjugate map is

```text
w = C(z,u),
X_P = w_P,      X_R = w_R-v,
Y_P = -a,       Y_R = v.
```

This is the complete Bswap contract. It is not the earlier
triangular-reader formula. The unitary code now acts on the mixed
cohort consisting of selected Y and ordinary X.

## Phase checks and inherited operators

All retained native recipes, ordered frame bases, source input
views, and ordinary output views are exact records from the pinned
reviewed provider and direct-formation packet. The 88 ordinary
output records are a subset of the accepted 96-record table.

The direct H9 recipe is inherited from the accepted identity-wrapper
refinement. Sixteen Q-to-FULL checks are fresh: eight new selected
large ports in each provider. Each check compares the exact Pauli
action and an exact Gaussian-dyadic reference state, which fixes the
global phase. The other selected H8 recipes are exact copies of the
accepted line-entry records.

No physical phase is inferred from the scalar response. The
inverse-adjoint keeps every native phase record unchanged and
checks its rebound target and ordered entry/exit frames.

The one-alphabet native identities lift by tensor products. The
complete scalar codes apply entrywise with fixed scalar
coefficients at each field width. This does not replace a tensor
native operator by a one-bit scalar polynomial or an O(f) sequence
of field scans.

## Validation and remaining work

The producer checks both providers and all four word types. Each
complete complex-linear map has all 640 independent complex
columns, equivalently all 1,280 real columns. Each component macro
is checked independently as a real matrix before it is applied to
the complete content state.

Both inverse orders of the forward and selected-conjugate maps
pass. All final frames and all 416 helper outputs pass. The complete
serialized words are replayed. A wrong atomic component ADD is
rejected in every word.

Run in new directories:

```text
python3 emit_unitary_clean.py --out <new-directory>
python3 -O emit_unitary_clean.py --out <another-new-directory>
```

Normal and optimized payloads and receipts are byte-identical.
Independent native review is separate. The code and its scalar
word have an independent review; that review alone does not
certify this new native service.

The root lane proposed the unitary completion target and the
coordinate lower bound. This lane constructed the actual 24-field
completion and the complete native words. The existing cyclic
providers supplied the transfer geometry and phases. The native
review lane identified the need for explicit complete component
macro boundaries. The controller and cover lanes study routed
caller composition. AI assistance was used throughout.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
