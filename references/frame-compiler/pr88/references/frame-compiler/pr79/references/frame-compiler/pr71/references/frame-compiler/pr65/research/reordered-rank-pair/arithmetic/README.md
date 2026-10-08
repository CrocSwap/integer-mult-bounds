# Exact arithmetic for the reordered rank-pair witness

The selected complete paid profile admits

- bit saving `a = 5103158916233/100000000000000000`;
- backoff `h = 1/1000000000000`, unchanged from PR63;
- `kappa = 2041159402879/40000000000000000 = 0.000051028985071975`.

All 47 strict assembly inequalities and all seven margins pass. The next bit
saving on the 1e-18 grid has moment strictly above one; the next kappa on that
grid fails the unchanged balanced assembly. The finite sufficient arithmetic
cutoff remains `log2(input) >= 14000000000000`. This is an eventual arithmetic
threshold, not a practical runtime claim or the complete all-size threshold.

The exact gain above PR63's `5102757/10^11` is
`56602879/40000000000000000`, approximately 0.0027731518 percent relative.
The construction gain is separated from parameter precision:

| Check | Bit saving | Kappa | Gain versus PR63 |
|---|---:|---:|---:|
| Same 1e-11 grid and same h as PR63 | 0.00005103158 | 0.00005102897 | 0.0000000014 |
| Refined 1e-18 grid; same h | 0.000051031589162330 | 0.000051028985071975 | 0.000000001415071975 |

The first row passes even with PR63's original low-order exponential bounds,
and its next bit grid point fails with those bounds. Thus its 1.4e-9 gain does
not depend on tightening the numerical enclosure. Precision adds a further
`602879/40000000000000000 = 1.5071975e-11`.

## Reproduction and source linkage

Run from any checkout location using Python 3.11 or later:

```sh
python3 -B research/reordered-rank-pair/arithmetic/refine.py
python3 -B research/reordered-rank-pair/arithmetic/audit.py
python3 -B -m unittest discover -s research/reordered-rank-pair/arithmetic -p test_arithmetic.py -v
```

The default commands recompute and compare without writing outputs. An
intentional certificate update uses `--record` on the first two commands.
`refine.py` accepts `--profile PATH` and `--certificate PATH`; `audit.py`
accepts `--certificate PATH` and `--receipt PATH`.

`certificate.json` pins `../paired-candidate.json`, both arithmetic scripts,
the inherited logarithm implementation and the inherited balanced assembly
by SHA256. All paths are repository relative. It includes the complete exact
per-child logarithm and exponential intervals, weighted moment bounds,
assembly slacks, all seven margins, next-grid failures, comparisons and
sufficient arithmetic cutoffs. `audit-receipt.json` records an independently
computed enclosure and ten deliberate assembly failures.

This package checks the supplied complete paid profile. The parent
`../verify.py` checks the words, physical replay, actual profile/CRT results,
paid profile assembly and its correspondence to `../paired-candidate.json`.
An arithmetic pass alone does not prove that physical linkage.

## Rational logarithm enclosure

For `y >= 1`, put `z = (y-1)/(y+1)`. With `0 <= z < 1`,

`log(y) = 2 * sum(j>=0, z^(2j+1)/(2j+1))`.

Every term is nonnegative. Truncation after indices `0,...,J-1` is therefore a
lower bound. For the tail, `2j+1 >= 2J+1` and the powers form a geometric series,
so the upper remainder is

`2*z^(2J+1)/((2J+1)*(1-z^2))`.

The inherited helper reduces by powers of 2 to `1 <= y <= 2`, uses `J=32`,
adds the corresponding multiple of `log(2)`, then rounds downward/upward to
the 1e-30 rational grid. These operations preserve the enclosure.

The independent audit instead reduces by powers of 3/2 to
`1 <= y <= 3/2`, uses `J=60`, and adds the corresponding multiple of
`log(3/2)`. Its exact logarithm enclosure is checked to lie inside the recorded
inherited interval for every child. The two implementations share the
mathematical atanh-series identity but use different range reduction, term
counts and evaluation code; neither relies on machine floating-point logs.

## Rational exponential and complete moment enclosure

For a child of dimension `t`, multiplicity `n`, arity `m` and width `W`, the
weight is `w=t*n/(m*W) > 0`. With bit saving `a>0`, its contribution to the
characteristic moment is `w*exp(a*log(m/t))`. The complete histogram includes
all paid parts; neither rare children nor physical transitions are omitted.

