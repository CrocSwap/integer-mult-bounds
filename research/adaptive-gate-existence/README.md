# Adaptive compiler gates at a moment crossing

A moment crossing plus strict pointwise mirror slack suffices for the adaptive
compiler in [zxv’s #4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483).
The tilted-mean gap follows from the mirror condition itself. The resulting
normalized rank-one leaf cost satisfies

```text
L(n) <= A n^t* (c + log n)^p
```

at the **exact crossing exponent** `t*`, with a funded ordinary base range.
This answers #4483’s broader-admission question for a sufficient class of
profiles. It does not assert gate existence for every favorable moment profile.
There is no new κ or selected-frontier change.

## The new implication

For finite integer target and paid histograms, let
`T(t)=sum W_k k^t` and `P(t)=sum P_r r^t`, with `2<=k<=m` and `1<=r<m`.
Assume the inherited native compiler contract, a crossing `T(t*)=P(t*)` at
`0<t*<1`, and the pointwise mirror inequalities

```text
E_J(t*) <= beta S_J(t*) for every elementary mirror cell J,
0 <= beta < t* m^(t*-1).
```

[PROOF.md](PROOF.md) establishes the following chain:

1. Integrating the signed mirror coefficients against `dz/z` gives the
   strictly positive tilted-mean gap. A second weighted integral gives
   positive rank-one surplus at the crossing.
2. Integer height parameters and rational tail parameters exist, with fixed
   strict guards on an interval immediately above the crossing.
3. The predecessor’s shifted-logarithmic argument works with equality at
   its lower endpoint: every actual local tangent exponent is larger than
   `t*`. Its base range and normalization are paid explicitly.

The proof credits #4483’s mean-separation heuristic, arbitrary-height flow,
Chernoff estimates and logarithmic majorant. The added result supplies their
missing sufficient existence criterion and the critical-endpoint argument.
This is a written mathematical proof with author-side AI review, not a formal
kernel proof or independent human verification.

At any fixed exponent with `T(t)>=P(t)`, the proof also gives an exact
criterion for the two tail gates and their ordering guard: they are feasible
if and only if some `lambda>0` satisfies
`T(t-lambda) exp(lambda mu_P(t)) < P(t)`. This reduces that parameter
existence question to one scalar inequality; mirror and native contracts
remain separate.

## Exact witness and obstruction

The abstract profile `W_16=1, W_256=4; P_1=59, P_81=1` has the exact crossing
`T(1/2)=P(1/2)=68`. It is a histogram fixture, not a claimed native word.
[WITNESS.json](WITNESS.json) uses

```text
a=b=1, M=4096, s=lambda=1/4,
p=12, c=24, ell0=128, n0=2^1544.
```

The new standard-library checker certifies every exponent in
`[1/2,33/64]`, including every elementary mirror cell:

| Guard | Exact certified bound (decimal display) |
| --- | --- |
| Mean-gap derivative | at least 4 |
| Mixed tail upper bound | below .622356 |
| Root tail upper bound | below .660349 |
| Mirror factor / source capacity | `1/80 < 1/32` |
| Funded recurrence lower bound | above 272.857919 |
| Required recurrence threshold | `155/3` |

The funded majorant is
`A n^(1/2)(24+log n)^12`, where
`A=2^772/(24+1544 log 2)^12`. The enormous cutoff is an explicit proof
fixture; no practical threshold claim follows.

The counterexample `W_4=4, W_64=17; P_1=4, P_16=1` at `t=1/2` passes
moment surplus, mean separation and mirror slack (`1/17 < 1/16`), yet no
positive choice of the two-tail geometry works. Jensen’s inequality and
one target term prove this for all parameters. Thus favorable tests at an
arbitrary exponent cannot replace the crossing hypothesis. This excludes
these simultaneous Chernoff gates, not all possible compilers.

## Application to retained native inventories

`root_application.py` checks the two frozen rank inventories used by #4483.
It authenticates the p7 receipt from #4433 and matches p16’s #4479 compact
consumer inventory to #4470’s native receipt. It executes no producer code.

| Profile | Unique crossing within this open bracket | Mean-gap lower bound | Mirror upper bound | Capacity lower bound |
| --- | --- | ---: | ---: | ---: |
| p7 | `(.997313, .997314)` | 1.723542 | .320851 | .984543 |
| p16 | `(.996979, .996980)` | 1.042284 | .562814 | .982101 |

These coarse outward bounds certify the **hypotheses at each actual root**.
They are not new root refinements or new κ values. The theorem therefore
supplies a critical-exponent polylog majorant for each inventory under its
inherited native contracts. The checker also certifies explicit constants at the actual roots,
using the predecessor’s authenticated geometry and logarithmic parameters:

| Profile | Ordinary base cutoff `n0` | `p` | `c` | Funding lower bound | Required upper bound |
| --- | --- | ---: | ---: | ---: | ---: |
| p7 | `121*256^100` | `1/10` | 38 | .028589 | .023329 |
| p16 | `145*1024^650` | `2/5` | 133 | .048546 | .042809 |

For each isolated root `theta`, set
`A=n0^(1-theta)/(c+log n0)^p`. Then the stated
`L(n)<=A n^theta(c+log n)^p` holds for every integer `n>=1`.
The uniform exponent covers are `.997483` and `.997067`; p7 uses a
conservative mirror factor `.322` for its wider interval. These are explicit
changes to the certification bounds. The native words and paid invoices
remain the source inputs.

For each bracket, exact opposite moment signs give existence. The tilted
means satisfy `mu'(t)=Var_t(log rank)>=0`, so
`mu_T(lo)-mu_P(hi)>0` certifies uniqueness on that bracket. On each mirror
cell, `E_J(hi)/S_J(lo)` bounds every ratio inside the bracket; all ranks
are at least one. The capacity `t m^(t-1)` increases for positive `t`.
The source inventories and their native correctness remain distinct claims.

## Reproduction and coverage

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/adaptive-gate-existence
python3.12 -I -O -B research/adaptive-gate-existence/verify.py
```

The verifier authenticates its declared predecessor inputs before checking
anything scientific. It uses exact rational root brackets, logarithm-series
tails and a positive exponential partial sum; no predecessor executable is
imported. It checks the two integral identities symbolically on square-rank
fixtures, half-open mirror endpoints, an uncovered source window, and nine
semantic rejection controls. Optimized Python retains all checks.
The separate application checker uses outward binary rational log/exp
intervals, 48 exact algebraic power controls and twelve additional semantic
rejections. Finite checks corroborate the proof and its witness; they do not extrapolate
an all-rank theorem from sampled ranks. `SOURCES.json` pins the canonical
base and all consumed evidence. `TASK.json` records scope, overlap and the
checkpoint. The old task card is retained as provenance; this explicitly
changed scope follows #4483’s concrete open question.

## Remaining obligations

The theorem concerns normalized leaf counts under #4483’s inherited native
contract. Arbitrary-input all-column correctness, distinct owners, literal
paid chronology, whole-job adapters, restoration, integer batch widths,
movement, precision, stock, fixed-tape costs, analytic transfer and exact
recovery remain required. No native or outer producer suite was rerun.
No numerical width bound or complete multiplication theorem is established.

## Open next questions

- Can a weaker bound against the actual capped measure replace strict
  pointwise mirror slack? First retain the mass on an offending window;
  a new distribution-dependent estimate is required.
- Can the polylogarithmic loss be reduced, or its constants made useful for
  a particular native profile? The p7/p16 critical-root constants are certified here; first compare
  geometry choices while keeping the base normalization and complete consumer bill.
- Can an actual small adaptive word supply complete physical and precision
  constants? Start from its chronological batches and owned native executor;
  the histogram proof does not supply that implementation.

Credit zxv (#4436/#4483), Jacob Alan Sussman’s integer compiler, Ryanson
Jonathan’s corrected #4459 mirror method, Cinna Davis and the retained native
and outer contributors. The p7/#4433 source and @1337isnot1337’s p7 controller lineage,
Cinna Davis’s #4470 p16 word and Dugongue’s #4479
compact consumer retain their attribution. Related #4507/#4519 batch-width work and #4521
expanded accounting have different scopes. Prepared by Dillon with substantial
OpenAI Codex assistance, including separate proof-development and adversarial
review agents. Apache-2.0.
