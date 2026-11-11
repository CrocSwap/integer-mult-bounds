# Half-exponent adjacent-quotient tie

For the net splitting tax at exponent `t = 1/2`, the unique tie between adjacent
integer quotients `m` and `m + 1` occurs at a continuous peak
`z = m + θ_m` with `0 < θ_m < 1/2`. On the interval `(m, m+1)` the best
integer quotient is `m` to the left of that peak and `m + 1` to the right.

This is a written theorem. [PROOF.md](PROOF.md) derives it from the envelope
facts already on main in `research/sharp-net-splitting-tax` (PR #6769). It
answers that package's request to compare the two optimized candidates for one
fixed rational exponent, including which side of the midpoint the tie occupies.
PR #7135 proves a general-exponent staircase and leaves `θ_m < 1/2` open; that
pull request is not an input here. The `t = 1/2` side of the midpoint is proved
for every integer `m ≥ 1`, not certified on a finite list.

No selected-frontier value moves. The live selected κ remains
`363005817/100000000000`. There is no supplier inventory, paid profile, or
claim that a nearest-integer rule holds for any exponent other than `1/2`.

## Result

Let `g_σ(q)` be the optimized net coefficient of #6769 at `t = 1/2`, and let
`z(σ)` be its continuous peak. For each integer `m ≥ 1` there is a unique
`τ_m > 1` with `g_{τ_m}(m) = g_{τ_m}(m+1)`, and `z(τ_m) = m + θ_m` satisfies
`0 < θ_m < 1/2`. Equivalently, `g_σ(m+1) > g_σ(m)` whenever the peak is the
midpoint `m + 1/2`.

The proof produces the explicit critical curve
`q(u) = (2σ - 1) u^2 (2σ + 1 - 4 σ u) / (2 σ u - 1)^2`,
where `u` is the square root of the optimizing remainder, shows that this
curve is strictly convex and strictly decreasing, and reads the skew of the
envelope off that convexity. `verify.py` checks the cleared identities and
the factored derivatives. Those checks are algebraic identities, not a finite
census of `m`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -I -W error -B research/half-exponent-quotient-tie/verify.py
python3 -I -O -W error -B research/half-exponent-quotient-tie/verify.py
python3 -B scripts/research_package.py --package research/half-exponent-quotient-tie
```

The verifier prints `PASS_HALF_EXPONENT_QUOTIENT_TIE`. The package check
prints `PASS_REGISTERED_RESEARCH_PACKAGE` when the metadata pins match.
No selected cold replay, Lean, Docker, or network call is required.

## Scope

Task `scope-navigation`, scope changed. The catalogue item asks for one
misleading historical-current path or one bounded family index. The current
sentence in `docs/ci-verification.md` still titles the #6030 replay as
current, while `certificates/selected-result.json` and
`docs/research/current-status.md` name #7000. That sentence was not edited.
`research/historical-selected-replay-gap` pins the live digest of
`docs/ci-verification.md` and requires `authenticated_input` to reject an
unrecognized update of that path. The card's scope-change trigger forbids
rewriting a frozen package in order to change historical wording, and this
session did not reopen that admission.

The delivered result is the `t = 1/2` transition rule above: a bounded index
of one obstruction family (where the adjacent net-tax tie sits), with the
general-exponent case left open. Ordered eligible reading used for this
session, after removing claimed, delivered, and unpaidmoon-owned topics, is
recorded in the pull request. This package is item 9's scoped mathematical
remainder, not a second copy of #7135 and not a κ climb.

## Open next questions

- For a general exponent `0 < t < 1`, is `θ_m < 1/2` for every integer
  `m ≥ 1`? The `t = 1/2` convexity comes from an explicit radical curve.
  The same comparison would follow from convexity of
  `μ(q) = (s_q^(1-t) - t) / (1 - s_q^(1-t))` at the fixed peak `σ = ζ(z)`,
  but that convexity is not proved here. A finite sample is not a proof.
  The blocker is an identity for general `t` with no closed form for `s_q`.
- What is the coefficient `c` in `1/2 - θ_m ∼ c / m` as `m → ∞` at
  `t = 1/2`? It would turn the strict inequality into a rate. Start from the
  third derivative of `log g` on the explicit curve `q(u)`. Nothing in the
  present argument computes that coefficient. The blocker is the expansion of
  the inverse `u(q)` at `u = 1/2`, which this package does not carry out.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance.
The envelope facts are CubeJerry's #6769. Nick Petalas's open PR #7135 states
the half-window question and proves the general-exponent staircase without
the midpoint side; this note does not rely on that pull request. Apache-2.0.
No independent human or proof-kernel review.
