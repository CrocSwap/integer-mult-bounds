# A paid varying gauge on one complex helper

L276 can use a changing power-of-two scale instead of one constant scale across
the retained seven-slot k8 word. Eighteen inserted SCALE macros cost 28 primitives
per real component and save 200 in ADD coefficient work. The net saving is 172
per component, or **344 scalar primitives per complex invocation**, in each
orientation. The best constant gauge on this same helper saves only 74.

| Complete local scalar word | Before | After | Saved |
|---|---:|---:|---:|
| Forward | 149,002 | 148,658 | 344 |
| Backward | 149,018 | 148,674 | 344 |

Status: finite scalar construction and a scoped single-helper optimum. This
does not change the paid recursive profile, prove native/global admission, or
claim a new kappa or runtime improvement. The selected conditional kappa at the
base remains `836330098538459/500000000000000000`.

## Reproduce

From the repository root, with Python 3.11+ and the standard library:

```sh
python3 -I -O -B research/k8-varying-gauge-seed37/verify.py
```

Expected, after the complete replay and rejection controls:

```text
PASS_K8_VARYING_GAUGE_16_HELPERS_NO_NEW_KAPPA helper=276 saved=344/344 columns=712 orientations=2 controls=12
```

The command is offline, writes no files, and works from another directory using
the script's absolute path. `--json` prints the checked certificate. The
certificate carries every incident ADD's zero-based original event index and
chosen exponent; `search.transform` deterministically emits the complete word
from this schedule and the pinned original. Canonical JSON hashes cover both
complete emitted words. There is no dependence on gzip headers for new evidence.

## Fixed sources and completed domain

The exact investigation base is
`dd6403f774a0891093a006ae9716c02e371b1fdb`. The [claim](CLAIM.md) records
the three candidate tasks, fresh OS-random seed 37, overlap checks and stopping
rule. [SOURCES.json](SOURCES.json) pins all seven consumed/context files and
four archived members. The loader checks that the PR1042 `slots/local` provider
is byte-identical to the provider in the actual selected PR1094 replay archive,
and checks the receipt linking PR1094 to PR1042.

There are 237 eligible helpers with zero entrance, FULL exit, no residual wrapper,
no center role, and no COPY or CLEAR use. Seed 37 selects sorted entries [37:53]:
264, 265, 266, 267, 268, 269, 270, 271, 272, 274, 276, 278, 279, 280, 281, 283.
Both orientations were completed for all 16. Each candidate changes exactly one
helper. The winner is L276 in both orientations, with 121 incident ADDs. The
forward exponent domain after exact clamping is [-11, 2], and backward is [-2, 11].
The emitted winner actually uses only exponents -4 through 1 forward, and -1
through 4 backward. Its last exponent is zero.

We optimize over all integer exponent schedules on the selected single helper,
allowing changes before each incident ADD and a restoration at exit. Every
original SCALE remains literally present and is priced separately. The domain
does not merge original and inserted SCALEs, optimize multiple helpers together,
change the lowerer, or change any ADD's operands, order, or frame. This is a new
schedule class relative to constant gauges, not a larger numerical search of
the constant class. No global helper optimum is claimed.

## Why the complete map is preserved

At every point let the transformed helper value be `2^k` times its original
value, with all other registers unchanged. For an ADD with this helper as target,
multiply the coefficient by `2^k`; with this helper as source, multiply it by
`2^-k`. An inserted `2^(new_k-k)` SCALE updates this invariant. Original SCALEs
on the helper commute with its positive dyadic gauge. Start and finish at k=0,
so arbitrary initial helper dirt is restored exactly. The argument is linear
over complex inputs and applies separately to real and imaginary components.

All original nonscalar events remain byte-for-byte equal as JSON values, including
frame climbs, adapters, centers and recursive children. Each inserted SCALE has
the helper's current frame, checked by replaying that helper's original climb
chain. The helper has no residual wrapper or center operation. Commutation across
the unchanged homogeneous linear frame transfers uses the inherited realization
contract; this package does not newly discharge that contract or run its compiler.

## Exact optimum in the declared class

Write an incident coefficient as `q = sign(q) p 2^e`, with p a positive odd
integer. The retained PR696 lowerer costs

```text
c(q) = 1 + bit_length(p) + popcount(p) + |e| - [p=1 and e=0].
```

For the j-th incident ADD, let s_j be +1 for a helper target and -1 for a helper
source. Choosing k_j changes its coefficient cost by

```text
f_j(k_j) = c(q_j 2^(s_j k_j)) - c(q_j).
```

The complete incremental cost per real component is

```text
|k_1| + sum_j f_j(k_j) + sum_{j>1} |k_j-k_(j-1)| + |k_last|.
```

This includes entry, every intermediate change, exit, and every source access
and coefficient-work clear in the literal lowerer. Multiple gauge changes
between consecutive incident ADDs cannot beat their total absolute change.
Moving their net change immediately before the next ADD has the same scalar
effect because intervening original helper SCALEs commute. No hidden free
restoration is assumed.

Let I be the integer interval containing zero and every breakpoint `-s_j e_j`.
Clamping an exponent to I cannot increase its node cost: each node is an absolute
value plus a possible downward unit discount at its breakpoint. Clamping also
cannot increase any transition or boundary distance. Thus some optimum over
all integers lies in I. This proves the finite reduction; testing a large
interval alone would not prove it.

The optimizer solves the finite chain by exact integer dynamic programming,
with transitions `D_j(k) = f_j(k) + min_l(D_(j-1)(l) + |k-l|)` and final cost
`min_k(D_last(k)+|k|)`. It breaks equal-cost ties by fewer inserted SCALE macros,
then smaller total exponent magnitude and lexicographic path order. Optimality
concerns the stated primitive cost, not these presentation tie-breakers.

