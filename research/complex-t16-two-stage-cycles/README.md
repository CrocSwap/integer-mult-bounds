# T16 owner map from a class-level re-solve and guided realisation on the selected supplier, with a proved packing ceiling

On the unchanged selected PR1094 supplier, this owner map admits conditional
**κ = 0.001673614205725695** (conservative surcharge 0.001673614202872892).
That is **+5.7035e-4 relative** (+9.540e-7) over the selected record
0.001672660197076918 and +9.334e-7 over open PR1407 (0.001672680818492982).
Against this PR's earlier versions it is +9.297e-7 over the first
(0.001672684510394236), +9.113e-7 over the second (0.001672702955495933),
+5.600e-7 over the third (0.001673054161426948) and +2.723e-7 (+1.6271e-4
relative) over the fourth (0.001673341928508063). The local gauge44 word, helper
widths, 144-call order, windows, physical stock, native supplier and PR589 bit
supplier are unchanged. The unchanged PR1087 strict replay passes.

This version also adds a **proved packing ceiling** (`PROOF.md`,
`ceiling_bound.py`): on this supplier no legal owner map can have more than
4,887 completely idle cap-48 bins (this map: 4,880; selected: 4,866), and the
search surrogate `Σ f ln f` is at most 908,139.013 (this map: 907,271.883).
This bounds the surrogate, not κ.

