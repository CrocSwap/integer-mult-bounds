# R439 one-slot multi-column interleaving: scatter 88 -> 84

**Status: construction (finite exact scalar circuit). No new kappa, no optimality
claim, no native/physical admission.**

## What changed

PR2407 (Ross Richardson) interleaved one retained column (column 0) of the
R439 scatter with the 303 fixed deferred target-undo gates of the PR2115 split
(ideal303, kept undo gates {31,51,52}) and reduced the complete scalar scatter
from 94 to 88. Its Open next question 2 asked whether several improved columns
can share one chronological undo pass under one live COPY slot. No such search
had been made.

This package states the one-slot constraint and gives an exact witness:

- one private COPY slot; each retained column `j` gets one COPY interval
  `[copy_cut, erase_cut]` of cuts of the fixed 303-gate undo;
- intervals are chronological and do not overlap. A handoff at the same cut is
  allowed: ERASE then COPY, both before undo gate `cut`;
- a tap `(c, i)` adds the live copy into target `i` at cut `c`. Its final
  response is `U_after(c) e_i`.

The complete stream has **84 scatter ADDs (11,057 ADDs in total)**. PR2407 has
88 / 11,061 and the PR2115 split has 94 / 11,067. All 306 undo gates are kept
(3 kept + 303 deferred, same records in the same order), as are the nine rank-7
COPY/ERASE pairs and the 2,911 ordered MOVEs. The paid histogram
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` and the rank mass of 5,129
are unchanged. The inherited guards still pass: `64F^3B^2` has 95 bits
(< 104) and `2^18F^5B^4` has 181 bits (< 192), with F = 25,717 and
B = 5,030,078. The reverse majorant B rises (split 94: 5,024,524; PR2407 88:
5,026,856; here 5,030,078) but stays inside both guards. These guards are
PR2407's source-normalised positive scalar envelopes, not an all-size
physical precision theorem.

The baselines 94 (PR2115 split, PR2279 split-ideal optimum) and 88 (PR2407),
and the deferred-split and interleaving model itself, come from PRs that were
**open and unmerged** (not on main) when this package was prepared; their
heads are pinned in `SOURCES.json` under `predecessors`. The 84 stream's
correctness does not depend on them: `verify.py` re-derives the split from
main's pinned word and exporter and replays everything literally. The
"94 -> 88 -> 84" comparison and the admissibility of the model do depend on
them.

| order | column | COPY interval | taps | tap cuts (non-COPY-cut taps) | split (cut 0) taps | change |
|---|---|---|---|---|---|---|
| 1 | 2 | [0,0] | 8 | 0 | 8 | 0 |
| 2 | 3 | [0,0] | 4 | 0 | 4 | 0 |
| 3 | 5 | [0,0] | 11 | 0 | 11 | 0 |
| 4 | 4 | [0,18] | 5 | 0, 17 `(17,87)` | 8 | -3 |
| 5 | 7 | [18,18] | 5 | 18 | 5 | 0 |
| 6 | 8 | [18,18] | 13 | 18 | 13 | 0 |
| 7 | 1 | [18,42] | 15 | 18, 39 `(39,9)` | 16 | -1 |
| 8 | 6 | [42,42] | 13 | 42 | 13 | 0 |
| 9 | 0 | [42,182] | 10 | 42, 69, 126, 182 `(69,6) (126,24) (182,3)` | 16 | -6 |
| | **total** | | **84** | | **94** | **-10** |

Column 0 is re-decomposed. PR2407's witness needs `[0,182]`, with taps at
0/104/126/182. This one keeps the same saving of 6 inside `[42,182]`. That frees
the prefix `[0,42]` for column 4 (-3: target 87 is tapped at cut 0 and again at
cut 17, after its source gates at cuts 1, 3, 13 and 16) and column 1 (-1: target 9
is tapped at cut 39, after its source gate at cut 38). Columns 7 and 8 at cut 18 and
column 6 at cut 42 are single-cut segments at their cut-0 cost. Three columns
have non-trivial intervals and the peak live COPY count is 1.

## Reproduce

From the repository root (Python standard library, ~3 s; run here only under
CPython 3.14.4):

```sh
python3 -I -B research/r439-one-slot-multicolumn-interleave/verify.py
```

Expected output:

```
PASS_R439_ONE_SLOT_MULTICOLUMN scatter=94->88->84 ADDs=11067->11061->11057 interleaved_columns=3 dirty_columns=661 controls=13 no_new_kappa no_optimality_claim
```

Generic launcher: `python3 scripts/research_package.py --package research/r439-one-slot-multicolumn-interleave`.
`VERIFY.json` registers the repository's Python 3.12 replay. No 3.12
interpreter was available for this session, so the launcher refused to run the
replay locally; only `--check-only` (PASS_PACKAGE_METADATA_AND_PINS) and the
direct command above under CPython 3.14.4 were run. Hosted CI is the first
3.12 run.
Use `--output DIR` to write `records.bin`, `frames.json` and `RESULT.json` for
native replay.

What `verify.py` checks (the code is adapted from PR2407's verifier, generalised
from one tapped column to an ordered list of one-slot segments):

1. The live inputs are pinned (SHA256 and Git blob). The PR2115 split is
   re-derived: literal inverse basis, kept gates {31,51,52}, and an unchanged
   complete target operator.
2. Algebra: each column appears once and the intervals are chronological. Every
   tap lies inside its interval. The XOR of the suffix responses equals column
   `j` of the scatter.
3. Literal stream: the exported split is rebuilt with the nine segments
   interleaved into the 303 undo records. Replay covers all 661 dirty input
   columns in both orientations, checks that the private slot is free at every
   COPY and that its snapshot is unchanged at every ERASE, the frame invoice,
   the paid profile, the ordered MOVEs and the two precision guards. The
   peak live COPY count is measured during the invoice replay (it is 1); the
   one-slot property itself is enforced by requiring a free slot at each COPY.
4. Deleting the taps and COPY/ERASE records leaves exactly the exported split
   stream. So every undo gate and every other record is kept, in order, and the
   COPY/ERASE multiset is unchanged.
5. Calibration: the original, split-94 and PR2407-88 streams rebuilt by this
   code are byte-identical to the record SHA256s in PR2407's `RESULT.json`.
6. Thirteen negative controls must each be rejected with the expected reason:
   overlapping intervals (algebraic and literal), wrong cut, dropped tap and
   swapped columns (algebraic and literal), a tap outside its interval, a
   missing undo gate, a premature ERASE, a wrong tap frame and an underpriced
   COPY. Reversed tap order within segments is accepted as an equivalent
   presentation.
7. The second 84 schedule found by the packaged search (identical DP output
   for both recorded seeds in `SEARCH.json`) passes the same algebraic check,
   two-orientation literal replay, invoice and strip-equality at 84 / 11,057.
8. The fixed receipt `RESULT.json` must match.

Verification is single-lineage: `verify.py` is an adaptation of PR2407's
verifier, and the only other checker in the package (`search/search.py`) uses
the same suffix-response method. There is no separate independent
implementation in this package (PR2407 shipped one for its 88 stream). The
reviewers' independent forward-simulation and literal-replay scripts for this
session are not packaged.

## How the witness was found (search record)

`search/search.py` is not part of the acceptance check. It works over "atoms"
(target `i`, lifetime segment `k` between undo gates with source `i`). There are
412 distinct responses `U_after(c) e_i`, available on contiguous cut ranges.
A column representation is a set of atoms, and its canonical COPY core is
`[max lo, min hi]` (a single cut) or else `[min hi, max lo]`. The search runs:
(1) exact single-cut options at all 304 cuts; (2) seeded tabu walks on random
cut intervals, whose moves are gate relations, pooling every visited state that
costs no more than the cut-0 cost; (3) an exact DP over one-slot chronological
schedules restricted to the pooled options; (4) exact meet-in-the-middle
exclusion of weight <= 4 over the full cut range.

```sh
nice -n 10 python3 -I -B research/r439-one-slot-multicolumn-interleave/search/search.py --seed 6 --walks 30000 --out "$TMPDIR/search-seed6.json"
```

(about 4.5 min; write the output to a scratch path, not the checkout). The
packaged runs are recorded in [SEARCH.json](SEARCH.json), each a single process
under CPython 3.14.4; a reviewer re-ran seed 6 and got a byte-identical record.
**Seed 6 (30,000 walks) and seed 606 (60,000 walks)** both gave DP optimum 84
over their pooled options and the same pooled per-column minima. Both seeds
output the *same* 84 schedule (col 4 on [1,17], col 8 at 17, col 1 on [18,39],
cols 6 and 7 at 39, col 0 on [50,182]); it differs from WITNESS.json, and
`verify.py` replays it in full as a second accepted 84 schedule, so the 84
result is regenerable from packaged code. WITNESS.json
itself came from an earlier exploratory pass that was not packaged. That pass
ran the same tabu move on every interval of the cut grid
{0,6,...,210} ∪ {7,16,29,61,63,104,105,126,136,176,182,184,192,303} for columns
0, 1, 4, 6 and 8 (seeds 6000+j), used exact single-cut costs for the other
columns, and then ran the same DP. It also gave 84; verify.py replays its
schedule in full.

- **Exact per-column lower bounds within the one-slot tap model on
  ideal303 / {31,51,52}** (taps drawn from the 412 responses `U_after(c) e_i`
  of this fixed order, full cut range, so valid for every interval): column 3
  has minimum weight exactly 4; every other column needs >= 5 taps. Within that
  model, columns 3, 4 and 7 (4, 5 and 5 taps) are therefore optimal in the
  witness. These are not lower bounds for other circuit forms, multi-slot
  schedules, other undo orders or other kept sets.
- **Heuristic pooled per-column minima** (any interval, ignoring the slot):
  10, 14, 8, 4, 5, 11, 12, 5, 12 for columns 0..8, a sum of 81. The cheaper
  representations of columns 1, 6 and 8 have cores that collide with column 0's
  `[42,182]` or column 4's core `[1,17]` under one slot. Column 1's cost-14 cores
  all start at cut 18 and end at cut 126 or later. Column 6 costs 12 only at cut 6
  or on intervals that start at cut 6 or 30 and end at cut 194 or later. Column
  8's cost-12 cores all contain cut 136. Column 0's cost-10 cores are `[11,182]` and `[50,182]`. The DP over the
  pooled options found nothing below 84.
- This is a **failed search beyond 84 over a finite heuristic option pool. It is
  not a lower bound**: 84 is not claimed optimal, and the gap is between 44
  (exact, within the same tap model) and 84.

## Scope, inherited assumptions, unresolved obligations

- Scalar-only finite construction on one fixed word, undo order (ideal303) and
  kept set. It inherits PR2407's model: the R439 word and exporter from main,
  the PR2115 split, PR2279's split-ideal accounting for the 94 baseline, and the
  one-slot COPY/ERASE frame invoice of PR2407's verifier.
- Target deferral uses PR2115's replacement H5 contract (`V R = I` replaces H5
  with the H2 target clause). That contract is inherited, not re-proved here.
- No kappa change: every rank charge is unchanged.
- Not natively replayed. Python literal replay is not a native parser or
  physical COPY-lifetime admission (PR2421 / PR2373 lineage). That obligation is
  open.
- Whole-call hosting / owner binding is open. Concurrent PR2437 (Ross
  Richardson) binds PR2407's *single-window* 88 stream to the PR1627-style
  ideal whole-call snapshot/owner contract. That binding has not been re-run on
  this stream, which has three non-trivial COPY windows and same-cut
  ERASE/COPY handoffs.
- As in PR2407, these remain unexecuted or inherited: native compiler and
  physical recursive scratch allocation, all-size and common-label
  realization, precision/tapes beyond the two source-normalised guards, exact
  recovery, analytic transfer and outer assembly.
- H2/K interface flags of the source word remain false, as in PR2407.
- Predecessor baselines and models are from open, unmerged PRs (see above).

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. **Is 84 optimal for one-slot schedules on ideal303 / {31,51,52}?** A lower
   bound would close PR2407 OQ2 for this order. First step: exact weight-5..7
   exclusion per column and core for columns 1, 6 and 8. Blocker: triple tables
   (~11.7M sums) exceed this session's memory budget.
2. **Does the 84-tap stream pass PR2421 native replay and the PR2373 parser?**
   First step: run `verify.py --output DIR` and feed `records.bin` to PR2421's
   replay. Blocker: PR2421 is not on the base commit.
3. **Does the PR2437 whole-call ideal-hosting binding extend to the 84
   stream's three COPY windows and same-cut handoffs?** First step: run
   PR2437's binding check on `records.bin` from `verify.py --output DIR`.
   Blocker: PR2437 is open and not on the base commit; its binding is stated
   for one live window.
4. **Do other undo orders or kept sets admit cheaper one-slot schedules?**
   Columns 1, 6 and 8 have cheaper pooled representations that collide under
   ideal303. First step: make the order a parameter of `search/search.py`.
   Blocker: guards and split-ideal accounting must be re-established per order.

## Provenance

Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Live inputs (pinned in
[SOURCES.json](SOURCES.json)):
`research/r439-bsection-stars-seed01/candidate.json.gz` (sha256 `b452d2c2...45ee`),
`research/e8-bit-carrier-skeleton/code/bit/export_records.py` (`8a599960...0eb3`),
`research/e8-bit-p111-tuned/code/xcheck_p.py` (`af3decc8...d80e`). Adapted code:
PR2407 head `4944211cee666eb8631b990cb0f33cfa68666485`,
`research/r439-single-copy-interleaving/verify.py` (Git blob `07724f60d7e8`),
Apache-2.0. Predecessor heads (all open/unmerged): PR2115 `b56dceff`, PR2279
`81fed971`, PR2356 `8ffeca2c`, PR2407 `4944211c`, PR2421 `71d10b28`,
PR2437 `4ac2b382`.

## Credit

Predecessors: Ross Richardson (PR2407: single-copy interleaving, verifier
adapted here), starship-s (PR2421, native replay of PR2407), Charles Bethin
(PR2279: split-ideal optimum 94), Ross Richardson again for concurrent
PR2437 (ideal whole-call hosting of the PR2407 single-window stream; related,
not covering this stream), Sricharan Vagvala (PR2356: suffix/interleaving
method, column-7 five-tap minimum), Sagar Thakrar (PR1062 R439 word, PR2115
deferred split), Gareth Davidson (PR2373), DreamingOfClouds and eumemic
(PR589/PR555), and the retained exporter/checker lineage (Dylan Crow, eumemic).

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
