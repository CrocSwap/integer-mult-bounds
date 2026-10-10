# Discovery (not run by verify.py)

`verify.py` never searches. It reads the frozen layers in `../layers/` and checks them; this directory records how they
were found and is the tool for re-pinning when a module changes.

`make_layer.py` applies one recipe to three module files and writes `layers/<set>/`:

1. the source-aligned graph of PR #194's pipeline with the given modules (the construction of `aligned_word.py`);
2. carrier arcs: the deterministic Hopcroft-Karp carrier matching of PR #200/#233's harness (`pr233/matching.py`,
   ordering `reverse`) with the arcs of local donors dropped, then PR #162's greedy extension restricted to query
   donors (`extend_floor.py` is `extend.py` of the harness with that donor floor, two lines);
3. `compile_closure` + `select`, then PR #200's operation-frame descent on the aligned word (`pr233/physical_opt.py`
   endpoint moves, `pr233/bundles.py`, `pr233/joint.py`; at most three cycles);
4. `source_aligned_local_v4.py`'s forward closure with the descended frames as the preferred frames;
5. reuse pairs on these frames, two recipes: `parity` (`source_aligned_local_v4.py --avoid-parity-erasure`: PR
   #193's minimum-weight full matching that avoids PR #184's parity erasures) and `mw` (PR #200/#233's maximum-weight
   late compensated pairing, `pr233/pairs_mw.py`, last late pair moved to the phase cut);
6. kernel pairs: PR #184's flow with its own kernel matching on the tree that `aligned_word.py` writes (none are
   found on the four committed layers).

The committed files of both sets were written by this script and are identical to the layers of the original
exploratory runs. `layers/cmod/` belongs to `modules/tmod_cmod_v2.json` (a reheated continuation of the triple
module's anneal) with the pair and all-but-one modules of the first round; it was re-pinned with the commands below.
The annealing of the module files themselves (numba simulated annealing of each module against the exact compile
ledger of the aligned word, started from PR #168 v4's modules) is research code with workspace paths and is not
included; the modules are inputs here, checked by the tree's own contract loaders and priced by the chain. A
centre-sharing variant (the pair module also supplies the star centre as a 46th root, about +2.7% over the
same-recipe control on the numerical five-stage root) needs a change to `Graph.finish` of PR #202's tree and is not
packaged.

## Re-pinning after a module changes

    python3 -B research/complex-module-anneal/discovery/make_layer.py --set cmod --tmod <new tmod.json>   # ~5 min
    python3 -B research/complex-module-anneal/verify.py --write   # re-pins modules/ and layers/, sets the claims
    python3 -B research/complex-module-anneal/verify.py           # must PASS; then update README.md and PROOF.md

`make_layer.py` copies a module given outside `modules/` into it and records the set's three files in
`SOURCE.json` (`module_sets`); modules not given keep their current entries. `verify.py --write` sets each claim to
the largest 10⁻⁷ grid point its exact bounds certify.

## Vendored harness (`pr233/`)

PR #233's discovery files (Chafik Boukhalfa with Anthropic Claude and OpenAI Codex assistance; Apache-2.0; PR #162
extension DaysSky et al.), unchanged: `matching.py`, `physical_opt.py`, `bundles.py`, `joint.py`, `pairs_mw.py` and
their `README.md` (which also names `harness.py`, `flow_frames.py`, `extend.py`, not needed here). sha256:

    59d1cd30e67d3511cf799140eb248e785e77aaccff7c47a22a0feef8fb6f021e  matching.py
    cbfd06026a44df30944781262848c88ec987ca5e80381e35ae7ad715a9db1fce  physical_opt.py
    71c81bc858e62e03e2a5230c16c4c199a027c24402cdc937bd4ded60f4ee3286  bundles.py
    e4857418f6e16d6fbb1815d3c4148116e35a6b9940cb57acb2b563da5621b92c  joint.py
    aa927718ad27bebcfa2bddeb3704d4721433c2d4e6b6e218ceb9d28a07cd6c83  pairs_mw.py
    1bd628da0afbccfd9baafc2d51cd96a51a4e46c782b783a1c16bea04fd88d98c  README.md
