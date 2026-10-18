# T16 owner map from a global class-level repack and evacuation LNS on the selected supplier

On the unchanged selected PR1094 supplier, this owner map admits conditional
**κ = 0.001673341928508063** (conservative surcharge 0.001673341925655596).
That is **+4.0757e-4 relative** (+6.817e-7) over the selected record
0.001672660197076918 and +6.611e-7 over open PR1407 (0.001672680818492982).
Against this PR's earlier versions it is +6.574e-7 over the first
(0.001672684510394236), +6.390e-7 over the second (0.001672702955495933) and
+2.878e-7 (+1.7200e-4 relative) over the third (0.001673054161426948). The
local gauge44 word, helper widths, 144-call order, windows, physical stock,
native supplier and PR589 bit supplier are unchanged. The unchanged PR1087
strict replay passes.

**Scope.** This is a conditional T16 packing on the same supplier, with no new
mechanism. The map is stated and verified **only against the merged selected
PR1094 map**: `DIFF-vs-selected.json` changes 1,638 of its 69,120 rows
(1,415 helpers move to another bin; 223 more rows only change their slice
offset). It depends on no open PR. It claims no packing optimum and no
unconditional multiplication theorem.

## Versions of this PR

1. κ 0.001672684510394236: two-stage ejection cycles on PR1407's map (a
   23-row successor of PR1407).
2. κ 0.001672702955495933: depth-8 ejection cycles alternated with CP-SAT
   large-neighbourhood re-assignments, then a min-diff re-assignment to 70
   changed rows against the selected map.
3. κ 0.001673054161426948: a global class-level repack followed by the same
   cycle/LNS loop, then a class-level min-diff re-assignment (1,661 changed
   rows, 1,435 relocations).
4. This version, κ 0.001673341928508063: version 3's shipped map continued
   with a new LNS neighbourhood (evacuation of nearly empty bins), then the
   same class-level min-diff re-assignment. Unlike version 3, the idle profile
   again majorizes the selected one (`PROOF.md`).

## Construction

A bin is `(owner replica, idle child, port)`. Its capacity and borrowing window
come from the selected PR1094 plan. A placement puts one whole helper role of
one call into a bin. It must fit the free capacity, the call must lie strictly
inside the bin's window, and the bin's physical family must be unused by every
other helper in that call. No helper is split and no call is reordered.
Helpers of the same call and width are interchangeable under these rules.

### Why a global repack

Version 2's loop (ejection cycles plus CP-SAT LNS) had slowed to steps of about
1e-9 in κ. Three observations led to a global model instead:

* κ is, to good accuracy, a linear function of the surrogate `Σ f ln f` over
  the idle fragments (free capacities `f`), so the surrogate is a usable
  objective for a global model; only the exact engines decide acceptance.
* Inside one physical family the bins' windows never overlap. So the family
  rule (R4) reduces to "at most one helper per bin per call", and two bins with
  the same capacity and the same set of allowed calls (a *class*: 144 classes
  of 224 bins each) are interchangeable.
* The problem therefore becomes a class-level pattern/flow model: how many bins
  of each class get each width pattern, and how many helpers of each
  (call, width) each class hosts.

### κ search (`search/`, `SEARCH.json`)

Steps 1–3 are version 3's search; steps 4–5 are new in this version.
Starting from version 2's raw search output (content `a7e8f0ca…`):

1. **Stage 1** (`glob.py`): CP-SAT over pattern counts and flows per class,
   with per-(class, call) Hall constraints (a call can use at most as many bins
   of a class as there are bins whose pattern holds the widths it needs) and
   Gale–Ryser-style constraints for several helpers of one width in a bin
   (they need distinct calls), maximising the surrogate. Best stage 1:
   906,706 surrogate units (the start map had 905,605).
