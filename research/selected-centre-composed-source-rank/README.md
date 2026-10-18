# Exact composed scalar source rank for two selected centre calls

**Finite scalar-projection certificate; not a native centre-path obstruction,
new supplier, or improved κ.** The selected record and all frozen sources are
unchanged. This package computes the centre source maps of selected forward
calls **time 0 / time 1, stage 0, replicas 0 / 8**, composing the complete first
scalar call before the second. It does not assume that different physical owner
IDs imply independent values at later execution cuts.

## Result

The two calls each use 704 local owner roles. Their owner sets overlap on **30
hosted physical families**, giving **1,378** formal input coordinates jointly.
The exact projection retains all scalar operations but treats frame transports,
ordinary adapters and residual adapters as identity. Physical owners are one
scalar coordinate each: their native chart/address structure is not modeled.
This is a precisely defined projection, not an assertion of native equivalence.

`verify.py` propagates every ordinary input column through both complete scalar
programs, snapshots the eight source rows at each `centers` boundary, checks
all ordinary endpoints and private-centre clearing, then proves over Q:

| Quantity | Exact value |
|---|---:|
| Rank of stacked sixteen centre-source maps | 16 |
| Rank of their two 88-row scatter-output maps | 16 |
| Source rank restricted to the 224 initial source-data owners | 16 |
| Shared physical owners | 30 |
| Source maps of call 1 changed by completed call 0 | no |

The source-data-only nonsingular minor has columns
`0,1,2,3,4,5,6,12,7168,7169,7170,7171,7172,7173,7174,7180`.
Thus the computed independence does not rely on extra information in hosted
helper dirt. Each call's eight source support sizes are
`111,106,110,107,104,105,103,106`; these are actual propagated maps, not eight
coordinate selectors. `RESULT.json` records every rational coefficient.

An additional exact witness is obtained by solving this minor for source
values `(e0,-e0)`. All eight pairwise pooled source sums vanish, while the demanded
scatter output is nonzero. The verifier directly evaluates both assertions;
`pooled_sum_kernel_witness` records the nonzero initial data coordinates.
Explicitly, on owners `(0,1,2,3,4,5,6,12)` set
`(3,-1,2,-1,-1,-1,-1,-1)/4`, and on the corresponding owners plus 7168
set its negative; set every other owner to zero.

## Scoped information lemma

Let `x` be the initial scalar owner vector. Let `P x` and `Q x` be the two
recorded source maps, and `T x` the recorded scatter increments on the two
separate output panels. Consider a **linear boundary replacement** whose sole
source-dependent transcript to its output computations is `z=E x`, with `d`
scalar components. Fix the same initial target and host dirt in two runs.
If their output differences must equal `T x`, then `T=R E` for the decoder's
linear map `R`, so

```
d >= rank(T).
```

Conversely, at the purely linear-information level, a basis of the row space
of `T` is a sufficient transcript; this says nothing about its frame legality
or cost. For this explicit projected pair the verified rank is 16, ruling out
an **eight-scalar-total-only** transcript. This is not a lower bound on the
number of arbitrary native recursive calls.

