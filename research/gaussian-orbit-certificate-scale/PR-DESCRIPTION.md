# Classify Gaussian tensor symmetries and prove the optimal scale of orbit certificates with explicit rounding and materialization limits

## Why this matters

The preceding Gaussian orbit package constructs smaller ordinary Stein
generator representations, but leaves open how far the same global-symmetry
construction can go. A better cycle count alone also leaves its complete
cost unresolved. This package determines the optimal cycle-count scale over
**all exact permutation symmetries** of the stated homogeneous Gaussian
kernel, and proves that the specified dense boundary-vector format still
has almost quadratic size.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Exact published predecessor:
[`8f1a09fb4f696bd5f20e1953210936308571416e`](https://github.com/CubeJerry/integer-mult-bounds/commit/8f1a09fb4f696bd5f20e1953210936308571416e).
Its proof objects were independently fetched and hashed in DEPENDENCIES.json;
the earlier branch is unchanged. This is an independent scoped theorem and
audit, not another conditional coefficient optimization.

## Exact results

For `H_xy=q^(||x-y||²) v^(sum(x-y))` on `{0,...,n-1}^d`, `n>=2`,
`0<q<1`, `v>0`, every exact symmetry is a coordinate permutation when
v!=1, or a signed coordinate permutation when v=1. This begins with
arbitrary permutations of all `T=n^d` vertices. The inverse has the same
group.

Writing g(d) for the classical maximum order in S_d, the minimum cycle
count c* satisfies `T/g(d)<=c*<4T/g(d)` for v!=1, and
`T/(2g(d))<=c*<4T/g(d)` for v=1. Disjoint prime-power rotations give the
upper bound, with a uniform correction at most `(3/2)exp(8/9)<4`. The
4-cycle exception is treated exactly. Landau's classical asymptotic then
determines the optimal logarithmic saving in this certificate class.

The corresponding dense2c-vector boundary format has optimum size
`Theta(T²/g(d))=T^(2-o(1))` for fixed n. Its writes alone eventually
exceed direct dense axis application, even with optimistic scalar costs.
The package charges a uniform selector, orbit enumeration and both layout
permutations rather than treating the new order as free.

Explicit entry/product separation conditions extend symmetry containment
to perturbed tables. A common rounding rule retains the construction, and
factorwise error epsilon transfers as
`delta<=d epsilon(1+epsilon)^(d-1)`. A polynomial-parameter/linear-precision
corollary preserves the same certificate scale even for tiny shifts.
Arbitrary errors can destroy symmetries, so an error bound alone does not
preserve the upper construction; coarse rounding can add symmetries.

## Checks and reproduction

```
python -I -W error -B research/gaussian-orbit-certificate-scale/verify.py
python -I -O -W error -B research/gaussian-orbit-certificate-scale/verify.py
```

Both commands ran and produced byte-identical `status: PASS` JSON, retained
in RESULT.json. Coverage includes7337 partitions versus a separate
prime-power dynamic program;770 direct signed/unsigned orbit fixtures
versus Burnside;768 constructions;594 correction cases; thirteen complete
small exact/rounded automorphism searches; and ten failure controls.
The d5,n2 control explicitly shows that maximum order need not minimize
the finite cycle count: lengths2+3 give12 cycles, while a5-cycle gives8.
All six canonical provenance pins were checked against the exact base.
Finite tests corroborate PROOF.md; they do not establish its asymptotic
claims by extrapolation.

## Limitations, remaining obligations and kappa status

**No new kappa.** The selected full bound remains conditional and all five
foundational assumptions remain. The lower bound concerns full-cycle
certificates from one global exact symmetry and their stated dense format.
It is not a displacement-rank lower bound, an arbitrary-ordering result,
or an obstruction to implicit generators, compressed combinations or
different algorithms. Rounded inverse nonsingularity, conditioning and
stable production are separate obligations.

Actual source factors must be matched in n,q,v and satisfy a paid global
error bound. Physical gaps, periodic tails, phases, source access and the
complete all-axis/three-transform caller remain unadmitted. Open next
questions in README/TASK identify implicit application, actual-source
matching and representations outside the global-symmetry class.

## Credit and AI assistance

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
orchestrator proposed the all-symmetry/Landau objective and adjacency-gap
rounding extension; the worker independently derived and checked the
classification, correction constant, exact controls and cost boundaries.
The published orbit package and its originating displacement/rounding
research are credited predecessors. Landau's maximum-order theorem,
necklace/Burnside counting and cube symmetries are credited classical facts;
see Deléglise--Nicolas--Zimmermann,
[JTNB2008, DOI10.5802/jtnb.644](https://doi.org/10.5802/jtnb.644),
equations(2),(6). No global-priority claim is made for those ingredients.

## Independent review

Root proof review checked the all-vertex symmetry classification, prime-power correction, exact cost scope and rounding extension, and independently confirmed the cited Landau equations in the primary paper. A separate standard-library checker imports no worker code: it enumerates complete small vertex permutation groups, compares integer partitions with grouped knapsack, traverses literal word orbits and detects six false extensions. Normal and optimized receipts agree. REVIEW.md and INDEPENDENT-RESULT.json record this model-assisted review; no human or formal-kernel acceptance is claimed.

## Publication checks

All four canonical registered commands, six exact canonical provenance comparisons, two published predecessor proof pins, committed bytes/modes, whitespace and official export/input integrity passed. The full-history check is unavailable in this shallow checkout; no pass is claimed. PUBLICATION-CHECKS.json records the evidence. No hosted CI, human acceptance or formal-kernel proof is claimed.
