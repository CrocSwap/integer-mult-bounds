# Attribution and licence

Apache-2.0 applies. Original headers, licences, notices and AI-assistance disclosures are preserved. The
credits below do not imply review or endorsement.

This package is PR #315's p = 10 package with a new bit word. #315 is the cube-size change (p = 12 → p = 10) of
#285's gen5 five-stage package. Every inherited design, generator, checker, layout and bank method below is used
at the new cube size; no inherited idea is claimed.

## Base package

- **PR #315** (`research/five-stage-p10-banks/`, DreamingOfClouds with Anthropic Claude assistance) is the base.
  Its verification code, complex supplier, all-but-one module and p = 10 port are used unchanged. Its own
  contributions are listed under "Retained from #315" below. #315's package is not modified.

## Inherited, unchanged or with generalized constants

- **Five-stage architecture and finite interface package:** Henry Grant (hcg890), PR234, and Jacob Sussman's
  five-stage construction and gcert/1 export. The complete inherited five-stage credits are in
  `UPSTREAM-PR234-NOTICE.md`.
- **Package machinery:** eumemic's source527 package, prepared with substantial OpenAI Codex assistance, with
  its lineage: Dugongue's PR207/PR216 finite and bank admissions, Rohan Arun's PR211 and sennemmi's PR230 frame
  work, and eumemic's PR210. Their notices are retained verbatim in `notices/`. This covers:
  - the scalar program `scalar/word.py` (byte-identical);
  - the physical event emitter, the parity fusion and the raw-ledger census;
  - the stage-private bank template and checker;
  - the moment, prime and finite-bill checks, and `verify.py`.

  In this package their p = 12 constants are derived from the cube size or pinned in `word-pins.json`. The
  logic is unchanged, apart from the exact bank tiler that replaces gen5's fixed bank patterns.
- **Banks:** Evan McKinney's PR197 completed-bank method. Rohan Arun's PR237 published the width-120
  application first. Here the banks have width 100.
- **Complex supplier (this variant, unchanged from #315):** the centre-sharing complex program
  `inputs/complex/gcert1-p11-cmod-centre-mw-flow.json.gz`. It is local research, not published, prepared by
  DreamingOfClouds with Anthropic Claude assistance (Apache-2.0). It is the source-assisted complex word of
  PR #184/#194, built with PR #304's recipe on three query modules:
  - the new centre-sharing pair module `pmod46_ptc1_final.json` (45 pair outputs and the star centre);
  - an earlier re-annealed disjoint-triple module, `tmod_final.json` (v1, 2,069 additions). This is not PR #304's
    `tmod_cmod_v2.json`.
  - PR #304's all-but-one module, as `qmod_q1_snap1.json`.

  PR #304's `aligned_word.py` cannot build it unchanged. The program was built by a local 46-root loader (not
  shipped) with a 10-line patch to PR #144's `Graph.finish` (icekylinx). The patch and the three modules are
  shipped as provenance in `inputs/complex/centre-mw/` of #315 and #325, whose `NOTICE` gives the details (this
  package replaces that program by #327's p = 10 program; see the last section). The rest of the recipe
  is PR #304's: PR #233's maximum-weight reuse pairs, icekylinx's PR #184 frame flow and exact lift, and PR #256's
  emitter.
  PR #304's full notice and credits are in `inputs/complex/NOTICE-PR304`.

  The gcert bytes are kept as emitted (their JSON keys are not in canonical order), because a separate Lean run
  checked exactly these bytes (`wht_main_block_B2Gcc27x`, exponent 1 − 7727140/10¹⁰, with Sussman's unchanged
  generator; see `README.md`). No Lean check is pinned here. Every verification run checks the program with
  Sussman's `gx.check1` (exact scalar identity) and `gxcore` mirror.

  It builds on Avi Eisenberg (ikeboy)'s PR193/PR194 helper and Chafik Boukhalfa (chafreaky)'s PR200/PR233/PR256
  work. It runs inside Sussman's five-stage certificate, whose original disclosures are in `inputs/complex`.

  The complex checks (`code/complex_{labels,scalars,splice,basis}.py`, `portable_complex.py` and the
  `complex_supplier()` block of `math_check.py`) are taken as re-pinned for this program in a copy of PR #296's
  package (Chafik Boukhalfa, chafreaky), which first generalized those checks to a new gcert. That was done by DreamingOfClouds with Anthropic Claude assistance.