Arbitrary initial target dirt cannot furnish missing source information because
it is fixed when taking differences. Restored host dirt cannot help unless the
replacement exposes additional source-dependent observations along the way;
such observations are additional transcript components and must be counted.
We do **not** infer a general cyclic/mixed transport inequality from this lemma.
A history-dependent native argument would need the complete boundary and
hosting-credit hypotheses of [PR1664](https://github.com/CrocSwap/integer-mult-bounds/pull/1664).

Equal source maps have stacked rank eight. Distinct source maps can also have
rank eight: the verifier reverses the order of the second eight maps and checks
this example. Consequently, map inequality alone is not the obstruction;
the joint demanded information is. A rank-eight transcript does not alone
license a physical shared path when centre maps/charts differ.

## Complete unchanged centre-phase invoice

For this pair the literal phases contain:

| Operation | Both calls |
|---|---:|
| Rank-8 transport children | 16 |
| Source COPY | 16 |
| Initial and final CLEAR | 32 |
| Scatter ADD | 352 |
| Total listed macros | 416 |
| Sum of recursive transport ranks | 128 |

The full scalar continuations, including helper restoration, are checked for
both calls. All 30 overlapping host variables are shared in the composition;
none is cloned for free. Every centre COPY, CLEAR and scatter ADD is charged.
Initial centre clears are counted from the emitted program; the verifier's
private rows start absent, so it does not independently certify arbitrary
native private-centre dirt. Ordinary helper/target dirt **is** fully symbolic.

This is an **unchanged baseline invoice**, not a new globally admitted cost.
There is no proposed routing, hosting or precision rewrite, hence no changed
moment or justified charge saving to submit to `ceiling.ceiling`. The scalar
transcript exclusion must not be restated as a native minimum of 128. Original
word hosting, precision and full supplier admission remain inherited, not
reverified here.

## Native limitation and useful handoff

The exact source cuts occur at different times. The interpreter intentionally
ignores `climb`, `adapter`, `residual_adapter` and centre frame operators while
keeping their scalar event order and centre transport invoice. It follows the
style of the inherited emitter's scalar algebra check, not a native frame
checker. In particular it is not established that identity-projected rank is
a lower bound for the true 512-address operator rank.

The missing implication is an injective lift of the displayed source-data
minor through the actual frame operators and owner charts, with the 30 shared
host families and complete first-call continuation. Without that lemma this
result remains a reproducible source-map handoff, not an obstruction to native
centre sharing. No arbitrary-pair census, retiming exclusion, all-size theorem,
Lean proof, or independent human proof review is claimed.

## Replay and controls

Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/selected-centre-composed-source-rank
python3.12 -I -O -B research/selected-centre-composed-source-rank/verify.py
```

Expected direct output:

```text
PASS_SELECTED_PAIR_SCALAR_SOURCE_RANK source_rank=16 scatter_rank=16 data_rank=16 shared_owners=30 rank_mass=128 controls=5
```

`verify.py --write` regenerates `RESULT.json`; ordinary replay recomputes and
compares every receipt field without writing. The five semantic controls check
equal maps, distinct dependent maps, pooled-sum loss of a nonzero output,
omission of a scatter ADD, and omission of the final centre clear. The latter
two must fail for the corresponding endpoint/private-state reason. All checks
use explicit exceptions and remain active under `-O`.

Observed final verification: CPython **3.12.12**, Darwin arm64. Receipt
generation, registered replay and isolated optimized smoke all passed in
**2.77 seconds combined**. The registered launcher reported
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. No full repository
suite, native frame replay or supplier cold replay was run.

The required starting example was executed before refinement:
`research/complex-local-word-ceiling/verify.py` reported
`PASS_COMPLEX_LOCAL_WORD_CEILING`, with `a_ceiling=0.00169005410908900006`.
`levers.py` reported the ideal shared-two relaxation `a_cap≈0.003213`, factor
`1.90`, `kappa_cap≈0.003203`. Those are favorable planning numbers only and are
not this package's result.

## Sources, overlap and attribution

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. `SOURCES.json` binds Git
provenance and live source bytes; `verify.py` additionally pins the selected
replay archive and its global-template, emitted-program and canonical-word
members. No pending PR code is imported. The selected 480-helper emitted word
is used, not the 492-helper historical evidence directories.

Closest predecessors, with exact heads in `TASK.json`:

- [PR1708](https://github.com/CrocSwap/integer-mult-bounds/pull/1708), Cinna Davis
  (`1337isnot1337`): forward shared-source fanout.
- [PR1748](https://github.com/CrocSwap/integer-mult-bounds/pull/1748), ToikY:
  shared reverse centre phase and precision guard.
- [PR1664](https://github.com/CrocSwap/integer-mult-bounds/pull/1664), Andrey Mas
  (`an664`): conditional dirty-host history-span inequality.
- [PR1684](https://github.com/CrocSwap/integer-mult-bounds/pull/1684): selected
  single-call scalar cut-rank application.
- [PR1829](https://github.com/CrocSwap/integer-mult-bounds/pull/1829): adjacent
  selected owner/chart identity census. This package adds propagated composed
  source maps and a collision witness for **one pair**, not a wider census.

The general linear rank lemma is standard and is not claimed as new. Credit
ctoth's [discussion1516](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516),
Rohan Arun's selected #1094 owner placement, Jeremy Kothe's retained word,
and the inherited compiler/emitter lineage (including icekylinx and
DreamingOfClouds). The precise new artifact is the selected paired scalar
computation on shared physical-owner variables.

Coordination: [discussion1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).
Overlap search used the complete cached 539-open-PR/524-discussion snapshot
from 2026-10-14 13:09–13:10Z, including bodies/comments, and targeted predecessor
head checks before publication. Arbitrary diffs and every closed submission
were not searched; this is not a novelty guarantee.

Prepared by Adam Gall with substantial OpenAI Codex assistance in mathematical
scoping, implementation, experiments and packaging. Apache-2.0.

## Open next questions

1. **Native lift:** propagate the sixteen displayed pivot columns through the
   actual 512-address native prefixes and first-call continuation. This matters
   because scalar projection rank alone is insufficient. The blocker is the
   missing operator/frame independence lemma.
2. **Priced additional information:** specify any proposed side-channel,
   noncoincident readout or cyclic hosting interface and its complete bill.
   First bind its endpoint/continuation to PR1664's hypotheses. No such changed
   interface is supplied here. Structured details are in `TASK.json`.
