# Two-rate precision for the complete selected P104 word

The exact PR6030 word admits **15 native / 16 scalar guard bits**, instead of
uniform 16, under the retained completed-operation relative-error contract.
It also admits **14 native / 17 scalar bits**. These are the only Pareto
corners of the stated causal sufficient rule over all nonnegative integer
guards. No new kappa is claimed.

The first schedule saves 3453 guard bits across operation occurrences, from
363488 to 360035. The second allows four times the native defect of uniform 16
and needs one more scalar bit. It is cheaper when the per-native guard price
exceeds 19265/3453 times the per-scalar price. These are exact allocation
comparisons, not measured runtime or physical tariff savings.

Both schedules give final public Hilbert error below B, where B bounds each
initial field norm. At t extra bits in both classes, error is below B*2^-t.
Every intermediate ideal-plus-error field norm is below 1024B. All 22803 events,
770 public inputs, 29 owned fields, 3453 native sites and 19265 scalar sites are
included. COPY, INIT and owned reset are exact premises. [PROOF.md](PROOF.md)
gives the contract, causal induction and complete-domain proof.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/p104-two-rate-guards
```

Python 3.12 and the standard library suffice. Normal and optimized replay check
source bytes, all ideal endpoint rows, five finite frontier corners, two exact-
class exclusion corners, both complete signed error transposes, equality with
the unchanged uniform evaluator, 36 independent rational fixtures and nine
rejection controls. [CERTIFICATE.json](CERTIFICATE.json) gives the finite guard
boundary. [RESULT.json](RESULT.json) stores exact rational bounds and digests.
Default replay is read-only. `verify.py --write` regenerates the result.

The constructor's monotone search examined 57 pairs rather than all 1089 pairs
in 0..32. The independent certificate boundary checks do not trust that search.
The two exact-class corners extend the written classification beyond 32; the
finite implementation interface remains 0..32 plus an exact-class sentinel.

This is a new source-bound sufficient schedule, not a claim that the failed
corners are impossible under a more precise error model. The source's unitary
native/common-chart premise and exact COPY/reset contract remain required.
Physical child implementation, non-additive precision costs, layout, tape,
compiler, outer admission and the selected frontier remain unchanged. No
independent human review or formal proof-kernel acceptance is claimed.

## Open next questions

Bind one actual rounded child and scalar backend to either Pareto corner.
Measure or prove the complete precision price, including range, conversion,
source protection and cleanup. Use 14/17 only if its saved native work exceeds
its extra scalar work. The missing backend contract blocks a physical saving.
A new event word or a new local error law needs new source binding and bounds.

## Sources, family decision and credit

Canonical base 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
[Claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19363163).
Current main, handoffs, live open P104 precision PRs, full cached PR/Discussion
history and all in-scope main notes were checked before this task. The source
is the current selected word; no pending branch is a runtime dependency.
The work takes the later-word question in p104-gauge-error-covariance. Its
scope adds precision allocation to source-specific error recomputation.

The family decision is to stop at this complete two-class frontier and hand
it to a named backend. More class splits need a real cost model; a lower sum
of abstract guard bits alone does not justify a new implementation campaign.

Credit DreamingOfClouds/PR6030 and PR5907 for the selected word; Ali Romman's
PR5830, causal covariance and PR5819/5826/5831 methods; Adam Gall, ywz65,
Mason Hale, Pierre-Loic Doulcet and all retained P104/native/compiler authors.
The signed-row error method is retained. New mixed-rate construction, exact
frontier, integer evaluator and checks: Ali Romman with substantial OpenAI
Codex assistance; no subagents. Apache-2.0. Frozen source bytes stay unchanged.
