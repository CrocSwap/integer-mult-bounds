# Exact reconciliation of the archived J-versus-kappa rankings

**Research consolidation / independent arithmetic verification; no new kappa.**
Rohan Arun's archived campaign item 55 reports nine disagreements between the
first-order proxy `J` and the historical kappa calculation. This package checks
that claim from the retained integer histograms using new exact interval code.
It resolves the pair-count convention and supplies a concrete correction to one
numerical claim in the original report. The original sources are preserved.

## Result

| Census | Exact count |
|---|---:|
| Archived design records | 761 |
| Distinct integer histograms | 496 |
| All unordered design pairs | 289,180 |
| Identical-histogram pairs (exact ties) | 1,511 |
| Strictly ordered pairs | 287,669 |
| Proxy/root ordering agreements | 287,660 |
| Proxy/root ordering reversals | 9 |
| Distinct reversing histogram pairs | 8 |

Thus **287,669 is the complete non-tied pair count**, rather than all pairs of
761 records or a random sample of pairs. All 1,511 excluded pairs have identical
histograms, hence the same proxy, recurrence and nominal kappa. No unresolved
interval comparison is counted as a tie or discarded. The nine design-pair
reversals include two comparisons involving the same histogram: `u0039` and
`u0095` against `u0242`.

The report's additional claim that every reversal has `|Delta J| <= 0.9` is
false for `u0089` versus `u0302`. Independently bounded exact logarithms give

```
4627807923/5000000000 < J(u0302) - J(u0089) < 9255615847/10000000000
                 0.9255615846 < gap < 0.9255615847
```

Both endpoints exceed `9/10`. This is a concrete numerical counterexample to
that bound, not a failed search. It leaves the nine-reversal finding intact.
The report's broader observation that these are near ties remains reasonable.

| Pair | Smaller J | Larger nominal kappa |
|---|---|---|
| u0006 / u0241 | u0006 | u0241 |
| u0039 / u0242 | u0039 | u0242 |
| u0089 / u0302 | u0089 | u0302 |
| u0095 / u0242 | u0095 | u0242 |
| u0133 / u0580 | u0580 | u0133 |
| u0185 / u0370 | u0185 | u0370 |
| u0242 / u0427 | u0427 | u0242 |
| u0264 / u0492 | u0492 | u0264 |
| u0283 / u0540 | u0283 | u0540 |

## Reproduce

Python 3.9 or newer, standard library only; no network or solver is needed:

```sh
python3 -I -B research/historical-j-order-reconciliation/validate.py
```

Expected final marker:
`PASS_HISTORICAL_J_RECONCILIATION_AND_CONTROLS`.
The underlying census prints
`records=761 histograms=496 pairs=289180 ties=1511 agreements=287660 reversals=9 no_new_kappa`.
It recomputes and compares every field in [RESULT.json](RESULT.json), then runs
mathematical and corruption controls. Direct census command:
`python3 -I -B research/historical-j-order-reconciliation/verify.py`.
Use `--output /absolute/new-result.json` to generate a new result; existing
outputs are refused and failed checks do not replace them.

## Mathematical scope and reconstruction

Write the saved local histogram as `h_r`, with `1 <= r <= 20`, and
`mass = sum(r*h_r)`. The p=10 layout in the pinned PR315 `word_pins.py` has
`h=20`, `v=960`, `m=100`, 60 physical replicas and normalization by five.
The normalized paid profile used here is

```
H_r = 60 h_r + 23040 * 1_{r in {4, 19, 38, 42}},
D = 12 (4v - 5h(h-2)) = 24480,
W = (sum(r H_r) + D)/100 = 3 mass/5 + 23976.
```

Every record's `mass`, `N` and `Wn` is checked against these integers. In
particular, a hypothetical nonintegral stock is rejected rather than floored.
Following the pinned historical `moment.py`, the increasing moment is

```
M(a) = sum_r [r H_r / (100 W)] exp(a log(100/r))
       + [3200 sum_r H_r / (10^16 W)] exp(a log(100)).
```

This includes all four idle ranks and the historical bad-class fallback.
Each distinct histogram has a rational bracket `[a_lo,a_hi]` with strictly
certified `M(a_lo)<1<M(a_hi)`. Positive coefficients and `r<100` make `M`
strictly increasing, so its root lies uniquely between the endpoints.
Stored floating roots propose brackets only; incorrect proposals fail exact
moment signs. Stored floating `J`, original `kappa` and `kappa_fl` never decide
an ordering. The fresh `kappa_re` field is checked only for containment in the
independently obtained nominal-kappa interval.

