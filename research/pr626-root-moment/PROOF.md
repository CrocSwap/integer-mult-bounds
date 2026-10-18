# Exact rational-power enclosure and the checked obligation

Prepared for arkfx with substantial OpenAI Codex assistance; Apache-2.0.

## The precise finite statement

Let `H[r]` be the complete paid child profile in the selected #626 assembly,
`m=73`, `W=7168`, and let `b` be the supplier saving. The native moment is

```text
M(b) = sum_r H[r]/W * (r/m)^(1-b)
     = sum_r r*H[r]/(m*W) * (m/r)^b.
```

The conservative model adds

```text
F(b) = (32*m^2*sum_r H[r])/10^16 * (1/W) * (1/m)^(1-b)
     = 32*m*sum_r H[r]/(W*10^16) * m^b.
```

This is the rank-one exceptional-set profile charged by `check_moment` in the
base commit's `research/complex-k492-owner-repair/code/assemble.py`. The native
complex model omits that charge under the reviewed #559 exact-cover recurrence
correction. The construction-level correctness of both models is inherited.

For the source-recorded `b_N = 65528268492323474503 / 40000000000000000000000`
and `b_C = 327641341885943404413 / 200000000000000000000000`, the package proves
these particular real-number inequalities through rational enclosures:

```text
M(b_N) < 1 < M(b_N + 10^-24)
M(b_C) + F(b_C) < 1 < M(b_C + 10^-24) + F(b_C + 10^-24).
```

These are the local moment obligations. They are not the assembled κ claim.
All profile coefficients are positive and every `m/r > 1`, so each model is
strictly increasing in `b`; the adjacent-endpoint decisions enclose its unique
threshold within the recorded interval. Existence follows here from continuity
and the opposing strict signs. No claim of global supplier optimality follows.

## Enclosure argument

Take an exact rational base `a >= 1` and exponent `0 <= b <= 1`. Set
`D=2^K`, `k_L=floor(bD)` and `k_U=ceil(bD)`. Monotonicity gives

```text
a^(k_L/D) <= a^b <= a^(k_U/D).
```

Thus no analytic tail estimate is needed. The binary digits of an integer
`0 <= k < D` write `k/D` as a sum of selected `2^-i`, for `1 <= i <= K`.
Consequently `a^(k/D)` is a product of selected repeated roots
`a^(2^-i)`. At `k=D`, use `a` directly. At `k=0`, the empty product is one.

All intermediate intervals use a fixed scale `S=2^B`. An integer pair `(L,U)`
denotes the real interval `[L/S,U/S]`. Initially use
`L=floor(aS)`, `U=ceil(aS)`. Given such an enclosing pair, define

```text
L' = floor(sqrt(L*S))
U' = ceil(sqrt(U*S)).
```

Then `[L'/S,U'/S]` encloses the square root of every element of the original
interval. `isqrt(n)` gives the exact lower integer; add one for the upper
integer precisely when that lower integer's square is smaller than `n`.
This proves the root invariant for every step by induction.

For nonnegative enclosing pairs `(L1,U1)` and `(L2,U2)`, multiplication gives

```text
floor(L1*L2/S)/S <= product <= ceil(U1*U2/S)/S.
```

Induction over the selected binary factors proves that `dyadic(k)` encloses
`a^(k/D)`. Take only the lower endpoint of `dyadic(k_L)` and upper endpoint of
`dyadic(k_U)` to enclose `a^b`. This argument holds for any supported positive
depth and precision. An overly coarse grid may fail to decide a moment; it
cannot justify acceptance when the strict rational comparison fails.

The implementation uses `K=163`, `B=256`, sums all terms with `Fraction`, and
does not round the final sum. Multiplying by nonnegative rational weights and
adding intervals preserves containment. The four final certified intervals
lie strictly on their required sides of one; their exact endpoints are stored
in `CERTIFICATE.json` and reproduced on every run.

## Independent comparisons and failure distinctions

For each kernel fixture `a` and `b=p/q`, the checker separately evaluates

```text
lower^q <= a^p <= upper^q
```

with exact integer/rational exponentiation. Positive qth powers are strictly
increasing, so these comparisons independently establish containment for the
fixture without using the root enclosure's logic. Fixtures cover all 72
ratios `73/r`, denominators 2 through 13 with numerators 1 and `q-1`, four
endpoint cases, and 83 seed-83 additional integer bases with denominators
2 through 31. Duplicate fractions across denominators are retained as distinct
test fixtures; this is 1,743 comparisons, not 1,743 distinct rationals.

The two coarse kernel controls are concrete failures of unsafe enclosures:
using only `85/256` to approximate `1/3` from below omits the true cube root of
`73/48`; rounding the upper bound for `sqrt(2)` down omits `sqrt(2)` itself.
The separate package tests mutate the actual implementation and require
rejection. These controls corroborate the general invariant; they are not a
formal proof that every possible implementation error is detected.

The equal-count/rank-mass control replaces two rank-two children with one
rank-one and one rank-three child. Both totals are preserved, but the upper
native saving endpoint becomes accepted. Strict concavity of `r^(1-b)` for
`0<b<1` explains the reduced moment; the executable control supplies the exact
sign for this profile. This is a concrete arithmetic distinction, not a claim
that the altered profile has a realizable circuit.

Omitting idle children, replacing live stock by physical stock, or dropping
the conservative surcharge likewise demonstrates false acceptance in those
specific modified models. No such error is alleged against the retained
selected assembly. Its full profile and stated charge agree with this check.

## Dependency boundary

The checker authenticates five source files, binds the selected certificate
path/hash and source head, recounts invoice call multiplicities and the sum of
their paid profiles plus the separate idle profile, and checks rank mass and
deficit. These are consistency checks of frozen receipts. It inherits the
proof that the receipts enumerate every required recursive child and that
native complex surcharge removal is permitted. It does not independently
verify scalar maps, phase frames, physical hosting, restoration or all-size
realization. The selected maintainer review enumerates the remaining compiler,
common-label/mutable-basis, hosting, precision/tape and analytic assumptions.
No finite replay here formalizes the integer multiplication theorem.
