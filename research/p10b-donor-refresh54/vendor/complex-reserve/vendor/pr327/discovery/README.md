# Discovery (not run by verify.py)

`verify.py` never searches. It reads the frozen layers in `../layers/` and the module files in `../modules/` and checks
them; this directory records how they were found and is the tool for re-pinning when a module changes.

## Layers: `make_layer_p.py`

`make_layer_p.py` is PR #304's `discovery/make_layer.py` with three changes and nothing else: the cube size is a
parameter (`--p`, default 10: `Graph(p)`, triple module at p, pair module at p − 1, all-but-one module at p − 2 instead
of the literals 11, 10, 9), the centre-sharing graph is an option (`--centre46`, see `../centre46.py`), and the
maximum-weight pairing is `pairs_mw_p.py` (below). The recipe (the same for the control and both results):

1. the source-aligned graph of PR #194's pipeline with the given modules (the construction of `aligned_word_p.py`);
2. carrier arcs: the deterministic Hopcroft-Karp carrier matching of PR #200/#233's harness (`pr233/matching.py`,
   ordering `reverse`) with the arcs of local donors dropped, then PR #162's greedy extension restricted to query
   donors (`extend_floor.py`);
3. `compile_closure` + `select`, then PR #200's operation-frame descent on the aligned word (`pr233/physical_opt.py`
   endpoint moves, `pr233/bundles.py`, `pr233/joint.py`; at most three cycles);
4. `source_aligned_local_v4.py`'s forward closure with the descended frames as the preferred frames;
5. reuse pairs on these frames, two recipes: `parity` (PR #193's minimum-weight full matching that avoids PR #184's
   parity erasures) and `mw` (PR #200/#233's maximum-weight late compensated pairing, `pairs_mw_p.py`, last late pair
   moved to the phase cut);
6. kernel pairs: PR #184's flow with its own kernel matching on the tree that `aligned_word_p.py` writes. Two are
   found on the control's parity layer (`layers/pr168-v4-cut/kernel-pairs-parity.json`), none on the other five.

The committed layers were written by this script (about 90 s per set at p = 10):

    python3 -B research/complex-p10/discovery/make_layer_p.py --set pr168-v4-cut
    python3 -B research/complex-p10/discovery/make_layer_p.py --set anneal
    python3 -B research/complex-p10/discovery/make_layer_p.py --set centre        # --centre46 is read from SOURCE.json

Their arcs, frames and both pair lists are identical to those of the exploratory runs that first produced the
programs (cp10 `word_p.py`, a script version of the same recipe), and `verify.py` regenerates from them the programs
of those runs (same gcert/1 content apart from the `derived_from` string).

## The gauge-rank fix: `pairs_mw_p.py`

PR #233's `pr233/pairs_mw.py` (vendored unchanged) weighs a donor whose last frame has dimension dd by

    weight = 3 φ(h − dd) + φ(3f) − 3 φ(f − dd)      (f ≥ dd; otherwise excluded),   φ indexed 0 .. 3h, φ(3h) = 0,

with the gauge rank written as the literal `f = 18`. The selected gauges have rank h − 4, which is 18 only at h = 22
(p = 11), where every PR #233 / PR #304 layer lives, so the literal was harmless there. At other cube sizes it is a
latent bug: at h = 18 (p = 9) φ(3f) = φ(3h) = 0 and the two other terms cancel, so every weight is 0 and the
pairing returns no pairs at all; at h = 20 (p = 10) the weights and the cut-off are those of a rank-18 gauge although
the gauges have rank 16. `pairs_mw_p.py` differs from `pairs_mw.py` in one line, `f = o.h - 4`, and is identical to it
at h = 22. The weights only choose the pairs; every pair is checked by `verify.py` (the script's candidate rule and
`paircheck.py`), so the bug could never have produced an illegal pair, only a different (or empty) pairing.
Measured effect: on the PR #144 library modules at p = 9 the mw word went from 6016/10⁷ (no pairs) to 6562/10⁷ with
the fix; at p = 10 the library word was unchanged (6329/10⁷ both ways). On this package's layers the literal happens to be harmless too: `make_layer_p.py` run with PR #233's unchanged
`pairs_mw.py` (f = 18) returns the identical mw pair lists on the `anneal` and `centre` layers (all 1,680 gauges
paired either way; arcs, frames and parity pairs identical as well). The fix is needed for correctness of the
recipe at other h (p = 9, and any h where the weights change the matching), not for these programs.

## Modules