**Scope.** This is a conditional T16 packing on the same supplier, with no new
mechanism. The map is stated and verified **only against the merged selected
PR1094 map**: `DIFF-vs-selected.json` changes @CHG@ of its 69,120 rows
(@REL@ helpers move to another bin; @OFF@ more rows only change their slice
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
4. κ 0.001673341928508063: version 3's map continued with an evacuation LNS
   neighbourhood (nearly empty bins re-packed), then the same min-diff
   (1,638 changed rows, 1,415 relocations).
5. This version, κ 0.001673614205725695: version 4's map improved by
   class-level re-solves of a window model warm-started from the current map,
   each realised on concrete bins by a guided CP-SAT neighbourhood, then the
   same class-level min-diff re-assignment. The idle profile still majorizes the
   selected one (`PROOF.md`). New: a proved packing ceiling.

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

Steps 1–3 are version 3's search, steps 4–5 version 4's, and steps 6–7 are
new in this version.
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
6. **Class-level re-solve** (`winlp.py`, new). The window model of the global
   repack, as an IP over (capacity, window) classes: pattern counts per class,
   flows of each (call, width) to each class, time and width balance, and
   aggregate R4 cuts (for each group of classes that share physical families
   and each call, at most one helper per family). A full solve gives a target
   class solution. Each step then re-solves the model warm-started from the
   current map, frees only a random subset of 12–24 classes drawn from those
   that differ from the target (all others fixed to the current map), and
   requires a minimum surrogate gain (`GAIN`) at a penalty per unit of change
   (`PEN`).
7. **Guided realisation** (`lns2.py`, mode `guide`, new). The class solution
   of step 6 is realised on concrete bins by a CP-SAT neighbourhood made of
   the bins holding helpers whose class (call, width) count must drop, plus
   the bins whose pattern count must drop. CP-SAT maximises the surrogate
   exactly over that neighbourhood, and the result is kept only if the exact κ
   rises. `gloop.sh` repeats this toward one fixed target; `sloop.sh` loops
   steps 6–7. Two short `loopy.sh` runs first took version 4's map to
   0.001673344533458160 (not strict-replayed); strict-replayed checkpoints
   from there:
   0.001673373170972473 (`gloop.sh`), 0.001673393061983855,
   0.001673535326871893 and 0.001673614205725695 (`sloop.sh`, two loops whose
   best maps were synchronised; surrogate 907,271.88).

The search was **stopped while still improving** (the class-level loop was
still finding gains when it was stopped). It is a finite heuristic, not an
optimum. The
session's loop scripts compared κ strings in one place; `lns.py` and the loops
now compare κ as `Decimal` (the native assembler can drop trailing zeros, e.g.
`0.0016732131191366` for `0.001673213119136600`).

**Proved ceiling.** The earlier text here reported a heuristic ceiling of
"about 908.1k surrogate units" from `winbound.py` that could not be reproduced.
This version replaces it with a proof (`PROOF.md`, "A proved packing ceiling";
checked by `ceiling_bound.py`, which `verify.py` runs). The proof uses integer
weights `a(w) = ⌊7w/9⌋` per helper and `A(c) = ⌊7c/9⌋` per bin. Every bin's
helpers weigh at most `A(c)`, and total bin weight minus total helper weight
is 180,832 for every map. So **at most 4,887 cap-48 bins can be empty**, and
an exact knapsack over the per-bin slack gives **`Σ f ln f ≤ 4,887 · 48 ln 48 +
17 ln 17 = 908,139.013`** for every legal map. This map is at 4,880 empty cap-48
bins and 907,271.883. The bound is on the surrogate, not on κ. Pricing the
bound-attaining idle multiset `{1:2431, 17:1, 48:4887}` with the pinned
engines gives κ 0.001674088611862992 (`check.py`). This is only an indication
of the remaining room (4.744e-7 above this map); it is not a κ bound.
`winbound.py` and `aggbound.py` remain as search tools only.

### Min-diff re-assignment

Given the selected map A and the search output F, find a legal map with F's
idle profile (hence F's κ) that keeps as many placements of A as possible. A
placement is `(bin, call, width)`, since helpers of one call and width are
interchangeable. The raw search output F relocates 63,109 rows against A
(66,449 changed rows). This version reuses the class-level tools of versions 3
and 4:

1. `mindiff_cls1.py` (HiGHS, 1,800 s, warm-started from F): a class-level MIP
   over pattern counts and flows, with the idle profile fixed to F's,
   maximising the flow of A's (class, call, width) placements that stays in
   place. It stopped at the time limit with 67,539 placements' worth of flow
   (1,581 relocations) and 58 classes changed. The dual bound implies at least
   1,548 relocations for any legal map with F's profile once the tie-break
   weight (at most 0.001 per bin, 32,256 bins) is discounted. That is a
   solver-reported bound, not an independently checked certificate.
2. `mindiff_cls2.py` (CP-SAT pass, then HiGHS pass, per changed class)
   realised 56 of the 58 classes. Two stage-1 class solutions could not be
   realised, because stage 1 does not see that several helpers of one width in
   a bin need distinct calls:
   - Class 9 (capacity 16, calls 0–8) had the same unrealisable pattern as in
     version 4: fourteen bins with four width-4 helpers, while only calls 5, 6
     and 8 have more than two width-4 helpers.
   - Class 25 (capacity 32, calls 51–112) needed five (7, 7, 9, 9) bins and
     one (7, 8, 8, 9) bin. The class's 7s come from calls 92 (6), 98 (4) and
     99 (1), and its only 8s from calls 92 and 102. So the (7, 8, 8, 9) bin's 7
     is not from call 92. That leaves at most four 7-pairs with distinct calls,
     not five.

   Both patterns were forbidden with `BAN`. Stage 1 was re-solved twice with
   `KEEP` (all other classes fixed to the previous stage-1 solution) and
   `FREE` (the classes sharing calls with the banned one): first class 9 with
   13 overlapping cap-16 classes (optimal at once, same 1,581), then class 25
   with 20 overlapping cap-32 classes (optimal, 1,583). `mindiff_reuse.py`
   kept the class results that did not change. All 58 classes were realised;
   the merge gives 2,210 relocations.
3. `mindiff_lns.py` (two seeds): 2,210 → 2,183. One round of
   `mindiff_lns2.py` (two seeds, the better one kept): 2,170. It was stopped
   at the two-hour min-diff budget. The stage-1 solve took half of that
   budget, and the LNS was gaining only a few relocations per round.
4. `realize.py` keeps A's helper labels and offsets where possible:
   **2,170 relocations and 367 offset-only changes (2,537 changed rows)**,
   against 63,109 relocations in the raw search output.

This is a heuristic too. The relocation count is not proven minimal. Most of
the gap to the class-level count (1,583) comes from realising the class
solutions on concrete bins (stage 2 loses about 630 placements), so stage 1
is a loose relaxation here. The diff is larger than version 4's (1,415)
because the new profile is further from the selected one (14 more empty cap-48
bins instead of 8, 270 fewer residuals 3 instead of 205).

## Exact profile change

| | idle remainder profile | κ |
|---|---|---|
| selected PR1094 | `{1:2276, 3:377, 7:7, 48:4866}` | 0.001672660197076918 |
| PR1407 | `{1:2277, 3:377, 16:3, 48:4866}` | 0.001672680818492982 |
| version 1 of this PR | `{1:2278, 3:374, 8:1, 16:3, 48:4866}` | 0.001672684510394236 |
| version 2 of this PR | `{1:2280, 2:1, 3:363, 7:3, 16:4, 48:4866}` | 0.001672702955495933 |
| version 3 of this PR | `{1:2346, 2:3, 3:154, 5:9, 7:36, 8:2, 16:7, 28:1, 39:1, 40:1, 41:2, 44:41, 48:4829}` | 0.001673054161426948 |
| version 4 of this PR | `{1:2355, 2:2, 3:172, 7:3, 16:11, 48:4874}` | 0.001673341928508063 |
| this package | `{1:2392, 2:8, 3:107, 4:1, 7:5, 16:1, 48:4880}` | 0.001673614205725695 |
| proved bound (not a map) | at most 4,887 empty cap-48 bins; `Σ f ln f ≤ 908,139.013` | — |

Compared with the selected map, the idle profile changes by
`{1:+116, 2:+8, 3:-270, 4:+1, 7:-2, 16:+1, 48:+14}`. Fourteen more bins are
completely idle than in the selected map (version 4: eight), 270 residuals 3
and two residuals 7 are gone. The full paid profile is
`{1:349720, 2:60200, 3:62315, 4:20449, 5:11808, 7:5, 8:1152, 16:1, 48:4880}`.
Rank mass is still 1,041,408 and the deficit is still 5,120. Cross-replica
helper roles go from 57,480 to 57,420. With equal residual totals (237,024), the
new residual vector majorizes the selected one, so Karamata's inequality gives
the strict decrease of the complex moment for any strictly concave
per-residual weight. `check.py` asserts the majorization mechanically, and the
value of κ still comes from the exact engines and the strict replay
(`PROOF.md`).

`SPEC.expected.actual_73column_sigmas` is **10011** (selected: 10002; the raw
search output had 10564). This value is not a tuning knob. The strict audit
counts the distinct orthogonal 73-column charts that the realized owner
chronology uses. `assemble.py` pins that count against SPEC exactly, and an
`understated_actual_chart_types` mutation control guards it. It depends on the
map, so the strict verifier recomputes it on every replay.

Fraction of the complex endpoint gap: with the PR1240 local-word ceiling
endpoint a_hi = 0.001690054109089, this map realises **6.560%** of the complex
endpoint gap (version 4: 4.688%; version 3: 2.709%; version 2: 0.294%;
version 1: 0.167%; PR1407: 0.142%). The idle multiset that attains the proved
surrogate bound would, if a legal map realised it, price at κ
0.001674088611862992, or 9.822% of that gap. That number is indicative, not a
bound (`PROOF.md`).

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
   69/12/6/15 rejecting controls, and requires `actual_73_axis_charts` = 10011.
4. It runs `check.py`, an independent check adapted from the session's
   `checkmap.py`. That check uses the seed67 owner auditor (R1–R7, X1, X2 and
   11 controls) on both the selected and the candidate map. It also prices with
   the pinned exact engines and runs the PR1069 sweep on the strict replay's
   lowers. It asserts that the candidate's idle residual vector strictly
   majorizes the selected one (equal totals, partial sums of the sorted,
   zero-padded vectors), and `verify.py` requires that result. All κ decimals
   are compared as `Decimal`, never as strings, because the native assembler
   drops trailing zeros.
   It also prices the idle multiset that attains the proved surrogate bound
   (`indicative_ceiling_price`, indicative only).
5. It runs `ceiling_bound.py`, the proved packing ceiling (`PROOF.md`): it
   derives the bins and helper widths from `data/`, checks Theorems 1–3 with
   exact integer arithmetic (standard library only, under a second), and
   reports this map's empty cap-48 bins and surrogate against the bound.

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
stage2() {   # stage-1 json, cache dir, CP-SAT limit, HiGHS limit; the two halves ran in parallel
  for h in 0/2 1/2; do
    $PY --with ortools python -I $S/mindiff_cls2.py $S $1 $2 $3 $4 $h cp
    $PY $HI python -I $S/mindiff_cls2.py $S $1 $2 $3 $4 $h hi
  done; }
$PY $HI python -I $S/mindiff_cls1.py $S $F $W/c1.json 1800 $F       # time limit: 1,581 (bound: >= 1,548)
stage2 $W/c1.json $W/cache 60 150                                    # classes 9 and 25 not realised
# (class 25 alone with 300 s / 900 s limits: no solution; it is infeasible, see above)
BAN='[[9,[4,0,0,0,0]]]' KEEP=$W/c1.json FREE='[9,0,18,27,36,90,99,108,117,126,135,45,54,63]' \
  $PY $HI python -I $S/mindiff_cls1.py $S $F $W/c1b.json 900          # optimal, 1,581
python3 $S/mindiff_reuse.py $W/c1.json $W/c1b.json $W/cache $W/cache2  # 53 of 58 reused
stage2 <c1b.json with "changed" restricted to [0,9,18,27]> $W/cache2 60 300   # realised
BAN='[[9,[4,0,0,0,0]],[25,[0,0,1,2,1]]]' KEEP=$W/c1b.json \
  FREE='[25,7,16,34,38,43,52,56,61,65,79,88,97,106,110,115,119,124,128,133,137]' \
  $PY $HI python -I $S/mindiff_cls1.py $S $F $W/c1c.json 600          # optimal, 1,583
python3 $S/mindiff_reuse.py $W/c1b.json $W/c1c.json $W/cache2 $W/cache3   # 55 of 58 reused
stage2 $W/c1c.json $W/cache3 60 300                                  # classes 16, 25, 52: realised
$PY python -I $S/mindiff_cls2.py $S $W/c1c.json $W/cache3 $W/cls.json merge   # 2,210 relocations
$PY $HI python -I $S/mindiff_lns.py $S $F $W/cls.json $W/l1.json 40 1 300 30      # 2,183 (seed 2: 2,183)
$PY $HI python -I $S/mindiff_lns2.py $S $W/l1.json $W/l2.json 20 12 80 60         # 2,170 (seed 11: 2,176)
$PY python -I $S/realize.py $S $W/l2.json $W/OWNERS.json.gz
$PY python -I $S/buildcand.py $S $W/OWNERS.json.gz $W/pkg 10011   # count read from the native audit
```

The search steps of this version ran as follows (bash `$RANDOM` seeds in
places, wall-clock limits, and two loops whose best maps were copied between
them by hand-run sync steps, so not replayable bit for bit; which full-model
target file each loop used was not logged):

```sh
S=research/complex-t16-two-stage-cycles/search
PY="uv run -q --no-project --python 3.12 --with numpy --with scipy --with ortools"
# full class-level window + R4 model, hinted with a current map: a target class solution
$PY python -I $S/winlp.py $S <map> ip <TL> 1 2 <target.json>
# guided realisation toward one target (first checkpoint), then the re-solve loop
RUN=<memory cap prefix> $S/gloop.sh <dir> <version 4 map> <target.json> 2 <seed> <iters>
RUN=<memory cap prefix> $S/sloop.sh <dir> <best so far> <target.json> <seed> <iters>
```

Version 4's search steps (evacuation solve and `loopy.sh`) are described in
`SEARCH.json` (`fourth_version`).

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
  is to rerun `search/sloop.sh` from `data/OWNERS.json.gz` toward a full
  `winlp.py` target under a memory cap, strict-replay each new best, and rerun
  the min-diff step on the result. The proved ceiling leaves at most seven more
  empty cap-48 bins and 867 surrogate units.
- **A κ ceiling for owner packing.** The proved ceiling bounds the surrogate
  (908,139.013) and the number of empty cap-48 bins (4,887), not κ. Pricing
  the bound-attaining idle multiset gives κ 0.001674088611862992, but that is
  not a bound. A κ bound needs either a majorization argument (does the
  bound-attaining multiset majorize every attainable idle vector?) or the
  relaxation stated in the exact per-residual cost.
- **Is the ceiling attainable?** The window + R4 class model reaches it
  (solver-reported), but no concrete map is known with more than 4,880 empty
  cap-48 bins.
- **A smaller diff.** The min-diff map (2,170 relocations) is not proven
  minimal for its profile. The solver-reported relaxation bound is 1,548, and
  the stage-1 solution itself needs 1,583. Distinct-call (Gale–Ryser)
  constraints in `mindiff_cls1.py` would stop stage 1 from proposing
  unrealisable class patterns; this version needed `BAN` for two classes.
  Stage-2 realisation that also trades placements between classes, and longer
  `mindiff_lns2.py` runs, may shrink it.
