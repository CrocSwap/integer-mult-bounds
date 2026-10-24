# Adaptive sign screening for the frozen PR4470 mixed moment

Scoped exploratory engineering evidence, prepared for SHIN09-git with substantial
OpenAI Codex assistance. Apache-2.0. No mathematical novelty, new supplier, new kappa,
full replay speedup, or independent human review is claimed.

## Result and scope

The old #1669 screening experiment uses a different, fixed-target pricing model.
The current selected #4470 construction has two variable moment sums. This
experiment screens their **signed difference**, with all ranks and counts from
the frozen published raw invoice:

    M(a) = sum_r (targets[r] - paid[r]) * r^(1-a).

The raw moment condition is M(a)>0. It is only one necessary arithmetic stage.
Completion, uniform compilation, the BIT supplier and outer inequalities still
require their own evidence. Testing a numerical value equal to selected kappa
as a raw rate does not perform that transfer or prove that kappa.

On this one invoice:

| Raw test | 2/3-degree bounds | 4/5-degree bounds | 6/7-degree bounds | Full source engine |
|---|---|---|---|---|
| 0 | accept | accept | accept | accept |
| .00300123, predecessor rate | accept | accept | accept | accept |
| .00302015, selected number used as a raw test only | inconclusive | accept | accept | accept |
| .003020155, actual raw admission test | inconclusive | accept | accept | accept |
| .0030201659770, published root lower endpoint | inconclusive | inconclusive | accept | accept |
| .0030201659771, published root upper endpoint | inconclusive | inconclusive | reject | reject |
| .0031, deliberately excessive control | reject | reject | reject | reject |

These are new, generic alternating-Taylor enclosures, not a run of #1669's
unchanged quadratic implementation. A failure of our 2/3-degree screen to decide
is not an impossibility theorem for every quadratic approximation.

`verify.py` checks seven cases against two other exponential implementations:
an independently written reciprocal positive-series enclosure and the unchanged
upstream engine. The first two new implementations share a logarithm enclosure;
the upstream engine has its own implementation. Eleven control groups cover
signed cancellation, strict equality, zero-rate mass, changed charges, an exact
power identity, fallback execution and accepted/rejected gate behavior. These
checks are scoped arithmetic evidence, not independent native replay.

## Why the bounds are certified

For r>=1, binary reduction gives log r = k log 2 + log(r/2^k). For 1<=x<=2,
z=(x-1)/(x+1) lies in [0,1/3], and

    log x = 2 sum_(j=0)^(N-1) z^(2j+1)/(2j+1) + R,
    0 <= R <= 2 z^(2N+1) / ((2N+1)(1-z^2)).

Use N=72 and round outward to 192 binary fractional bits. All calculations use
integers and rational numbers; floating values in RESULT.json are display only.

Taylor's integral remainder for exp(-x), x>=0, has the sign of its first omitted
term. Thus the degree-(2d+1) partial sum is a lower bound, and the degree-2d
partial sum an upper bound. Evaluate each polynomial with interval arithmetic
at x=a log r. Equal bases are cancelled exactly first. A negative signed
coefficient reverses its interval endpoints. Summing these contributions
encloses M(a). Strict positive lower bound accepts; strict negative upper bound
rejects; otherwise the answer is inconclusive.

The separate positive-series engine bounds exp(x) by its degree-24 positive
partial sum and a geometric majorant of the remaining tail, then takes the
reciprocal. The upstream engine independently uses 80 logarithm terms, outward
fixed-point exponential arithmetic and scaling/squaring. We reproduce both
signs of the already published root bracket; we do not claim a new root.

Freezing target credit at its a=0 value produces a false acceptance at a=.0031.
The actual mixed moment rejects there. This control applies to that incorrect
migration assumption, not to the original #1669 implementation.

## Two different uses

`adaptive_margin` tries degree pairs 2/3, 4/5, 6/7, then falls back to the full
source engine. Its output is a certified **sign**, not the source engine's
same narrow interval. It is appropriate only when the caller needs a sign.