The independent cost check does not call the optimizer's price function or
transition routine. It obtains costs from literal PR696 instruction lists and
computes each distance transform with left-to-right and right-to-left sweeps.
It agrees on all 32 helper/orientation minima. A separate exhaustive example
checks all 3,125 schedules on a five-node, five-state chain with both operand
signs and the unit discount. This finite control supports the implementation;
the written argument above supplies the all-integer scope.

## Whole-word accounting and checks

Each complex invocation includes two real-component words. Both baselines and
both candidates replay exactly on all 712 independent formal input columns:
224 data coordinates, 480 dirty helpers and eight dirty private centers.
The centers end at zero; the helper coordinates return to their input values.
Forward performs the retained source-to-target update, and backward its retained
negative transpose update. The verifier also checks all 326 distinct ADD and 23
SCALE coefficients in these four words against the literal lowerer's exact local
map. An ADD checks all three inputs, including arbitrary initial coefficient work.

The literal primitive sweep prices every scalar instruction and tracks all
intermediate positive coefficient envelopes, including coefficient work before
division. Baseline and candidate have identical prefix bounds, 52 bits forward
and 68 backward, below the inherited 192-bit local magnitude allowance. A separate
conservative dyadic coefficient-grid calculation remains at depths 22 and 26.
These are local exact-arithmetic bounds, not a new physical precision theorem.

The paid profile per orientation is unchanged:

```text
rank 1: 2412; rank 2: 418; rank 3: 432;
rank 4: 142; rank 5: 82; rank 8: 8.
```

Consequently the recursive moment has no improvement from this package. All
helper inventory, copied information, adapters, frame changes, cleanup and
children stay in the complete word. The expected primitive saving of 344 is
the verified net price, not the optimistic coefficient-work saving of 400.

Twelve controls reject omitted first scales, unconjugated first ADDs, wrong
scale frames and incomplete schedules in each orientation, an unpaid coefficient
work clear, a missing source pin and a changed source pin. A separate constant
gauge whose final exponent is nonzero passes only with its paid exit SCALE;
omitting that restoration is the twelfth rejection. Default verification also
compares every proof-relevant certificate field with fresh computation.

Validation on macOS arm64, 2026-10-13, passed with CPython 3.14.8 in normal and
optimized mode and CPython 3.11.17 in optimized mode. The selected-record source
integrity command and all 25 existing `test_selected*.py` tests pass. An external
saved-certificate corruption produced exit 1 with `saved certificate mismatch`;
after restoration its SHA256 is
`3c5acedd505941f600124663c1bf53ddd4799573684b9da311e25a8c14780395`.
The default optimized command also passes from `/tmp` via its absolute path.

## Predecessors and scope

- @woklerx's [PR1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161),
  `d210969d3158a1e6c505e41f67dd84e555c88564`, gives constant single-helper
  gauges and the unit-discount cost formulation. This package extends the
  schedule class; it does not claim priority for helper rescaling.
- Hanson Sun / bbMisk's [PR1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214),
  `26162c56ec9c50a80e49949f36d4dd9a137a76a6`, gives a larger 576-primitive
  saving with two constant helper gauges. It explicitly excludes phase-varying
  gauges. This result is not a new best scalar bill across those different classes.
- @woklerx's [PR1170](https://github.com/CrocSwap/integer-mult-bounds/pull/1170),
  `df273e3cb1e62c1bfdf6599160b538e7a4b879d7`, consolidates original stage
  SCALEs. We retain them and make no combined-saving claim.
- Philipp / mightyOil's concurrent [claim in discussion 1258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1258)
  explores at least three simultaneous constant gauges using coordinate descent.
  Its claimed domain is distinct from this single-helper time-varying schedule.
  No result from that ongoing investigation is assumed or incorporated.
- The literal lowerer is Sagar Thakrar's retained PR696 contribution. The
  source vocabulary and supplier follow icekylinx's PR425/433/531 lineage,
  Jeremy Kothe's PR622 and mutable-leaver construction, Rohan Arun's slots and
  PR1094 placement, Hao Yan's T16 controller, and Douglas Colkitt's source-bound
  maintainer review. Their full attribution remains in the pinned source review.

Prepared by Sagar Thakrar / thakrarsagar with substantial OpenAI Codex assistance.
New work is Apache-2.0. No independent human review is claimed. No upstream,
selected-frontier, existing source or frozen evidence file is modified.

The pre-submission scan covered 853 open PR bodies through PR1257 and all eleven
current discussions. Main advanced to `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`
with historical reconciliation work; none of this package's seven pinned inputs
or the selected record changed. The original investigation base is preserved.

Full native/hosted admission, Linux execution, a whole-repository cold replay,
all-size compiler correctness, common-label and mutable-source realization,
whole-call hosting, global precision/tape, exact recovery, analytic transfer,
and bit H1-H5 obligations are not discharged here. This is not a formal proof
of the multiplication theorem.

## Open next questions

The smallest useful follow-up is to feed the emitted L276 word into the unchanged
native frame and hosted-supplier admission chain, preserving all 18 inserted
SCALEs and checking its exact invoice. That would determine whether this finite
scalar schedule can replace a production provider. The required integration is
the blocker; a scalar endpoint replay does not supply it.

Joint helper gauges or merging with original stage SCALEs define different cost
classes. They may help scalar constants, but their interactions need a fresh
complete invoice. The unchanged paid profile gives no evidence that either
would move kappa, much less reach 0.01.
