# Gate-frame retiming of the eleven-stage cross-copy word

PR 450 prices an eleven-stage cross-copy hosted bit supplier built on PR 443's
R740 word with target mixing. Its bit supplier binds. This package keeps every
ordered scalar addition of PR 450's mixed word and changes only the frame in
which 113 phase-B deliveries are executed. The helpers' climb chains coarsen,
the local cost per call falls, and PR 450's own pipeline, run unchanged, prices
the result at

```
kappa = 8441130528457 / 6250000000000000 = 0.001350580884553120
```

against PR 450's `269548909542967 / (2 * 10^17) = 0.001347744547714835`, a gain
of `567267367657 / (2 * 10^17)`, which is 0.2105 percent. The assembly stays
bit-bound with 6.29 percent of complex slack.

## The witness format

A word lists, for every gate, the frame of the pinned 944-frame family in
which it executes. PR 443's checkers accept a word when, along each register's
event sequence, the frames form a nested chain, each gate's frame contains the
integer support of its destination and of every non-target operand, every
phase-B gate on a target lies inside that target's cap, and the mixing identity
holds. The cost of a register is the sum over its climb steps of `d ln(78 / d)`
for the dimension increments `d`, so merging a helper's steps with a target's
steps lowers the cost.

A retiming witness is a frozen list of `(phase, gate index, old frame, new
frame)` entries with the content hash of the input word and of the output word.
`code/retime_apply.py` applies it: it checks the input hash, requires every
listed gate to carry the old frame, writes the new frame, re-lists phase B by
frame dimension, asserts that every phase other than B is byte-identical in
its scalar content, that B's scalar content is the same multiset, and that the
output hash matches. Re-listing B by dimension is legal because helpers are
constant in phase B and targets only receive, so a register's B frames need
only form a chain. The witnesses here change no phase-A gate.

## The route

1. PR 443's word `research/e8-r740-replica32/data/word.json.gz` (content
   `64d7d1e0…`). `data/witness-unmixed.json` moves 18 B deliveries, giving
   content `47fe60b6…`.
2. PR 450's `code/mix_target.py`, unchanged, mixes that word. The result has
   content `1674b395…` and 42 receivers. PR 450's own run had 46 receivers. Four
   dimension-5 receivers disappear because their partner chains changed, and
   the retiming more than compensates.
3. `data/witness-mixed.json` moves 95 B deliveries, giving content
   `dc389ecc…`, the retimed word.

The local profile per call moves from PR 450's
`{1:2460, 2:1012, 3:276, 4:315, 5:108, 6:42, 7:14, 8:9}` to
`{1:2401, 2:1019, 3:291, 4:315, 5:99, 6:60, 7:5, 8:9}`, with the rank mass
7534 unchanged. The local cost per call falls from 25,612.68 to 25,555.04 in
`ln 64` units. Eleven stages of that word plus the hosted remainder
`{14:1, 56:184}` give the bit histogram

```
{1: 26411, 2: 11209, 3: 3201, 4: 3465, 5: 1089, 6: 660, 7: 55, 8: 99, 14: 1, 56: 184}
```

at `m = 78`, `W = 1200`, deficit 408, and the bit root
`1352407420162920171433 / 10^24` against PR 450's
`674781707224226878971 / (5 * 10^23)`.

## What is unchanged

Entrance frames and the residual structure are untouched, so residual widths,
the frozen hosting selection `data/selection.json`, the global template, the
live stock 1200, the 8140 hosted residuals with 1807 split, the maximum child
56, the halving depth 3 and the row allowance 28416 are those of PR 450. The
complex side is PR 448's. The bootstrap, the 47 strict outer inequalities and
the four outer controls are PR 434's as run by PR 450.

## What verify.py runs

`verify.py` first runs PR 450's `verify.py` unchanged into `<out>/parent450`
and requires its published kappa. Then, with PR 450's binaries, geometry and
complex side, it applies the two witnesses, runs PR 443's export, stage cohort,
C++ legality, formal columns at `h` and at `K = 5` with the 24 omitted-bridge
controls, the six record mutations, PR 450's mix check with its four mutation
controls against the parent word, and the Gram check on 944 frames. It then
runs PR 450's global template, parent audit, tape emission with the frozen
selection, hosted audit with 20 mutations, and assembly, and compares the
result with `EXPECTED.json`.

Three negative controls must be rejected:

- the mixed witness applied to the parent word (input hash mismatch).
- `data/control-wrong-frame.json`, the mixed witness with one delivery moved
  to a dimension-1 frame (the legality checker aborts with an illegal MOVE).
- `data/control-mix-crossing.json`, an unconstrained search result on PR 450's
  mixed word that moves donor deliveries across their mix frame. It passes
  legality and fails the formal-column check. This is why the search behind
  the witnesses froze the mix gates and kept every delivery of a receiver or
  donor on its side of the mix frame.

## What binds

Every improving move is in phase B. Phase-A gates sit at their minimal support
frames, and lifting one forces its source to climb early at a cost larger than
the helper's saving. Further gains need changes to the gate structure, which
alter the scalar sequence and are outside this witness format. Three
independent annealing seeds and a 30-sweep continuation end within 0.05
percent of each other.

## Run

```
python3 -B research/e8-eleven-stage-retimed/verify.py /absolute/new/output --quick
```

The flag is passed to PR 450's verify.py and skips only PR 443's historical
regressions, as there.
