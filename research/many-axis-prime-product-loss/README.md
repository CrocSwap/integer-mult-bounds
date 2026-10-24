# Sharp product loss in the many-axis prime band

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: **scoped mathematical proof with finite corroboration**.
The many-axis prime band of [ToikY's #4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029)
implies the sharper full product bound

```text
T/S < (3d/(3d-1))^(d-1) < exp(1/3) < 349/250 < 3/2.
```

The last `3/2` is #4029's retained sufficient bound. The new constant
`exp(1/3)` is the least uniform upper bound implied by the band inequalities
alone. Sharpness here allows rational band points; no assertion of optimality
for prime selections is made. This neither changes the prime-supply cutoff
nor improves kappa.

## Exact domain and proof

Use the caller's actual axis count `D=d-1`, where integer `d>=2`. For each
axis, assume positive lengths satisfying the predecessor's half-open band

```text
1 - 1/(3d) < s_i/t_i <= 1 - 1/(4d),
S = product_i s_i,  T = product_i t_i,  i=1,...,D.
```

The conclusion is algebraic. It applies to the predecessor's prime lengths,
either of its two target scales, and every dimension for which those lengths
have been supplied. Prime abundance, distinctness, period guards, source
production and source admission are cited premises rather than new checks.
Neither a prime-number estimate nor the cutoff `ell>=2^32` enters this proof.

Each coordinate gives `t_i/s_i < 3d/(3d-1)`. Multiplying the `d-1` strict
inequalities proves the finite-d bound `T/S < A_d`, with

```text
A_d = (3d/(3d-1))^(d-1).
```

For `x>0`, integrating `1/(1+t)` on `[0,x]` gives

```text
x/(1+x) < log(1+x) < x.
```

Set `x=1/(3d-1)` and multiply by `d-1`. Then

```text
(d-1)/(3d) < log(A_d) < (d-1)/(3d-1) < 1/3.
```

Exponentiation proves the dimension-uniform bound. The exact rational
corollary follows from the positive Taylor series at `1/3`: sum terms
`j=0,...,10`, then bound the tail by its first term divided by `1-1/36`.
Every later ratio is at most `1/36`. The resulting rational upper bound is
strictly below `349/250`, as the checker verifies by integer arithmetic.

For fixed `d`, put every `s_i/t_i` arbitrarily close to the open lower
endpoint from above. This proves that `A_d` is the exact supremum under
the band assumptions. The displayed logarithmic squeeze also gives
`A_d -> exp(1/3)` as `d -> infinity`.

For completeness, one explicit admissible rational sequence realizes the
uniform sharpness without using the excluded endpoint:

```text
q_d = 1 - 1/(3d) + 1/(12d^2),
s_i/t_i = q_d for every one of the d-1 axes.
```

Its added term lies strictly between zero and the band width `1/(12d)`.
Writing `u_d=1-q_d`, integration gives
`u_d < -log(1-u_d) < u_d/(1-u_d)`. Consequently

```text
1/3 - 5/(12d) < (d-1)*(-log(q_d)) < log(A_d) < 1/3.
```

Thus `q_d^(-(d-1)) -> exp(1/3)`. Every smaller proposed uniform constant
fails for some rational band tuple. The targets `t_i` may remain powers of
two in this sharpness example, since multiplication by `q_d` supplies
rational `s_i`; integer or prime `s_i` are a stronger, unproved restriction.
The elementary logarithmic inequalities are standard. The contribution is
their exact application to this caller's product-loss envelope.

## Verification and reproduction

The universal quantifiers follow from the proof above. The standalone
standard-library checker corroborates the new envelope using complete small
rational boxes, rational logarithm intervals, endpoint approaches, an explicit
sharpness sequence and domain controls. It imports no predecessor executable
and replays no predecessor prime or source-admission certificate.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/many-axis-prime-product-loss/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/many-axis-prime-product-loss/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/many-axis-prime-product-loss
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/many-axis-prime-product-loss --check-source-history
```

Substitute another CPython 3.12 path as needed. The marker is
`PASS_MANY_AXIS_PRIME_PRODUCT_LOSS`. Stdout is a generated receipt bound to
the SHA256 of all five package files. Default replay is read-only and needs
no Git, network or external input files. Metadata validation separately
checks the historical provenance in [SOURCES.json](SOURCES.json).

Local CPython 3.12.15 on macOS arm64 passes both registered modes. The
checker enumerates 1,364 rational boxes, 511 finite-d logarithmic envelopes,
504 endpoint approaches and sixteen sharpness-limit probes. All nine invalid
input fixtures reject, and both stated boundary counterexamples pass.
Syntax/function-size inspection and development-mode warnings also pass.

The controls reject the open lower endpoint, out-of-band or nonpositive
lengths and an incorrect axis count. They accept the closed upper endpoint.
Using `D=d` is demonstrably unsafe: with `d=2`, the distinct prime lengths
107 and 109 both lie in the target-128 band, but
`128^2/(107*109) > 349/250 > exp(1/3)`.
The explicit sharpness sequence at `d=128` also exceeds `139/100`, rejecting
that smaller candidate constant. Runtime domain caps belong only to the
finite checker, not to the theorem.

## Limits

This is an elementary product estimate conditional on the displayed band.
It does not establish prime supply, improve its cutoff, execute an encoded
prime producer, lower physical costs or prove a complete multiplication
theorem. Native operations, source/target and period contracts, routing,
restoration, numerical recovery, stock, precision and tape costs remain
separate obligations. No selected cold replay, Lean or Docker was run.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

The structured versions are in [TASK.json](TASK.json).

1. Is the same supremum attained asymptotically by distinct primes within the
   retained two-scale domain? This would distinguish band-only sharpness from
   prime-restricted sharpness. Start with a narrowing band immediately above
   its lower endpoint and an explicit interval prime count; uniform abundance
   in that narrower band is not supplied here.
2. Can a fully charged prime-selection policy achieve a smaller product loss
   by selecting near the upper endpoint? Start with an actual caller's gap,
   period and queue contracts before narrowing its selection interval.
   Prime availability and the complete producer bill remain blockers.

## Provenance and credit

Base `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
The `uniform-transfer-audit` card is explicitly changed to this algebraic
side result in [TASK.json](TASK.json). The card's historical baseline command
raises `KeyError: 'bit_lower'` on the current selected certificate schema;
it is unchanged and is not evidence about this product estimate.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144301).

