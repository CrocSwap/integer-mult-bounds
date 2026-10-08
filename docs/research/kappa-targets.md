# Targets beyond the aligned-bit witness

October 7, 2026. This investigation starts from `research/aligned-bit`, commit
`5015011`, on `codex/raise-kappa`. The current conditional witness remains
`kappa=1624/10^12`. The results below are scoped upper bounds and necessary
conditions, not a new multiplication claim.

The first objective is a factor of 100 or 1,000, rather than another parameter
adjustment. Exact optimistic bounds show which construction assumptions must
change. Under the current three-stage construction, retaining the aligned
centers caps the possible improvement below **26.24 times**, even if every
auxiliary role were free. Keeping the current side-output compiler as well
caps it below **6.56 times**, even if all its additions were free.

The checks are in [audit_kappa_targets.py](../../scripts/audit_kappa_targets.py),
with [exact output](../../certificates/kappa-targets.json) and
[tests](../../tests/test_kappa_targets.py). They cover every admissible ground
size, including an infinite-tail bound. They do not exclude other centers,
terminal frames, scalar topologies, or assembly algorithms.

## Why assembly tuning is insufficient

Write `a=1-tau` for the available bit-network saving. The retained compact
layer has `lambda' > lambda > tau`. Thus its final margin satisfies

    g3 = epsilon (1-lambda') < epsilon a.

Direct layout has `g4=(1-epsilon)a`. Consequently every admitted witness
satisfies

    kappa < a min(epsilon,1-epsilon) <= a/2.

This bound survives improvements to the Gaussian cost or precision guard.
Such improvements can make a better network usable, but cannot amplify a
fixed bit saving by orders of magnitude within these margins.

## Making every auxiliary role free

Retain the full triple family, three tensor stages, aligned center trajectories
and the rational negative-source charge. For ground size h,

    v=C(h,3), N=v^3, m=h^3,
    D=N-6v^2 h(h-1), W>=2N.

Positive deficit requires `h>=39`. Even after discarding every auxiliary
role charge,

    eta=D/(Wm) <= (h-38)/(2h^3(h-2)).

The largest possible recurrence saving allowed by these counts is
`-log(1-eta)/log(h^3)`. Exact logarithm intervals separate `h=50` from every
other integer `39<=h<200`. There `eta=1/10^6`, giving

    a < 8.520745e-8,
    kappa < 4.260373e-8 < 27 * (1624/10^12).

For every `h>=200`, use `eta<1/(2h^3)` and
`-log(1-eta)<eta/(1-eta)`. Hence

    a < 1/[(2h^3-1) log(h^3)],

a decreasing bound already below the `h=50` lower interval at 200.
This is an optimistic ceiling, not an attainable zero-scratch construction.
Allowing odd h makes the bound stronger as a rejection test: the current
aligned pairing requires even h, and the maximizing h is even anyway.

## Keeping the current designated outputs

The current circuit compiler uses `R=c+q` roles per invocation, where c is
its number of additions and `q=3v+h` counts partial outputs and center totals.
Keep that compiler and the stage-1/stage-3 sharing arrangement. Even after
setting every addition cost to zero,

    R>=3v+h,
    W>=2v^3+2v^2(3v+h).

The same exact finite search and tail bound again select `h=50`, now with

    kappa < 1.064414e-8 < 7 * (1624/10^12).

This statement is limited to that designated-output compiler. A different
allocation scheme or scalar schedule needs a fresh role and rank count.

## Address dimensions required by larger targets

A broader necessary screen discards the centers too. Retain only the
rank-one terminal accounting `D<=N`, the two data banks `W>=2N`, and the
assembly cap above. Then

    kappa < -log(1-1/(2m)) / (2 log m).

The right side decreases with m. Exact rational intervals locate the last
integer m passing this optimistic screen for each target:

| Improvement over current kappa | Target kappa | Necessary m at most |
| --- | --- | --- |
| 10 times | `1.624e-8` | 1,106,181 |
| 100 times | `1.624e-7` | 130,674 |
| 1,000 times | `1.624e-6` | 15,911 |
| 10,000 times | `1.624e-5` | 2,022 |

These are necessary conditions, with zero losses and zero scratch assumed
only to make rejection conservative. Passing them is not evidence of a
network. In particular, the current `m=125000` barely survives the factor-100
screen before any center or scratch cost is paid, and cannot survive the
factor-1,000 screen.

## Research direction

The main targets are therefore a smaller address representation, a lower-loss
central construction, or a new scalar exchange topology with compatible
frames. The [affine-center audit](bit-breakthrough.md) rules out arbitrary
affine point-center predicates as a factor-100 route under its source-span
and target-complement frame rules, even with an optimal side-role count.
The [higher odd subset audit](label-breakthrough.md) excludes one natural
replacement family even with free scratch. Simple re-tuning and
side-addition reductions remain useful for incremental gains, but cannot
deliver the stated factor-100 objective under the retained central loss.

The constructive result of this pass is a
[dependency-path precision guard](assembly-breakthrough.md). It charges at
most `m+6h=15775` child calls on a coefficient path in the complex network,
instead of concatenating every call. With unchanged large guard constants,
this permits `beta=.001` and `C1=1.001099`. The complex leaf saving rises
from `3.36e-9` to `1.3986e-8`, giving room for a future stronger bit network.
An alternate baseline witness checks every assembly margin with this guard;
it retains exactly the current kappa. This new written extension is still
conditional and is not integrated into a new manuscript patch.

The inherited baseline passed `make verify`: 189 tests, 20 patch-application
checks, and unchanged certificate and patch regeneration. New research checks
are additive; the pinned upstream files and existing witnesses are preserved.
The completed follow-up passed the full `make verify` run with 212 tests and
all 20 patch checks. All 54 certificates and patches regenerated byte for
byte, including the four new research certificates.
