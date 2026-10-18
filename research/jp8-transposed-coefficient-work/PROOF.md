# Transposing a cleared work stream

## Endpoint identity

Take a fixed-source block `y_j += q_j x`, with `x` distinct from every
target. Targets may repeat. Its live-register matrix is `F = I + B`, where

```text
B = sum_j q_j e_(y_j) e_x^T.
```

Since no `y_j` is `x`, `B^2=0`; hence `F^(-T)=I-B^T`.
The backward block is therefore `x -= sum_j q_j y_j`. Its source registers
are unchanged, so the target updates commute within this block. No order
change across block boundaries is used.

The forward private-work program begins and ends with `clear(w)`. The
pinned constructor proves its live map is `F` and its final work is zero
for arbitrary incoming work. On the enlarged live-plus-work vector its
matrix is consequently `P = diag(F,0)`.

If the original primitive execution is `E_1,...,E_m`, then
`P = E_m ... E_1`. Transposing gives `P^T = E_1^T ... E_m^T`, implemented
by executing the transposed primitives in **reverse order**. Clear is a
self-transpose coordinate projection. Private doubling and halving are
self-transpose diagonal maps. A unit transvection transposes by swapping
source and destination, retaining its sign.

Let `D` change only the live coordinate `x` to `-x`. Then
`D P^T D = diag(I-B^T,0)`, since `D B^T D = -B^T`.
The original program never writes `x`, so its transpose never reads `x`
as the source of an off-diagonal update. The conjugation is implemented
without additional negation gates: simply reverse the sign of every
transposed update **into `x`**. Other transposed update signs stay unchanged.

Thus the concrete compiler is:

1. Reverse the complete primitive list, including both clears.
2. Keep private clears/doublings/halvings as written.
3. Swap source and target of each signed unit update.
4. Reverse that update's sign exactly when its new target is `x`.

This realizes the inverse-transpose live block while killing arbitrary
incoming work and returning it to zero. Each old primitive contributes one
new primitive, so the count is identical, including all source reads and
both clears. This algebraic argument is local to the stated register model;
it does not establish the inherited all-size multiplication theorem.

## Interfaces and complete costs

All affected original events are consecutive scalar additions in the
historical #626 JP8 `full_frame_cleanup`, at frame 1. The candidate generator
checks each backward macro against the exact signed scalar dual of its
forward counterpart. No source is written inside a forward block; no source
is written inside the backward fan-in except its common target. No child,
adapter, wrapper, frame change or private-center event lies inside a block.
All endpoints used by the block have native terminal frame 1.

The shared private stream is cleared before the next external event. Source
and target registers agree at block boundaries for arbitrary dirty inputs.
Non-scalar event streams, helper counts and recursive profiles stay exactly
as pinned. The new schedule needs no extra register or restoration pass.

The construction maps all 1,091 forward blocks, not a selected successful
subset. Their total saving is 32,810 real-component primitives in each
orientation. The backward equal-magnitude and power-only comparators save
19,688 and 30,026 respectively. Including every unchanged scalar primitive
gives 224,422 forward and 224,470 backward. The original adapter/compiler
allowances are retained in the complete unintegrated budget in EXPECTED.json.
No stronger kappa is inferred from this finite constant saving.

## Prefix growth is a separate obligation

Transposition preserves the endpoint and count; it does not in general
preserve the positive prefix envelope. For a simple counterexample, let
four independent source registers each have envelope 1 and the target have
envelope 1. The original backward block performs four additions with
coefficient `-1/4`. Separate preparation has envelope at most 1 and the
target ends at envelope 2, so the maximum is 2. The transposed shared circuit
first accumulates four sources in `w`, reaching envelope 4, then halves twice,
subtracts into the target and clears `w`. Its endpoint is the same but its
maximum is 4. The verifier executes this witness explicitly.

The concrete corpus contains 377 such isolated growth cases. At event span
`[24875,24886)`, common target 336 receives eleven contributions with
magnitudes `1/4,1/4,1/2,1/8,1/4,1/8,1/4,1/2,1/2,1/4,1/2`.
The original isolated maximum is `9/2`; the companion's maximum is `20`.
The certificate records the literal signed circuit and both exact values.
This is the largest isolated ratio in the corpus, `40/9`.

For the complete program, propagate positive envelopes independently of
signed matrix cancellations: additions and subtractions both add source
envelopes; scaling uses the absolute multiplier; clear sets zero. The
Fraction-based literal replay and the independent integer/dyadic recurrence
agree on the exact backward value

```text
16753412757380464429924108070201913461 / 8388608.
```

It is precisely the original 101-bit bound, below `2^192`. The paired
forward construction retains its original 64-bit bound. The finite full
replay, rather than an invalid blanket prefix-invariance rule, discharges
this obligation for these pinned programs.

## Independent finite checks

The second checker consumes literal backward circuits and original macros,
without importing the transpose compiler or the forward constructor. Each
block is executed on independent integer columns at scale `2^d`, where `d`
is at least its total number of halving instructions and every reference
coefficient denominator exponent. All intermediate columns are therefore
integral at that scale; each division is checked for exactness. This checks
6,776 block input columns, including dirty private work.

Its complete-program prefix checker represents positive dyadics as reduced
integer/exponent pairs and expands the original macros separately. It checks
literal costs and the exact full backward prefix, with no Fraction arithmetic.
Mutation controls include missing clears, inverse-sign errors and circuits
with the same endpoint but excessive intermediate growth. These are scoped
finite checks, not a formalization of the general multiplication theorem.
