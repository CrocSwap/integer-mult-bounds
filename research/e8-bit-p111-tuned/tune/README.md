# PR #555's punctured R439 bit word with two A-section transports

Two helper additions of PR #555's word (`data/bitE8mut-p111.json.gz`, v = 111, R = 439) are moved out of the D4 block-frame
mini-node gates they sit in and rerun at other frames. Nothing else changes: same registers, same scatter, same retained
totals (nine COPY ranks of 7, decoder constant 63), same frozen hosting selections, same pipelines.

| | PR #555 | this word | change |
|---|---|---|---|
| bit c, nine stages (PR #510's chain, 32 replicas, parameterised by `code/adapt9p.py`) | 0.001733052823330162099157 | **0.001733427039589844234749** (`1733427039589844234749/10^24`) | +0.0216% |
| bit c, eleven stages (PR #493's chain as parameterised by PR #545's `adapt.py`) | 0.001710608806098012673516 | **0.001710951900777583975622** (`855475950388791987811/(5·10^23)`) | +0.0201% |
| κ with #548's complex b (0.001593519419282307) | 0.001590984155135328 | 0.001590984155135328 | none |

κ is complex-bound for every cited complex supplier (#548, #544, #535, #531), exactly as with #555's word, so this changes
no κ. The gain is bit headroom only: c is above every cited complex b (the largest, #548's, is 0.0015935), so the bit side
does not bind. The local paid profile goes from `{1:1321, 2:1342, 3:80, 4:47, 5:102, 6:10, 7:18}` to
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` (rank mass 5,129 both; 27,234 records, 24,305 common-frame ADDs, payload
93 bits, 636 frames, all unchanged); the nine-stage global profile is `{1:381024, 2:400416, 3:22752, 4:26880, 5:29376,
6:17376, 7:26784, 42:288}`.

## What changed (`moves.json`, applied by `apply.py`)

Both moves take one summand out of a mini-node gate of phase A (the nine phase-A gates at the four D4 block frames 506-509, rank 4,
that carry a pseudo-target's B-part; gate and register numbers are those of the base word, helper h is register 222 + h):

- **hoist.** A[1993] is `helper 222 += {x17, h49, h71, h130, h191, h246, h248, h249}` at frame 509 (rank 4). The summand
  `helper 222 += helper 248` (register 444 += 470) becomes its own gate at rank-1 frame 79, placed immediately before that gate.
- **sink.** A[1994] is `helper 191 += {x17, h49, h71, h130, h149, h247, h249}` at frame 509. The summand `helper 191 += helper
  247` (register 413 += 469) becomes its own gate at rank-7 frame 517, the frame of the gate `helper 257 += helper 191 + helper
  74` (helper 257 is a retained total), placed immediately after base gate 2028.

Each move factors a multi-source addition, moves one summand across additions that commute with it and gives it another
frame from the existing catalogue; the dirty-register endpoint is unchanged on every column. C is rebuilt as the literal
reverse of the z-destination gates of A and B at the full frame (A has 2,075 gates, C 2,574). The profile changes by
`+2 e1 − e3 − 3 e4 + e6 + e7`, a zero rank-mass change. The independent checker (`xcheck_p.py`, with the interface lemma
H1-H5 and its word-level mutation controls) and the official cohort checkers accept the word, and the hosting programmes
rediscover the frozen selections.

## Where the moves come from, and why #541/#542/#548's move lists are not reused

The mechanisms are those of three open PRs on PR #510's R480 word: Dugongue's #541 (factor a multi-source helper addition, move
one summand across its commuting prefix and give it the source's rank-1 frame: the *hoist* is an instance of the same mechanism, applied to a helper summand already at a rank-1 frame rather than a source), Dugongue's #548
(observable pruning, frame-sensitive transports, Steinberg three-to-two cancellations: the *sink* is a transport of that kind) and
rohanarun's #542 (observable slice and least-frame assignment, on the same word). Their published moves are lists of R480 gate
numbers: the 60 two-x-source helper additions, the 227 zero-response gates of R480's dead totals, 20 transports and 7
cancellations by id. PR #555's word comes from the R420 L3 skeleton: it has no two-x-source additions and no zero-response
gates, and its gate numbering is different, so the lists cannot be applied. `tune.py` therefore re-runs the mechanisms as
searches on the word's elementary-operation form (one source per gate): single-operation transport with reframing under
exact commutation and frame nesting, Steinberg 3→2 with frame re-choice, frame reassignment, and the pruning and least-frame
steps. Run on the R480 word, the same code reproduces #541's local profile `{1:1260, 2:1320, 3:60, 4:180, 6:120, 8:9}` and
#548's `{1:1257, 2:1330, 3:43, 4:163, 6:137, 8:9}` exactly. Run on PR #555's word to a fixed point, it applies exactly the two
moves above; the pruning, Steinberg and least-frame steps have nothing to apply that lowers the moment. `apply.py --discover`
repeats that search inside `verify.sh` and asserts that it returns this word. The greedy search is not claimed optimal.

## Files

- `moves.json`, `apply.py`: the two moves, pinned to the base word's content hash, and their application with an exact replay.
- `bitE8mut-p111-tuned.json.gz`: the tuned word (rebuilt byte for byte by `verify.sh`).
- `tune.py`, `wlib.py`: the search engines (numpy) and the exact replay and paid-profile code.
- `fastc.py`: a quick exact pricer, `c = certify(288 × local paid profile + idle remainder, 64, 28416)`; the remainder is read off
  the base word's hosted audit. `verify.sh` checks that it equals the pipeline's c; it is not a substitute for the pipeline.
- `verify.sh`, `summary.py`, `EXPECTED.json`: the checks and every number.

## Checks

```sh
python -m pip install -r research/e8-bit-p111/requirements.txt
bash research/e8-bit-p111/tune/verify.sh /absolute/new/output
```

Python 3.11+ with numpy, sympy and scipy, a C++17 compiler (`CXX`) and Boost headers (`BOOST_INCLUDE`). The script rebuilds the
base word from #555's frozen plan, applies the moves and compares both byte for byte, runs the independent replay, the interface lemma,
the word-level and record-level mutation controls, the official legality and formal-column checkers at five, nine and eleven stages,
the Gram witnesses, and both price pipelines on the tuned word, and asserts the nine-stage c exactly
(`1733427039589844234749/10^24`) against `EXPECTED.json`. PR #555's own `verify.sh` is unchanged and still passes: it checks the
untuned word and the controls (`MANIFEST.sha256` lists the files of this directory).

## Credit and caveats

PR #555 (eumemic) is the base: the punctured R439 word, its generator, checkers, pricing pipelines and package structure are
used unchanged, building on #543 (R420 skeleton), #545 (punctured unit, DreamingOfClouds) and #510 (nine-stage chain). The
mechanisms are from #541 and #548 (Dugongue) and #542 (rohanarun). The searches, `apply.py`, `verify.sh` and this note were
prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.

All retained assumptions of #555 apply unchanged (mutable-source realization, whole-call hosting, the all-size compiler,
compressed windows, precision and tape contracts, the cited complex suppliers). The moves rewrite the phase-A writes of two
helpers inside mini-node gates; `xcheck_p.py` and the official checkers verify the result exactly. This is a conditional
finite construction, not a Lean proof, and it changes no κ.
