# Faster complete idle-helper pair replay

This package was produced by Nick Petalas. Apache-2.0.

The complete finite replay from [unpaidmoon's PR6338](https://github.com/CrocSwap/integer-mult-bounds/pull/6338)
takes **70.96% less median wall time** with the evaluation adapter here. Five
alternating runs per side on CPython 3.12.15, macOS 27.0.1 arm64, measured:

| Complete command | Median seconds | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| Baseline | 4.451050 | 4.325744 | 4.648085 |
| Adapter | 1.292454 | 1.286811 | 1.498913 |

All ten commands succeeded with identical complete stdout. Both modes include
interpreter startup, source authentication and the entire predecessor `main`.
The benchmark uses one subprocess at a time and the same interpreter options.
The machine has 18 logical CPUs; measured load averages were approximately
2.12, 2.03 and 2.00. Other concurrent work was not controlled. This is one
machine's wall-time measurement, not a universal speed guarantee.

The contribution is a scoped exact evaluation-equivalence argument, exhaustive
finite conformance and a measured runtime improvement. The predecessor's
idle-helper theorem remains a cited result. This package neither audits nor
extends it, supplies a physical implementation, or changes kappa.

## Exact change and coverage

The old pair loop repeatedly forms `(I+aL)(I+bR)-I`. Distributivity over the
integers gives exactly `aL+bR+abLR`. For each ordered pair the adapter forms
`LR` once and evaluates this expression at the same sixteen scalar pairs.
There are 14,400 ordered pairs, so full matrix products fall from 230,400 to
14,400. This removes exactly 216,000 matrix products. Every sampled matrix is
still evaluated.

The adapter precomputes the row-major indices of every 3-by-3 minor, then uses
the same six-term determinant polynomial without constructing a temporary
3-by-3 matrix. Each index list follows the source's row-combination and
column-combination order. A Boolean-vertex check of all 512 assignments proves
equality of the two multilinear determinant polynomials over the integers.

`replay.py` authenticates the frozen verifier's SHA256 before compiling its
source bytes directly. It replaces only `check_pair_rank` in that private
namespace, then calls the original `main`. No predecessor file is edited.
The adapter's supported domain is at most 120 square projectors of width 3
or 4; the actual complete source uses its 120 width-four projectors.

The separate conformance run compares:

- the full stdout of both complete source commands;
- the count of every original guard message, including **3,686,400** minor checks;
- the ordered SHA256 transcript of all **230,400** complete product matrices,
  including each of their sixteen integer entries;
- all 512 determinant-polynomial vertices and six rejection controls.

The matching matrix transcript is
`b64f711c3e8dad7f71702676fe48c1aa47b5ea8ac9b8b4ffb46f3136e99fdaa7`.
Transcript equality uses SHA256's usual collision-resistance assumption. The
distributive identity and explicit minor-index correspondence are the written
equivalence argument. The transcript is corroboration, not a replacement proof.
The source's diagonal-line grid, clean-helper direct words, short-register
control, block-projector control and pigeonhole checks still execute unchanged.

Both implementations reject an injected rank-three matrix with the original
reason. Empty, wrong-width and malformed-square adapter inputs reject. A
disposable source export with changed dependency bytes rejects before
executing the source. Explicit exceptions keep these checks active under `-O`.

An untimed cProfile run identified the pair loop as 10.981 of 11.015 cumulative
seconds. Temporary minor construction accounted for 4.195 cumulative seconds;
matrix multiplication for 2.447 and scaled-update construction for 1.355.
These overlapping profile times explain the optimization; they are not the
reported unprofiled wall-time measurements.

## Reproduction

From the repository root, use CPython 3.12 and the standard library. The local
interpreter used for the measurements was
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`.
Set `TMPDIR` to a directory outside the checkout for disposable controls.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/idle-helper-pair-replay/replay.py --mode baseline
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/idle-helper-pair-replay/replay.py --mode fast
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/idle-helper-pair-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/idle-helper-pair-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/idle-helper-pair-replay
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/idle-helper-pair-replay --check-source-history
```

The verifier prints `PASS_IDLE_HELPER_PAIR_REPLAY`, the full counts above and
`rejection_controls=6`. Timing is opt-in, never a CI performance assertion:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/idle-helper-pair-replay/benchmark.py --output /tmp/idle-helper-timing.json
```

The benchmark generates its record from actual subprocess results, binds the
adapter hash, records every run and checks exit status, stderr and full stdout.
Its output must be outside the checkout. A different machine should compare
its own alternating runs rather than apply the measured percentage above.

## Limits and engineering decisions

The adapter is opt-in and source-bound, with no shared-code or selected-record
change. Its rejection of changed source bytes is intentional invalidation.
Finite source checks do not discharge the selected construction's five
framework assumptions. No supplier cold replay, Lean, Docker, independent human
review or proof-kernel acceptance is claimed.

Power-of-ten inspection found no recursion and bounded all new loops by the
fixed fixture: 120 squared pairs, sixteen scalar pairs and at most sixteen
minors per assignment. Functions stay below sixty lines. Guards use explicit
exceptions, file and subprocess errors propagate, and subprocesses have
timeouts. Python warnings are errors in every registered command.

Three bounded runtime deviations remain. Rule 3 permits managed Python
allocation; each sampled matrix has at most sixteen entries, minors have nine
indices, and the observed source entries fit in one byte. No complete matrix
transcript is retained in memory. Rules 8 and 9 permit compilation of the one
authenticated source and replacement of its one named callable. Authentication,
the fixed private namespace, complete guard/transcript comparison and source
mutation rejection constrain these deviations. A future source or interface
change requires a fresh adapter and renewed conformance, rather than widening
these permissions implicitly.

## Open next questions

Does this evaluation method help another explicitly pinned minor-based fixture?
First profile that complete command and derive its own full transcript and
rejection contract. No second fixture or general dispatch API is supplied.
The structured question and blocker are in `TASK.json`. No continuation is
reserved by this contribution.

## Credit and overlap

unpaidmoon supplied PR6338's source verifier and scoped idle-helper result.
eumemic's PR288 supplies the formal model, Ali Romman's PR468 supplies its
low-span lineage, and Nick Petalas's earlier span lemma supplies the preceding
helper question. Those mathematical contributions retain their attribution.
Distributive expansion, loop-invariant reuse and indexed determinants are
standard techniques. The new contribution is their complete source-bound
evaluation adapter and measured replay improvement for this fixture.

Canonical main was `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
Live open/all-state object searches, main-tree README searches, merged keyword
searches, recent account work and current claims found no competing adapter for
this fixture. The cached overlap snapshot covered 369 open PRs and 6,285
Discussion records. Its sparse local scan omitted 8,799 notes; targeted searches
used the complete main Git tree. Neither that coverage nor absence of matches
certifies novelty against unpublished work.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361559).
