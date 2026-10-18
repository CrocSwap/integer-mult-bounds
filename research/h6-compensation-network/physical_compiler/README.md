# Exact local physical transition compiler

The current stronger result is the [universal affine recipe family](UNIVERSAL-THEOREM.md),
implemented in `universal.py`. It supplies exact minimal-rank recipes for
every indexed line/cap transition in the declared full-edge and bucketed
schemas, with two affine address movements and zero unit-phase factors.
Its proof, endpoint census and differential phase tests extend the bounded
generic-lowering experiment retained below. The full integrated supplier
interfaces remain open.

The retained `research/split-centres-global/vendor/clifford_exact.py`
supports the required17-bit minimal-rank transitions. This directory emits
and independently decodes17 representative recipes, with exact global phase.
It supplies a reusable lowering function and a uniform finite adapter bound;
it does not claim the full large network has been physically compiled.

Run with a Python runtime providing NumPy:

```sh
python3 -B research/h6-compensation-network/physical_compiler/compile.py
python3 -O -B research/h6-compensation-network/physical_compiler/compile.py
```

The verified runtime is Python3.12.14 with NumPy2.3.5. On this Mac its
executable is
`/Users/ross/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
The system Python has no NumPy. Both optimized and ordinary invocations
retain this directory's explicit checks.

## Exact representatives and serialization

For an actual odd address p, use the inherited source representative
`C_p`, target representative `F C_p^-1`, zero I, and FULL F. This agrees
with the norm-one source/target convention in
`notes/general-clifford-frames.tex`. Choosing the same exact representative
at each common gate makes the inherited endpoint adapters identities;
there is no unpriced conversion to a different canonical lift.

For every nested edge A→B, `compile_transition` lowers the literal operator
`T_B T_A^-1` to `L (C_[r] tensor I) R`, with R applied first. L and R
are actual rank-zero Gaussian-unit monomials: a binary address permutation,
translation, integer Z4 linear phase, symmetric binary quadratic phase,
and global unit phase. The recipes contain every integer field. The
independent decoder reconstructs those monomials through primitive
constructors; it never accepts only a frame label or symplectic matrix.

Every tested operator equality includes all34 signed Pauli generator
images and the complete131,072-coordinate Gaussian-dyadic |0⟩ state.
Two operators with the same signed Pauli conjugations differ only by a
scalar, because Pauli generators act irreducibly; their agreement on the
nonzero |0⟩ output determines that scalar. Thus these checks determine the
entire operator, including global phase, without testing every input basis
state. A unit-global-phase mutation deliberately preserves every signed
tableau column and is rejected by the state witness. Translation and
wrong-child-rank mutations are also rejected.

The NumPy evaluator uses integer real/imaginary numerators and powers-of-two
denominators. A pre-operation integer magnitude check prevents overflow.
Twelve bounded evaluator comparisons against the unmodified literal
compiler at dimensions2,3,4 cover all primitive gate types, inverse words,
and nonzero basis inputs. This acceleration changes no retained file.

## Tested actual chains and primitive counts

The actual source/target pairs are `(288,0)` with real pairing1,
`(351,0)` with real pairing3, and `(3,287)` with real pairing1. Their
binary labels are norm-one and mutually orthogonal on every tested edge.
All three helper paths lower with ranks `[1,15,1]`; their complete physical
products are exactly C17. Source tails and target climbs lower with
rank16. The K-center ascent and K-private descent lower with rank17.

`RECIPES.json` emits all17 recipes; `RESULT.json` records each adapter's
actual nonzero quadratic, linear and global phase factors and address
movement count. For example, the three rank15 middle transitions require
respectively55,32,70 unit-phase factors across their two adapters and two
combined affine movements. These counts are for the emitted recipes;
other valid lowerings may simplify the circuits further.

The two K rank17 transitions could simply use coordinate F and F^-1.
The generic retained lowering emits additional monomial factors for them;
those actual factors remain in the receipt and are charged. No finite
movement or scalar operation is declared free merely because its Fourier
rank is zero.

Reversal preserves inverse transitions exactly. The endpoints F^-1 and F
are reconciled by the explicit Pauli translation X_all: both `F^2=X_all`
and `X_all F^-1=F` are checked with signed generators and the phase witness.
This identity is physical, not only binary.

## Uniform bound and remaining gate

An h17 monomial contains at most136 off-diagonal quadratic terms,
17 linear Z4 terms and one global phase:154 unit-phase factors. A binary
permutation and translation can be performed as one affine address move
per complex coordinate. The receipt retains the looser171-phase bound
used by the adjacent bank audit; it is valid. Every positive-rank child
uses two such monomials. An unsimplified primitive circuit uses D, P, X
and a unit phase; combining P with X requires only the explicitly given
affine address map. These are finite local operation bounds, distinct
from Fourier rank and from the recursive stock invoice.

The remaining gate is the full immutable physical compilation: enumerate
and lower every distinct frame transition of the final network (including
any shared bucket frame), attach its exact representatives consistently to
all incidences, realize bank placements and pad operations, and count
actual whole-word adapters, movements, coefficient temporaries, routing,
literal/tape and precision. This directory has compiled17 representative
templates only. Its uniform monomial bound may conservatively price
uncompiled transitions, but it does not replace phase recipes for a
claimed fully compiled supplier. The inherited all-size and child-error
transfer interfaces remain separate obligations.

## Open next question

Apply this compiler to the reduced bucket network once its exact shared
frames are fixed, then produce a deduplicated all-transition recipe census
and full physical movement/adapter inventory before invoking the selected
supplier's outer interface.

Attribution: the retained exact compiler and general frame construction
are preserved unchanged, with their predecessor notices; this extension
was prepared with OpenAI Codex assistance under Apache-2.0.