- **Complex program checkers:** Jacob Sussman's reference checker `gx.py` (`gx.check1`) and his `gxcore.py`
  mirror of the two Lean checks. Both are Apache-2.0, Copyright 2026 Jacob Sussman, and are vendored unchanged
  from jacobalansussman/wht-power-saving-lean at f010392c in `inputs/complex/sources/` (`tools__gx__gx.py` is
  new here; `tools__gx__gxcore.py` was already pinned).
- **Physical-word classes:** Chafik Boukhalfa (chafreaky)'s PR200 `bit/word.py` and `bit/base_word.py`, vendored
  in `bitword/bit`. `base_word.py` is unchanged; its unused constant `P = 12` is left as PR200 wrote it.
  `word.py` changes only its input file names: PR200 hard-coded its own p = 12 names, and two lines (plus a
  comment) now read the cube size from the single pinned `graph_pP.json`; the frame-loading line also checks
  that the graph's p and h agree.
  `bitword/NOTICE-PR200` is PR200's own notice.
- **Checker:** eumemic's PR168-v4 `check_paired_cube_bit.py`, vendored unchanged and run with p = 10.
- **Generator:** eumemic's PR168 paired-cube bit generator (`bitword/producer/paired_cube_bit_word.py`), with
  #276's gen4 changes (arc-aware local design, centre-sharing pair module), #315's p = 10 entries, and this
  package's optional cube orientation (below).
- **Paired-cube framework and its developments:**
  - icekylinx's PR144: paired-coordinate/shared-core framework and configurable local channels.
  - PR161/PR168 (eumemic): annealed modules, nested schedules and the generator.
  - James Chang's PR166 and PR162's carrier rule.

## New in this package

All of the following was prepared by DreamingOfClouds with Anthropic Claude assistance.

**A new p = 10 bit word.** It is built on #315's package and differs from #315's word in four places:

- `pm_p10.json`: the pair module, re-annealed from #315's module. The objective is the exact one-instance
  compile cost with five-stage weights plus a penalty λ·debt, with λ from 150 to 300. The debt counts module
  additions that do not donate to a carrier arc. The module keeps 273 additions; its debt goes from 95 to 92.
- `local_design_p10.json`: the cube-local recipe trees, re-searched at p = 10 by 1-move steepest ascent from
  #315's design. The search was scored on the five-stage virtual price of the full word. It changes 2 of the 12
  plane recipes and uses 24 local additions per cube instead of 27.
- `cube_orient_p10.json` (new) and the generator change that reads it. This is a balanced, rotation-equivariant
  cube orientation. Each cube is a cyclic rotation of its sorted triple, and position 0 is the element after the
  largest cyclic gap. In the one orbit with gaps 4, 4, 2, position 0 is the element between the two gaps of 4.
  Every coordinate is position 0 in exactly 12 cubes. Without the file the generator uses sorted cubes. The
  generator also stores the symmetric local-plane and all-but-one entries that an oriented cube looks up. With
  sorted cubes these extra entries are never read, so the generator's output without the file is unchanged.
- `make_physical.py`: tiered reuse matching. Donors are admitted in tiers of decreasing end-frame dimension, and
  each tier extends the current matching by Kuhn augmenting paths. An augmenting path never unmatches a matched
  donor. The last tier is the whole candidate graph, run until no augmenting path remains, so the matching is
  still maximum. PR200's pair rules are unchanged. The matcher applies at every cube size, so these producers
  need not reproduce #315's or gen5's physical words; those packages keep their own producers.

The package also pins the new frozen arcs `arcs_p10.json`, the five new word files and the re-recorded
`word-pins.json`. Every verification file is byte-identical to #315's.

The module annealing, the local-design scan and the orientation analysis were run by Claude agents. Their search
scripts are not shipped; the data files they produced are. Every certified or pinned number was re-run with the
exact generator and the full verifier; the research narrative (annealing parameters, intermediate scores) was not.

## Retained from #315

All of the following was prepared for #315 by DreamingOfClouds with Anthropic Claude assistance.

**#315's p = 10 bit word.** Its all-but-one module `qmod_p10.json` (24 additions) is kept unchanged. #315's two
modules were annealed for p = 10, starting from restrictions of gen5's p = 12 modules. Its local design came from
a pair-aware local design search on the p = 12 word.

**Generator and producers at p = 10.** The generator gains its p = 10 MODULES/QMODULES entries and the variant-u
output merge at p = 10; its p = 12 behaviour is unchanged. The physical-layer producers become h-generic:

- `make_physical.py`: recipients of rank h − 3, residual widths in h, and the `--bank-parity` rule generalized
  to divisibility by m = 5h;
- `descent.py`: cost r·ln(5h/r).

`regenerate.py` gains a re-pinning mode.

**Package integration at p = 10.** This covers:

- `word_pins.py` (cube-size shape and strict pins) and `word-pins.json`;
- `discovery/repin.py` and `discovery/REPIN.md`;
- the cube-size generalization of every check listed in `PROOF.md`;
- the entrance-basis geometry checks for every rank present;
- the exact zero-padding bank tiler;
- the complex-bound assembly path of `math_check.py`, which certifies the bit at its root and feeds the capped
  saving;
- the fallback-inclusive certification of the complex coarse (both moment engines, adjacent grid point
  rejected);
- `code/complex_gx.py`, which runs `gx.check1` (exact scalar identity) and the `gxcore` mirror on the pinned
  complex program in every run, with a flipped-sign control, and the honest restatement of that dependency in
  `portable_complex.py`.

**Gen5 and gen4 work retained from #285/#276.** This covers:

- the `--bank-parity` option;
- the arc-aware local design machinery (`local_design()`) and the centre-sharing pair-module patch;
- `make_physical.py` and `descent.py` as implementations of PR200's stated rules;
- `prepare.py`, `virtual_check.py` and the `scalar_check.py` controls.

The circuit and module searches were run by Claude agents (simulated annealing, steepest ascent, CP-SAT and exact
compiles). Every certified or pinned number was re-run with the exact generator and the full verifier. No exclusive priority
is claimed for any inherited design or theorem interface.

## Transcript stages and the p = 10 complex supplier (this package)

This package is DreamingOfClouds' PR #325 (`research/five-stage-p10b-banks/`, Anthropic Claude assistance) with the
transcript stage stack of our PR #320 (`research/five-stage-p10-transcript-stages/`) re-derived on #325's word, and
with DreamingOfClouds' PR #327 p = 10 complex program as the complex supplier. Stage port, selections and the
complex transplant by Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance (Apache-2.0). Every mechanism
is inherited; the selections were re-derived on this word. #325's, #320's and #327's packages are not modified.
Credits, without implying review or endorsement:

- **Concave descent retiming:** Rohan Arun (rohanarun), PR #287 (`descent_transform.py`, rule and transform);
  search re-implemented to reproduce #287's frozen selection exactly (`discovery/descent_search.py`).
- **Target-prefix squares:** eumemic, PR #268/#273 (`target_transform.py`, OpenAI Codex assistance), as used in
  #287; search re-implemented (`discovery/target_search.py`).
- **Kernel entries:** PR254's kernel pairs and eumemic's #268 kernel transform; collective (multi-donor) families
  after #272; per-entry cuts, shared donors and the collective census are from our PR #282/#284/#290/#299. The
  shared-donor selection (donors shared by many entries, alternate response bases, maximum-weight closure) follows
  eumemic's PR #319 (OpenAI Codex assistance), read as a description only; the closure search
  (`discovery/coll/lines.py`, `planes.py`, `closure_pack.py`) is our own (#320), here run with 18 seeds.
- **Early restorations:** utcorvusvolat-dotcom, PR #280, with Dugongue's endpoint-aware composition in PR #283;
  ported to this pipeline in our PR #295.
- **Terminal sinks:** Dugongue, PR #283; the stricter screen of our PR #295.
- **Second (post-sink) descent:** the #287 rule with constructed join/meet frames from PR #291 (rohanarun) and
  connected chain-adjacent blocks after PR #270 (`descent2_transform.py`, the post-sink retiming of our PR #299). eumemic's PR #322
  applied the same search before the sinks on #320's word ("presink retiming", OpenAI Codex assistance); here it
  runs after the sinks and finds 47 gates.
- **Reorder (two rounds):** our PR #299 (reordering single additions into a neighbouring incidence frame;
  toggle-detection view of Khattar–Gidney, arXiv:2407.17966), #306 for the second round.
- **Downstream changes** (endpoint completions in the lowering, (σ, E) charts, determinant retention,
  completion-rank pricing) are from our PR #295/#299; the economy bank tiling is from our PR #320.
- **Complex supplier:** DreamingOfClouds' PR #327 (`research/complex-p10/`, Anthropic Claude assistance): the
  p = 10 centre-sharing program, its modules and layer (`inputs/complex/centre-mw-p10/`, whose `NOTICE-PR327`
  carries #327's full credits: icekylinx's PR #144/#184, Avi Eisenberg's PR #191/#193/#194, our PR #200/#233/#256,
  PR #304's recipe, Jacob Sussman's gcert/1 format, gx.py and gxcore.py). The generalisation of the five p = 11
  pins of #315's complex checks (PR #234/#296 lineage) to the certificate's h, v, R is new here (`COMPLEX-P10.md`).
