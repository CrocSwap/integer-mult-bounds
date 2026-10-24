# Independent review of the new-core native implementation

The local native implementation passes. This review closes the native
phase dependency of `NEW-CORE-LOGICAL-REVIEW.md` for both new provider
words. Together, the two reviews establish the clean-J local maps on all
632 live fields, with 408 arbitrary borrowed helpers and 91 private zero
buffers. The local bill is 164514 real scalar primitives and native rank
mass 5073. The native profile is
`{1:2433, 2:724, 3:228, 4:102, 5:20}`.

The review does not establish a complete supplier. The global controller,
owner assignment, private storage, recursive child hosting, precision,
and complete kappa calculation remain separate obligations.

## Evidence and independence

`check_new_native.py` reads the fresh recipes in
`../new-native-recipes-20261017`. Its constants pin the decompressed
canonical words and local programs, the serialized standard recipes,
the residual recipes, and the new literal dual recipes. The words come
from PR3133 and the byte-equal provider objects in PR3148. This review
uses their new frames and new warps. It does not substitute an earlier
provider's geometry.

The checker imports the pinned independent interpreter
`../interface-proof/verify_native_lift.py`. It does not import the recipe
generator, `clifford_exact.py`, or the producer's proof checker. The
interpreter computes the action on all 18 Pauli generators and the exact
512-entry Gaussian dyadic image of the zero basis vector. It uses exact
integer arithmetic. It does not use a floating point tolerance.

These checks prove operator equality, including global phase. If two
unitary operators have the same action on the Pauli generators, their
quotient commutes with every coordinate X and Z. Commutation with all Z
makes the quotient diagonal. Commutation with all X makes every diagonal
entry equal. Equality on the nonzero image of the zero basis vector fixes
that scalar as one. Thus one checked state and all Pauli generators prove
the equality on every input. This is not a claim that the checker tests
512 separate basis inputs for every recipe.

For each provider the checker verifies:

- All 1130 frame bases and all 3036 directed child classes.
- All 224 source and target endpoint adapters.
- All 72 raw logical warp operators.
- All 180 standard physical warp classes.
- All 180 literal dual physical warp classes.
- All 56 residual wrapper classes, on 195 helpers.
- Every native occurrence in both clean-J words: 3507 children, 240
  warps, 978 ordinary adapters, and 390 residual adapters.

## Frames, wrappers, and composition

Let Gamma_U be the canonical frame of a binary subspace U. The checker
constructs it from U by an independent basis extension and the defining
permutation, quadratic phase, and coordinate Fourier gates. Each child
recipe is compared with `Gamma_V Gamma_U^-1`. The checker also verifies
that its frames are nested and that its paid rank is the absolute
difference of their dimensions.

The source endpoint reference is the port-line operator C_q. The target
endpoint reference is `F C_q^-1`. The corresponding adapters are checked
against these operators, not only against their recorded frame numbers.
The other data endpoints are I at input and FULL at output.

For a borrowed helper with entry E and terminal V, the raw residual is
`S = Gamma_V Gamma_E^-1`. A serialized recipe gives
`S = L C_[w] R`, where `w = dim(V)-dim(E)`. The checker proves both this
factorization and

    L^-1 S R^-1 = C_[w].

This is the required native action on w coordinate factors. It restores
the other `9-w` factors exactly, including phase. The helper width profile
is `{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}`. The proper terminal frames are
used as recorded; they are not replaced with FULL.

The placement of these wrappers is also checked. No wrapped helper is
used by the added correction, the zero-frame precondition, or its
compensation before the entry wrapper. In particular, this check covers
the 61 helpers with entry I and a proper terminal. No proper-terminal
helper is used in the FULL-frame cleanup. These facts let the wrapper
factorization compose with the previously checked whole logical map.
All remaining scalar operations have equal operand frames, as proved in
the separate logical review. Every native record is bound to the exact
source record that the clean-J word retains.

## Backward warp convention

The literal inverse transpose of a unitary logical warp K is its
entrywise conjugate. The original serialized event labels are the same
for the two orientations. The orientation must therefore select the
correct physical recipe when it uses the literal dual convention.

The new dual tables pass the independent test against

    Gamma_V conjugate(K)^sign Gamma_U^-1.

Every such recipe has rank zero. The distinction is real: 172 of the 180
dual physical recipes differ from the standard table for each provider.
The review does not treat the two tables as byte-equal.

There is a general closure theorem behind this result. Let K be a
monomial Clifford operator whose nonzero entries are fourth roots of
unity. In a standard basis, write K as an affine permutation with phase
`i^(c + alpha.x + 2q(x))`, where q is a binary quadratic form. The quotient
`conjugate(K) K^-1` has phase `2(c+alpha.x)` modulo four, after an affine
change of coordinates. It is a signed Z Pauli. If
`W = Gamma_V K Gamma_U^-1` is monomial, then

    Gamma_V conjugate(K) Gamma_U^-1
      = (Gamma_V P Gamma_V^-1) W

for that Pauli P. Clifford conjugation preserves the Pauli group, and a
Pauli is monomial. The dual product is therefore monomial. Apply the same
argument to `K^-1` for a negative occurrence. The fourth-root hypothesis
holds for every source K. With an arbitrary global phase, the quotient
is instead a scalar times a Pauli; monomial closure still follows, but
the serialized phase contract needs the stated hypothesis.

The whole backward scalar map was proved over free invertible warp
generators. Thus it also permits a consistent same-K implementation. The
literal dual tables give the direct inverse-transpose implementation
without the need to use that alternative interpretation.

## Checks, limits, and reproduction

The run used Python isolation and optimization:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/check_new_native.py --providers base extra --out work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json

It returned `PASS_INDEPENDENT_NEW_CORE_NATIVE_RECIPES`. Checks remain
active under `-O`. The receipt records all input pins and both providers.
Negative controls reject a wrong global phase that has the correct Pauli
action and a wrong FULL terminal. A further check confirms that literal
conjugation changes some source warp operators.

Exact base operator identities imply the same identities for every
positive tensor power. This implication does not supply a caller's
exterior phases, legal source access, owner schedule, or recursive cost.
Those remain obligations of the complete construction.

The fresh source generation, source attribution, and commit-pinned links
are in `../new-native-recipes-20261017/NATIVE-LIFT.md`. OpenAI Codex
assisted this independent review. This is a separate agent calculation,
not a maintainer review. No PR, push, or publication commit was made.