Credit ToikY #4029 for the band, actual `D=d-1` reading, source construction
and prior `3/2` bound; unpaidmoon #4142 for the encoded-guard scope; Jose
Manuel #3935 for the tensor interface; and Tekalign #4024 for the CRT source
premise. Cinna Davis, Chafik Boukhalfa, Josie Elliston, the retained source08
authors and Harvey and van der Hoeven retain prime-selector credit.
Fiori, Kadiri and Swidinsky supply the analytic theorem used by the predecessor,
which is not used or reproved by this algebraic consequence. Frozen sources
and predecessor credit lines are unchanged.

Overlap checks covered live open PRs, recent handoffs and active Discussions,
recent account work, main-tree README formulas and merged/all-state searches.
The sparse local notes and unpublished work are limits. The concurrent
prime-supply cutoff result in
[#5149](https://github.com/CrocSwap/integer-mult-bounds/pull/5149) concerns a
different quantity and is not extended. It lowers the sufficient prime-supply
cutoff and retains the old product bound; this result sharpens the product
bound without deriving a prime-supply cutoff. No numerical cross-check of
that contribution was run.

Power of Ten inspection covers the one new code file. It has no recursion,
subprocesses, writes or runtime code generation; functions are under 60 lines.
All finite loops are bounded by `d<=512`, four choices on at most five axes,
eight endpoint steps, sixteen limit probes or twelve series terms. File reads
are capped at 256 KiB. Explicit exceptions preserve checks under `-O`.
Rule 3 has a managed-runtime deviation: CPython allocates integers and
containers. These fixed domains bound live algorithmic collections; runtime
allocation internals are not instrumented. A fixed-storage native rewrite is
required before allocation-prohibited use. Warning-strict normal and optimized
replays are the local diagnostics; no static type checker is configured here.
