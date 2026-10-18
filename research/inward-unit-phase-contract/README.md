# An executable inward unit-phase product contract

PR2298 section 6 uses a computed unit-phase product that does not increase
the operand norm and has error below `4h`, where `h=2^-p`. PR2413 notes that
this statement is not explicitly connected to the cited analytic lemma.
This package supplies a small integer kernel and a uniform proof of that
exact interface, given a certified enclosure of the intended unit phase.
It does not identify a defect in either predecessor.

For every `p>=1`, complex p-grid input `x` with `|x|<=1`, and rectangle
containing the intended unit phase `z`, assume both component widths are
at most `h/2`. Its endpoints are encoded as integer numerators over a
common dyadic denominator `2^Q`, with `Q>=p+1`, as in PR2313's `Interval`.
The kernel returns a p-grid value `y` with

    |y| <= |x|,
    |y-zx| < sqrt(25/2) h < 4h.

The result is a written interface theorem with an executable kernel, not
proof-assistant verification, a complete phase-generator audit or a new
outer-transfer theorem. No selected supplier or kappa changes.

## Kernel and proof

For a real interval `[l,u]`, choose zero if it contains zero. If positive,
round `l` toward zero to the p-grid; if negative, round `u` toward zero.
Use this independently for the two phase components, giving `w`.
This is Mason Hale's retained PR2313 `inward_quantize` operation; that
implementation and notice are copied byte-for-byte with exact pins.

For every real `a` in its component interval, the selected component has
magnitude at most `|a|`. Its distance from `a` is strictly less than
`h+(u-l) <= 3h/2` (a zero-crossing interval gives the stronger bound
`h/2`). Therefore `|w|<=|z|=1` and `|w-z|<(3sqrt(2)/2)h`.

Compute `wx` exactly using four integer multiplications and two additions
on the p-grid numerators. Round each resulting component toward zero to
the p-grid, giving `y`. Coordinatewise contraction gives
`|y|<=|wx|<=|x|`. Each product-rounding component error is less than h, so

    |y-zx| <= |y-wx| + |w-z| |x|
            < sqrt(2)h + (3sqrt(2)/2)h
            = sqrt(25/2)h < 4h.

The last comparison is exact: `25/2 < 16`. No transcendental numerical
approximation is used to establish the constant. The enclosure must
contain the **intended** phase; width and disk checks alone cannot prove
that semantic fact. The runtime rejects wrong grids, widths, input disk
and extracted phase disk before multiplication.

With this supplied dyadic endpoint encoding, projection uses comparisons
and binary shifts and takes O(Q+p) bit work. Conversion from arbitrary
rational endpoints is outside that linear projection bill and may require
integer division; the source's `Interval.rational` conversion belongs to
phase preparation. The
kernel then uses a fixed number of O(p)-bit operations and four integer
products, hence O(Q+M(p)) bit work for an ordinary multiplication cost
M(p). Signed intermediates of `2p+3` bits suffice; inputs and outputs use
`p+2` signed bits per component. This is a local arithmetic bill.
Generating enclosures, chirp descriptors, tape layouts and recursive
supplier/outer timing remain separate. The kernel is a sufficient
implementation of the cited interface, not a claim that every existing
outer implementation already executes these exact steps.

## Source binding and finite evidence

[PREDECESSORS.json](PREDECESSORS.json) pins Jose Manuel's PR2298 proof at
`8507498d363735ced0b0a3f02d5ecf80ed3e3805` and Mason Hale's PR2313 phase
enclosure code at `190637e62401516c72b267859c0dd51cac607f6d`. The latter
uses rational Taylor remainders. Its analytic enclosure argument is
retained as a dependency; this package does not claim to re-prove it.
The new theorem applies to any valid narrow enclosure, independently of
that particular producer.

The checker exhausts 50,064 products over 48 exact rational unit phases
and every disk-grid input at p=2,3,4. A separate exact rational product
checks the error and norm. It also executes 1,581 actual pinned phase
enclosures (all roots with denominator 2 through 32 at p=2,8,16), checks
their widths, and exercises 12,648 products. Their maximum component width
is `15/65536` times h, below the required half-grid width. All four exact
rectangle corners independently bound each resulting error.

Five semantic controls distinguish nearest phase rounding, signed floor
phase rounding and signed floor product rounding (each can increase norm),
an overwide phase enclosure and an out-of-disk operand. The rational phase
`(21/29,20/29)` at p=2 rounds to `(3/4,3/4)` under nearest rounding, outside
the unit disk. Thus ordinary nearest rounding does not implement the norm
contract, even though an additive error budget might remain valid.

```sh
python3.12 -I -O -B research/inward-unit-phase-contract/verify.py
python3.12 -B scripts/research_package.py --package research/inward-unit-phase-contract
```

Verification checks source SHA-256 and Git blobs before importing retained
code, then compares [RESULT.json](RESULT.json) without rewriting it. The
selected-chain baseline is source-binding orientation only; the full
selected replay and hosted CI are not claimed.

## Open next questions and credit

Can a full sequential chirp producer supply the half-grid phase enclosures
at PR2298's claimed cost over its complete eventual parameter domain? The
next step is to connect a named fast phase generator's output and cost
theorem to this narrow interface. The finite root fixtures and dense
PR2313 reference do not establish that asymptotic implementation.

Credit Jose Manuel/PR2298 for the precise outer contract; Sagar
Thakrar/PR2413 for its audit clarification; Mason Hale/PR2313 for inward
quantization, exact interval phase generation and the retained notice;
Harvey and van der Hoeven and the source07/08 lineage for the analytic
construction. New composition proof, kernel and checks prepared for ywz65
with substantial OpenAI Codex assistance. No human or formal review is
claimed. Apache-2.0.
