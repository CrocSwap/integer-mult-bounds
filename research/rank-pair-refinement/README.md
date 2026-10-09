# A parameter refinement above PR #63

The pinned PR #63 construction admits the conditional witness

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\boxed{\kappa=\frac{51027584062253}{10^{18}}
=0.000051027584062253.}
\]

This exceeds PR #63's `5102757/10^11` by exactly
`14062253/10^18`, or approximately **0.0000275581%** of its exponent saving.
It is a small parameter improvement. The physical construction is inherited
unchanged, and this is not a measured runtime improvement.

The comparison pins [PR #63](https://github.com/CrocSwap/integer-mult-bounds/pull/63)
at `aa7701b68540b7863d3b66a414e4319915d6282d`. The inherited original
OpenAI #109 framework, analytic and all-size compiler, fixed-alphabet tape,
routing, prime-selection, precision and recovery hypotheses remain assumed.
The newer construction lies outside the maintainer's PR #39 audit.

## Exact witness

| Quantity | Value |
| --- | --- |
| Bit saving `a` | `25515094004731/500000000000000000` |
| Positive backoff `h` | `1/10^18` |
| Complex saving | `717/10^7` |
| `beta` | `1/20` |
| Bit dimension `m` | `575` |
| Physical width `W` | `137151806` |
| Total rank | `78860441550` |
| Rank deficit | `1846900` |
| Maximum child width | `529` |

`certificate.json` records the complete paid child multiplicities, each moment
term, all 47 assembly inequalities and seven margins, the exact rational
parameter choices, source hashes, and eventual arithmetic thresholds.
`SOURCE.json` identifies the immutable construction inputs.

## Why the refinement works

For the complete child profile, let `n_t` be the multiplicity at width `t`.
The recursive characteristic moment is

\[
M(a)=\sum_t \frac{t n_t}{575W}\exp\!\left(a\log(575/t)\right).
\]

Every paid endpoint, data block, copied center, and auxiliary transition from
PR #63 remains in this sum. Its weighted rank is checked against `575W-1846900`.
The pinned arithmetic bounds each logarithm by the positive atanh series with
a geometric remainder. We tighten the exponential enclosure using

\[
P_8(x)=\sum_{j=0}^{8}\frac{x^j}{j!},\qquad
P_8(x)\leq e^x\leq P_8(x)+\frac{x^9}{9!(1-x/10)},\quad 0\leq x<1.
\]

The tail bound holds because ratios after the first omitted term are at most
`x/10`. Each weighted term is rounded outward onto the `10^-50` grid using
integer arithmetic. Exact rational summation proves `M(a)<1`; it also proves
`M(a+10^-18)>1`. Positivity of all `log(575/t)` makes the moment strictly
increasing. This brackets the fixed profile's root at the stated resolution;
it establishes no optimality over other constructions.

The inherited balanced assembly uses

\[
q=a(1-2h),\qquad \epsilon=\frac{1-h}{1+q},\qquad G=\epsilon q.
\]

The new choices preserve positive `h` and require `kappa<G`. The unchanged
assembly checker recomputes all its other parameters, verifies all 47 strict
inequalities and all seven margins, and rejects the next `10^-18` kappa grid
value with these fixed parameters. The limiting value as `h` tends to zero
is `a/(1+a)`; strictness is preserved by the positive rational backoff.

The moment upper slack exceeds `1.0653e-20`, and the controlling assembly
margin exceeds kappa by more than `6.3441e-19`. Smaller backoff increases
eventual size requirements: the sufficient common arithmetic cutoff here is
`log2(input size) >= 14000000000000000000`. Other inherited eventual
conditions still apply. This number has no practical speed interpretation.

## Reproduction and verification scope

From the repository root, using Python 3.11 or newer:

```sh
make rank-pair-refinement-verify
make rank-pair-verify
make verify
```

The first command checks the source hashes and independently regenerates the
new arithmetic certificate. The second reproduces the inherited compiler
words, dirty-basis replay and fixed-basis profiles. The third runs the
repository's full verification target, including the new refinement.
To regenerate the new certificate deliberately:

```sh
python3 research/rank-pair-refinement/refine.py --record
```

`independent-audit.json` records a separate arithmetic cross-check using a
different logarithm enclosure. `validation.json` records the actual local
reproduction outcome. Finite computation does not discharge the inherited
general mathematical hypotheses or constitute full formal verification.

## Attribution

Prepared with substantial OpenAI Codex assistance in response to Thomas
DiFiore's request. This increment consists of parameter selection, a tighter
elementary exponential enclosure, and reproducible exact arithmetic.

Dominik Scholz supplies PR #63's composition; Chafik Boukhalfa supplies PR #60's
rank-first reclamation; Avi Eisenberg supplies PR #62's interval strips and
pair assembly; eumemic supplies PR #57's frame compiler. Alejandro Zarzuelo
Urdiales's PR #61 provides the preceding parameter-refinement approach.
PR #63 already explicitly identifies finer grids and backoff as available
refinements. All inherited notices, community credits, original OpenAI and
Harvey–van der Hoeven attribution remain in force. Apache-2.0 applies subject
to the existing source-specific notices.
