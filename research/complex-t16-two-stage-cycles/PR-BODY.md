# Record candidate: T16 owner map from class-level re-solve and guided realisation on the selected supplier (κ=0.001673614205725695), with a proved packing ceiling

## Contribution

This PR adds `research/complex-t16-two-stage-cycles`, a registered research
package. It is a conditional T16 owner map on the **unchanged selected PR1094
supplier**, with no new mechanism, plus a proved packing ceiling for that
supplier.

- **κ = 0.001673614205725695** (conservative 0.001673614202872892).
- That is **+5.7035e-4 relative** (+9.540e-7) over the selected record
  (0.001672660197076918) and +9.334e-7 over open PR1407
  (0.001672680818492982). Over this PR's earlier versions it is +9.297e-7
  (first, 0.001672684510394236), +9.113e-7 (second, 0.001672702955495933),
  +5.600e-7 (third, 0.001673054161426948) and +2.723e-7, or +1.6271e-4
  relative (fourth, 0.001673341928508063).
- Idle remainders go from `{1:2276, 3:377, 7:7, 48:4866}` (selected) to
  `{1:2392, 2:8, 3:107, 4:1, 7:5, 16:1, 48:4880}`. Rank mass 1,041,408 and
  deficit 5,120 are unchanged. The new residual vector majorizes the selected
  one (equal totals 237,024; `check.py` asserts the partial-sum comparison), so
  by Karamata's inequality the complex moment strictly decreases for any
  strictly concave per-residual weight. The value of κ comes from the pinned
  exact engines and the strict replay.
- **Standalone diff against the selected map:** `DIFF-vs-selected.json`
  changes 2,537 of 69,120 rows: 2,170 helpers move to another bin and 367 rows
  only change their slice offset. Widths, call order, windows and the local and
  bit suppliers are unchanged. No open PR is needed.
- The unchanged PR1087 strict replay passes all 11 stages, with controls
  69/12/6/15. `actual_73column_sigmas` is 10011: the strict audit recomputes
  this chart count for the realized map and `assemble.py` pins it.
- The seed67 owner auditor passes R1–R7, X1, X2 and its 11 controls. Pricing
  with the pinned exact engines and the PR1069 sweep agree with the replay.

With the PR1240 local-word ceiling endpoint a_hi = 0.001690054109089, this map
realises 6.560% of the complex endpoint gap (fourth version: 4.688%; third:
2.709%; second: 0.294%; first: 0.167%; PR1407: 0.142%).

It claims no packing optimum and no unconditional theorem. All PR1094
inherited assumptions remain.

## Proved packing ceiling

`PROOF.md` ("A proved packing ceiling") and `ceiling_bound.py` (standard
library, exact integer arithmetic, run by `verify.py`) prove two bounds for
**every** legal owner map on this supplier. The proof relaxes the problem to
plain bin packing: windows and the family rule are dropped.

- The instance has 32,256 bins (capacities 8, 16, 32, 48; counts 10,752,
  7,168, 7,168, 7,168) and 69,120 helpers (widths 4, 5, 7, 8, 9; counts
  144 × (56, 32, 30, 122, 240)). Both are derived from the package data.
- **At most 4,887 cap-48 bins can be empty.** Give each helper weight ⌊7w/9⌋
  and each bin weight ⌊7c/9⌋ (6, 12, 24, 37). The helpers in a bin never weigh
  more than the bin. The total slack is 587,776 − 406,944 = 180,832 for every
  map, and an empty cap-48 bin uses 37 of it. This map has 4,880 empty cap-48
  bins; the selected map has 4,866.
- **The search surrogate `Σ f ln f` is at most 4,887 · 48 ln 48 + 17 ln 17 =
  908,139.013.** This comes from an exact knapsack over the per-bin slack. A
  plain LP dual gives 908,156.14. This map is at 907,271.883.
- Solver-reported, not checked: the class-level window LP and the window + R4
  IP reach the same optimum, so windows do not tighten the bound.

This bounds the surrogate and the number of empty cap-48 bins, **not κ**. As
an indication only, pricing the bound-attaining idle multiset
`{1:2431, 17:1, 48:4887}` with the pinned engines gives κ 0.001674088611862992
(9.822% of the complex endpoint gap). This replaces the earlier version's
"≈908.1k" heuristic ceiling, which could not be reproduced.

## How the map was found

Inside a physical family the bins' windows never overlap. So the family rule
reduces to at most one helper per bin per call, and bins with the same capacity
and the same allowed calls are interchangeable. κ is close to linear in the
surrogate `Σ f ln f` over idle fragments, which the search uses as its
objective; only the exact engines decide acceptance.

1. **Earlier versions' search.** A global class-level repack and
   cycle/LNS loop (third version), then an evacuation LNS neighbourhood
   (fourth version), up to κ 0.001673341928508063.
