# R439 phase-B schedule: multi-write shear programs for all ten blocks

**Finite bit-circuit construction; no new kappa.** This replaces every
phase-B block of the selected PR589 tuned punctured R439 word
(`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`) with a
shorter exact program on the same registers at the same frame, found by one
deterministic search in the full multi-write shear class. The complete
exported local word falls **24,305 -> 24,053 ADDs** (252 complete ADDs:
126 forward gates and their 126 literal reverse-cleanup gates).

| quantity | before | after |
|---|---:|---:|
| phase-B block gates (all ten) | 388 | **262** |
| complete ADD records | 24,305 | **24,053** |
| all scalar records | 27,234 | 26,982 |
| forward positive bound | 49,347 | **26,653** |
| composed reverse positive bound | 1,113,070 | **776,006** |
| local payload | 93 bits | **90 bits** (cap 104) |
| paid profile / rank mass | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` / 5,129 | unchanged |
| nine rank-seven COPY/ERASE pairs | 9 / 9 | 9 / 9 |
| bit saving / kappa | conditional, complex-bound | unchanged, no new kappa |

All 661 register frame paths are identical before and after (every block
register is touched by its replacement program), so the frozen hosting and
paid profile carry over unchanged. Each replacement block has exactly the
same integer transfer matrix as the block it replaces, so the programs agree
over every commutative coefficient ring and on arbitrary dirty F2 inputs; the
exact F2 endpoint holds on all 661 dirty-input columns and the inherited
H1-H5 interface conclusions of the pinned `xcheck_p.py` hold on the spliced
word.

## Per-block results against the recorded state of the art

| frame | slice | word | this search | best previously recorded |
|---|---|---:|---:|---|
| 506 | `B[102:128)` | 26 | **21** | 24: PR #891 single-write class minimum; open PR #1001 independently claims 21 |
| 507 | `B[128:163)` | 35 | **24** | 30: PR #880 fixed two-factor splits; PR #884's README records an unpublished 24-gate orientation candidate |
| 519 | `B[163:205)` | 42 | **27** | 32: open PR #908 by title |
| 508 | `B[205:242)` | 37 | **21** | 30: PR #873 whole-block schedule, PR #891 class minimum |
| 520 | `B[242:283)` | 41 | 37 | 29: open PR #923 — **not beaten here** |
| 509 | `B[283:314)` | 31 | **21** | PR #891: infeasible in the single-write class; open PR #973 independently claims 21 |
| 521 | `B[314:361)` | 47 | **30** | 31: merged PR #884 factorization (no minimality claimed) |
| 522 | `B[361:404)` | 43 | **29** | 33: open PR #906 trajectories |
| 523 | `B[404:449)` | 45 | **26** | 39: PR #891 single-write class minimum; 40: open PR #857 |
| 524 | `B[449:490)` | 41 | **26** | 27: open PR #914 by title |

Nine of ten blocks improve on every recorded claim; frame 520 does not beat
open PR #923's claim and its local reverse total grows (368 -> 830) even
though the composed word-level reverse bound falls. No concurrent
implementation or saving is imported: every program here comes from the one
search below against the pinned word. The comparison rows for open PRs
#908/#914/#923 use their titles and bodies, not their code.

**Overlap refreshed at submission (2026-10-13, after the search and
verification completed).** Open PR #1001 (frame 506 at 21) and PR #973
(frame 509 at 21) independently reach the same counts as two blocks here;
that is convergent evidence from separate searches, and both are credited.
Open PR #989 composes the four blocks of PRs #880/#873/#908/#914 at
24,305 -> 24,233 ADDs; this search's programs on those same four frames
(507: 24, 508: 21, 519: 27, 524: 26) are strictly shorter than the counts
they compose (30/30/32/27), and this one word covers all ten blocks at
24,305 -> 24,053. The phase-A prefix-resynthesis line (#904/#936/#952/#980)
is a different mechanism and is not composed here.

## Class and search

A block is a sequence of single-source additive gates `dest += src` on its
own registers; its exact integer transfer matrix `M` satisfies `M >= I`. Any
replacement program of such gates is exactly a path of legal nonnegative row
or column subtractions from `M` to the identity (row = peel a last-applied
gate, column = peel a first-applied gate). The class is therefore **all**
multi-write shear programs on the block's own registers: shared intermediate
rows and mid-construction reads are inside it. It strictly contains PR
#891's whole-block single-write class and PR #880's fixed factor splits, and
equals the subtraction class sampled by PRs #884 and #906. Programs that use
registers outside the block, or non-additive gates, are outside the class.

`search.py` runs, per block, with `random.Random(20261013 + frame)`:

1. 6,000 min-excess greedy reductions with random tie-breaks;
2. 4,000 uniform random legal trajectories (path cap 90);
3. one width-6,000 beam search for a path strictly below the incumbent.

The stopping rule is complete: all 10,000 trajectories and the beam phase
finish for every block; there is no adaptive stopping. Coverage is all ten
phase-B blocks of the pinned word, once each. The search is deterministic;
`search.py` regenerates `CANDIDATE.json` byte for byte (about ten minutes
with one worker per block). **"Best found" is not a minimality result**: no
block has a certified class minimum here, and shorter programs may exist.
As weak context only, `rank(M - I)` (an admissible lower bound on any shear
program) is 8 for frame 506, 11 for frame 521 and 10 for frame 523.

## Reproduce

Standard-library Python 3.11+ from the repository root:

```sh
python3 -I -B research/r439-bsection-multwrite/verify.py
```

Expected (about two minutes):

```text
PASS_R439_BSECTION_MULTWRITE gates=388->262 ADDs=24305->24053 columns=661 controls=8 rank_mass=5129 kappa=unchanged
```

`search.py` (about ten minutes, parallel) regenerates `CANDIDATE.json` and
prints `PASS_R439_BSECTION_MULTWRITE_SEARCH ... gates=388->262`.

## Verification

`verify.py` imports no search code. It checks the source SHA-256 pins; each
block's register binding, gate shape, exact integer transfer matrix and all
2^10-2^12 Boolean block truth tables; the ten-way splice (applied from the
end of B backwards) and the rebuilt literal reverse cleanup; all 661
register frame paths; the exact F2 endpoint on all 661 arbitrary dirty-input
columns; the H1-H5 interface via the pinned `xcheck_p.py`; the paid profile
and rank mass; and the exported bills and positive/payload bounds via the
pinned `export_records.py`. Eight mutation controls must be rejected (mutated
source, dropped gate, illegal frame, swapped block, omitted cleanup gate,
deleted gate with matching cleanup, illegal frame in the spliced word, stale
cleanup). The exact report is pinned in `CERTIFICATE.json` and compared on
every run.

## Scope and obligations

Only `research/r439-bsection-multwrite/` is added. `upstream/`, the selected
certificate and every consumed supplier source are unchanged. This is a
conditional finite construction and a completed bounded search, not a Lean
proof and not a new kappa: the bit side does not bind the selected witness
(kappa is complex-bound at 0.001661957774647029 at the base commit), so the
result is bit headroom only. The class excludes scratch registers outside each block and
non-additive gates; the D-prefix substitution candidates (#915/#926/#941)
are a different, not-adopted mechanism whose savings are not composed here.
The C++ native legality and 5/9/11-stage replays, the hosted invoice, the
global assembly, the selected cold replay, Lean formalization and remote CI
are not run here. All inherited all-size/compiler, common-label/mutable-source,
whole-call hosting, precision/tape and analytic assumptions remain. The
spliced word is a research witness; it is not proposed as the selected
frontier.

## Credit

The word and its generators, checkers and pricing pipelines are eumemic's
(PR #543/#555, on #510's nine-stage chain and #545's punctured unit), with
DreamingOfClouds (PR #589 tuning), Dylan Crow (record exporter), Zhihao Chen
and the retained supplier lineage. The phase-B whole-block framing is PR
#891's (Aaron Wang), the fixed-factor framing is PR #880's (Krishnendu
Purohit), the factorization/subtraction searches are PRs #857/#884/#906's,
and the independent-verifier pattern follows PR #884 (martin Rv); their
objects and savings are compared above but not imported. Concurrent claims
from PRs #908/#914/#923, the convergent per-block claims #973/#1001, the
four-block composition #989, and the four/five/six-wire prefix line
(#904/#936/#952/#980) are credited and not composed. Prepared with help
from opencode.
Apache-2.0. No independent human review is claimed.
