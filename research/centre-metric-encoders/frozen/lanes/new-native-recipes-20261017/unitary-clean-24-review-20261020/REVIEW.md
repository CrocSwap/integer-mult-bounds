# Independent review of the clean 24-coordinate native interface

The eight frozen local words pass. The review checks both providers,
both forward entry types, the inverse-adjoint, and the selected-bank
conjugate. Each word has the stated map on all 640 independent complex
input fields. The other 416 complex fields remain unchanged. No
material error was found in the frozen packet.

The [producer freeze](../../new-core-transfer-20261017/low-displacement-20261020/unitary-clean-24-20261020/FREEZE.json) is
`95fa9e61ddf860f3305fff398996077b6ecc164c011d37b60f6db0e459719fc5`.
The decompressed native payload is
`472935ba574b78c6ec1fd6f02fc1c0c29d37b53f73ec55b8583904bd5d5af245`.
The exact inputs and their hashes are in [INPUTS.json](normal-final/INPUTS.json).
The results are in [REVIEW.json](normal-final/REVIEW.json).

## Scope and method

The [checker](check.py) imports only the pinned arithmetic helper from
an earlier independent review and the pinned independent spatial
interpreter. It does not import the producer's native emitter,
Gaussian helper, Clifford compiler, or scalar checker.

The main replay is a reverse propagation of 1,280 real input columns.
The checker expands the literal component instructions, including
the complete source-code block. A separate forward row trace checks
the same endpoint and measures the bounds at complete block ends.
Both real and imaginary input components are independent.

The [block derivation](BLOCK-DERIVATION.md) proves why the real
component words are valid at a common complex frame. An individual
component instruction need not preserve that frame. Each complete
Gaussian ADD and the complete source code are contiguous blocks.
The checker proves their real matrices, checks their fields at the
two block boundaries, and excludes native or map instructions inside
the block.

The code matrix and the separate paid code words have the
[independent code review](../../independent-review-20261017/unitary-footprint-review-20261020/REVIEW.md)
with freeze
`c537f75e6b76397e8fa390cd03a01e8021b7e0e55ff6c8932c3cc439613d0a61`.
That review supplies the actual 24-coordinate centre recovery,
unitarity, ordinary-row identities, and mode support. This review
checks their use in the complete native word. It also checks both
unitary orders again through the real matrix of C.

## Complete local maps

Let P be the actual 24-coordinate projection and let R=I-P.
For the forward word, put `w=Cx`. The exact content map is

```text
X'_P=-z,       X'_R=w_R,
Y'_P=w_P,      Y'_R=v+w_R.
```

The I-entry contract has `X=Qx`, `Y_P=z`, and `Y_R=v`.
The Q-entry contract has `X=Qx`, `Y_P=Q_P z`, and `Y_R=v`.
All X outputs and all selected Y outputs have FULL. The ordinary
Y outputs have the stated `F9 q_p` frames.

For the selected conjugate, write `x=(a,u)` and `y=(z,v)`.
Put `w=C(z,u)`. Its content map is

```text
X'_P=w_P,      X'_R=w_R-v,
Y'_P=-a,       Y'_R=v.
```

The arbitrary selected baseline is retained with its sign. The
construction uses no zero field. The checker also checks the
unpermuted inverse-adjoint and both inverse orders of every content
map.

The dual uses the chronological real inverse-transpose of each
complete block. This gives the complex inverse-adjoint. It conjugates
each Gaussian coefficient and preserves the complete C block
boundary. Unitarity gives `C^{-*}=C`; no commutation of C with P or R
is used.

The selected-bank conjugation changes every native target,
component index, and input-adapter target. Both selected entry
fields have the same Q phase and both selected exit fields have
FULL. The checker verifies these exact phase records. There is no
runtime boundary swap.

## Native paths, phases, and fields

For each provider, the checker reconstructs the deletion of 380
events, including 192 H1 calls. It proves that no retained event
reads or writes a removed selected target. It binds all 552 retained
transfer slots to their original event indices and actual mode
coordinates. There are 328 nonzero Gaussian transfers.

