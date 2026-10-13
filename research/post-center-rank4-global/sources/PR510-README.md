# Bit word R480 at nine stages: c = 0.001587447106092548137108

**The R480 bit word of PR #503 (PR #493's word with its nine totals on dead registers), priced in the nine-stage
whole-residual hosted pipeline instead of the eleven-stage one.** The word is unchanged. Only the stage count changes,
from eleven stages (m = 78, eight pooled replicas) to nine (m = 64, 32 replicas). The nine-stage pipeline is the
PR #443/#444 lineage with PR #442 whole-residual hosting, vendored byte-identical from PR #463.

| quantity | value |
|---|---|
| bit c, nine stages, 32 replicas, every helper residual hosted whole, no banks (10^-24 grid) | `396861776523137034277/250000000000000000000000` = **0.001587447106092548137108** |
| PR #503, R480 at eleven stages (rebuilt and checked by the parent run) | 0.001574753352953808650916 (this package: **+0.806%**) |
| PR #493, R489 at eleven stages | 0.001565442026981656908596 (this package: **+1.4057%**) |
| κ with #484's complex b (draft; Lemmas A and G), complex-bound | `662515748707749/500000000000000000` = 0.001325031497415498 (unchanged) |
| κ with #471's / #458's complex b, complex-bound | 0.001303530097714685 / 0.001295523322678044 (unchanged) |

The bit side does not bind, so κ does not move with any of the three cited complex suppliers. The gain is bit-side
headroom.

## Why nine stages win for R480

The bit price is the root c of Σ_t n_t·t·(m/t)^c = m·W. Each stage adds its local invocations, and each odd stage adds
an idle advance. On #472's eleven-stage schedule, the rank-7 idle children of the even stages (7,680 per run) cannot
host any width-8 residual, so they are paid in full. With R480's small helper count, nine stages host every residual
whole: 138,240 = 9 × 32 × 480, with 0 banks and maximum child 8. The smaller window m = 64 then prices lower than
m = 78. The same chain gives R489 at nine stages 0.001576648413160438658485, +0.716% over #493 (not shipped). On
R715/R740 the comparison went the other way (s = 11 was best), which fits the smaller R here.

## What runs (`verify.py`)

0. This package's `MANIFEST.json`, and the pinned manifests of #503 and #493. `SOURCE.json`: every vendored file's
   git blob id equals PR #463's file at head `cdf0c1c` (recomputed). Seven of them (`bank_routes.py`, `tile_m.py`,
   `e8core.py`, `hosting_core.py` and the three moment engines) are also byte-identical to #493's vendored copies.
P. Parent: #503's `verify.py` (`--light` in light mode; full mode also runs #493's `verify.sh`). It rebuilds the
   R480 word from #493's plan and runs #493's whole checker chain on it at eleven stages:
   - relaxed #370 checker and `interface.py`, with mutants;
   - legality and the five- and eleven-stage formal columns;
   - Gram;
   - hosted audit and assembly.
   This package reuses its records and its #386 nine-stage geometry (built by #493's `code/nine/geometry.py`).
1. Nine-stage formal columns: #381's `columns_k` with KPAIRS = 4 and RHELP = 480. 1,440 columns over F2 through 9
   invocations, 2,160 bridge additions, 18/18 omitted-bridge controls rejected, prefix payload 102 bits < 104.
2. Nine-stage template (`global_k.py`, 32 replicas, 288 local invocations; local and unbanked global F2 columns
   replayed; omitted bridge shears rejected) and the parent audit (`audit_parent_k.py`, adapted, see Scope).
3. Hosting: #442's programme through `emit_k.py --discover` rediscovers `data/selection9-r480.json` exactly. All
   138,240 helper residuals are hosted whole on idle data coordinates, with 0 banks. Independent hosted audit
   (`audit_hosted_k.py`): PASS, with its template mutations rejected.
4. `code/assemble9.py`: the nine-stage bit invoice of #463's `assemble_k.py`, verbatim, and both #315 moment engines
   with the 10^-16 bad-branch allowance (next grid point rejected). Then #493's per-supplier outer loop, verbatim:
   six bootstrap levels, 47 strict inequalities, next_grid / zero_eta / zero_beta / unit_beta controls. It is run with
   #484, #471 and #458 (cited complex b, `data/complex-b.json` of #493).