2. **Class-level re-solve** (new, `search/winlp.py`). The window model is an
   IP over (capacity, window) classes: pattern counts, flows of each
   (call, width) to each class, time and width balance, and aggregate R4 cuts
   for each family group and call. Each step re-solves it warm-started from
   the current map. Only a random 12–24-class subset may change, drawn from
   the classes that differ from a full-model target. Each step must gain a
   minimum surrogate amount and pays a penalty per unit of change.
3. **Guided realisation** (new, `search/lns2.py` mode `guide`). The neighbourhood
   is the bins holding helpers whose class (call, width) count must drop, plus
   the bins whose pattern count must drop. CP-SAT then maximises the surrogate
   exactly over it, and a result is kept only if the exact κ rises.
   `search/gloop.sh` and `search/sloop.sh` loop this. Strict-replayed
   checkpoints: 0.001673373170972473, 0.001673393061983855,
   0.001673535326871893 and 0.001673614205725695. The search was **stopped
   while still improving**.
4. **Min-diff re-assignment** at the same idle profile, hence the same κ. The
   raw map relocates 63,109 rows against the selected map. The class-level
   min-diff tools (`search/mindiff_cls1.py`, `mindiff_cls2.py`,
   `mindiff_lns.py`, `mindiff_lns2.py`, `realize.py`) give 63,109 → 2,210 →
   2,170 relocations, i.e. 2,537 changed rows of which 367 are offset-only.
   Two stage-1 class patterns could not be realised, because several helpers of
   one width in a bin need distinct calls. The README gives the counting
   argument for each. Both were excluded with `BAN` and stage 1 was re-solved
   locally. The class-level relaxation implies at least 1,548 relocations for
   any legal map with this profile (solver-reported). The min-diff stopped at
   its two-hour budget, so the shipped map is not proven minimal.

`SEARCH.json` records the checkpoints and the commands. `lns.py`, `lns2.py`,
the loops, `check.py` and `verify.py` compare κ as `Decimal`, because the
native assembler can drop trailing zeros.

## Earlier versions of this PR

- **First version**, κ 0.001672684510394236: two-stage ejection cycles on
  PR1407's map, a 23-row successor of PR1407, with the ancestry checked by
  content.
- **Second version**, κ 0.001672702955495933: a longer cycle/LNS search, then
  a min-diff re-assignment to 70 changed rows (55 relocations) against the
  selected map; the PR1407 ancestry check was dropped.
- **Third version**, κ 0.001673054161426948: a global class-level repack and
  the cycle/LNS loop, then a class-level min-diff re-assignment to 1,661
  changed rows (1,435 relocations). Its idle profile did not majorize the
  selected one, so it relied on the exact engines alone for the sign.
- **Fourth version**, κ 0.001673341928508063: an evacuation LNS neighbourhood
  in the same loop, then the class-level min-diff to 1,638 changed rows (1,415
  relocations); its profile majorized the selected one again.

This fifth version replaces the map, the diff and the search record, and adds
the proved packing ceiling. PR1407 (pai-scaffolde) remains the starting point
of the search line and the source of the whole-helper semantics and all-input
argument. PR2077 (lydakis) remains the origin of the vacancy-chain idea. Their
four literal moves still do not compose (`search/compose.py`).

## Provenance

- **Chooser:** this work was not drawn by `scripts/choose_research_task.py`. It
  was self-selected as the review-and-compose task: a review of PR1407 and
  PR2077, a test of whether they compose, and then a search on the stronger
  map. `TASK.json` records it under the closest card, `selected-packing`, with
  `scope_status: changed` and this reason.
- **Base:** `0fdd7d82`. The 287 pinned inputs are listed in `INPUTS.json` and
  `SOURCES.json`.
- **Credit:**
  - pai-scaffolde (PR1407): starting map of the search line, whole-helper
    semantics and all-input argument.
  - George Lydakis (lydakis, PR2077): the vacancy-chain idea.
  - Rohan Arun and Jeremy Kothe: the PR1050–PR1094 line and the selected
    supplier and map.
  - Josie Elliston: the seed67 auditor, PR1091.
  - Sagar Thakrar: the independent pricing sweep, PR1069.
- **Prepared by** Philippe Van Velzen with substantial Claude Code (Claude
  Opus 5.5) assistance. No independent human review is claimed.

## Reproduce

```sh
python3 scripts/research_package.py --package research/complex-t16-two-stage-cycles --check-only
python3.12 scripts/research_package.py --package research/complex-t16-two-stage-cycles
```

The full replay takes about 60 s and uses only the standard library. The
search is optional and needs numpy, ortools, scipy and highspy; the README and
`SEARCH.json` give the commands.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