Every retained native recipe and ordered frame record is byte-equal
to the accepted source. Every source input adapter and ordinary
output adapter is bound to its actual field. The 88 ordinary output
adapters are an exact subset of the accepted table.

The sixteen old selected H8 kernels per provider are exact copies
of the independently reviewed line-entry kernels. The eight new
distinct H8 kernels pass all 512 spatial input columns in a separate
Gaussian-integer interpreter. This checks 4,096 distinct columns,
including their full global phase. The results bind both providers.
The direct H9 identity-wrapper kernel is inherited by exact equality.

The inverse-adjoint preserves each exact unitary native operator
and its phase. Its field binding is checked again after the selected
permutation. The native identities lift by tensor products. The
scalar blocks act on the field index and commute with the common
complex spatial frame. No one-bit polynomial substitution is used.

All top-level instructions stay in the 224 data fields. The other
416 arbitrary complex fields are the identity in the full replay.
There is no private field, CLEAR operation, or extra field.
Recursive child hosting is a separate obligation.

## Exact local invoice and bounds

All eight words cost 16,020 real scalar primitives:

| Part | Real scalar primitives |
| --- | ---: |
| Retained and retuned core | 7,392 |
| Complete source code | 8,052 |
| 24 signed rotations | 576 |
| Total | 16,020 |

The real component word has 4,154 instructions. Its tariff is
computed from those instructions. It does not assume a complex
multiply primitive.

| Entry or word | Native profile | Children | Rank mass | Input views | Output views | Native side maps, upper bound |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| I forward | 1328 H1 + 64 H2 + 48 H3 + 24 H9 | 1464 | 1816 | 112 | 88 | 2880 |
| Q forward or either dual | 1328 H1 + 64 H2 + 48 H3 + 24 H8 | 1464 | 1792 | 136 | 88 | 2928 |

At complete block ends, the content component row one-norm is at
most 10 for the forward words and 5 for the dual words. The binary
height at these ends is at most 2. Within one complete block, the
largest component row one-norm is 16 for the forward words and 7
for the dual words. The respective local binary heights are 3 and
4. These internal bounds use that block's physical input components.

In particular, the dual's literal code word has height 4. The
height 2 bound for the separately emitted C* word cannot be used
for this different word. None of these bounds includes a recursive
child's internal arithmetic or rounding error.

## Reproduction and limits

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/unitary-clean-24-review-20261020/check.py --source-freeze 95fa9e61ddf860f3305fff398996077b6ecc164c011d37b60f6db0e459719fc5 --payload-sha256 472935ba574b78c6ec1fd6f02fc1c0c29d37b53f73ec55b8583904bd5d5af245 --out <new-directory>
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/unitary-clean-24-review-20261020/check.py --source-freeze 95fa9e61ddf860f3305fff398996077b6ecc164c011d37b60f6db0e459719fc5 --payload-sha256 472935ba574b78c6ec1fd6f02fc1c0c29d37b53f73ec55b8583904bd5d5af245 --out <another-new-directory>
```

Expected output:

```text
PASS_INDEPENDENT_UNITARY_24_CLEAN_NATIVE
```

The negative controls reject a wrong Gaussian component sign,
reversed scalar chronology, and a wrong native global phase.
Normal and optimized review receipts and input manifests must
match byte for byte. The separate reproduction record reports
that comparison and the final source-byte check.

This review establishes the local native interfaces and the stated
local invoice. It does not establish routed composition, a terminal
decoder, recursive helper hosting, finite-precision correctness,
map implementation cost, or a complete supplier improvement. In
particular, the 24 stored coordinates do not make a later
hole-to-data conversion free.

The producer lane supplied the native word. The matrix review lane
checked the code and its footprint. The native review lane supplied
the complete component-block requirement and this independent
physical replay. The source providers and earlier phase reviews
supply the unchanged native geometry. AI assistance was used.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