2. **Stage 2** (`glob5.py`): per class and width, a max-flow from calls to
   bins realises the stage-1 solution with distinct calls per bin. Stage 1 is a
   relaxation, so 80 helpers stayed unplaced; they were inserted greedily where
   they cost the least surrogate. The realised map had κ 0.001672432283943020,
   lower than the start but with a very different profile.
3. **Loop** (`loopx.sh`): chain2 ejection cycles alternated with CP-SAT LNS
   plateau steps (`lns.py`, now with a worker-count setting `NW` and an `f3`
   neighbourhood mode), keeping the best map by exact κ. Strict-replayed
   checkpoints: κ 0.001672894024167899 and 0.001673054161426948 (version 3).
4. **Evacuation neighbourhood** (`lns.py`, mode `evac`, size `NB`). On
   version 3's map, many cap-48 bins held only a few small helpers. The new
   neighbourhood picks 1–3 such stranded bins (used ≤ 20), bins with spare
   room and full bins whose windows contain some of the stranded helpers'
   calls, and a few empty bins; it frees all their helpers and re-packs them
   exactly with CP-SAT. A single 102-bin solve from version 3's map emptied
   35 cap-48 bins (+291 surrogate units, 906,247 → 906,538) and gave
   κ 0.001673213119136600.
5. **Loop with evacuation** (`loopy.sh`): `loopx.sh` with `evac` in the mode
   mix. Strict-replayed checkpoints: 0.001673243717212927,
   0.001673272876788591, 0.001673312438393585, 0.001673322090452138 and
   0.001673341928508063 (surrogate 906,774).

The search was **stopped while still improving** (near the end it still found
gains every 10–20 minutes). It is a finite heuristic, not an optimum. The
session's loop scripts compared κ strings in one place; `lns.py` and the loops
now compare κ as `Decimal` (the native assembler can drop trailing zeros, e.g.
`0.0016732131191366` for `0.001673213119136600`).

**Heuristic ceiling (not a proof).** `winbound.py` groups bins by class and
drops the per-bin constraints. In the session, this relaxation gave an
optimistic ceiling of about 908.1k surrogate units, which by the near-linear
κ–surrogate relation corresponds to roughly κ ≈ 0.0016741 (this map: about
906.8k). This number is **not certified**: the κ–surrogate relation is only
approximate, and a rerun of the shipped script for the third version (one
CP-SAT worker, 900 s) did not close its bound (it stopped at 983k). It is
reported only as a rough sense of how much room the surrogate may leave;
`aggbound.py` is a coarser variant that ignores calls and windows entirely.

### Min-diff re-assignment

Given the selected map A and the search output F, find a legal map with F's
idle profile (hence F's κ) that keeps as many placements of A as possible. A
placement is `(bin, call, width)`, since helpers of one call and width are
interchangeable. The raw search output F relocates 62,678 rows against A
(66,211 changed rows). This version reuses version 3's class-level tools:

1. `mindiff_cls1.py` (HiGHS): a class-level MIP over the same pattern counts
   and flows as the repack, with the idle profile fixed to F's, maximising the
   flow of A's (class, call, width) placements that stays in place. HiGHS
   solved it to optimality in 247 s: 68,087 placements' worth of flow (1,033
   relocations) at the tie-broken optimum, 48 classes changed. Every legal map
   with F's profile is feasible for this relaxation, so the reported dual bound
   implies at least 1,002 relocations for any such map once the tie-break
   weight (at most 0.001 per bin, 32,256 bins) is discounted. That is a
   solver-reported bound, not an independently checked certificate.
