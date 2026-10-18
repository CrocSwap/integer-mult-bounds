# Uniform verification of the U8 owner supporting inequality

**Independent verification; no new kappa.** The rank-one supporting inequality
used in PR942's all-replica owner bound holds for every real `0 < b <= 1/3`,
with a uniform strict margin at all 42 other positive residual ranks below 48.
This extends the retained pointwise check and adds a quantitative penalty for
departing from the formal rank-1/rank-48 profile. See [PROOF.md](PROOF.md).

For the fixed whole-helper ledger, define

```
phi_b(r) = r*(73/r)^b,
c_b(r) = 48*phi_b(r)-r*phi_b(48),
v(r) = 48*u(r)+13*r.
```

For each attainable `r` other than 0, 1, and 48, the result is

```
c_b(r)/c_b(1) - v(r)/925 > 554/925      (0 < b <= 1/3).
```

The formal idle lower bound for every positive replica count T is
`(T/37)*(6*phi_b(1)+11086*phi_b(48))`. Equality in the integer relaxation
requires `37 | T`; this is not an owner-feasibility certificate. The proof also
bounds the number of other positive residuals in any near-equality profile.

## Reproduce

From the repository root, with Python 3.10+ and a writable temporary directory:

```sh
python -B research/u8-supporting-uniform/test_verify.py
```

Expected: **8 tests, OK**. This runs both standalone checks under `-O -S -B`,
checks the inherited literal model without executing it, and rejects nine
corrupted mathematical certificates plus a changed pinned source. Each
certificate control must fail for its expected reason, not an earlier error.
There are no third-party dependencies or network requests.

The two standalone commands are:

```sh
python -B research/u8-supporting-uniform/verify.py
python -B research/u8-supporting-uniform/independent_check.py
```

Expected output starts with `PASS_U8_SUPPORTING_UNIFORM` and
`PASS_U8_SUPPORTING_INDEPENDENT`, respectively. Regenerate to a **new** file:

```sh
python -B research/u8-supporting-uniform/verify.py --write /path/to/new-certificate.json
```

The output must equal [CERTIFICATE.json](CERTIFICATE.json) byte for byte.
Sources use exact committed-byte SHA-256 pins, so clone with
`git -c core.autocrlf=false clone ...` on Windows. The moving selected-result
pointer is recorded only as context at the base; it is not a runtime dependency.

## Evidence and independence

- `verify.py` multiplies a finite bivariate generating function to enumerate
  all 1,163 legal width-count vectors. It uses integer bisection to enclose
  `(48/r)^(1/3)` at denominator `10^12`.
- `independent_check.py` recursively enumerates the vectors and uses integer
  Newton iteration on the different radicand `48*r^2`. It validates the
  primary certificate as well as the independent proof integers.
- The capacity census is `8:6, 16:27, 32:215, 48:915`. All 45 attainable ranks
  are retained, including zero, rank one, rank 48, and negative-credit ranks.
  The primary minimum scaled margin is `292232800689300/526848237133 > 554`,
  at rank 44. The independent minimum proof integer is `1794386594565 > 0`,
  also at rank 44.
- The written proof shows the cost ratio decreases with b. Exact checks at
  `b=1/3` therefore cover the continuum; a finite exponent sample is not being
  called a proof. The certificate also records the exact failure
  `-22800/47` at rank 32, b=1, for an unjustified broader interval.

Neither implementation imports a retained search or moment engine or the
other implementation. They intentionally share the stated mathematical model
and source pins. Independent computational implementation does not imply
independent human peer review or proof-assistant formalization.

## Provenance, overlap, and scope

Exact base: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
Assignment seed **77** selects independent verification. [CLAIM.json](CLAIM.json)
records candidate tasks, selection, bounded domain, and local coordination.
[SOURCES.json](SOURCES.json) freezes the inherited sources and dependency heads.
At the base, the selected conditional result is PR942's
`kappa = 1661960547713947/10^18`; this contribution does not change it.

The prices and ledger are due to Chafik Boukhalfa's PR795/PR890. Jonathan
Capalbo's PR942 supplies the pointwise all-T supporting argument being extended.
Charles Bethin's PR850 proves a stronger **integer** optimum for the fixed
72-call (T=8) instance over the same exponent interval. The present fractional
all-T lower envelope does not supersede that result. Joel Pulikkan's concurrent
PR962 independently reconstructs the T37 owner composition; no code or owner
data from that pending PR is used here. Full credits and disclosure are in
[NOTICE.md](NOTICE.md).

This package changes only its research directory. It proves no new supplier,
owner assignment, cost recurrence, outer bound, kappa, runtime speedup, or
largest possible exponent interval. All-size/compiler, common-label and
mutable-source realization, whole-call hosting, precision/tape, analytic
transfer, and bit-interface obligations remain inherited. It does not replay
the native supplier or certify the full multiplication theorem.

The experiment has no stochastic search: seed 77 selects the object; the final
domain is every legal bin count vector at capacities 8/16/32/48 and every
attainable residual. Enumeration stops only after exhausting that finite
domain. The real exponent interval is discharged by the written argument.

See [VALIDATION.md](VALIDATION.md) for the executed checks and their limits.
