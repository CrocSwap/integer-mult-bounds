# Attribution and licence

Apache-2.0 applies. Original headers, licences, notices and AI-assistance disclosures are preserved. The
credits below do not imply review or endorsement.

This package is a cube-size change (p = 12 → p = 10) of #285's gen5 five-stage package. Every inherited design,
generator, checker, layout and bank method below is used at the new cube size; no inherited idea is claimed.

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
- **Complex supplier (this variant):** the centre-sharing complex program
  `inputs/complex/gcert1-p11-cmod-centre-mw-flow.json.gz`. It is local research, not published, prepared by
  DreamingOfClouds with Anthropic Claude assistance (Apache-2.0). It is the source-assisted complex word of
  PR #184/#194, built with PR #304's recipe on three query modules:
  - the new centre-sharing pair module `pmod46_ptc1_final.json` (45 pair outputs and the star centre);
  - an earlier re-annealed disjoint-triple module, `tmod_final.json` (v1, 2,069 additions). This is not PR #304's
    `tmod_cmod_v2.json`.
  - PR #304's all-but-one module, as `qmod_q1_snap1.json`.

  PR #304's `aligned_word.py` cannot build it unchanged. The program was built by a local 46-root loader (not
  shipped) with a 10-line patch to PR #144's `Graph.finish` (icekylinx). The patch and the three modules are
  shipped as provenance in `inputs/complex/centre-mw/`, whose `NOTICE` gives the details. The rest of the recipe
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
  #276's gen4 changes (arc-aware local design, centre-sharing pair module).
- **Paired-cube framework and its developments:**
  - icekylinx's PR144: paired-coordinate/shared-core framework and configurable local channels.
  - PR161/PR168 (eumemic): annealed modules, nested schedules and the generator.
  - James Chang's PR166 and PR162's carrier rule.

## New in this package

All of the following was prepared by DreamingOfClouds with Anthropic Claude assistance.

**The p = 10 bit word.** It has three data files:

- `pm_p10.json`: pair module, 273 additions;
- `qmod_p10.json`: all-but-one module, 24 additions;
- `local_design_p10.json`: cube-local recipe trees from a pair-aware local design search.

The two modules were annealed for p = 10, starting from restrictions of gen5's p = 12 modules. The package also
pins the new frozen arcs `arcs_p10.json`.

**Generator and producers at p = 10.** The generator gains its p = 10 MODULES/QMODULES entries and the variant-u
output merge at p = 10; p = 12 behaviour is unchanged. The physical-layer producers become h-generic:

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

The circuit and module searches were run by Claude agents (simulated annealing, CP-SAT and exact compiles). Every
reported number was re-run with the exact generator and the full verifier. No exclusive priority is claimed for
any inherited design or theorem interface.

## Transcript stages (this package)

The stage stack is ported from the gen5 Python pipeline at p = 12 to the p = 10 word by Chafik Boukhalfa
(chafreaky) with Anthropic Claude assistance (Apache-2.0). Every mechanism is inherited; the selections were
re-derived on this word. Credits, without implying review or endorsement:

- **Concave descent retiming:** Rohan Arun (rohanarun), PR #287 (`descent_transform.py`, rule and transform);
  the search was re-implemented to reproduce #287's frozen selection exactly before it was run here
  (`discovery/descent_search.py`).
- **Target-prefix squares:** eumemic, PR #268/#273 (`target_transform.py`, OpenAI Codex assistance), as used in
  #287; search re-implemented (`discovery/target_search.py`).
- **Kernel entries:** PR254's kernel pairs and eumemic's #268 kernel transform; the collective (multi-donor)
  families follow #272; per-entry cuts, shared donors and the collective census/packing are from our PR #282/#284/
  #290/#299 (Chafik Boukhalfa, Claude assistance); the multi-seed restart packing is Rohan Arun's PR #300.
  The shared-donor selection (donors shared by many high-cardinality entries, alternate response bases,
  maximum-weight closure) follows eumemic's PR #319 (OpenAI Codex assistance), read as a description only; the
  closure search here (`discovery/coll/lines.py`, `planes.py`, `closure_pack.py`) is our own re-implementation
  run before the kernel stage.
- **Early restorations:** utcorvusvolat-dotcom, PR #280 (cleanup screen and emitter), with Dugongue's
  endpoint-aware composition in PR #283; ported to this pipeline in our PR #295.
- **Terminal sinks:** Dugongue, PR #283; the stricter screen of our PR #295.
- **Reorder:** our PR #299 (reordering single additions into a neighbouring incidence frame; toggle-detection view
  of Khattar–Gidney, arXiv:2407.17966).
- **Second descent tools** (searched, empty here): constructed join/meet frames from PR #291 (rohanarun) and
  connected blocks after PR #270.
- **Downstream changes** (endpoint completions in the lowering, (σ, E) charts, determinant retention,
  completion-rank pricing) are from our PR #295/#299; the economy bank tiling is new here.
