# Ternary follow-up: change the compiler before increasing the prime

October 7, 2026. Research on `codex/raise-kappa`, branching from
`research/aligned-bit`. No exponent beyond the imported PR #7 result is
asserted here.

Zhihao Chen's [PR #7](https://github.com/CrocSwap/integer-mult-bounds/pull/7),
at commit `6725c6a17b17871a35353fd29157f4ed851bc114`, supplies a conditional
`kappa=373/10^11=3.73e-9 > 2^-28`. Its five-subset construction changes the
payload to F3 while retaining rational address labels. The earlier
[binary polynomial-label obstruction](label-breakthrough.md) does not cover
this change of characteristic. The contribution and its dependencies are
credited in [NOTICE](../../NOTICE).

The imported producer certificate reproduced exactly, including the full
C++ support enumeration and all 365 replacement-star templates. The full
certificate also reproduced, its independent pinned-source patch applies,
and the supplied note builds. These are reproduction checks, not independent
verification of the complete multiplication theorem.

## What larger primes buy under the same architecture

For a prime p, take the `(2p-1)`-subsets of `[h]`, with common `(p-1)`-set
centers and the rational form

    H = I - (p-1)/(2p-1)^2 J.

The source/target inner product is `|S intersect T|-(p-1)`. Lucas's theorem
gives, for `0 <= j <= 2p-1`,

    binomial(j,p-1) - [j=p-1] = [j=2p-1] mod p.

For a fixed center C, write the common coordinates as t. A vector in the
span of its source indicators has sum `(2p-1)t`, so its squared norm is
the sum of the squares outside C. Those outside coordinates span all
`h-p+1` dimensions; the center coordinates are their sum divided by p.
Thus the center span is positive definite, with dimension `h-p+1`.
This proves the relevant local identity and span dimension. It does not
construct the global side circuit, bank matching, or a multiplier for p>3.

Retain three tensor stages, the existing negative source projections,
the assembly ceiling `kappa<a_b/2`, and the center returns. Set

    v = binomial(h,2p-1), c = binomial(h,p-1), b = binomial(2p-1,p-1),
    D/v^2 = v - 6c(h-p+1), m = h^3.

Giving every auxiliary role away yields
`eta <= (v-6c(h-p+1))/(2h^3 v)`. Retaining the designated-output compiler
instead requires `R >= bv+c`, and replaces the final v by `v+R`.
In both cases the optimistic bit saving is `-log(1-eta)/log(m)`.

| Payload | Best h | Free-scratch kappa ceiling | Separate-output ceiling |
| --- | ---: | ---: | ---: |
| F3 | 28 | 4.557e-7 | 4.142e-8 |
| F5 | 29 | 6.538e-7 | 5.148e-9 |
| F7 | 33 | 4.556e-7 | 2.654e-10 |

Numbers are rounded upwards; the certificate uses rational enclosures.
The finite search covers `h<200`. For the tail, let `f=1` for free scratch,
or `f=1+b` for retained outputs. Since `eta<1/(2h^3 f)` and
`-log(1-eta)<eta/(1-eta)`, the bit saving is strictly below

    1 / ((2h^3 f - 1) log(h^3)).

This decreases with h, and its value at 200 is below the finite maximum.
For all primes `p>=11`, `h>=2p>=22` and `b>=binomial(21,10)`; the same
bound puts the separate-output kappa below `7.18e-12`. Smaller h has no
positive deficit. Thus merely increasing the payload prime with this
compiler cannot provide the desired orders of magnitude. F3 already has
the best optimistic separate-output ceiling among all primes p>=3.

The useful opening is the gap between the F3 columns: eliminate allocations
for the ten partial outputs per target and reduce the additions that feed
them. Even attaining the free-scratch column requires a new implementation;
it is not a certified exponent or a forecast.

The direct producer now removes the ten-output restriction. The remaining
scale is still large: at fixed h28 with the same center losses and assembly,
a factor of ten over the aligned-bit starting witness requires at most
2,659,452 total auxiliary roles per invocation, and a factor of 100 requires
at most 177,493. With one direct side output per target and retained pair
totals, the latter leaves at most 78,835 additions under the `c+q` compiler.
These exact necessary bounds use the full logarithmic recurrence saving;
they do not assume its first-order approximation. A factor of 1,000 is
excluded at h28 even when all auxiliary roles are free. The certificate
separates these role-budget screens from the conditional constructions.

## The dependency-path guard composes with PR #7

The [guard proof](assembly-breakthrough.md) extends to the new paired complex
producer. Its local labels satisfy the same schedule, and every invocation
still has only central downward edges, each of rank h. The full h28 control
checks all three stage directions with the actual compiled roles.

PR #7 shares auxiliary banks between stages 1 and 3. This does not invalidate
the path proof: every shared role joins a completed stage-1 invocation to a
later stage-3 invocation, with nested frames of dimensions h and `m-h`.
The triple partner permutation has even intersection with its input, so the
binary join is orthogonal. There is no sharing between invocations of the
same stage. A directed path visits at most one invocation per stage and
crosses at most three central returns. Thus `D(path)<=3h` and

    q=m+6h=22120, 22120^1000 < 21952^1001.

The requirement is chronological, monotone sharing with no additional
returns within a stage; completely disjoint scratch banks are sufficient
but unnecessary. New sharing schemes still need their own frame audit.

With `beta=1/1000`, `rho=1001/1000`, `zeta=1/10000`, the new guard has
`C1=1.001099`. The old large coefficient constant remains sufficient.
The paired complex leaf saving becomes `3.8961e-8`, or 5.1948 times PR #7's
bit saving `7.5e-9`. Every exact assembly constraint and final margin passes
at the unchanged PR #7 kappa. This clears assembly room for a better bit
network, without establishing one.

Reproduce with `python3 scripts/experiments/ternary_direction.py` and
`python3 -m unittest discover -s tests -p test_ternary_direction.py`.
The result is [ternary-direction.json](../../certificates/ternary-direction.json).