For `J = sum_r r h_r log(100/r)`, unique prime factorization gives an integer
linear combination of logs of `2,3,5,7,11,13,17,19`. The new checker bounds
these logs with the positive atanh series after binary range reduction:

```
log(y) = 2 sum_{j=0}^{79} z^(2j+1)/(2j+1) + R, z=(y-1)/(y+1),
0 <= R <= 2 z^161 / (161 (1-z^2)), 1 <= y <= 2.
```

This differs from the historical alternating Mercator implementation. Bounds
are rounded outward to denominator `2^192`. Exponentials use directed integer
Taylor arithmetic through degree 18 and the positive tail bound
`t_18*x/19/(1-x/20)`, valid here for `0 <= x < 1/10`. Rounding occurs outward
at every step. All final comparisons use integers or rational numbers.

The historical arithmetic kappa map is also reconstructed from PR315
`math_check.py`: floor the root to the `10^-18` grid, check it is below the
retained complex cap, apply three ordinary-leaf steps starting at
`384599/10^10`, then the retained eta transformation and strict final grid.
Every root bracket is below the cap and below `1/1000`. On that range each
leaf update `x -> (1-c)c+cx` is increasing in its input and in `c` along the
nonnegative recurrence: its derivative in `c` is at least `1-2c>0`.
The outer rational transformation and grid floors are nondecreasing.
Applying them to both root endpoints therefore bounds the nominal kappa.
The intervals are disjoint for every distinct histogram pair, so grid floors
cannot change the reported pair ordering. These are ordering certificates;
we do not certify every last digit of each stored kappa.

## Sources, attribution and limits

Base commit: **91a2094f2e022930069e8cfdc810a3ea1b81cd09**. At this base the
selected conditional witness is #799 with #589/#555 at
`1661634653669567/10^18`; its certificate, actual X4 construction and maintainer
review were read. This historical dataset does not compete with that witness.

[SOURCES.json](SOURCES.json) pins the archived PR368 head
`fa8ab946df57ebadae1a470b637c2a590a0a5317`, its D-results Git blob, the exact two
retained archive members, the original report and notice, and PR315 head
`64bccfb67494f7c4549bfb2f186b400a3cfefb42`. All plain source snapshots match
GitHub's Git blob IDs. The histogram is stored as gzip for size; its
**decompressed original bytes** are the equality criterion, not a regenerated
gzip-container digest. Archive-member blob hashes describe the payloads, not
separate tracked Git objects. All historical Python files are reference data;
only a secondary test imports the old moment engine for three consistency
checks. The new census does not call it.

Credit **Rohan Arun and the original campaign contributors** for the data,
original nine-disagreement observation, evaluator and archive; **DreamingOfClouds**
for the p=10 package; and the earlier five-stage, bank, compiler and supplier
contributors named in the preserved notices, including **Henry Grant, Jacob
Sussman, eumemic and Evan McKinney**. The archive entered main through #477.
This work claims no discovery priority for proxy misordering. Adjacent archive
consolidations #743 and #907 and provenance work #867 concern different objects;
none is a mathematical dependency here.

Prepared for **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance** in the investigation, implementation, checks and writing.
Apache-2.0, with original notices and AI disclosures retained. No independent
human review or proof-assistant verification is claimed.

The domain is exactly the 761 retained histogram records, not all physical
words or all possible histogram perturbations. Identical histograms are exact
ties; overlapping intervals for any other pair would stop the checker. The
stopping rule is completion of every unordered pair, with no time-truncated
or randomly sampled arithmetic coverage. Assignment seed **96** and the three
candidate scopes are recorded in [CLAIM.json](CLAIM.json).

This replay does **not** regenerate the 761 designs, establish their physical
admissibility, rerun all 47 assembly constraints, verify the complex supplier,
or discharge inherited all-size/compiler, realization, hosting, precision/tape
and analytic hypotheses. It is neither a new supplier nor a formal proof of
the full multiplication theorem. The selected frontier and `upstream/` are
unchanged. [VALIDATION.md](VALIDATION.md) records executed checks and limits.