5. Findings (a) and (b) below, on R480 and R489.
6. Every number against `EXPECTED.json`.

```sh
BOOST_INCLUDE=/path/to/boost python research/e8-r480-nine-stage/verify.py /absolute/new/output --light   # 10 to 15 minutes
BOOST_INCLUDE=/path/to/boost python research/e8-r480-nine-stage/verify.py /absolute/new/output           # + #503 full (+ #493 verify.sh)
```

Finite invoice (nine-stage, as in #463): prefix 193 bits (charged 256), two-level coefficient 425 bits (charged 512),
row coefficient 18,355 < 20,161, halving depth 2.

## Findings on the R489 family (knowledge)

Checked by `verify.py` (step 5, on R480 and on #493's R489):

- **(a) An LP floor of 480 for R480's skeleton.** `code/findings/flowlp2.py` solves a min-flow LP on the frame lattice of
  one 4-frame. Registers are unit flows, sources are free at their lines, helpers are born at frame zero, and the
  dual is a max-weight antichain. The lattice has the 4 lines, the 6 cells and two transverse quads per cell. The
  node lower bounds come from the junk-dimension lemma: two dirty branches of a cell span only one vector that
  carries the cell sum. So a cross cell needs ≥ 3 registers, and a matching cell, whose two pure sources bring no
  junk dimension, needs ≥ 4. The optimum is **16 helpers per 4-frame, 480 over the 30 frames**. Without these bounds
  the optimum is 8. The bound rests on three hypotheses:
  - (H1) 3 branches per source (the spherical 4-design carrier bound);
  - (H2) every cell sum feeds 2 transverse quads;
  - (H3) the matching-cell sources feed the block frame.

  `code/findings/levels.py` reads R480's own frame visits and shows the word attains every node bound. Its 120 cross
  cells hold 3 helpers each, and its 60 matching cells hold 2 helpers and 2 sources each. Each of the 480 helpers
  stands at exactly one cell and at exactly one D6 frame, so **levels 2 and 6 are tight antichains**. Levels 1, 4
  and 7 carry 240, 360 and 240 helpers. A word with fewer helpers must break H1, H2 or H3. `verify.py` checks the LP optimum given these node bounds, and the tight levels on R480's own data. The junk-dimension lemma and the flow model itself (that every word of the family is such a flow) are argued here, not machine-checked.
- **(b) Kernel pivots are exactly 0.** `code/findings/piv0.py` checks R480 and R489. Each of the 120 root-line
  entrance classes (the helpers whose first frame contains the line) has linearly independent delivery vectors,
  i.e. nullity 0. Nullity is monotone, and coordinate and higher-rank entrance classes are sub-classes. So the
  maximum pivot count of #443's kernel is 0 for coordinate and root-line entrances of any rank. Every residual stays
  width 8. That is why the eleven-stage schedule's rank-7 idle children stay unhostable, and why nine stages win.

Exploration outside the package, not run by `verify.py`:

- **(c) The helper ledger is at its floors.** There are 240 carriers, at the 4-design bound (two per source). The
  other 240 registers are the junk-dimension count per cell: one extra per cross cell, two per matching cell. Every
  shared symbol is held by exactly as many registers as the Dilworth width χ of its read frames. So the
  copy-removal methods built on the #370-lattice words (read-then-climb, XOR fusion, Bcw inlining with ILP chains)
  have nothing to act on here.
- **(d) Idle fusion has no legal glue.** Fusing a pair's successive idle advances would put the rank-7 children to
  use, but it needs glue between the pair's two members, and none is legal:
  - An X→Y bridge add mixes frames at rank 1 in #445's geometry (X wires contain the line q, Y wires do not).
  - With X→X and Y→Y shears only, a Gröbner-basis test finds no glue for K = 2..5 (the basis is [1], so there is no
    solution even over ℂ).

  A check that compares only pair levels misses the X/Y frame difference. #493's own audit hard-codes the twin
  X→X/Y→Y form, so it is not affected.

## Scope (stated plainly)

- **(a) Vendored, not cited.** The nine-stage pipeline (`global_k`, `audit_parent_k`, `emit_k`, `audit_hosted_k`,
  `hosting_k`, `bank_routes_k`, plus #443's `bank_routes`, `tile_m`, `e8core`, `config`, the #315 engines and #442's
  `hosting_core`) is not on the hub's main branch. It is in open PRs #463 and #450 (and their parents #443, #444, #442).
  It is vendored byte-identical from #463 (DreamingOfClouds, branch e8-carrier-rekid-r715, head
  `cdf0c1c6540df987467988fd771340670f4136f3`), with path, git blob id, sha256 and lineage per file in `SOURCE.json`.
- **(b) Not #472's pooled pipeline.** The nine-stage emitter is the per-replica one (#444/#442 lineage), with 32
  replicas in 4 groups of 8. It is not #472's eleven-stage emitter with eight pooled replicas, which #493 and #503
  use. Its finite prefix is #443's per-stage product bound 2^nb·cf^(K+1)·cb^K (193 bits). It is not #472's
  chronological physical-family bound (5,479 bits for R480 at eleven stages). The prefix enters only the finite
  cutoffs, not c.
- **(c) One adaptation of a vendored audit.** `code/adapt.py` makes two listed edits to `audit_parent_k.py`. The first
  points the vendored path at the vendored directory. The second concerns the template control "omit a residual
  route factor". That control mutates the first residual isometry that has a route factor (a non-empty
  `gaussian_reduction`). In R480 every helper enters at frame zero, so the only isometry is the identity, which has
  no route factor. The selector therefore raises StopIteration, and the audit could not start. The control is
  vacuous in that case (there is no factor to omit), so it is skipped exactly when no isometry has a route factor.
  Every other control runs (17 rejected), and `verify.py` asserts that the skipped control is absent.
