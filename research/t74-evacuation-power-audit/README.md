# T74 evacuation: exact allocation audit and one power-sum crossover

PR2575's evacuation of PR2530's owner allocation passes an independent
literal allocation replay. It changes **694 role descriptors**, moves **547
whole helpers to other bins**, and changes **462 residual ranks**, out of
281,052 helper occurrences and 149,184 idle bins in each map.

The recursive rank bill has exactly one crossover in the full range
`0 < p < 1`. There is a unique `p_*` with

```
0.289994 < p_* < 0.289995.
```

PR2575 is strictly cheaper for `p_* < p < 1` and strictly dearer for
`0 < p < p_*`. Thus the evacuation improves this bill throughout the current
small-saving regime `p = 1-a`, but it is **not** a power-sum improvement for
every exponent. This is a finite allocation certificate and a scoped analytic
proof. It does not claim a new supplier, a new endpoint, a new κ, or an error in
PR2575's stated endpoint. PR2575 does not claim the all-exponent statement.

## Exact objects and independent coverage

The base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (priority revision 4).
The compared public sources are:

| Source | Exact head | Role |
| --- | --- | --- |
| [PR2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530) | `b4012098048e12500b2d33d2e84be281915a27ac` | Source-partner words, starting allocation, call order and plan |
| [PR2575](https://github.com/CrocSwap/integer-mult-bounds/pull/2575) | `921c229b4f030121a1d305de6259e174cd391955` | Evacuated allocation, emitted owners and retained parent schedule |

[Source index](SOURCE-INDEX.json) records the upstream path, Git blob, SHA256
and size of each unmodified retained file. No predecessor Python code is
imported or executed. The source README files and notice preserve attribution
and explain the original checking. The comparison is against these heads, even
if later records change. The selected result is unchanged. The claim is in
[discussion #2616](https://github.com/CrocSwap/integer-mult-bounds/discussions/2616).

The checker independently performs these operations:

1. Compare every JSON field of both complete BORROW-WORDs between the PRs,
   and compare the call order and provider dispatch. The provider widths are
   derived from the complete sets of vectors in the helper endpoint subspaces,
   in surviving-label order, rather than accepted from a width histogram.
2. Expand the retained parent's thirty per-replica source events in the actual
   666-call order. Reconstruct all 1,332 strict idle windows from last physical
   touches, including all 666 bridges. Compare the resulting windows, child
   sides, call widths and dispatch with PR2530's plan.
3. Replay both complete allocations with integer occupancy bitsets. Check every
   helper occurs once per call, all widths are whole, each physical family is
   distinct within a call and disjoint from that call's active data, all slices
   fit and are disjoint, and every occupied slice union is an initial prefix.
   Recount all 149,184 bins, including zeros, with exact rank conservation.
4. Reconstruct all eleven fields of every PR2575 emitted owner and compare with
   its retained `OWNERS.json.gz`. Compare the global profiles after adding the
   **common source-reported local profiles**. Their local frame invoice is
   inherited; identical words and dispatch make it cancel in the new result.
5. Form the signed histogram from the recounted bins, and check the analytic
   certificate and exact endpoint signs below. Compare the full generated
   receipt with [RESULT.json](RESULT.json), preserving JSON value types.

The original PR2575 `reconstruct.py`, `independent_core.py` and hosted audit
already check allocation constraints. Replaying those constraints here is
corroboration, not a newly discovered gap. The added result is the exact
comparison of the two concrete maps and the **unique crossover theorem**,
which distinguishes a favorable near-one exponent from arbitrary concave
power costs. PR2571's alternate fill, PR2588's changed local helper labels,
retired-lender exhaustion in PR2573, and private-buffer pooling are different
questions. This package does not optimize another owner map.

## Signed rank certificate

Let `H_old` and `H_new` be the positive-rank idle histograms. Their difference
`d_r = H_new[r] - H_old[r]` is:

| r | 1 | 3 | 5 | 7 | 8 | 14 | 16 | 23 | 32 | 48 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d_r | 114 | -1 | -18 | 170 | -114 | 1 | -172 | 1 | 74 | 1 |

All other differences vanish. The exact sums are `sum d_r = 56` and
`sum r*d_r = 0`. The zero-bin count falls from 93,329 to 93,273, so both maps
still have the same total bin count. Of the 547 helpers moved between bins,
76 have width 4, 118 width 7, and 353 width 9. The remaining 147 changed role
descriptors only change their offsets inside the same bin.

Write

\[
 F(p)=\sum_r d_r r^p.
\]

For a common positive normalization `W*73^p`, the new minus old recursive
rank cost is `F(p)/(W*73^p)`. Both complete local words and their invocation
counts are identical, so their rank costs cancel regardless of how those
common local costs are independently admitted. This comparison does not
assert that unexamined movement, precision or outer charges cancel.

## Proof of the unique crossover

Define the continuous piecewise-linear function

\[
 S(t)=\sum_r d_r\min(r,t).
\]

The checker recomputes its complete knot table:

| t | 0 | 1 | 3 | 5 | 7 | 8 | 14 | 16 | 23 | 32 | 48 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S(t) | 0 | 56 | -60 | -174 | -252 | -461 | -1031 | -1223 | -691 | -16 | 0 |

It is linear between knots and zero for `t >= 48`, by equality of rank mass.
Its unique interior sign change is at `q=57/29`, with `S(t)>0` for `0<t<q`
and `S(t)<0` for `q<t<48`. These statements follow from the table and linearity;
there is no sample-based inference about the intervals.

For `r>0` and `0<p<1`, splitting the integral at `r` gives

\[
 r^p=p(1-p)\int_0^\infty \min(r,t)t^{p-2}\,dt.
\]

Consequently, `F(p)` has the sign of

\[
 J(p)=\int_0^{48}S(t)(t/q)^{p-2}\,dt
     =q^{2-p}\frac{F(p)}{p(1-p)}.
\]

For `p>0` this integral and its derivative are well defined: near zero,
`S(t)=56t`, so `t^(p-1)` and `t^(p-1)*log(t)` are integrable. On each compact
subinterval of `p>0` they provide an integrable bound for differentiation.
Therefore

\[
 J'(p)=\int_0^{48}S(t)(t/q)^{p-2}\log(t/q)\,dt<0.
\]

Indeed, below `q` the first factor is positive and the logarithm negative;
above `q` these signs reverse. The integrand is strictly negative except at
isolated points. Thus `J` is continuous and strictly decreasing.

The rational enclosures in the receipt prove

```
8458/10^9 < F(0.289994) < 8459/10^9,
-230477/10^9 < F(0.289995) < -230476/10^9.
```

The intermediate value theorem supplies a zero between those endpoints;
strict decrease of `J` supplies uniqueness and the asserted signs on all of
`0<p<1`. Also `lim_{p->0+} F(p)=56` and `F(1)=0`. This explains why the
otherwise favorable evacuation is not an exponent-independent concentration
improvement. No transcendental root approximation is an acceptance condition.

### Exact enclosure method

[power.py](power.py) uses only integers and rational numbers. To enclose
`log(r)`, write `r=2^k*y`, `1<=y<2`, and apply
`log(y)=2*sum_{j>=0} z^(2j+1)/(2j+1)`, `z=(y-1)/(y+1)<=1/3`.
After 64 terms the omitted sum is at most
`2*z^129/(129*(1-z^2))`; the same series at `z=1/3` encloses `log(2)`.
Convert outward to the integer scale `2^160` and multiply by the exact rational
exponent. For `0<=x<=4`, the first 101 exponential terms are evaluated with
outward integer rounding. After term 100, the next term times
`102/(102-4)` bounds the entire tail. Signed summation reverses endpoints for
negative coefficients. The receipt retains the full integer bounds.

## Reproduction and controls

From the repository root, with standard-library CPython 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/t74-evacuation-power-audit
python3 -I -O -B research/t74-evacuation-power-audit/verify.py
```

Expected mathematical output:

```
PASS_T74_EVACUATION_POWER_AUDIT roles_per_map=281052 changed_bins=462 crossover=(0.289994,0.289995) controls=9
```

A direct replay takes about ten seconds on the checked environment. Normal
replay writes no files. To regenerate into a **new** path, use
`verify.py --write-receipt /path/to/new-receipt.json`; existing paths are refused.

Nine semantic controls reject: missing role, Boolean time, negative offset,
invalid physical window, duplicate physical family, overlapping slices at
different calls, an occupancy-prefix hole, reversed cost direction, and lost
rank mass. Reversing the fill row order preserves the result. Independent
integer square-root enclosures check the log/exp evaluator at exponent 1/2 for
every proof rank; exponent 1 checks exact integer values. Additional package
integrity controls are implemented in [check_integrity.py](check_integrity.py).

## Limits

This audit certifies the frozen whole-helper allocation model and its
recursive rank-cost comparison. It does not replay local dirty scalar maps,
Gaussian phases, full native lowering, physical Clifford charts or projectors,
parent/compiler realization, precision/tape/stock bounds, the bit supplier,
outer inequalities, or a complete multiplication theorem. Common words and
local profile bindings are checked; their correctness is inherited. A fixed
spectrum crossover does not bound every evacuation or prove either fill
optimal. There is no formal-kernel or independent human review.

## Open next questions

1. Does another legal evacuation give a nonpositive signed hinge function at
   every knot, hence a power-sum improvement for the entire range `0<p<1`?
   Start with one changed connected set of bins, preserve exact windows and
   whole helpers, and check its signed hinge table before running full admission.
   The blocker is a concrete legal replacement, not a more precise root.
2. Can a larger search retain several exact spectra instead of optimizing only
   one exponent? The crossover here shows that a fixed winner need not dominate
   the whole range. First compare one existing alternative fill on exactly the
   same words and order; source identity and independent allocation replay are
   prerequisites. This is a search-design question, not a prediction of a new κ.

The structured task, stopping rule and questions are in [TASK.json](TASK.json).
The final main/head refresh at 2026-10-15 16:29:41 UTC found no source or
guidance changes. [OVERLAP.json](OVERLAP.json) records the dated coverage and
limits of the overlap check.

## Credit and license

Jeremy Kothe (@jeremykothe2), with the assistance disclosed in PR2575, produced
the evacuated fill. Philippe Van Velzen (@philippeVV), PR2559, introduced the
evacuation method. @zxv, PR2530, supplied the source-partner lifetimes, eight
aliases, call order and starting allocation. Cinna Davis (@1337isnot1337),
PR2226, introduced anticipatory dirty borrowing. Tekalign (@tekuuu), PR2436,
Vlado Vojdanovski, PR2322, and the retained T74/native/controller lineage keep
credit for their constructions and source checks. The source notices are
retained. The integral identity and one-sign-change argument are elementary;
the new claim is their source-bound application to this pair of allocations.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) derived the proof, implemented and checked the verifier,
and wrote the package. No independent human review is claimed. Apache-2.0.
