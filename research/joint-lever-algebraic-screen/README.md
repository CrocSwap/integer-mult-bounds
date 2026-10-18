# Exact joint rank-cap and centre-charge screen at a=1/99

In the explicitly optimistic joint-lever model below, **rank cap14 is the
first cap that can pass the moment screen even with a free centre**. At cap16,
the largest passing integer centre charge is **8**: one rank8 centre child
passes, but nine rank units already fail. All3,315 rank/charge decisions are
certified using integer99th-root brackets, without logarithms, exponentials
or the predecessor moment implementation.

This sharpens the joint free-centre/rank16 planning example in
`complex-local-word-ceiling/levers.py`. It is an independent arithmetic
screen, **not** an attained decoder, packing or supplier improvement. The
selected bit endpoint also falls short of1/99, so no headline1% saving follows.

## Explicit favorable model

Retain width73,896/9 live families per call, one unpaid coordinate per family,
and idle rank cap51 from the source model. The selected local word has mass
5586, of which64 is its eight rank8 centre children. Replace all5522 units
of noncentral local mass by fractional children of rank at most r. Keep a
centre charge c, billed as c/8 rank8 children. The coverage law leaves exactly
1646 idle units, optimistically billed as1646/51 rank51 children.

At a=1/99 the favorable moment is

`[ (5522/r)(r/73)^(98/99) + (c/8)(8/73)^(98/99)`
`  + (1646/51)(51/73)^(98/99) ] / (896/9)`.

For fixed rank mass, cost per rank unit decreases with rank: it is proportional
to `r^(-1/99)`. Hence the rank-r fractional replacement lower-bounds every
noncentral histogram with that mass and cap r. The screen is necessary under
these hypotheses, not sufficient. The centre component is kept separate and
fully charged. Counts may be fractional; no indivisibility, chronology,
gathering, frame adaptation, dirty-state admission or implementation cost is
claimed free in an actual construction. Those costs are absent only in this
explicit optimistic relaxation.

The search covers r=1..51 (the retained halving guard excludes52), c=0..64.
At each r, cost increases strictly with c. The receipt records every largest
passing integer charge and the exact upper slack; when a next integer exists,
its positive lower excess is recorded too. It also reports the corresponding
whole rank8 call limit. Centre-free alone and rank16 reblocking alone both
fail at1/99, while their combination passes, independently corroborating the
source lever comparison.

## Exact method and reproduction

For each r, binary search finds the unique integer y satisfying

`y^99 * 73^98 <= r^98 * 2^(96*99) < (y+1)^99 * 73^98`.

Thus `(r/73)^(98/99)` lies in `[y/2^96,(y+1)/2^96]`. All weights are
nonnegative rational numbers, so summing endpoints is rigorous. Every tested
moment separates strictly from one. This method imports no predecessor
arithmetic engine. Exact endpoint-power comparisons check every enclosure.

```
python -B research/joint-lever-algebraic-screen/verify.py
python -B scripts/research_package.py --package research/joint-lever-algebraic-screen
```

Python3.12 standard library; source SHA256/Git pins and scope are recorded in
`SOURCES.json`/`TASK.json`. Controls reject both single-lever targets, missing
centre charges and reversed rank ordering. No selected cold replay, native
execution, Lean proof, new root bracket for an actual supplier or new kappa.

PR1605 treats partial integer reblocking of rank1 children at a different
target, with extra block overhead; PR1791 prices centre-sharing overhead on
actual selected profiles. This screen changes the whole noncentral profile,
retains an explicit rank8 centre tariff and uses the joint1/99 target.

## Open next questions

Can a legal decoder realize a rank14-or-larger noncentral profile while
retaining at most one rank8 centre call at cap16? Start with a complete small
dirty-state construction and charge its adaptations against this screen.
The blocker is a realizable interface and full cost, not another optimizer
seed or a tighter floating-point estimate.

## Credit

Douglas Colkitt and Claude supplied the packing model and ideal levers;
Sagar Thakrar's coverage identity and the Rohan Arun/Jeremy Kothe selected
supplier lineage remain credited. Arham Tahir's PR1605 and the separate
PR1791 overhead analysis are complementary. Prepared by woklerx with
substantial OpenAI Codex assistance; Apache-2.0.