Write `u=a*log_lower` and `v=a*log_upper`. The checker verifies
`0 <= u <= v < 1`. For `S_d(x)=sum(j=0..d, x^j/j!)`, positivity gives

`S_d(u) <= exp(a*log(m/t))`.

At `v`, the first omitted term is `v^(d+1)/(d+1)!`; each later term divided by
its predecessor is at most `v/(d+2) < 1`. A geometric majorant therefore gives

`exp(a*log(m/t)) <= S_d(v) + v^(d+1)/((d+1)!*(1-v/(d+2)))`.

The primary checker uses `d=8`. It rounds the lower expression downward and
the upper expression upward to the 1e-40 rational grid, multiplies by each
positive exact weight, and sums. Directed rounding can only widen the
interval. Every arithmetic operation uses integers and exact Fractions.

The independent audit evaluates the exponential by a recurrence through
degree 12. It checks `v<1/1000`, rounds input bounds outward, and bounds the
remaining tail by twice the first omitted term. This is valid because all
successive tail ratios are below 1/2. It independently confirms that the
accepted upper moment is below one and the successor lower moment is above
one. No empirical epsilon, decimal-log assumption or float tolerance enters
the acceptance decision.

All weights and `log(m/t)` are strictly positive, since `0<t<m`. The true
moment is therefore strictly increasing in `a`. Binary search on the rational
grid is valid, and the adjacent accepted/rejected bounds bracket its unique
threshold in the searched interval. Inconclusive interval overlap raises an
error; it is never silently classified as success or failure.

## Balanced assembly and scoped limits

The inherited parameterization sets

`q=a*(1-2h)`, `epsilon=(1-h)/(1+q)`, and `G=epsilon*q`.

The inherited checker recomputes the semantic/product-stock bridge, all 47
strict slacks and all seven margins, and confirms `G` is the controlling
margin. The selected kappa is the greatest 1e-18 grid point strictly below
`G`. The next grid point must fail; equality does not satisfy a strict
inequality. Beta remains 1/20, complex saving remains 717/10^7, semantic C1
remains one, and row-stock degree remains 2000.

For any allowed positive backoff, `G<a/(1+a)`. The rejected bit successor
therefore gives a strict upper bound `a_next/(1+a_next)` for kappa in this
same complete-profile balanced family. The remaining possible gain above
this witness from parameter changes alone is less than 1.544284e-16. This
scoped statement says nothing about other profiles, graph families or
assembly parameterizations. Shrinking the backoff further would increase
some sufficient eventual cutoffs; this witness retains PR63's backoff.

## Failure controls and tests

For both the preferred fine-grid witness and its coarse-grid comparison,
the audit rejects the next kappa grid point, zero backoff, original prefix,
old guard and old exposure formulas. These are fixed-parameter controls;
they do not optimize or disprove alternative parameter families.

The eight tests reproduce the complete certificate and independent receipt,
reject the next bit grid point, reject a forged accepted saving, reject a
forged profile hash, reject omission of an assembly constraint, reject a
float saving, and ensure optimized Python cannot disable assertions.
Physical failure controls belong to the parent verifier.

## Attribution and limits

The physical construction retains Avi Eisenberg's PR62 interval-strip and
core-aware pair graph, Chafik Boukhalfa's PR60 rank-first reclamation and
eumemic's PR57 compiler, as composed and checked in Dominik Scholz's PR63.
The source graph order changes are described in the parent proof. The
inherited arithmetic and assembly retain their source notices and credit,
including James Chang's PR34, Zhihao Chen, RaD/hipotures and all predecessor
contributors. This package was prepared with substantial OpenAI assistance.

Alejandro Zarzuelo Urdiales's
[PR61 parameter refinement](https://github.com/CrocSwap/integer-mult-bounds/pull/61),
at reviewed head `afb7cb67d1858641315cfbf4ac768ee64a8eff3a`, provides the
precedent for refining rational grids/backoff on a fixed physical witness.
No PR61 source code is copied here. The table above explicitly separates that
parameter-only refinement from the gain due to changed physical profiles.

The logarithm/exponential series arguments here are informal mathematical
proofs checked through exact rational computations; they are not Lean or
other proof-assistant formalizations. The base theorem, all-size compiler
and frame transfer, fixed alphabet/tape representation, scalar/envelope
interpretation, routing, prime selection, recovery and remaining eventual
thresholds remain inherited obligations. No global optimum, complete formal
integer-multiplication theorem, or measured practical speedup is claimed.
All inherited licenses and notices remain applicable.