The four p = 10 modules were made in two steps, neither of which is part of the proof (the files are inputs, checked
by the rebuilt tree's contract loaders and priced by the chain):

1. **Zero restriction of a p = 11 module file** (`../module_cut.py`): the inputs touching one dropped point are set
   to zero and the module is pruned. The seeds were chosen by scoring every single-point cut of PR #168 v4's and PR
   #304's p = 11 files with a closed-form evaluator of the aligned word's compile ledger (agent-cmod's evaluator with
   the p = 10 constants), or, for the control, by fewest additions.
2. **Simulated annealing at p = 10** (numba annealers of the triple, pair and all-but-one modules against that
   closed-form ledger, adapted from the bit side's annealer; research code with workspace paths, not included). The
   energies E below are that evaluator's; they ranked candidates, the chain priced them.

| module file | parent (p = 11) | cut | anneal at p = 10 | additions |
|---|---|---|---|---|
| `tmod_t2_p10.json` | PR #304 `tmod_cmod_v2.json` | point 4 dropped (E 41003.3) | chain t1, 2 M iterations (E 38527.9), then t2, 2 M iterations (E 38212.6) | 1,322 |
| `pmod_p3_p10.json` | PR #168 v4 `pmod_J0_full_6.0666810e-4.json` | point 4 dropped, fewest additions (E 212891.7) | chain p3, 12 M iterations (E 104151.4) | 269 |
| `qmod_sa1_p10.json` | PR #304 `qmod_cmod.json` | point 0 dropped (E 77839.5) | chain q1, 8 M iterations (E 77695.0) | 24 |
| `pmod46_pc1_p10.json` | PR #304 `pmod_cmod_dropin.json` | point 5 dropped (E 113224.8) | chain p1, 12 M iterations (E 104311.7); `add_centre.py` appends the 37th root (a greedy disjoint cover of existing nodes summed pairwise, 7 parts); chain pc1, 12 M iterations with the centre root kept (E 102111.1 in centre mode) | 291 |
| `tmod_pr168_p10.json` (control) | PR #168 v4 `tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json` | point 6 dropped, fewest additions | none | 1,220 |
| `pmod_pr168_p10.json` (control) | PR #168 v4 `pmod_J0_full_6.0666810e-4.json` | point 4 dropped, fewest additions | none | 256 |
| `qmod_pr168_p10.json` (control) | PR #168 v4 `qmod_climb3u_best.json` | point 1 dropped, fewest additions | none | 24 |

`verify.py` re-derives the three control files byte for byte with `module_cut.min_cut` from the rebuilt tree. The
three cut seeds of the annealed modules are `module_cut`'s cuts of PR #304's files at the points listed (checked once
against the seed files; the seed files themselves are not shipped). The pair module of the PR #304-recipe set
descends from PR #168 v4's pair module, the other three annealed modules from PR #304's; the effort is asymmetric
(about 1.5 h of annealing at p = 10 against PR #168's and PR #304's anneals at p = 11).

## Re-pinning after a module changes

    python3 -B research/complex-p10/discovery/make_layer_p.py --set anneal --tmod <new tmod.json>   # ~90 s
    python3 -B research/complex-p10/verify.py --write   # re-pins modules/ and layers/, sets the claims
    python3 -B research/complex-p10/verify.py           # must PASS; then update README.md and PROOF.md

`make_layer_p.py` copies a module given outside `modules/` into it and records the set's files in `SOURCE.json`
(`module_sets`, with `centre46` for the centre-sharing set). Delete a superseded module file from `modules/` before
`--write`.

## Vendored harness (`pr233/`)

PR #233's discovery files (Chafik Boukhalfa with Anthropic Claude and OpenAI Codex assistance; Apache-2.0; PR #162
extension DaysSky et al.), unchanged, as PR #304 vendors them: `matching.py`, `physical_opt.py`, `bundles.py`,
`joint.py`, `pairs_mw.py` and their `README.md`. sha256:

    59d1cd30e67d3511cf799140eb248e785e77aaccff7c47a22a0feef8fb6f021e  matching.py
    cbfd06026a44df30944781262848c88ec987ca5e80381e35ae7ad715a9db1fce  physical_opt.py
    71c81bc858e62e03e2a5230c16c4c199a027c24402cdc937bd4ded60f4ee3286  bundles.py
    e4857418f6e16d6fbb1815d3c4148116e35a6b9940cb57acb2b563da5621b92c  joint.py
    aa927718ad27bebcfa2bddeb3704d4721433c2d4e6b6e218ceb9d28a07cd6c83  pairs_mw.py
    1bd628da0afbccfd9baafc2d51cd96a51a4e46c782b783a1c16bea04fd88d98c  README.md

`extend_floor.py` is PR #304's (`extend.py` of the harness with a donor floor, two lines). `add_centre.py` is the
greedy centre-root step of the centre-sharing pair module (DreamingOfClouds with Anthropic Claude assistance,
Apache-2.0).
