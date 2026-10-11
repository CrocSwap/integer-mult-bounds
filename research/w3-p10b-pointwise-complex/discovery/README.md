# Discovery (not run by verify.py)

`verify.py` never searches. It reads `spec/c2.json`, `modules/` and `layers/c2/` and checks them. This note says
how they were found.

**Recipe.** The layer is PR #327's recipe (`discovery/pr327/make_layer_p.py`, steps 1–6, the `mw` recipe only).
`pipe.py` is our re-implementation of those steps for screening module sets, about 90 s per set at p = 10:

1. build the centre-sharing source-aligned graph from the per-invocation spec;
2. find carrier arcs with the Hopcroft–Karp carrier matching (ordering `reverse`, local donors dropped), then
   extend them with PR #162's greedy extension restricted to query donors;
3. run `compile_closure` and `select`, then PR #200's operation-frame descent (up to three cycles);
4. take the forward closure, with the descended frames as preferred frames;
5. pair donors with PR #233's maximum-weight late compensated pairing (`pairs_mw_p.py`, f = h − 4);
6. compute kernel pairs with PR #184's `complex_frame_flow.py`. It found none here.

`pipe.py` built the graph with our per-invocation builder (`CXUP_SPEC`). `spec_graph.finish_spec` is the same
builder without its orientation option, which was left at the identity.

**Modules.** The search ran in two steps:

1. **Shared modules.** PR #325's bit-word pair and all-but-one modules replaced PR #327's in the complex word. The
   result is the companion program `spec/uniform.json` + `layers/uniform/`, at 7932/10⁷ and Lean-checked. PR #346
   independently ships a complex supplier with the same coarse saving. Float five-stage roots: PR #327's set
   7.795976e-4, #325's pair module only 7.8754e-4, #325's all-but-one module only 7.8515e-4, both 7.9321e-4.
2. **Pointwise pair modules.** Starting from step 1, a greedy hill climb ran on the exact compile proxy. Its
   moves replace the pair module of one point i, for both bits at once, by a random local rewrite of it
   (re-derive one addition, or re-root one output, keeping the module contract); a move is kept if the proxy
   improves. The best
   state, `spec/c2.json` (`modules/pointwise/pmod_i0..9.json`, six distinct files), gives float root 7.94023e-4,
   R 6,253 and 6,779 arcs. Its layer was then re-found by `pipe.py`, and the program was certified with the steps of
   PR #327's `chain()`. The pointwise modules are data for the proof: their contracts are checked by `load_pmod46`,
   and the whole word is checked by the chain.

**Not shipped.** The climb driver, the module annealers and the compile proxies are research code and are not
included.
