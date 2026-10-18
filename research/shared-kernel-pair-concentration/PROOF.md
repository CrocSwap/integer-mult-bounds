# Interleaved pair concentration

## Pinned construction and change

The source is Yiyang (@Lyy-iiis), PR2857, commit
`0b2e2537b368a0cade07ce3f71452ea018ebe394`, package
`research/shared-kernel-repacking`. Its local words and all native operations,
frames, helper widths, private buffers and cleanup are retained exactly. The
source itself depends on Jeremy Kothe's PR2833 at
`e9307b48d7d1b690939935ecef0f8e524e6d92f4`. `DEPENDENCIES.json` pins the
entire PR2857 package, including its inherited proof/admission adapters.

Take two copies of the source T37 chronological allocation. A call `(s,r)` at
time `t` becomes `(s,r+37k)` at time `2t+k`, for `k=0,1`. An owner row
`[t,h,r,ch,port,off]` becomes `[2t+k,h,r+37k,ch,port,off]`. Each replica's
30 source events retain exactly their original order. The final two global
cover/translation events retain their original role in the full reconstruction.
This is an interleaving of disjoint original blocks, with shared private buffers
used sequentially; it is not concurrent reuse of a dirty buffer.

In each source copy, bin `(35,16,37)` has capacity 16 and contains exactly
helper 297 of call 329, width 7, at offset 0. Its unused rank is 9. In the doubled
allocation, move just the first copy's role:

| Item | Before | After |
| --- | --- | --- |
| Call/helper | `(658,297)` | `(658,297)` |
| Owner replica/child/port | `(35,16,37)` | `(72,16,37)` |
| Offset | 0 | 7 |
| Occupancies of the two bins | 7, 7 | 0, 14 |
| Idle ranks | 9, 9 | 16, 2 |

No other role changes. At the destination the second copy's original width-7
role occupies offsets 0 through 6, so the new role occupies offsets 7 through
13. The independent checker derives strict windows from the expanded original
source events, checks the actual moved call lies inside the destination window,
and checks per-call physical families, offsets, capacities and every helper.
Thus it does not assume that an arbitrary interleaving or cross-copy move is
legal. All 271,728 roles, 666 calls and 74 original stage projections are checked.

## Recurrence price

Let `H_r` be the complete paid profile, including every idle child, and let
`W` be live families. The complex recurrence moment is

`M_H(a) = (1/W) sum_r H_r (r/73)^(1-a)`.

Doubling the source profile and W leaves this moment unchanged. The transfer
changes the doubled profile by exactly `H2 + H16 - 2 H9`. For `0<a<1`, the
function `x^(1-a)` is strictly concave on positive x, and 9 is the midpoint of
2 and 16. Therefore `2^(1-a)+16^(1-a)<2*9^(1-a)`. This proves a strict moment
saving throughout the relevant interval. It does not add a local word saving
to an unrelated packing gain.

The resulting full profile is
`{1:1611720,2:427573,3:183550,4:85248,5:26196,8:5328,16:1,48:26758}`.
It has rank mass `4,816,512 = 73*66,304 - 23,680`.
There are 66,304 live families and 66,794 physical families; the additional
490 are the retained 408 helpers, eight centres, 72 private buffers and two
other boundary families. Prefix/precision costs use the inherited block-norm
contract at T74 and are checked in full admission, not extrapolated from T37.

## Exact endpoint and multiplication exponent

`exact_moment.py` independently encloses logarithms by a range-reduced atanh
series with an explicit geometric tail, and exponentials by positive Taylor
terms with an explicit tail. All rounding is directed integer arithmetic;
gmpy2 is optional acceleration only. It brackets the new complex root in

`[0.001720097402339781716060441963,
  0.001720097402339781716060441964]`.

The admitted lower endpoint is the 24-place rational
`C = 0.001720097402339781716060`.
The retained modern outer wrapper then yields

`kappa = C - 10^-46 - 10^-70`.

Against PR2857's exact `0.001720096628684832600972 - 10^-46 - 10^-70`,
the gain is exactly
`48353434319693 / 62500000000000000000000 = 7.73654949115088e-10`.
The old doubled profile fails at the new C, and advancing C by one 24-place
grid step also fails. The full outer ledger, not just this moment argument,
is needed for the integer-multiplication kappa claim. The older supplier-only
bootstrap kappa is a separate number and is not used as the comparison.

## Retained proof obligations

All inherited conditional obligations remain: all-size compiler and common
labels; mutable-source access and restoration; whole-call hosting; precision,
coefficient work and tape accounting; exact recovery; analytic transfer; PR559
recurrence correction; and the PR589 bit supplier's H1–H5 assumptions. The
block norm contract and complete physical/private-buffer bill are retained.

In particular the PR1673/PR1758/PR1786 outer lineage still requires its uniform
Gaussian/locality, accretive Toeplitz circuit, structured boundary stability,
fine-prime padding and explicit-metadata halo arguments. Finite small-matrix
replays do not prove uniform analytic stability. The fine-padding wrapper uses
the explicit-metadata halo branch, not the inapplicable `K0^2=o(p)` branch.
The source's sparse-union schedule, per-visit record cost and positive asymptotic
slacks are retained. All-size cutoffs may be enormous; no practical cutoff is
claimed. The source contains the full credited proof notes and limitations.

The complete admission adapter is the unchanged PR2857 adapter; no validation
predicate or expected result was edited for this construction. It discovers
counts from the generated literal allocation, freezes those results, and then
restarts the complete strict release against them. Its internal historical
comparison remains PR2848; our separate final binding additionally requires
strict improvement over the reproduced exact PR2857 headline.

This is conditional finite evidence plus a scoped mathematical argument, not a
formal proof of the complete asymptotic multiplication theorem. An exponent
saving is not a measured runtime speedup.
