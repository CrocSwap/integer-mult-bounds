# R439 phase-B whole-block survey: two shortenings and seven class boundaries

Finite bit-supplier result for the punctured R439 word of PR #555/#589
(`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`), against base
commit `f567884aeb8851b6e794af1184119a3bfbe1e631` (selected PR799/PR589,
conditional kappa 0.001661634653669567). **No new kappa.** All phase-B blocks
of the word are self-contained integer-linear programs over their own
registers; this note searches each of the ten of them in one class, splices
the two shortenings it finds into one verified word, and certifies why the
class cannot shorten the other seven.

## Result

The complete exported local word falls **24,305 -> 24,289 ADDs** (8 forward
gates and their 8 literal reverse-cleanup gates):

| quantity | before | after |
|---|---:|---:|
| block 506 additions (`B[102:128)`) | 26 | **24** |
| block 523 additions (`B[404:449)`) | 45 | **39** |
| complete exported ADDs | 24,305 | **24,289** |
| exported records | 27,234 | 27,218 |
| forward positive bound | 49,347 | 49,347 (equal) |
| composed reverse positive bound | 1,113,070 | **1,090,494** |
| payload | 93 bits | 93 bits (cap 104) |
| local paid profile / rank mass | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` / 5,129 | unchanged |
| bit saving / kappa | conditional, complex-bound | unchanged, no new kappa |

All 661 register frame paths are identical before and after (every block
register is touched by its replacement program), so the frozen hosting and
paid profile carry over unchanged. Forward integer maps of both replaced
blocks are exactly equal; the exact F2 endpoint holds on all 661 dirty-input
columns; the inherited H1-H5 interface conclusions of the pinned
`xcheck_p.py` hold on the spliced word.

## Survey of all ten phase-B blocks

Class: the **whole-block single-write class** of open PR #873 (block 508),
with the neighboring framings of PR #844 (fixed two-factor splits) and PR
#857 (integer factorization): each register's final integer row is realized
once, in some realization order, as its entry singleton plus a subset of
donors, where each donor is either the completed final row of a register
realized earlier or the entry singleton of a register realized later, and
each donor is used at most once per row. A row with `k` donors costs `k`
additions. Programs that consume a register mid-construction (multi-write
interleavings) are **outside** the class and are not searched.

| frame | slice | gates | class minimum | status |
|---|---|---:|---:|---|
| 506 | `B[102:128)` | 26 | **24** | construction, spliced |
| 507 | `B[128:163)` | 35 | none | infeasible; donor-supply witness (row 3, col 4: demand 3 > supply 1) |
| 508 | `B[205:242)` | 37 | 30 | cross-check: reproduces PR #873's certified minimum exactly |
| 509 | `B[283:314)` | 31 | none | infeasible in class (global; no per-row witness) |
| 519 | `B[163:205)` | 42 | none | infeasible; donor-supply witness (row 2, col 8: 2 > 1) |
| 520 | `B[242:283)` | 41 | none | infeasible; donor-supply witness (row 9, col 9: 1 > 0) |
| 521 | `B[314:361)` | 47 | none | infeasible in class (global; no per-row witness) |
| 522 | `B[361:404)` | 43 | none | infeasible; donor-supply witness (row 5, col 3: 2 > 1) |
| 523 | `B[404:449)` | 45 | **39** | construction, spliced; beats open PR #857's 40-gate witness |
| 524 | `B[449:490)` | 41 | none | infeasible; donor-supply witness (row 6, col 9: 3 > 2) |

Row/column indices of the witnesses are local to the block's sorted register
list; the witness rows carry the wire numbers too. A donor of a row must fit
the row's goal entrywise (all values nonnegative), so summing **every** fitting
donor, including mutually exclusive singleton/row pairs, over-approximates
the achievable column supply. A demand above that sum rules out the row for
every realization order at once: an order-independent certificate that needs
no trust in the dynamic program. Blocks 509 and 521 have no such row; their
infeasibility is a joint order obstruction certified only by the two
exhaustive dynamic programs (`search.py` forward, `verify.py` backward, whose
distances are pinned in `EXPECTED.json`).

The infeasibility results are scoped statements about this class. They are
not impossibility theorems for the blocks: blocks 509 and 520 have published
shorter programs in other classes (PRs #843 and #844), which use exactly the
mechanisms (shared partial sums, fixed-factor decompositions) this class
excludes. The survey therefore also explains why those claimed-block methods
do not transfer to the unclaimed blocks.

Two concurrent PRs landed on unclaimed blocks after this survey's search
completed, both in factor-split classes: open PR #880 (frame 507, 35 -> 30
via two fixed positive factors) and open PR #884 (frame 521, 47 -> 31 via a
bounded factorization search). The certificates here show their objects are
exactly two of the blocks with no whole-block single-write program: a
shorter program for frames 507 and 521 must use factor-level intermediate
donors or multi-write interleavings, which is what those constructions do.
This is independent structural evidence for their mechanisms; their
implementations and savings are not imported and are not part of the spliced
word.

## Method

`search.py` (discovery) runs a dynamic program over realized-register
subsets; each transition realizes one row with a minimum donor subset found by
meet-in-the-middle subset sums. It writes `CANDIDATES.json` (full search
record) and `CERTIFICATE.json` (bindings, candidate gates, source pins).
Deterministic, no randomness, standard library only.

`verify.py` (independent) imports no search code. It re-derives every class
minimum or infeasibility with a backward Bellman recursion and its own
iterative-deepening donor enumeration, rechecks the donor-supply certificates
by direct counting, and for the spliced word recomputes forward/reverse
integer maps, all 1,024/4,096 block Boolean truth tables, the literal cleanup
reversal, register frame paths, the exact F2 endpoint on all 661 columns, the
H1-H5 interface via the pinned `xcheck_p.py`, and the exported bills and
positive/payload bounds via the pinned `export_records.py`. Twelve mutation
controls must be rejected. Three real defects during development (a reversed
subtraction in the backward donor recursion, a left-to-right splice that
shifted block 523's indices, and a no-op mutation control) were each caught
by one of these checks; see `VALIDATION.md`.

## Block 523: relation to open PR #857

PR #857 (seed 18) replaces the same block with a 40-gate program found by a
bounded randomized integer-factorization search, reporting "no shorter
reverse-dominated candidate" in their search and allowing reverse growth to
1,228,514 with a 94-bit payload. The 39-gate witness here is a different
mechanism: a certified minimum of the single-write class, with the minimum
re-derived by an independent recursion. Its local reverse map is not
entrywise dominated (16 entries strictly shrink, a few grow), but the
composed exported reverse bound of the whole word **drops** to 1,090,494 and
the payload stays at 93 bits. Their implementation and savings are not
imported; both results should be credited to their authors.

## Reproduce

Standard-library Python 3.11+ from the repository root:

```sh
python3 -I -B research/r439-bsection-survey/search.py
python3 -I -B research/r439-bsection-survey/verify.py
```

Expected (verify, ~90 s):

```text
"status": "PASS_R439_BSECTION_SURVEY"
"columns": 661
"survey_frames": [506, 507, 508, 509, 519, 520, 521, 522, 523, 524]
"spliced_frames": [506, 523]
bill_before.adds = 24305, bill_after.adds = 24289
bill_before.forward_positive_bound = bill_after.forward_positive_bound = 49347
bill_after.reverse_positive_bound = 1090494
bill_after.payload_bits = 93
12 negative controls rejected
```

`search.py` regenerates `CANDIDATES.json` and `CERTIFICATE.json` byte for
byte (checked across runs). `verify.py` needs no third-party packages; the
exporter and interface checker are used unmodified from their pinned
locations.

## Scope and obligations

Only `research/r439-bsection-survey/` is added. `upstream/`, the selected
certificate and every consumed supplier source are unchanged. This is a
conditional finite construction and a scoped class-infeasibility survey, not
a Lean proof and not a new kappa: the bit side does not bind the selected
witness (kappa is complex-bound at 0.001661634653669567), so the result is
bit headroom and certified search coverage only. The minima are certified
only inside the single-write class; multi-write interleavings and shared
partial sums are not excluded, and "no class program exists" is not an
impossibility theorem. The C++ native legality and 5/9/11-stage replays, the
hosted invoice, the global assembly, the selected cold replay, Lean
formalization and remote CI are not run here. All inherited all-size/compiler,
common-label/mutable-source, whole-call hosting, precision/tape and analytic
assumptions remain. The spliced word is a research witness; it is not
proposed as the selected frontier.

## Credit

The word and its generators, checkers and pricing pipelines are eumemic's
(PR #543/#555, on #510's nine-stage chain and #545's punctured unit), with
DreamingOfClouds, Dylan Crow (record exporter), Zhihao Chen and the retained
supplier lineage. The whole-block single-write class and the
independent-recursion verification pattern follow open PR #873 (block 508)
with attribution; the fixed-factor framing is PR #844's and the factorization
search is PR #857's (both objects and savings not imported). The four
claimed blocks' cross-checks (508/509/520/523) are recorded so the survey is
complete. Prepared with help from opencode. Apache-2.0. No independent human
review is claimed.
