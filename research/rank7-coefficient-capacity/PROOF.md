# Coefficient construction fits the conditional A-stage capacity

## Statement and boundary

Use the exact two PR3076 provider words retained by PR3089, and PR3078's three
literal lowering policies. The scientific main baseline is
`d8e0f83f00191df62174b641e9fff055c357f641`. Exact predecessor commits and
source bytes are in [VENDOR.json](VENDOR.json).

Let each initial normalized real or imaginary input component be an integer
in `[-L,L-1]`, where `L=2^(P-1)` and `P>=3`. Retain PR3089's exact residual
adapter endpoint hypothesis, canonical frame interpretation, Gaussian monomial
warps and conjugated frames in the inverse-transpose orientation.

Replacing every ordinary prelude/A scalar by any of the three literal recipes
preserves its endpoint, restores its source and clears its initially-zero
scratch. Every changed recipe register fits the same arithmetic capacity as
the predecessor's covered endpoints and frame conversions. The complete
covered computation therefore needs seven common fractional bits and `P+20`
signed bits, or 84 bits at `P=64`.

This supplies the previously excluded scalar coefficient-construction
microstates. It does not supply residual adapter interiors, recursive child
arithmetic or errors, centres and later phases, a physical bit implementation,
stock, ownership, movement or a complete supplier invoice. CLEAR is a charged
unit instruction here. Its physical realization is not proved.

## Why normalized microstates describe physical values

At a scalar event the physical target and source have the same canonical
frame `F`, and their actual correlated normalized rows are `t` and `s`.
Scratch starts at zero. Forward, the local physical rows are

```text
F(t), F(s), F(0).
```

Backward, replace F everywhere by its complex conjugate. Each unit operation
is a real linear COPY, CLEAR, signed ADD, NEG, DOUBLE or HALF. It commutes with
F and its conjugate. After any recipe prefix each physical local row is thus
`F(alpha*t + beta*s)` for the exact rational local weights alpha and beta.
This identity describes matching recipe prefixes on the real and imaginary
components. If the components execute sequentially, each component still has
its own checked prefix, so the same componentwise capacity applies.
Source writes in the source-walk policy follow the same identity. A scratch
field can be interpreted in the common frame because zero has every frame;
actual provision and movement of that field remain physical obligations.

The verifier computes those weights from the literal recipe bytes and
substitutes the current correlated rows, including cancellation. Separately,
an integer interpreter starts from those same t and s rows on denominator
`2^32` and executes the literal unit instructions. Every HALF checks its
remainder. Every changed row agrees exactly with the rational substitution.
At each macro's end the integer interpreter checks

```text
ADD:   [t + q*s, s, 0]
SCALE: [q*t,     0, 0]  with no source operand
```

The expected target comes from a separate application of the original scalar
macro. This is a second interpreter of the coefficient arithmetic, not an
independent reconstruction of all inherited supplier semantics. The engines
share the pinned normalized-row propagation and source generator.

## Grid and magnitude bounds

For a reduced dyadic normalized row u, let d be its largest denominator
exponent and N its sum of absolute rational coefficients. Formal warp words
are retained rather than identifying unknown operator relations. Their actual
Gaussian monomial actions preserve symmetric component bounds, so this can
overestimate N but cannot undercharge it.

For a rank-r canonical frame put `E=ceil(r/2)`. The paired Fourier identity
used by PR3089 gives at most `d+E` fractional bits and symmetric component
magnitude at most `L*N*2^E`. Conjugation preserves the bounds. The fresh replay
checks the independent axes, canonical Fourier gate lists and monomial
invertibility of all 1,124 frames in each provider.

Apply this bound after every unit instruction. Unchanged rows were already
covered at their preceding write, at the initial input, or by the inherited
frame/conversion envelope. The zero scratch requires no larger bound. All
macro endpoints are unchanged, so PR3089's correlated conversion and pair-first
C-numerator bounds continue to apply without modifying those circuits.

The exact finite envelopes are identical in both providers and for all three
coefficient policies:

| Covered arithmetic | Forward d | Forward B | Backward d | Backward B |
|---|---:|---:|---:|---:|
| Coefficient microstates alone | 5 | 2928 | 7 | 550 |
| Including inherited endpoints/conversions/C numerators | 5 | 4896 | 7 | 934 |

B denotes a symmetric magnitude bound in units of L. These are sufficient
envelopes, not sharp minima. The microstate witnesses and all instruction
hashes are in [RESULT.json](RESULT.json).

On common fractional grid D=7, the signed capacity condition is strict:

```text
L * B * 2^7 < 2^(W-1).
```

Since `4896*128 = 626688 < 2^20`, W=`P+20` suffices for every P>=3.
Separate forward and backward grids retain the predecessor's `P+18` and
`P+17` sufficient widths. Input negation by a Gaussian phase can produce +L,
so equality at the positive signed limit must not be accepted. Controls include
a source that doubles to this forbidden limit and then restores itself, and a
source that transiently needs an eighth fractional bit and then restores itself.
Endpoint checks alone accept both; the microstate capacity checks reject them.

## The instruction comparison

Each provider and orientation contains 5,964 ordinary prelude scalars and
4,028 A scalars, hence 9,992 macros. There are 29 distinct kind/coefficient
templates. The exact recipes give:

| Policy | Unit instructions for one component | Both components |
|---|---:|---:|
| Explicit scratch control | 32391 | 64782 |
| Source digit walk | 28855 | 57710 |
| Target digit walk | 28855 | 57710 |

The saving is 7,072 real unit instructions per provider word and orientation
through this prelude/A interval. Both walk policies retain the scratch fallback
when a walk is not cheaper. The target-walk policy never writes its source.
Any scratch used is checked zero at each macro's completion. The control and
walk recipes are inherited from PR3078; the contribution here is binding their
actual construction microstates to PR3089's native capacity.

These counts give no cost to the excluded operations and do not constitute a
complete physical bill. In particular, a unit shift, copy or clear is not a
claim of one Boolean gate. The recursive child profile, selected kappa and
supplier admission are unchanged.
