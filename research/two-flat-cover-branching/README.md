# Faster exact requirement enumeration for the four-flat decoder search

**Tooling improvement and a scoped enumeration proof; no new kappa.** This answers
route B of [Discussion2954](https://github.com/CrocSwap/integer-mult-bounds/discussions/2954).
The expensive routine enumerates minimal pairs of flats covering a residual set
of P112 labels. Branching on an uncovered label replaces enumeration of every
flat spanned by a subset. A mutual residual-span test removes dominated outputs.
[PROOF.md](PROOF.md) proves completeness and exact minimal-antichain equivalence.

Final registered same-input measurements on this machine:

| Check | Pinned original | Replacement | Speedup |
| --- | ---: | ---: | ---: |
| 25,001 distinct residual masks | 128.91 s | 3.91 s | 33.00x |
| Full 12-pair search, including unchanged setup | 246.70 s | 117.86 s | 2.09x |
| Option-generation stage inside that search (CPU) | 132.34 s | 4.04 s | 32.77x |

[RESULT.json](RESULT.json) records the environment, measurements and exact result
hashes. These are not hardware-independent speed guarantees or estimates for the
complete hundreds-of-millions-of-pairs search. The earlier exploratory full run
measured 2.41x; the table gives the final measured replay, which also traces and
regenerates the complete residual request corpus.

## Reproduce

Python 3.12+ standard library and a C compiler supporting GNU C11/unsigned
`__int128` (tested with GCC 16.2.1), on Linux:

```sh
python3 -I -B research/two-flat-cover-branching/verify.py --work /tmp/two-flat-replay
```

The work directory must not exist. Expected final line:
`PASS_TWO_FLAT_COVER_BRANCHING`. Allow about eight minutes on the tested machine.
It authenticates source bytes, compiles the reference and replacement, compares
all 25,001 kernel outputs, checks all 2,048 subsets/capacities over F2^3 using an
independent explicit-set oracle, rejects implementation mutants and overflow,
runs a sanitized kernel, then compares all requirement JSON and complete outer
outputs on the same 12-pair benchmark. `--kernel-only` and `--full-only` separate
the two parts. `build.source(fast=True)` produces the source-bound adapter; the
frozen vendor file is never rewritten. [VERIFY.json](VERIFY.json) registers both
bounded commands. A fresh temporary build receives all generated artifacts.

## Evidence and completed coverage

Seed 46 assigned structural decoder research and selected class-C row 46's
(6,5,4,4) cover. Fix V1 orbit representative 46 in the pinned source order; select
12 distinct V2 indices with Python `random.Random(46).sample(range(776805),12)`.
The exact indices are in `data/pairs.txt`; they define the replay independently
of future random-library changes. Eleven pairs survive the original preliminary
filter. All 11 exported requirement records, 5,509 closure leaves, rank histogram,
and final span-two result are identical. This tiny slice is **not** an outer
search completion or a universal rank bound.

The original plan was rank-directed pruning of the closure phase. Profiling
showed 132 s in option generation and under 1 s in closure, so one evidence-driven
pivot targeted the actual bottleneck. The exploratory greedy search stopped at
200 seconds/362,954 trials on the first pair, found only rank two, and establishes
no impossibility claim. Its search is not part of the delivered verifier.

The direct kernel corpus contains all 25,001 distinct (mask,c,d) requests from
25,991 option calls in the sampled source run. Its labels and masks are bundled;
the full replay regenerates that exact request corpus and its reference comparison, rather than accepting a saved PASS line.
The compressed data88 payload exactly matches the pinned upstream bytes.

## Scope, source and attribution

Scientific base: `afc158a25ef3e0bd80de81d1eb5339f0dace118e`.
Source: DreamingOfClouds' help branch, exact commit
`1b25759bff5486293a9083ebbe0097b5f6642e08`, package
[`research/k2-class-c-help`](https://github.com/DreamingOfClouds/integer-mult-bounds/tree/1b25759bff5486293a9083ebbe0097b5f6642e08/research/k2-class-c-help).
[SOURCES.json](SOURCES.json) pins every bundled input. The source already uses the
branch rule in its *feasibility* function `dfs4`; this work applies it to complete
minimal-option enumeration. Retain that predecessor credit and the #2816/#2826/
#2862 E8/K2 lineage. Their catalogue completeness, RRC and decoder conclusions
are not newly established here. The selected result remains
0.001672660197076918; higher PR headlines are separate conditional claims.

Tekalign (@tekuuu), with substantial OpenAI Codex assistance in investigation,
implementation, proof drafting and verification. No independent human or formal
kernel review is claimed. Apache-2.0; bundled predecessor code retains its
original bytes and attribution. No selected-frontier, shared-code or `upstream/`
changes.

## Open next questions

- Measure additional representatives and all five class-C configurations using
  the exact option comparison before estimating campaign cost. First step: new
  fixed pair files, same source pins. Current measurements cover one small slice.
- A much stronger gate or orbit reduction is still needed for the full search.
  First step: profile the now cheaper generator versus outer feasibility/setup
  costs. This speedup alone does not make a 100-million-pair census affordable.
- Independently review the catalogue/orbit/real-rank premises before turning any
  full no-crack run into a decoder floor. This package discharges only the
  minimal-cover generation step, not those mathematical obligations.