`reject_gate_margin` also calls the full source engine after a positive screen.
It only avoids that work for certified rejections. This preserves the original
quantitative interval for accepted candidates that need it downstream. Equality
and unresolved intervals invoke the full fallback. It does not skip native,
ownership, completion, compiler, source-binding or outer validation.

## Measurements

`TIMINGS-FINAL.json` contains 252 fresh Python processes: 21 adjacent blocks per
case, three cases, four methods, rotating and reversing method order. Each
process includes startup, imports, input parsing, both source hash checks, cold
logarithm caches and the decision. OS file caches were not flushed. The first approximately 10 seconds overlapped
with a local verification run; other host contention was uncontrolled; timings are descriptive, never acceptance thresholds.

The baselines are the unchanged source moment calculation at exponent 1-a and
an exact algebraic factoring of the same engine as r*exp(-a log r). The latter
helps distinguish fewer terms from merely changing the exponential argument.

Median paired process-time changes relative to the unchanged source engine:

| Case | Sign-only adaptive | Rejection-only gate | Gate faster pairs |
|---|---|---|---|
| Actual raw admission test, accepts | 34.14% less | 11.01% more | 1/21 |
| Published root upper endpoint, rejects | 31.45% less | 32.12% less | 21/21 |
| Excessive .0031 control, rejects | 33.40% less | 35.41% less | 21/21 |

Relative to the factored full baseline, the rejection-only gate saves 29.97%
and 34.41% on the two rejecting cases, and costs 13.72% more on the accepting
case. Percentages are medians of paired ratios, not ratios of separate medians.
The three rates are fixtures, not an observed candidate population. No claim
about the complete PR, selected verification job, or multiplication runtime is
supported by these measurements.

## Reproduce

Tested on Python 3.12, standard library only; no Git, network, GPU or external dependency
is needed after downloading this directory. From this directory:

```sh
python -I -B verify.py
python -I -O -B verify.py
python -I -B benchmark.py --pairs 21 --output NEW-TIMINGS.json
```

`verify.py` compares the complete recomputed receipt to RESULT.json; `--write` is
an explicit authoring path. Benchmarking requires a
fresh output path. `VALIDATION.json` records local registered replay and source-only integrity
controls. The public verifier runs under optimized Python in a temporary export,
and mutations of the input, engine and expected receipt must reject. `SOURCES.json` and `NOTICE.md` retain provenance.

## Open next questions

The exploration's checked main was b91956876e5b4122fd89179f1b57557ff8378f15,
priority revision 7, selected kappa 60403/20000000. Publication was refreshed
against bee95ce88f9f19802f0613f92838895cd0e14a1f with unchanged source bytes.
The final overlap search covered 305 open PRs, 4,090 Discussion records and all
6,690 tracked top-level package README/TASK records, with complete reported
pagination/inventory. OVERLAP.json preserves the query and related matches.
Closed PRs were represented by local packages and the ledger, not a fresh full
closed-PR API census. This is not a proof of novelty or review of every code diff.

Related work includes #1669's frozen fixed-target surrogate; the local October
15 PR2260 timing study; `ceiling-integer-taylor`, which keeps an older engine's
exact intervals and changes its arithmetic implementation; and the current
PR4470 arithmetic/strictification audits. Our contribution is a local migration
probe and measurements, not a replacement for those results.

The next useful test is one **actual candidate batch or sign-only caller** with
this same complete raw-moment model. Measure rejected, accepted and inconclusive
candidates, retaining all necessary downstream checks. Do not integrate the
gate into accepted-certificate generation on the basis of the sign-only speedup.
Stop if complete caller runtime does not improve, if most candidates pass, or
if a caller requires interval values that the screen cannot supply.

Registered replay from the repository root:

```sh
python -B scripts/research_package.py --package research/mixed-moment-screen
```
