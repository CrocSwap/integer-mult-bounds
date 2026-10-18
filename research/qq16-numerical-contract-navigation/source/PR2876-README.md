# Compute the common rounding scale of a QQ16 line

[Nick Petalas's PR2811](https://github.com/CrocSwap/integer-mult-bounds/pull/2811)
provides a Boolean circuit for a rounded Gaussian pair, with the rounding
exponent supplied as an input. This package computes that input from the
**whole owner-local line**, including signed absolute values, zero detection
and a check of the promised grid boundary. It supplies one missing arithmetic
term; no recursively admitted child price or complete physical bill follows.

For `q >= 1` signed `w`-bit components and fixed `0 <= p < w`, put
`m = max_j |x_j|`. The literal circuit returns

```
d = max(0, floor(log2(m)) - p), with d=0 at m=0;
zero = (m == 0);
admissible = (m == 0 or m >= 2^p).
```

On the finite-format predecessor's admissible inputs, this is exactly its
common-grid rounding exponent. The total gate count, including both flags, is

```
G_scan(w,q,p) = w*(4q+2) - 2p + S(w-p) + 3,
S(n) = sum_{0 <= i < n} popcount(i).
```

The basis is two-input AND/XOR/OR and one-input NOT. Wires, constants and fan-out
are free in this irreversible combinational model. This is an exact invoice
for the emitted construction, with redundant gates retained, not a minimum.
For the predecessor's `W=456`, `w=453`, `p=122` example and `D` complex payload
coordinates per owner, **one scan costs `3624D + 1984` gates**.

## Proof and combination with the pair circuit

For each signed component, XOR all `w` bits with its sign and add that sign
using a ripple increment. This costs `3w` gates. The result is its **unsigned**
absolute value, including `-2^(w-1)`, whose magnitude needs all `w` bits.
Discarded final carry implements arithmetic modulo `2^w`; every absolute
value is at most `2^(w-1)`, so its unsigned interpretation is exact.

OR the magnitudes componentwise, costing `(q-1)w` gates. The highest set bit
of this OR is the highest set bit of their maximum: a bit above every
magnitude's leading bit is absent from every operand, and a maximizing
operand supplies the highest bit. No numerical maximum/comparator tree is
needed. This does not permit OR-ing the original signed encodings.

Scan positions `w-1,...,p`. Maintain `seen` and emit
`hit_i = a_i AND NOT seen; seen = seen OR a_i`. Exactly one hit is set when
`m >= 2^p`, at its leading position; none is set otherwise. These cost
`3(w-p)` gates. OR that hit into the output bits of constant `i-p`, costing
`S(w-p)` gates. Low positions cost `p` more ORs. Three final gates compute
`zero = NOT(high OR low)` and `admissible = high OR zero`. Adding these counts
proves the formula. The exponent has `bit_length(w)` bits, matching PR2811's
runtime input. It lies in `[0,w-1-p]`, inside that kernel's legal `[0,w]` range.
The proof works for all widths and component counts; finite builder limits
and test domains are separate.

[PR2807's finite-format proof](https://github.com/CrocSwap/integer-mult-bounds/pull/2807)
supplies `p=k`, `Qmax=Q0+3p+6`, `W=Qmax+E+20`, and a within-line component bound
strictly below `2^(W-4)` in common-grid integer units. With `w=W-3`, this gives
valid signed kernel inputs at every factor boundary. Its grid invariant
ensures a nonzero line has `m >= 2^p`; a zero line yields zero even with `d=0`.
The scan does not supply that invariant or reprove the predecessor's range or
error theorem. For inputs with `0 < m < 2^p`, it reports inadmissible and the
stated clamped extension; it does not certify the predecessor's relative error.

Compute `d` **once before the complete line**, then wire that same exponent
to every pair in every tensor factor. Exact signed coordinate wrappers preserve
`m`; their cost remains separate. Disjoint pair outputs inherit the factor's
range bound; their two redundant sign bits can be removed by wiring before the
next factor. PR2811's exact pair theorem and induction over the ordered factors
then give exactly the predecessor's integer rounded line. The exponent need
not be recomputed between pairs or factors. A four-coordinate fixture proves
that choosing a separate scale for each pair can change the answer.

Let `D` be complex coordinates per owner, `lambda` tensor factors, `N` owners,
and `L=w+2`, `ell=bit_length(w)`. Using PR2811's kernel count

```
G_pair(w) = 24L*ell + 52L + 4*2^ell + 4ell + 4,
```

one line's scan-plus-pair arithmetic uses at most

```
N * (G_scan(w,2D,p) + lambda*(D/2)*G_pair(w)).
```

This counts one scan per line per owner, not per factor. An identity projected
direction may be skipped; counting `D/2` pairs remains an upper bound. For the
unchanged 336-line decoder, multiply by 336. At the published `lambda=1`,
`h=73`, `b=64`, `Q0=64`, `E=0` example (`D=2^73`, `W=456`, `p=122`), the total is

```
22,054,368*N*D + 666,624*N gate evaluations.
```

Of this, `20,836,704*N*D` is the existing pair subtotal and
`1,217,664*N*D + 666,624*N` is the new scan term. These are mathematical
circuit sizes/evaluation counts, not a claim to have materialized a circuit
at `D=2^73`, reusable hardware area, tape time or recursive native rank.

## Reproduce and evidence

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py --package research/qq16-block-scale-scan
```

The direct replay is read-only and works without Git:

```sh
python3.12 -Werror -I -O -B research/qq16-block-scale-scan/verify.py
```

Expected: `PASS_QQ16_BLOCK_SCALE_SCAN assignments=309494 scan=3624*D+1984 no_new_kappa`.
The registered command repeats normal/optimized replay and five artifact groups.
`--write` creates an absent receipt and refuses overwrite.

[RESULT.json](RESULT.json) records 309,494 exhaustive signed-block/reserve cases
across 67 circuits: all one-component inputs through width 8, two-component
inputs through width 6, and four-component inputs through width 4, each at every
legal reserve. All include zero, negative powers of two, the most-negative
value and blocks below the admissible grid boundary. Another 313 fixtures cover
widths 9,16,65,453,1024,4096. Exact emitted gate counts are checked. The
popcount count routine is compared with direct sums at 0..1024.

The authenticated, unchanged PR2811 pair code is reused with credit. There are
258 complete small tensor-line comparisons against a separate Fraction
nearest-even oracle, with both signs and one, two or three ordered factors.
The scan itself imports no predecessor implementation. Five semantic mutations
fail: wrong exponent, missing zero flag, false admissibility, broken negative
carry, and using source sign bits as magnitudes. The pair-local-scale control
also fails; fourteen malformed construction/input cases reject. Five CLI groups
check Git-free read-only replay, source authentication before execution, typed
or missing receipts, duplicate JSON keys and deterministic exclusive regeneration.

[PREDECESSOR.json](PREDECESSOR.json) binds three small snapshots to Git blobs and
SHA256 at this package's main base; the executable pair snapshot also equals
PR2811's original head. The README snapshots include main's integration notes.
[SOURCES.json](SOURCES.json) preserves historical source provenance; live
predecessor packages and the selected record are unchanged. All result checks
use explicit exceptions and run with Python optimization enabled as well.

## Scope and family decision

This is a **local arithmetic obligation**, refined from `joint-query-controller`.
It closes the missing supplied-exponent term in PR2811's direct Boolean model.
The quantified proof is written; the finite checks do not prove a complete
multiplication theorem. No human or formal-kernel review, full native semantic
replay, selected cold replay or new kappa is claimed.

The builder is an offline bounded Python reference with managed allocations.
It caps width at 4096, component count at 1024 and total input bits at 65,536;
bit-sliced evaluation caps batches at 65,536 assignments. Its gate count is at
most `4qw + w*(2+ceil_log2(w)) + 3`, hence at most 319,491 with these caps.
The theorem and symbolic invoice do not require constructing huge payloads.

Inputs are read through free circuit fan-out; no source component is overwritten
by this scan. Retaining/erasing the exponent, realizing fan-out and circuit
workspace, physical scan/address travel, signed encoding, wrappers/maps,
restoration, other scalar instructions, entry/F0/B1 errors, and an actual
output consumer remain separate charged obligations. No reversible or fixed-tape
implementation is supplied. A numerical bit subtotal cannot replace an admitted
recursive rank-one tariff. The family decision is **narrow and stop**: do not
start more local gate optimization without a pinned complete caller budget.

## Open next questions

Can a pinned admitted child/caller realize this scan and the pair circuit within
its complete allowance? Start by specifying the signed payload layout and where
one common exponent survives all tensor layers, then charge its physical scan,
circuit work, movement, cleanup and consumer together. The missing admitted
representation and complete caller ledger block that transfer. This package
does not declare unknown costs zero. [TASK.json](TASK.json) records the structured
question, exact scope, claim and overlap limitations.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in derivation, code,
verification and writing; Apache-2.0. Evidence is author-checked.

Credit **Nick Petalas / PR2811** for the retained exact pair circuit and its
invoice, **PR2807/2771/2736** for the finite format, relative block scale and
completed-error contract; **ywz65 / PR2707/2540**, **Arham Tahir / PR2681**,
**Ali Romman** and the QQ16/native/geometry lineage. Ross Richardson's floor-grid
and reversible-lifting contracts in Discussion2727 are distinct and retain their
credit. Absolute-value circuits, leading-bit encoders and popcount identities
are standard; the contribution is their exact source-bound scale interface,
composition check and additional invoice. Original source notices are retained.
