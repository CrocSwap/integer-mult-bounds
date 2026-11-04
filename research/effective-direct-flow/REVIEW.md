# Separate adversarial review of the effective direct-flow argument

**Disposition:** the reviewed written argument proves the stated explicit
upper majorant for the pinned historical scalar recurrence, conditional on
the stated classical Beurling--Selberg approximation theorem and the
authenticated predecessor flow identities. No unresolved mathematical
objection was found in this review. This is AI-assisted review, not human
peer review, a proof-kernel check, or physical supplier admission.

Reviewed files:

- `LOCAL_LIMIT.md`: SHA256
  `07702eabadefa4e2c435d6ea7e60c781aaa786fa875cab773a5962d8d2a2efe3`.
- `PROOF.md`: SHA256
  `e7dbe4e1705a307e9eb32f6f06b340fb2c49948cc749110d6be2c6fb3da94ea9`.

The reviewing worker did not write these two files or the numerical verifier.
It did contribute an earlier, coarser characteristic-function separation
estimate during discovery. Consequently the later review is not claimed to
be wholly independent of the discovery of that ingredient. The sharper
constants, interval smoothing, mixed-layer propagation and final induction
were reconstructed from the submitted drafts in a separate review pass.
The numerical source law and predecessor mathematical identities remain
shared dependencies.

## Local-limit checks

The review checked the following implications directly from the written
hypotheses, rather than treating a small numerical experiment as an all-size
argument:

1. The centered support and variance bounds give
   `|phi(t)| <= exp(-v*t^2/3)` for `|t|<=1/6`. The Taylor remainder constant
   is `5/6 + 9/48 = 49/48`; integrating the telescoping estimate gives
   `147/(16n)<10/n`.
2. Nearest-integer phases at `log 2` and `log 3`, followed by separation of
   the distinct integers `2^q` and `3^p`, give the stated lower bound for
   the larger phase residual. The coefficient
   `log(2)*log(3)/(2*pi)<1/8` permits angular cutoff `2*log(n)`.
   The two retained atom pairs give the required
   `exp(-sqrt(n)/320)` bound for the nth characteristic-function power.
3. With the explicitly stated angular Fourier convention, the Selberg
   spatial defect is `2*pi/T`. The signed minorant has the same sufficient
   absolute-integral bound as the majorant. Fourier inversion is legitimate
   because the bounded Fourier transforms have compact support.
4. Enlarging the majorized interval and contracting the minorized interval
   before taking their limit handles the actual atomic law, including
   either convention at a cap. No density of the discrete sum is assumed.
5. Both remainder expressions used in the symbolic onset decrease on the
   declared domain. The exact comparisons at `w=60`, and then
   `c_sigma*2/log(n)<15/10^12<10^-8`, support the stated all-size cutoff.
6. Layer-cake transfer is valid for the exponential half-line kernel.
   The complement kernel is decreasing since its inner function is convex
   with `x*Q_s'(x)>=Q_s(x)`. The derivative singularity at `x=1` does not
   invalidate continuity or monotone Stieltjes integration.

The exact finite verifier authenticates the source and establishes its atom,
centered-moment and other numerical hypotheses. It was executed successfully
in this review pass, as detailed below. The analytic review does not replace
those checks or claim a formal proof of the external Selberg theorem.

## Complete-flow and induction checks

The review independently reconstructed the tilted normalization. A mixed
base contributes
`A^(G-1)*q^h*exp(-alpha*B)*exp(alpha*u)`. Dividing by the proposed
`F_G` therefore yields the multiplier `(1-q)*q^h*c_sigma*sqrt(G)`.
The full leaf term has coefficient `J*P(s)/121^s`; its terminal paid letter
is unconditioned. In particular no terminal cutoff or missing factor of
the paid rank is used.

The source and boundary windows match the predecessor's strict cap tests.
Discarding root-source capacity is safe because it is nonnegative. The
signed-window error is bounded by the sum of absolute kernel heights, not
by cancellation. Stieltjes integration uses the same half-open windows as
the flow and remains valid at atoms.

All three ranges of mixed layers were checked separately. In the retained
range, conditioning on the target letters leaves a bounded shift and at
least `n_LLT` paid letters. The middle range uses the location-uniform
probability bound only. The last range, including zero paid letters, uses
the trivial supremum bound and geometric weights. The omitted infinite
geometric weight of the limiting integral is separately charged.

The arithmetic quantities reconstructed in this pass include

```text
Q = 52092027504,
3*10^-8*Q = 1562.76082512,
8*Q/((3/500)^2*10^18) = 0.011576006112.
```

The two finite Gaussian flattening bounds, the retained-layer index limits,
and the elementary exponential comparisons for both tails were checked.
The leaf half-line includes every interval after 5000, with no uncharged
truncation. Its error and all mixed errors fit the declared total 1600.

Finally the exact rank-one conservation surplus is 608. This makes the
linear function an all-rank upper solution of the complete recurrence,
so `L(n)<=n` follows before the improved induction starts. It supplies the
explicit initial-range constant `N0^(1-s)` without enumerating that range.
Uniformity in the actual level offset gives every integer `N>=N0`, not
just level starts. The strong induction includes zero complements via
`L(0)=0`.

## Diagnostic corroboration and limits

The following commands were executed successfully in the isolated worktree:

```text
python -I -W error -B research/effective-direct-flow/verify.py
python -I -W error -B research/effective-direct-flow/independent_checks.py
python -I -W error -B research/effective-direct-flow/diagnostic.py
```

The exact verifier returned `PASS_EFFECTIVE_DIRECT_FLOW`, including the
outward lower bound `47053.890913` for the 512-term full margin, all numerical
premises, symbolic uniform budgets and complete-flow controls. The separate
`Fraction` oracle checked 3969 interval pairs, 1764 valid divisions, 2205
zero-interval rejections and 630 signed ceilings. These controls exercise the
verifier's arithmetic implementation; they are not an independent proof of
the analytic theorem. The rounded 90-digit Decimal diagnostic, with literal
inventories and no repository numerical imports, gave the corroborating
512-term margin `47053.893158567844...`. It is not an acceptance gate.

A separate elementary floating calculation, importing no package engine,
evaluated 2999 positive-binomial terms at the midpoint of the predecessor
tilt bracket. It gave approximately

```text
K(s) = 266657973.81101257,
V(s) = 266610919.7758388,
K(s)-V(s) = 47054.035173773766.
```

This agrees with the claimed conservative margin `>40000` but is only a
diagnostic. The outward rational certificate, not these floats, establishes
the numerical acceptance decision.

One minor exposition issue was reported and resolved: the local-limit
statement now explicitly includes interval length zero, and proves the
singleton inequality by continuity from above for shrinking positive-length
intervals. The final amendment also explicitly defines centering at the mean
for the general-law formulation. Both changes were checked against the
argument; neither changes any quantitative bound. No unresolved issue from
this review remains.

The review does not establish a lower onset, a better recurrence exponent,
the physical correctness of the raw supplier, the selected P104 construction,
or any discharge of native, owned-erasure, compiler, precision/tape or
analytic-recovery assumptions. The complete finite source-flow identities
are retained predecessor mathematics, with the package's declared bounded
checks as corroboration.

Prepared for @alephnan with substantial OpenAI Codex assistance. Apache-2.0.