2. `mindiff_cls2.py` (CP-SAT pass, then HiGHS pass, per changed class):
   realise each class's stage-1 solution on its 224 bins, keeping as many of
   A's placements as possible; unchanged classes keep A. Stage 1 is a
   relaxation, and class 9 (capacity 16) was proven infeasible: its stage-1
   solution used eleven bins holding four width-4 helpers each, which need
   four distinct calls per bin, while the class's calls other than 5, 6 and 8
   have only four width-4 helpers between them (so at most four such bins).
   Fixing class 9 to A, as version 3 did for its unrealisable classes, makes
   stage 1 infeasible here (A's class 9 has six bins with residual 7; the
   target profile has only three), and fixing it to F's class values raises
   the stage-1 optimum from 1,033 to 1,456 relocations. Instead, a new `BAN`
   option of `mindiff_cls1.py` forbids that one pattern in class 9; stage 1
   re-solved to the same optimum (1,033), and all 47 changed classes were
   realised (5 class results reused with `mindiff_reuse.py`). Result: 1,518
   relocations.
3. `mindiff_lns.py` (version 2's LNS, F = the raw search output) and
   `mindiff_lns2.py`: 1,518 → 1,496 (`mindiff_lns.py`, the better of seeds 1
   and 2), then rounds of `mindiff_lns2.py` (any legal
   placement inside the neighbourhood, two seeds per round, the better one
   kept): 1,478, 1,459, 1,435, 1,415. It was stopped at the two-hour min-diff
   budget while still gaining about 20 relocations per round.
4. `realize.py` keeps A's helper labels and offsets where possible:
   **1,415 relocations and 223 offset-only changes (1,638 changed rows)**,
   against 62,678 relocations in the raw search output.

This is a heuristic too. The relocation count is not proven minimal; the gap
to the solver-reported relaxation bound (1,002) is large because stage 1 is a
loose relaxation of the bin-level problem.

## Exact profile change

| | idle remainder profile | κ |
|---|---|---|
| selected PR1094 | `{1:2276, 3:377, 7:7, 48:4866}` | 0.001672660197076918 |
| PR1407 | `{1:2277, 3:377, 16:3, 48:4866}` | 0.001672680818492982 |
| version 1 of this PR | `{1:2278, 3:374, 8:1, 16:3, 48:4866}` | 0.001672684510394236 |
| version 2 of this PR | `{1:2280, 2:1, 3:363, 7:3, 16:4, 48:4866}` | 0.001672702955495933 |
| version 3 of this PR | `{1:2346, 2:3, 3:154, 5:9, 7:36, 8:2, 16:7, 28:1, 39:1, 40:1, 41:2, 44:41, 48:4829}` | 0.001673054161426948 |
| this package | `{1:2355, 2:2, 3:172, 7:3, 16:11, 48:4874}` | 0.001673341928508063 |

Compared with the selected map, the idle profile changes by
`{1:+79, 2:+2, 3:-205, 7:-4, 16:+11, 48:+8}`. Eight more bins are completely
idle than in the selected map (version 3 had 37 fewer), 205 residuals 3 and
four residuals 7 are gone, and eleven residuals 16 appear. The full paid
profile is
`{1:349683, 2:60194, 3:62380, 4:20448, 5:11808, 7:3, 8:1152, 16:11, 48:4874}`.
Rank mass is still 1,041,408 and the deficit is still 5,120. Cross-replica
helper roles go from 57,480 to 57,419. With equal residual totals (237,024), the
new residual vector majorizes the selected one again (version 3's did not), so
Karamata's inequality gives the strict decrease of the complex moment for any
strictly concave per-residual weight; `check.py` asserts the majorization
mechanically, and the value of κ still comes from the exact engines and the
strict replay (`PROOF.md`).

`SPEC.expected.actual_73column_sigmas` is **10006** (selected: 10002; the raw
search output had 10649). This value is not a tuning knob. The strict audit
counts the distinct orthogonal 73-column charts that the realized owner
chronology uses. `assemble.py` pins that count against SPEC exactly, and an
`understated_actual_chart_types` mutation control guards it. It depends on the
map, so the strict verifier recomputes it on every replay.

Packing ceiling: with the PR1240 local-word ceiling endpoint
a_hi = 0.001690054109089, this map realises **4.688%** of the complex endpoint
gap (version 3: 2.709%; version 2: 0.294%; version 1: 0.167%; PR1407: 0.142%).

## Reproduce

Run from a complete checkout at or after base `0fdd7d82`, with Python 3.12 and
the standard library only:

```sh
python3 scripts/research_package.py --package research/complex-t16-two-stage-cycles --check-only
python3.12 scripts/research_package.py --package research/complex-t16-two-stage-cycles
# or directly, keeping the work tree:
python3.12 -I -B research/complex-t16-two-stage-cycles/verify.py --work /abs/fresh/dir
```

`verify.py` follows the PR2077 package (`research/complex-t16-vacancy-chain`):

1. It checks the 287 pinned inputs (`INPUTS.json`) and the package inventory
   (`MANIFEST.json`).
2. `build.py` applies `DIFF-vs-selected.json` to the merged selected PR1094
   map. It checks that only owner fields change, counts the changed and
   relocated rows, recomputes the idle histogram with its own packing checker,
   and regenerates `PLAN.json` and `SPEC.json` byte for byte.
   `OWNERS.json.gz` is compared on its decoded payload.
3. It restores the PR1087 archive (`upstream1087.tar.gz`), checks all 179
   archived files, overlays only the three data files, and extracts the selected
   R480 gauge44 provider from `selected-replay.tar.gz` (`LOCAL-PINS.json`). It
   then runs the unchanged `verify_t16.py`, which covers all 11 stages and
   69/12/6/15 rejecting controls, and requires `actual_73_axis_charts` = 10006.
4. It runs `check.py`, an independent check adapted from the session's
   `checkmap.py`. That check uses the seed67 owner auditor (R1–R7, X1, X2 and
   11 controls) on both the selected and the candidate map. It also prices with
   the pinned exact engines and runs the PR1069 sweep on the strict replay's
   lowers. It asserts that the candidate's idle residual vector strictly
   majorizes the selected one (equal totals, partial sums of the sorted,
   zero-padded vectors), and `verify.py` requires that result. All κ decimals
   are compared as `Decimal`, never as strings, because the native assembler
   drops trailing zeros.

The full replay takes about 60 s and stays under 1 GB of RAM. `evidence/`
holds the receipts of the local run.

The search needs third-party packages and proves nothing; `SEARCH.json` records
the commands and checkpoints. Solver time limits are wall clock and some seeds
came from bash `$RANDOM`, so a rerun can land on a different map of similar
quality. The min-diff step, from the search output F (content SHA256 in
`SEARCH.json`), ran as follows:

```sh
S=research/complex-t16-two-stage-cycles/search; W=<work dir>; F=<search output F>
PY="uv run -q --no-project --python 3.12"; HI="--with scipy --with highspy"
stage2() {   # stage-1 json, cache dir; the two halves ran in parallel
  for h in 0/2 1/2; do
    $PY --with ortools python -I $S/mindiff_cls2.py $S $1 $2 60 150 $h cp
    $PY $HI python -I $S/mindiff_cls2.py $S $1 $2 60 150 $h hi
  done; }
$PY $HI python -I $S/mindiff_cls1.py $S $F $W/c1.json 1800 $F            # optimal, 247 s, 1,033
stage2 $W/c1.json $W/cache                                               # class 9 infeasible
BAN='[[9,[4,0,0,0,0]]]' $PY $HI python -I $S/mindiff_cls1.py $S $F $W/c1c.json 1200 $F   # optimal, 1,033
python3 $S/mindiff_reuse.py $W/c1.json $W/c1c.json $W/cache $W/cache2    # 5 of 47 reused
stage2 $W/c1c.json $W/cache2                                             # all realised
$PY python -I $S/mindiff_cls2.py $S $W/c1c.json $W/cache2 $W/cls.json merge   # 1,518 relocations
$PY $HI python -I $S/mindiff_lns.py $S $F $W/cls.json $W/l1.json 40 2 300 30     # 1,496 (seed 1: 1,501)
$PY $HI python -I $S/mindiff_lns2.py $S $W/l1.json $W/l2.json 20 11 80 60         # 1,478
$PY $HI python -I $S/mindiff_lns2.py $S $W/l2.json $W/l3.json 25 13 80 60         # 1,459 (seed 12: 1,468)
$PY $HI python -I $S/mindiff_lns2.py $S $W/l3.json $W/l4.json 20 22 80 60         # 1,435 (seed 21: 1,446)
$PY $HI python -I $S/mindiff_lns2.py $S $W/l4.json $W/l5.json 18 32 80 60         # 1,415 (seed 31: 1,419)
$PY python -I $S/realize.py $S $W/l5.json $W/OWNERS.json.gz
$PY python -I $S/buildcand.py $S $W/OWNERS.json.gz $W/pkg 10006
```

The search steps of this version ran as follows (bash `$RANDOM` seeds, so
not replayable bit for bit; the single evacuation solve's exact seed and `NB`
were not logged):

```sh
S=research/complex-t16-two-stage-cycles/search
PY="uv run -q --no-project --python 3.12 --with numpy --with ortools"
# one evacuation solve from version 3's map (the session's solve had 102 bins)
NB=<n> NW=2 $PY python -I $S/lns.py $S <version 3 data/OWNERS.json.gz> <out>/t 1 <seed> 60 evac
# then the loop, restarted from each strict-replayed best
RUN=<memory cap prefix> NB=200 $S/loopy.sh <dir> <best so far> 2 <seed>
```

## Assumptions retained

The all-size compiler, common-label/mutable-source realization, whole-call
hosting, precision/tape, exact recovery, analytic transfer and PR589 bit H1–H5
assumptions of the selected PR1094 record remain. The native local receipts are
reused with source binding; the ancestry is not rebuilt cold. Hosted CI and
maintainer acceptance are separate.

## Credit

- **pai-scaffolde, PR1407**: the search line started from its owner map
  (through the first version of this package), and this package reuses its
  whole-helper neutral-path semantics and all-input argument. The final map is
  no longer a row-for-row descendant of PR1407's map, but the line of work is
  its.
- **George Lydakis (lydakis), PR2077** contributed the vacancy-chain idea of
  propagating free capacity through occupied bins, the ancestor of the
  ejection cycles. Its four literal moves do not compose with PR1407 (all 15
  subsets are illegal on PR1407's map; `search/compose.py`).
- **Rohan Arun and Jeremy Kothe**: the PR1050–PR1094 owner-packing line and the
  selected PR1094 supplier and map.
- **Josie Elliston**: the seed67 owner auditor (PR1091), used in `check.py` and
  in the search's legality oracle.
- **Sagar Thakrar**: the independent pricing sweep (PR1069), used in `check.py`.
- The strict verifier, exact engines and their predecessors keep their original
  authors and notices, which are unchanged.

Prepared by Philippe Van Velzen with substantial Claude Code (Claude Opus 5.5)
assistance. No independent human review is claimed. New material is Apache-2.0.

## Open next questions

The structured versions are in `TASK.json`:

- **Continue the κ search.** It stopped while still improving. The first step
  is to rerun `search/loopy.sh` from `data/OWNERS.json.gz` under a memory cap
  (or a new global repack from it), strict-replay each new best, and rerun the
  min-diff step on the result.
- **A certified packing bound.** The class-level relaxation (`winbound.py`)
  gives only an uncertified surrogate ceiling. A bound stated directly in the
  exact cost (or a proven κ–surrogate inequality) would show how much κ owner
  packing can still give on this supplier.
- **A smaller diff.** The min-diff map (1,415 relocations) is not proven
  minimal for its profile; the solver-reported relaxation bound is 1,002, and
  the LNS polish was still improving when stopped. Longer `mindiff_lns2.py`
  runs, or Gale–Ryser constraints in `mindiff_cls1.py` so that stage 1 stops
  proposing unrealisable class patterns, may shrink it.
