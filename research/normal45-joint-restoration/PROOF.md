# Joint restoration and the clean-buffer boundary

This is an independently implemented finite algebra check of Marius-Paul
Dumitrean's PR2942 at `a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`, with a
written general block-matrix observation. It is not a native circuit proof,
supplier admission, formal-kernel proof, or new exponent claim.

## Exact model

Each provider has 112 source coordinates, 112 arbitrary target coordinates,
and 408 arbitrary dirty helper coordinates: 632 independent inputs. The 72
removed coordinates are absent. A private buffer is separate from its dirty
helper: the parent has 82 private zero slots and the final word has 86. These
slots must start zero. Every source and dirty helper must return to its own
input; the forward target map is `target[i] += source[i]`. The dual map is the
inverse transpose, `source[i] -= target[i]`.

The 72 warp names are independent invertible noncommuting operators. We work
in the dyadic group algebra of the free group on those names. A coefficient
is an exact dyadic rational and a monomial is a freely reduced operator word
attached to one independent input. Equality of all coefficients in this
algebra specializes to every choice of invertible operators on a rational
vector space. This is an algebraic statement; no Clifford phase, physical
frame or rounding theorem follows from it.

`verify.py` implements each sparse row with integer numerators and one common
power-of-two denominator. Addition aligns denominators and removes zeros;
left multiplication by a warp prefixes one letter and cancels an adjacent
inverse. Both operations are exact by their definitions. Starting with one
unit monomial for every original input, induction on the literal primitive
sequence therefore computes every coefficient of the complete linear map.

For inverse-transpose replay, write `D_j = K_j^(-T)`. A scalar addition changes
destination and sign, a scalar scale is inverted, and a warp uses `D_j`.
A correction `t += q K_a ... K_b s` becomes
`s -= q D_b^(-1) ... D_a^(-1) t`. The implementation's two-symbol fixture
checks this order explicitly; free words distinguish commuting mistakes.

## The complete finite words

The replay reads only the eight hash-bound JSON inputs. It imports no
predecessor producer or checker. The B sequence is reconstructed from its
literal gates and ordered warp-position records. The complete program is
initial operator corrections, precondition, compensation, A (including its
prelude), the delivery cut, B with its warps, and restore.

At the forward delivery cut the checker compares every target row, every
declared cold-helper row, and every cold-helper column against the stated
map. Thus a restored helper cannot still leak into another live row. The
private slots remain zero. The final helper-end set is exactly the parent's
82 helpers plus `{249,267,251,265}`, with each inherited endpoint unchanged.

The cleanup recipe is reconstructed independently: remove target writes and
the prelude from the non-target middle, reverse its complete gate list,
invert every primitive, and replace every restored helper reference `h` by
its private slot `704+h`. The literal cleanup must equal this recipe exactly.
The parent has 4,829 such gates and the final word has 4,992. Full replay then
checks every original output row and every private zero return, in both
orientations, for both parent and final providers.

The separate `independent.py` does not share arithmetic or replay code. It
pushes selected columns and pulls covectors backward through each actual
step-refitted middle. Its paired-boundary derivation and finite coverage are
in [INDEPENDENT.md](INDEPENDENT.md). In particular it checks the ordered
compensation product and preservation of prior extracted directions.

## Why forward cleanup alone is insufficient

Here is a written all-dimension observation, separate from the finite source
check. Let an invertible linear circuit act on original coordinates `x` and
private coordinates `z`. Suppose its forward clean-buffer contract is

```
F(x,0) = (A x,0),
```

where A is invertible. Then, in these coordinates,

```
F = [[A, B], [0, D]],
F^(-T) = [[A^(-T), 0], [-D^(-T) B^T A^(-T), D^(-T)]].
```

The first block identity follows by evaluating every original basis vector;
invertibility of F and A implies invertibility of D. The second is obtained
by multiplying the block inverse and then transposing. Consequently
`F^(-T)(x,0) = (A^(-T)x,0)` for every x if and only if B=0: multiply the
lower-left zero identity by the invertible `D^T` and `A^T`. Forward
clean-buffer correctness alone does not prove the dual zero-return contract.
Both checks prove original/private decoupling, but they do **not** prove D=I
or permit arbitrary dirty private buffers.

The source supplies a concrete sensitivity witness. Delete only the first
final cleanup gate, `register94 -= 4 * private265` (`private265` is register969).
For each provider the complete forward replay still passes on every original
input with private buffers zero. In inverse-transpose replay every original
row still has its expected value, but private register969 has coefficient
`-1` on original input register2. This exact nonzero coefficient disproves
dual private-zero return. The valid submitted word contains the gate and
passes both orientations. This is a control against incomplete verification,
not a defect allegation against PR2942 or its two-orientation checker.

Other controls replace compensation by the stale parent map, reverse the
terminal blocks while regenerating cleanup, omit the final cleanup gate,
invert an anticipatory operator, and violate the private-zero premise. Each
is rejected by its mathematical predicate. Splitting one cleanup addition
into two equal dyadic additions is accepted as a semantically equivalent
positive control; canonical-recipe equality is deliberately bypassed only
for these explicitly labelled algebraic fixtures.

## Cost consequence and limits

PR2942's proposed mechanism shares terminal frame overhead across four helper
extractions. Its reported per-call delta is `18 H1 - 8 H2 + 6 H3 - 6 H4`,
four helper widths change 9 to 8, and four additional private zero buffers
remain charged. Those are the source's cost claims, not a complete invoice
independently established here. This result checks the essential simultaneous
algebraic premise under which its downstream cost comparison can matter.

Actual frames and warp realizations, native phases, chronological owners,
source movement, full physical storage, precision, recursive/outer invoices
and inherited all-size assumptions remain separate. The selected record is
unchanged. The finite formal-word identity and the written block observation
have not been checked by a proof-assistant kernel or independent human.

Credit Marius-Paul Dumitrean/PR2942, Mason Hale/PR2917, Jeremy Diviney/PR2908,
Jeremy Kothe/PR2894/2833, Yiyang Lu, Dugongue, Tekalign, icekylinx and the
retained source lineage. Prepared for Ross Richardson with substantial OpenAI
Codex assistance and a separate AI mathematical check. Apache-2.0.