- **(d) Review point: the mutable-source interface at nine stages.** R480, like #493's R489, writes source registers
  below the full frame (577 gates at block D4 frames), under #425's mutable-basis interface. #493 justifies the
  realisation by #472's PROOF ("Shared physical labels": the pullback of D_F on F2-valued streams does not depend on
  whether a register is called a source, helper or target). The nine-stage pipeline's address realisation is
  #443/#444's (replica groups) with #442's hosting, and that proof text does not discuss source registers as
  destinations. What carries over unchanged:
  - #425's four word-level hypotheses. They are properties of the word, not of the stage count, and #493's
    `interface.py` checks them on R480 in the parent run: no target feeds a source or helper; D only at frame zero;
    C = the literal U⁻¹ at the full frame; B writes only targets.
  - The local invocation itself: the same word, with the same #386 frame operators D_F per call. #445's eleven-stage
    geometry extends this, and the nine-stage one is its parent.
  - The exact F2 replay. `global_k.py` replays every local and unbanked global column of the nine-stage template,
    including the data families that the source ports occupy, so sources written and restored inside each call are
    checked at the composition level, as are the nine-stage formal columns.

  What is not separately re-proved here is #493's realisation sentence for #443's address map. We state it as the
  same argument, because the pullback is a statement about one local invocation on its own owners, and the replica
  grouping only chooses which owners. A reviewer should treat it as a listed conditional interface, as #493 does at
  eleven stages.
- Everything else #493 and #503 are conditional on carries over unchanged: the all-size bit/Gaussian compiler,
  target-label realisation, whole-call correlated-helper hosting (#442), compressed windows, restored work, common
  grid and tape, precision, row and analytic contracts. Complex savings are cited from their PRs' receipts. The κ
  with #484 rests on #484's Lemmas A and G. No unconditional multiplication theorem, Lean proof or κ = 1 result is
  claimed.

## Credits

eumemic (#493: the R489 carrier-skeleton word, its generator and checks). PR #503 (R480: totals on dead registers).
The nine-stage pipeline: chafreaky (#443 replica kernel and global template, #444 replicated idle hosting, with OpenAI
Codex), DaysSky (#442 idle-axis whole-residual hosting), Zhihao Chen (#386 nine-stage geometry), DreamingOfClouds
(#315 moment engines; #450/#463 eleven-stage adaptations of the pipeline, vendored here), Dylan Crow (#370 checkers);
DaysSky also wrote #381's `columns_k`. Details in `NOTICE.md` and `SOURCE.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0 (`LICENSE`).
