# JP8 backward fan-in in the full-frame cleanup

The construction replaces 999 maximal runs in the pinned JP8 backward local
program. Each run consists of consecutive additions to one target, with one
non-unit coefficient magnitude. The replacement uses one existing coefficient
work stream and saves 19,688 real-component arithmetic operations. It preserves
the exact block map and the full program's charged prefix envelope.

The scope is `full_frame_cleanup`, frame 1, with live-register sources and
targets. Other phases and forward JP8 stay unchanged. This is a finite local
arithmetic result. It does not replace the selected supplier certificate or
claim a new global kappa bound.

## Inputs and relationship to prior work

The source program and canonical word are the JP8 files under
`research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/`.
The original coefficient price is the binary-Horner rule in
`research/complex-k492-owner-repair/code/invoice_allcold.py` and its inherited
`emit_local.py`. The package pins those repository inputs rather than depending
on an open pull request.

The description and metadata of [PR #722](https://github.com/CrocSwap/integer-mult-bounds/pull/722)
were inspected at `a0766ab0fab379e1997fadc3ca157578d57986c1`.
It is a conceptual predecessor for sharing coefficient preparation across a
contiguous run; its implementation was not independently reviewed here.
Its reported common-source scan and
this common-target construction have different access and workspace arguments.
This construction collects sources into one work stream and emits the binary
coefficient into the target, so a second temporary stream is unnecessary.

## Exact block map

Write a run of length `g >= 2` as

```text
target += epsilon_i * n / 2^k * source_i,  i = 1,...,g
```

Here `n > 0`, `k >= 0`, and `epsilon_i` is either sign. The fraction is in
lowest terms. No source is the target. Sources need not have independent
values, because the argument is an identity of linear maps.

Let `W` be the original coefficient work register for one real component.
The replacement performs the following operations.

1. Clear `W`.
2. Add each signed source to `W` once.
3. Halve `W` exactly `k` times.
4. Read the bits of `n` from least to most significant. Add `W` to the target
   at each set bit and double `W` between successive bit positions.
5. Clear `W`.

After step 2, `W = S = sum_i epsilon_i * source_i`. At bit position `j`,
`W = 2^j S / 2^k`. The sum accumulated into the target is therefore
`n S / 2^k`, exactly the original update. Every source and every other live
register stays fixed.

The entry clear removes arbitrary incoming private dirt. The exit clear maps
the work register to zero. The original per-addition Horner lowering has the
same two clear operations, so the block maps agree on the private input column
as well as every live column. This is equality with the original erase-to-zero
semantics, not a claim that arbitrary private dirt is reversibly restored.

Apply the same real scalar schedule to both components of a complex stream.
The schedule needs only the work register already used by the original
lowering for that component. It does not require two simultaneous complex
temporary streams or an additional physical helper.

## Access and frame conditions

Frame 1 has rank 9, equal to the local frame height. The inherited local audit
requires every source and target of a scalar event to be present in that
event's frame. Each selected run has constant frame metadata equal to 1.
All its sources remain unchanged throughout the run, and the target is not
among them. The sources can therefore be read while forming `S` before any
target accumulation. The cleared coefficient register represents the zero
stream in that same frame.

No replacement crosses a phase event, recursive child, frame change, wrapper,
or scalar operation of a different kind. The recursive schedule and all
source-register lifetimes outside the replaced run are preserved. Restricting
the construction to the full-frame cleanup avoids any additional claim about
temporary representation at a partial frame.

## Charged arithmetic cost

Put `b = bit_length(n)` and `p = popcount(n)`. The inherited implementation
charges `3 + (b - 1) + p + k` operations per real component for each addition.
The three operations are the entry clear, target accumulation, and exit clear.

The replacement charges `g + 2 + k + (b - 1) + p`. It includes all signed
source additions, both clears, every halving and doubling, and every target
addition. Thus the scalar saving is

```text
g * [3 + (b - 1) + p + k] - [g + 2 + k + (b - 1) + p]
  = (g - 1) * [2 + (b - 1) + p + k] > 0.
```

The selected 999 runs contain 3,022 original additions. Their cost falls from
18,075 to 8,231 scalar operations. Doubling for the two real components gives
the saving of 19,688. The complete backward arithmetic price falls from
257,280 to 237,592 real-component operations. The forward price remains
257,232. These counts do not alter recursive-child or wrapper charges.

## Prefix bound

Use the inherited nonnegative envelope at each block boundary. Let `T` bound
the target and let `A = sum_i E_i`, where `E_i` bounds source `i`. Signed source
accumulation never exceeds `A`. After the halvings and doublings, the largest
possible work-register envelope is

```text
A * max(1, 2^(b - 1) / 2^k).
```

All binary target additions have nonnegative envelope coefficients. Every
target prefix is bounded by `T + n A / 2^k`, the same envelope as the original
block endpoint. The prefix bound accounts for the possibly larger unscaled
source sum when the common coefficient is below one.

Replaying this rule through the whole pinned backward program, with the
original lowering on every unchanged event, gives the same envelope for both
programs.

```text
16753412757380464429924108070201913461 / 8388608 < 2^101
```

This stays below the inherited `2^192` local payload allowance. Entry private
columns have envelope one before the first clear and are included in the
initial bound. The construction inherits the original analytic assumptions
for primitive arithmetic and recursive children. It supplies no new global
precision or asymptotic exponent argument.

## Verification obligations

The verifier must bind the source bytes, enumerate exactly the stated domain,
emit each charged operation, and compare every block on exact rational basis
columns including the private work input. It must also check the primitive
prefixes and aggregate invoice. An omitted entry clear must fail on private
dirt; an omitted exit clear must fail the final private column check. A changed
source sign, coefficient bit, target, or source must fail map equality when it
changes the block map. Understated arithmetic or workspace claims must be
rejected separately from endpoint equality.

The package is scoped to these local obligations. It leaves supplier
promotion, outer-bound recomputation, and other candidate run domains for
separate review.
