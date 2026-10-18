# complex-571-cold14-st2: conditional κ 0.001636241501576388

## Definition

The witness `cold14` is the PR558 geometry (112 data columns, h = 9, 492 helpers per provider word (the K-triangle helper count R; the width-8 spot helpers are the helper-map images [264, 276, 288, 300] of PR558's 270, 282, 294, 306), 8 centres, 9 stages × 8 replicas = 72 calls) served by 2 provider words, each a pinned base word followed by typed build steps: **jp8** (71 calls) = the K-triangle skeleton word (R = 492 helpers; 4 scheduled triangles, `data/TRI-SCHEDULE.json`) → `port_stage` (raw504 → promoted558 of the 504-helper chain, replayed through the helper map) → `port_stage` (promoted558 → jp8_504:0 of the 504-helper chain, replayed through the helper map) → `port_stage` (jp8_504:0 → jp8_504:1 of the 504-helper chain, replayed through the helper map) → `port_stage` (jp8_504:1 → jp8_504:3 of the 504-helper chain, replayed through the helper map) → `frame_regroup` (24 frame regroupings) → `hyperplane_end` (34 helpers end at a hyperplane U instead of FULL) → `cold_end` (28 cold helpers end at a dim-4/7/8 frame U instead of FULL, after a 1019-gate rank-0 premix at the head of A, 112 lower-frame cleanup gates and an exact refactored cleanup); **ck** (1 calls) = the K-triangle skeleton word (R = 492 helpers; 4 scheduled triangles, `data/TRI-SCHEDULE.json`) → `port_stage` (raw504 → promoted558 of the 504-helper chain, replayed through the helper map) → `port_stage` (promoted558 → ck_504:base of the 504-helper chain, replayed through the helper map) → `port_stage` (ck_504:base → ck_504:0 of the 504-helper chain, replayed through the helper map) → `port_stage` (ck_504:0 → ck_504:1 of the 504-helper chain, replayed through the helper map) → `port_stage` (ck_504:1 → ck_504:2 of the 504-helper chain, replayed through the helper map) → `frame_regroup` (24 frame regroupings) → `hyperplane_end` (34 helpers end at a hyperplane U instead of FULL) → `cold_end` (26 cold helpers end at a dim-4/8 frame U instead of FULL, after a 1007-gate rank-0 premix at the head of A, 106 lower-frame cleanup gates and an exact refactored cleanup). The `port_stage` steps read the words of the 504-helper shadow chains **ck_504** = PR571's `frontier-composition/combined-prefix-word/FULL-WORD.json.gz` → `greedy_kernels` (12 multi-cut cold kernels, PR568's constructor) → `frame_coalesce` (6 frame coalescences, PR583's constructor) → `gate_move_coalesce` (2 coalescences, each after moving an addition past commuting additions; 2 moves); **jp8_504** = the frozen PR558 promoted word → `cold_kernel` (PR568 `data/EIGHT-COLD.json`) → `multicut` (PR568 `data/EIGHT-MULTICOLD.json`) → `frozen558_scalar_audits` (inherited static44 and rank-five audits; word unchanged) → `joint_prefix` (PR575, variant `eightcold`), rebuilt in the same run and pinned like the providers but never dispatched. Each step runs a pinned, unchanged constructor plus its paired omission or negative-control audit; a hyperplane-ended helper starts at its entrance frame E, ends at the hyperplane U, and pays residual width |U| − |E|; a cold-ended helper starts cold (E = ∅) and ends at its low-dimensional frame U, so it pays |U|; every other helper ends at FULL, so its width stays h − |E|. The dispatch (which provider serves each (stage, replica) call), the asynchronous call order and the literal owner map are `data/PLAN.json` (`provider_calls`, `order`) and `data/OWNERS.json.gz`, at the dispatch jp8 ×71, ck ×1 (the aggregate free-dispatch LP selects jp8 at every time; ck is pinned at time 5 because the global controls need two dispatched providers); the owner map is an exact per-time-Hall exact-window MIP solution (RINS around the exact-window LP vertex, 240 s, warm-started from PR627's map; solver status/gap not recorded) (see `data/cand.json`), and PLAN is the window MIP's PLAN with the provider registry re-derived from the admitted provider locals (widths over the word's R helpers) and `profile`/`assignment_sha256` recomputed from the map (Stack492 mkplan.py); the resulting paid profile is {1:181421, 2:29094, 3:32112, 4:11809, 5:4898, 6:288, 8:576, 9:2, 32:1, 39:1, 48:2221} with live 7168, physical 7670 and deficit 2560, giving κ = 409060375394097/250000000000000000 = 0.001636241501576388 (conservative model 0.001636241498709272).

## Files

| file | role |
|---|---|
| `data/WITNESS.json` | **inputs only**: geometry, pinned sources, the provider build chains above, dispatch and call order, and PLAN/OWNERS/recipes by SHA-256 |
| `data/EXPECTED.json` | **expected values only**, all derived by recomputation (`spec.py generate`): per-step word hashes and control counts, per-provider artifacts, programs and profiles, global profile and counts, κ. Bound to WITNESS.json by hash |
| `data/PLAN.json`, `data/OWNERS.json.gz` | dispatch, call order and literal owner map (inputs, pinned by WITNESS.json) |
| `data/recipes/` | the package's own step recipes (inputs, pinned by WITNESS.json); `data/recipes/atm3-step0-promote.json`, `data/recipes/atm3-step1-greedy_kernels.json`, `data/recipes/atm3-step2-frame_coalesce.json`, `data/recipes/atm3-step3-gate_move_coalesce.json`, `data/recipes/k492-atm3-cold_end.json.gz`, `data/recipes/k492-atm3-frame_regroup.json`, `data/recipes/k492-atm3-hyperplane_end.json` is not used by the witness (a provider the owner solve did not dispatch; `data/cand.json` lists it) |
| `data/cand.json` | the search candidate (schema candidate/1), an input of the search side: the provider chains (PR622's K-triangle chains with ColdThird's h4a cold_end recipes; the jp8 recipe additionally carries PR627's two factored ends (590, 581) with a re-derived premix and the q92 absorption), the dispatch rule and the PLAN rule, and the owner search (start map `owners.warm_owners`, solver settings, LP pattern inputs, objective and the solve result), with package-relative and `NAME:` source references. The verifiers do not read it |
| `PROOF-COMMUTING-PREFIX.md` | proof note for the construction (documentation; no verifier reads it) |
| `PROOF-NOTE-R.md` | proof note for the construction (documentation; no verifier reads it) |
| `PROOF-NOTE.md` | proof note for the construction (documentation; no verifier reads it) |
| `data/search/WARM-OWNERS.json.gz` | search input named by `data/cand.json` (`owners.warm_owners`): PR627's `data/OWNERS.json.gz` (complex-571-cold14-k492b, jeremydiviney), the warm start of the aggregate LP and the MIP. The shipped `data/OWNERS.json.gz` is the search's result; the verifiers do not read this file |
| `data/search/DISPATCH.json` | search input named by `data/cand.json` (`owners.search_inputs`): the dispatch {time: provider}: jp8 everywhere except ck at time 5; the verifiers do not read this file |
| `data/search/LP-PATTERNS-AGG.json` | search input named by `data/cand.json` (`owners.search_inputs`): aggregate free-dispatch LP relaxation over the st2 words {ck, jp8} (crossover, tight 3), warm-started from PR627's map; the verifiers do not read this file |
| `data/search/LP-PATTERNS-EX.json` | search input named by `data/cand.json` (`owners.search_inputs`): exact-window LP relaxation (crossover) at that dispatch over the base patterns plus aggregate-LP patterns with weight >= 0.01; the verifiers do not read this file |
| `data/search/TEMPLATE-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): the PLAN whose windows/order/registry template the nominator reuses (same as PR622's); the verifiers do not read this file |
| `data/search/WARM-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): PR627's data/PLAN.json, matching WARM-OWNERS.json.gz; the verifiers do not read this file |
| `data/SPEC.json`, `verify.py`, `verify.sh`, `code/` | the combined spec and package verifier (PR604's verifier and code, byte for byte); they verify the same record |

`data/PLAN.json` carries `"status": "LITERAL_OWNER_NOMINATION_PENDING_ADMISSION"`. That label was written by the owner nominator before admission and is kept unchanged because WITNESS.json pins PLAN by hash; admission is what the verifiers below establish, and the label carries no meaning for them.

## Verification

The pinned sources are not merged; fetch their pinned commits first:

```sh
git fetch origin pull/568/head:pr568 pull/571/head:pr571 pull/569/head:pr569 pull/575/head:pr575 pull/583/head:pr583 pull/531/head:pr531
git worktree add --detach ../pr568 71c99ac935a33bb7b59a1b4a7af8725a939b0b90
git worktree add --detach ../pr571 b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3
git worktree add --detach ../pr569 897213a855b7fb8a1b8b0e552a2f5c42e6c1b326
git worktree add --detach ../pr575 eac6f7e378ab622dac50a2fd4b7ef6eab014de44
git worktree add --detach ../pr583 89be768f0157f5a3d8e4db69cf1748768605eac9
git worktree add --detach ../pr531 e07a8a3f9f79c22113398a0c5dbbc7601f489b3e
```

Generic verifier (`research/witness-spec-tools`, PR587 with the `frame_coalesce`, `gate_move_coalesce`, `hyperplane_end`, `cold_end`, `port_stage` and `frame_regroup` step types and the `k_triangle` base; its `code/build_hpe.py`, `code/hpe_controls_atc.py`, `code/build_cold_end.py`, `code/cold_end_controls.py`, `code/hpe_audit_and_transport.py`, `code/hpe_*_local.py`, `code/construct_k_triangle.py`, `code/build_port_stage.py` and `code/build_frame_regroup.py` must be byte-identical to this package's `code/` copies, which define the hyperplane-end and cold-end constructors, their controls and the generalised native chain). It builds everything from `data/WITNESS.json` and only compares against `data/EXPECTED.json`:

```sh
T=research/witness-spec-tools
python3 $T/spec.py check --package research/complex-571-cold14-st2 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=../pr531/research/direct-delivery504-global
python3 $T/verify.py --package research/complex-571-cold14-st2 --work /tmp/complex-571-cold14-st2 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=../pr531/research/direct-delivery504-global
# kappa 0.001636241501576388
```

`verify.py` checks the package MANIFEST and every source, PLAN, OWNERS and recipe pin; replays PR558; rebuilds each provider word through its build chain (each step's input and output content hash pinned, 15 steps); localizes each word (hyperplane- and cold-ended words through the generalised native chain, with `0:U` wrappers for cold ends); then runs binding, the physical owner audit with 23 controller mutants, a fresh finite invoice, both exact moment engines, 114 assembly controls, the phase-timing controls and the generated-identity controls.

The original package verifier gives the same result from `data/SPEC.json`:

```sh
python3 -B research/complex-571-cold14-st2/verify.py --work /tmp/complex-571-cold14-st2-spec \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=../pr531/research/direct-delivery504-global
```

Both use only the Python standard library and require assertions (no `-O`). The result is conditional on the inherited assumptions listed in NOTICE.md.

## Construction and history (the package README as committed)

- **κ = 0.001636241501576388** (conservative model 0.001636241498709272), +0.0223% over PR632 (0.001635877117861902) and +0.0289% over complex-571-cold14-h4a (0.001635768210079684).
- **Construction.** complex-571-cold14-h4a (ColdThird's dim-8 cold ends on PR622's K-triangle words) with **PR627's two factored jp8 cold ends** (jeremydiviney; helpers 590 and 581 at dim-7 frames) stacked on h4a's jp8 `cold_end` recipe. ck is h4a's. Code is h4a's reviewed code; only `data/recipes/k492-jp8-cold_end.json.gz`, the owner map, PLAN and SPEC change.
- **Premix re-derivation.** PR627's rank-0 premix is re-derived exactly in h4a's basis (row then column gates on cold non-ended helpers at frame `[]`, so that row and column 590/581 of the total map are unit vectors off the targets).
- **q92 absorption.** h4a's dirt release at anchor 1665 (q95 += −¼·S403) leaks into end 581 through port 92; one extra dead-port absorption at the same anchor, q92 += ¼·S403, cancels it (exact linear solve; residual empty). It is admitted by the ColdThird allowlist.
- **Review.** H4aReviewer, Addendum 2: SOUND for the local stages (rebuild by the reviewed `apply`, exact endpoint replay in all orientations, `:157`, (N) for the new (0, U7) pairs, 46 controls, profile Δ against h4a {1:+2, 2:+2, 5:−2}). Details in `PROOF-NOTE.md`, section "st2".
- **Line endings.** The reviewed tree had three CRLF files; they are committed as LF only. For each, `crlf_bytes.replace(b'\r\n', b'\n') == lf_bytes` holds and no lone `\r` remains:
  - `code/build_cold_end.py`: reviewed (CRLF) 2fdfdadc2e24f5b024092ffcce144e23a2b2d618fa1d4ebfb3a8179e1fba9cbc, committed (LF) 864b4701dd73afd0c9d99761b7a749f3354c48985730f17054e18c052996a668
  - `code/cold_end_controls.py`: reviewed (CRLF) 3082412baf5eeb12241afb0815f82d4b0519a4e903e1f9cf9739109cf524308c, committed (LF) 0c404f49e90457520f1788ee6741c9ac154a5814c54ad6cb83b59c44552ebc84
  - `verify.py`: reviewed (CRLF) 9db990b50e0a5c8918871dff02404bfcc9a8d143f483a6c310ea36b9d80b8c76, committed (LF) 4c8dea601fe9255bd9fbbf7840d3bfacc3dcf0b1deaf7ffab467e3c10648a3b7
  The other 21 reviewed files are byte-identical to the reviewed tree (H4aFinish `CODE-SHA256-AT-REVIEW.txt`).
- **Dispatch and owner map.** jp8 ×71, ck ×1 (the aggregate LP picks jp8 everywhere; ck is pinned at time 5 because the global controls need two dispatched providers). The owner map is an exact per-time-Hall exact-window MIP solution (RINS, 240 s, warm-started from PR627's map; the solver's status/gap line was not recorded). Global paid profile {1:181421, 2:29094, 3:32112, 4:11809, 5:4898, 6:288, 8:576, 9:2, 32:1, 39:1, 48:2221}.
- `data/SPEC.json` `expected.entering_helper_roles` is corrected from the inherited 16356 to the audited 16714; `verify.py` does not read this key.

### Predecessor: complex-571-cold14-h4a, conditional κ 0.001635768210079684

- **κ = 0.001635768210079684** (conservative model 0.001635768207214129), +0.0147% over PR626 (0.001635527380375392) and +0.0212% over PR622 (0.00163542231500688).
- **Construction.** PR622's K-triangle words with ColdThird's h4a `cold_end` recipes (`data/recipes/k492-{jp8,ck}-cold_end.json.gz`): per word, 4 extra cold ends S1.3, S3.3, S5.3, S7.3 at the dim-8 hyperplane U8a = [256,128,65,33,17,9,4,2], each with 2 lifted partners, plus dead-port absorptions (dirt releases and L-side gates) admitted by a widened forward-absorption allowlist in `code/build_cold_end.py::apply` and independently in `verify.py::cold_end`. Per word the paid profile changes by {1:+4, 4:+4, 6:-4} against PR622 v3 and 4 helpers go from width 9 to width 8. See the ColdThird section of `PROOF-NOTE.md`: soundness rests on the transport's exact arbitrary-dirt endpoint replay plus the `hpe_audit_and_transport.py:157` guard, not on the allowlist's deadness condition.
- **Controls.** The `cold_end` step pins 46 rejected controls per word (38 inherited + 8 ColdThird). The inherited `ab_centre` control is re-pinned from ENDPOINT to COLDPRE when dim-8 cold ends are present, and its centre is chosen outside the cold set (`PROOF-NOTE.md`, "Inherited control re-pin").
- **Dispatch and owner map.** Free dispatch ck ×1, jp8 ×71 (per-time argmax of the aggregate free-dispatch hosting LP over {ck, jp8}); the owner map is an exact per-time-Hall exact-window MIP solution (RINS around the exact-window LP vertex, warm-started from PR626's owner map). Global paid profile {1:181364, 2:28952, 3:32112, 4:11808, 5:5040, 6:288, 8:576, 39:4, 48:2212}.
- `data/SPEC.json` pins the h4a build (and `expected.entering_helper_roles` = 16572, the audited value; PR622 carried 16356) (cold_end `recipe_sha256`, `negative_controls` = 46, `output_content_sha256`) and every global stage, from a discovery run followed by a strict `verify.py` run.
- **Review and line endings.** H4aReviewer (SOUND-WITH-FIXES) reviewed the code with the hashes in H4aFinish's CODE-SHA256-AT-REVIEW.txt. Three of those files were CRLF in the reviewed tree and are committed with LF line endings only; for each, `crlf_bytes.replace(b'\r\n', b'\n') == lf_bytes` holds and no lone `\r` remains:
  - `verify.py`: reviewed (CRLF) 9db990b50e0a5c8918871dff02404bfcc9a8d143f483a6c310ea36b9d80b8c76, committed (LF) 4c8dea601fe9255bd9fbbf7840d3bfacc3dcf0b1deaf7ffab467e3c10648a3b7
  - `code/build_cold_end.py`: reviewed (CRLF) 2fdfdadc2e24f5b024092ffcce144e23a2b2d618fa1d4ebfb3a8179e1fba9cbc, committed (LF) 864b4701dd73afd0c9d99761b7a749f3354c48985730f17054e18c052996a668
  - `code/cold_end_controls.py`: reviewed (CRLF) 3082412baf5eeb12241afb0815f82d4b0519a4e903e1f9cf9739109cf524308c, committed (LF) 0c404f49e90457520f1788ee6741c9ac154a5814c54ad6cb83b59c44552ebc84
  The other 21 reviewed files (the remaining code/ files and verify.sh) are byte-identical to the reviewed tree.

The rest of this README is PR622's README, unchanged except for the `data/search/` rows.

### Predecessor: complex-571-cold14-k492 (PR622), conditional κ 0.00163542231500688

### Definition

The witness `cold14` is the PR558 geometry (112 data columns, h = 9, 492 helpers per provider word (the K-triangle helper count R; the width-8 spot helpers are the helper-map images [264, 276, 288, 300] of PR558's 270, 282, 294, 306), 8 centres, 9 stages × 8 replicas = 72 calls) served by 2 provider words, each a pinned base word followed by typed build steps: **jp8** (65 calls) = the K-triangle skeleton word (R = 492 helpers; 4 scheduled triangles, `data/TRI-SCHEDULE.json`) → `port_stage` (raw504 → promoted558 of the 504-helper chain, replayed through the helper map) → `port_stage` (promoted558 → jp8_504:0 of the 504-helper chain, replayed through the helper map) → `port_stage` (jp8_504:0 → jp8_504:1 of the 504-helper chain, replayed through the helper map) → `port_stage` (jp8_504:1 → jp8_504:3 of the 504-helper chain, replayed through the helper map) → `frame_regroup` (24 frame regroupings) → `hyperplane_end` (34 helpers end at a hyperplane U instead of FULL) → `cold_end` (22 cold helpers end at a dim-4 frame U instead of FULL, after a 430-gate rank-0 premix at the head of A, 86 lower-frame cleanup gates and an exact refactored cleanup); **ck** (7 calls) = the K-triangle skeleton word (R = 492 helpers; 4 scheduled triangles, `data/TRI-SCHEDULE.json`) → `port_stage` (raw504 → promoted558 of the 504-helper chain, replayed through the helper map) → `port_stage` (promoted558 → ck_504:base of the 504-helper chain, replayed through the helper map) → `port_stage` (ck_504:base → ck_504:0 of the 504-helper chain, replayed through the helper map) → `port_stage` (ck_504:0 → ck_504:1 of the 504-helper chain, replayed through the helper map) → `port_stage` (ck_504:1 → ck_504:2 of the 504-helper chain, replayed through the helper map) → `frame_regroup` (24 frame regroupings) → `hyperplane_end` (34 helpers end at a hyperplane U instead of FULL) → `cold_end` (22 cold helpers end at a dim-4 frame U instead of FULL, after a 430-gate rank-0 premix at the head of A, 86 lower-frame cleanup gates and an exact refactored cleanup). The `port_stage` steps read the words of the 504-helper shadow chains **ck_504** = PR571's `frontier-composition/combined-prefix-word/FULL-WORD.json.gz` → `greedy_kernels` (12 multi-cut cold kernels, PR568's constructor) → `frame_coalesce` (6 frame coalescences, PR583's constructor) → `gate_move_coalesce` (2 coalescences, each after moving an addition past commuting additions; 2 moves); **jp8_504** = the frozen PR558 promoted word → `cold_kernel` (PR568 `data/EIGHT-COLD.json`) → `multicut` (PR568 `data/EIGHT-MULTICOLD.json`) → `frozen558_scalar_audits` (inherited static44 and rank-five audits; word unchanged) → `joint_prefix` (PR575, variant `eightcold`), rebuilt in the same run and pinned like the providers but never dispatched. Each step runs a pinned, unchanged constructor plus its paired omission or negative-control audit; a hyperplane-ended helper starts at its entrance frame E, ends at the hyperplane U, and pays residual width |U| − |E|; a cold-ended helper starts cold (E = ∅) and ends at its low-dimensional frame U, so it pays |U|; every other helper ends at FULL, so its width stays h − |E|. The dispatch (which provider serves each (stage, replica) call), the asynchronous call order and the literal owner map are `data/PLAN.json` (`provider_calls`, `order`) and `data/OWNERS.json.gz`, at the free dispatch ck ×7, jp8 ×65 (per-time argmax of the aggregate free-dispatch hosting LP over the K-triangle words {ck, atm3, jp8}; atm3 is never selected); the owner map is an exact per-time-Hall exact-window MIP solution (RINS around the exact-window LP vertex; 1800 s time limit, relative gap 1.0e-7) (see `data/cand.json`), and PLAN is the window MIP's PLAN with the provider registry re-derived from the admitted provider locals (widths over the word's R helpers) and `profile`/`assignment_sha256` recomputed from the map (Stack492 mkplan.py); the resulting paid profile is {1:181579, 2:29864, 3:31267, 4:11520, 5:5040, 6:576, 7:1, 8:576, 21:1, 48:2213} with live 7168, physical 7670 and deficit 2560, giving κ = 10221389468793/6250000000000000 = 0.00163542231500688 (conservative model 0.001635422312138865).

### Files

| file | role |
|---|---|
| `data/WITNESS.json` | **inputs only**: geometry, pinned sources, the provider build chains above, dispatch and call order, and PLAN/OWNERS/recipes by SHA-256 |
| `data/EXPECTED.json` | **expected values only**, all derived by recomputation (`spec.py generate`): per-step word hashes and control counts, per-provider artifacts, programs and profiles, global profile and counts, κ. Bound to WITNESS.json by hash |
| `data/PLAN.json`, `data/OWNERS.json.gz` | dispatch, call order and literal owner map (inputs, pinned by WITNESS.json) |
| `data/recipes/` | the package's own step recipes (inputs, pinned by WITNESS.json); `data/recipes/atm3-step0-promote.json`, `data/recipes/atm3-step1-greedy_kernels.json`, `data/recipes/atm3-step2-frame_coalesce.json`, `data/recipes/atm3-step3-gate_move_coalesce.json`, `data/recipes/k492-atm3-cold_end.json.gz`, `data/recipes/k492-atm3-frame_regroup.json`, `data/recipes/k492-atm3-hyperplane_end.json` is used only by `data/cand.json` (a menu provider the owner solve did not dispatch), not by the witness |
| `data/cand.json` | the search candidate (schema candidate/1), an input of the search side: the provider chains (the K-triangle skeleton with PR604/B3 chains ported stage by stage (port_stage, frame_regroup) and ColdBeyond v3 cold_end recipes re-derived on the ported words), the dispatch rule and the PLAN rule, and the owner search (start map `owners.warm_owners`, solver settings, LP pattern inputs, objective and the solve result), with package-relative and `NAME:` source references. The verifiers do not read it |
| `PROOF-COMMUTING-PREFIX.md` | proof note for the construction (documentation; no verifier reads it) |
| `PROOF-NOTE-R.md` | proof note for the construction (documentation; no verifier reads it) |
| `PROOF-NOTE.md` | proof note for the construction (documentation; no verifier reads it) |
| `data/search/WARM-OWNERS.json.gz` | search input: PR626's `data/OWNERS.json.gz` (complex-k492-owner-repair), the warm start of the owner solve (calls whose words widened are repaired by the solver). The shipped `data/OWNERS.json.gz` is the search's result; the verifiers do not read this file |
| `data/search/DISPATCH.json` | search input: the dispatch {time: provider} = per-time argmax of the aggregate free-dispatch LP selections over the h4a words {ck, jp8}; the verifiers do not read this file |
| `data/search/LP-PATTERNS-AGG.json` | search input: aggregate free-dispatch LP relaxation over the h4a words {ck, jp8} (crossover, tight 3); the verifiers do not read this file |
| `data/search/LP-PATTERNS-EX.json` | search input: exact-window LP relaxation (crossover) at that dispatch over the base patterns plus aggregate-LP patterns with weight >= 0.01; the verifiers do not read this file |
| `data/search/TEMPLATE-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): the PLAN of ColdBeyond's working package (PR604's dispatch ck ×44, atm3 ×22, jp8 ×6), whose windows/order/registry template the nominator reuses; the verifiers do not read this file |
| `data/search/WARM-PLAN.json` | search input: PR626's `data/PLAN.json`, matching WARM-OWNERS.json.gz; the verifiers do not read this file |
| `data/SPEC.json`, `verify.py`, `verify.sh`, `code/` | the combined spec and package verifier (PR604's verifier and code, byte for byte); they verify the same record |

`data/PLAN.json` carries `"status": "LITERAL_OWNER_NOMINATION_PENDING_ADMISSION"`. That label was written by the owner nominator before admission and is kept unchanged because WITNESS.json pins PLAN by hash; admission is what the verifiers below establish, and the label carries no meaning for them.

### Verification

The pinned sources are not merged; fetch their pinned commits first:

```sh
git fetch origin pull/568/head:pr568 pull/571/head:pr571 pull/569/head:pr569 pull/575/head:pr575 pull/583/head:pr583 pull/531/head:pr531
git worktree add --detach ../pr568 71c99ac935a33bb7b59a1b4a7af8725a939b0b90
git worktree add --detach ../pr571 b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3
git worktree add --detach ../pr569 897213a855b7fb8a1b8b0e552a2f5c42e6c1b326
git worktree add --detach ../pr575 eac6f7e378ab622dac50a2fd4b7ef6eab014de44
git worktree add --detach ../pr583 89be768f0157f5a3d8e4db69cf1748768605eac9
git worktree add --detach ../pr531 e07a8a3f9f79c22113398a0c5dbbc7601f489b3e
```

Generic verifier (`research/witness-spec-tools`, PR587 with the `frame_coalesce`, `gate_move_coalesce`, `hyperplane_end`, `cold_end`, `port_stage` and `frame_regroup` step types and the `k_triangle` base; its `code/build_hpe.py`, `code/hpe_controls_atc.py`, `code/build_cold_end.py`, `code/cold_end_controls.py`, `code/hpe_audit_and_transport.py`, `code/hpe_*_local.py`, `code/construct_k_triangle.py`, `code/build_port_stage.py` and `code/build_frame_regroup.py` must be byte-identical to this package's `code/` copies, which define the hyperplane-end and cold-end constructors, their controls and the generalised native chain). It builds everything from `data/WITNESS.json` and only compares against `data/EXPECTED.json`:

```sh
T=research/witness-spec-tools
python3 $T/spec.py check --package research/complex-571-cold14-k492 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=../pr531/research/direct-delivery504-global
python3 $T/verify.py --package research/complex-571-cold14-k492 --work /tmp/complex-571-cold14-k492 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=../pr531/research/direct-delivery504-global
# kappa 0.00163542231500688
```

`verify.py` checks the package MANIFEST and every source, PLAN, OWNERS and recipe pin; replays PR558; rebuilds each provider word through its build chain (each step's input and output content hash pinned, 15 steps); localizes each word (hyperplane- and cold-ended words through the generalised native chain, with `0:U` wrappers for cold ends); then runs binding, the physical owner audit with 23 controller mutants, a fresh finite invoice, both exact moment engines, 114 assembly controls, the phase-timing controls and the generated-identity controls.

The original package verifier gives the same result from `data/SPEC.json`:

```sh
python3 -B research/complex-571-cold14-k492/verify.py --work /tmp/complex-571-cold14-k492-spec \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=../pr531/research/direct-delivery504-global
```

Both use only the Python standard library and require assertions (no `-O`). The result is conditional on the inherited assumptions listed in NOTICE.md.

### Construction and history (the package README as committed)

### Definition

The witness `cold14` uses the PR558 geometry: 112 data columns, h = 9, 8 centres, and 9 stages × 8 replicas = 72 calls. Its providers are words with **R = 492 helpers** instead of 504, built on AtomScout's leaver-read K-triangle skeleton. There are 2 provider words, each a K-triangle base word followed by typed build steps:

- **jp8** (65 calls):
  1. `k_triangle`;
  2. `port_stage`: raw504 → PR558 promoted;
  3. `port_stage` × 3, porting PR568 `cold_kernel` → `multicut` → PR575 `joint_prefix` (eightcold);
  4. `frame_regroup` (24 K-read gate frames);
  5. `hyperplane_end` (34 helpers);
  6. `cold_end` (ColdBeyond v3: S b.10 in all 14 blocks, S b.9 in blocks 3–10, plus the E1 entering pair).
- **ck** (7 calls):
  1. `k_triangle`;
  2. `port_stage`: raw504 → PR558 promoted;
  3. `port_stage`: promoted → PR571 combined-prefix word;
  4. `port_stage` × 3, porting `greedy_kernels` → PR583 `frame_coalesce` → `gate_move_coalesce`;
  5. `frame_regroup`, `hyperplane_end`, `cold_end` as for jp8.

An exact per-time-Hall exact-window MIP chose the dispatch and the literal owner map from the menu {ck, atm3, jp8}.

### The K-triangle skeleton (`k_triangle`, `code/construct_k_triangle.py`)

`code/construct_k_triangle.py` is PR531's `code/construct_504.py` (research/direct-delivery504-global, a pinned source), extended by AtomScout's atom.

**The atom.** A coordinate pair p is *full* when the selected partition contains p in all three blocks that contain p. Then both of its triangles (p, ±1) are consumed only by K-coordinates. For each scheduled triangle:
- its three faces are never formed and never copied;
- every K-coordinate target reads its own leaver (the K-basis own token);
- it then reads the four unformed leavers of the other two faces, in a fixed legal order (`data/TRI-SCHEDULE.json`: the four (p, −1) triangles of the full pairs (0,1), (2,3), (4,5), (6,7)).

This saves 3 packet copies per triangle, so R = 504 − 12 = 492.

**Checks in the constructor.** It keeps every assertion of PR531's constructor (generalised to R):
- the side identity;
- every target frame inside hyper(P_t);
- exact clean cleanup;
- rank mass 9R + 1992.

It also writes `HELPER-MAP.json`, the 504 → 492 register map. Registers below 448 keep their ids, and the 12 removed packet copies have no image.

**Controls in `verify.py`, run once:**
- PR531's unchanged `construct_504.py` and this constructor with an empty schedule each reproduce PR552's `RAW504.json.gz` (content);
- the empty-schedule helper map is the identity.

### Porting the 504-helper chain (`port_stage`, `code/build_port_stage.py`)

**Shadow chains.** The 504-helper chains of PR604/B3 (`build.shadows`: jp8_504, ck_504) are rebuilt in the same run from pinned sources, with their own constructors, controls and content pins.

**What each `port_stage` step does.** It replays one shadow stage I4 → O4 onto the K-triangle word I8 through the helper map:
1. gates are matched by scalar operation;
2. the stage's frame changes, introduced gates and entrance (start_extra) changes are applied;
3. the K-triangle reads are kept after their predecessors' images;
4. the cleanup is the inherited inverse rule.

**Certification.** The constructor is only a transfer. Every ported word is certified by the generalised native audit (`code/hpe_audit_and_transport.py`: exact forward and inverse replay of every column, native frame chains). Every input, shadow input, shadow output and output is pinned by content hash.

### `frame_regroup` (`code/build_frame_regroup.py`)

This is PR583's `build_frames.py`, except that the per-change profile delta is pinned in the recipe instead of being fixed to {1:−2, 2:+1}. Its other properties:
- scalar operations, widths and helper responses are unchanged;
- the omission and over-promotion controls are rejected;
- the same independent comparison as `frame_coalesce` follows.

The 24 changes move the K-read gates of the eight K-coordinate targets to coalesced frames, each with delta {1:−3, 2:+3, 3:−1}.

### Helper count R in the global code

The global scripts (bind, emit, audit, invoice, assemble, assembly controls, generated-identity controls) take R from the provider words, and all providers must share it. The parent split-centres envelope keeps its own R0 = 504.

The width-8 spot check and the cold-helper width-swap controls use `width_spot_helpers`. These are the images of PR558's helpers 270, 282, 294, 306 under the helper map: [264, 276, 288, 300]. `verify.py` checks them against the constructor's `HELPER-MAP.json`.

`PROOF-NOTE-R.md` lists every 504 → R site, why it is sound, and one revert control per site that must fail on this package's R = 492 fixture. `PROOF-NOTE.md` is B3's note: ColdBeyond's cold_end primitives, including dead-port absorption, unchanged. It is followed by a new section on the soundness of the K-triangle atom, the port transfer and frame regrouping.

### Result

κ = **0.00163542231500688** (conservative model 0.001635422312138865). That is +0.0146% over complex-571-cold14-b3 (0.001635183729255778), on dispatch ck ×7, jp8 ×65.

The global paid profile is {1:181579, 2:29864, 3:31267, 4:11520, 5:5040, 6:576, 7:1, 8:576, 21:1, 48:2213} (live 7168, deficit 2560).

The value comes from `ASSEMBLY.json` of the strict `verify.py` run on this package's literal owner map.

`SPEC.expected.owners_per_call` (716 = 2·112 + 492) and `SPEC.expected.entering_helper_roles` (16356) hold the audited values of the strict run. B3 carried 728 and 17712 for them. `verify.py` reads neither key.

### Verification

Fetch the pinned sources at their commits, as for complex-571-cold14-b3, plus PR531 (`research/direct-delivery504-global`, on main at `e07a8a3f9f79c22113398a0c5dbbc7601f489b3e`). Then run:

```sh
python3 -B research/complex-571-cold14-k492/verify.py --work /tmp/complex-571-cold14-k492 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing \
  --source direct_delivery=research/direct-delivery504-global
# kappa 0.00163542231500688
```

`verify.py` performs these steps in order:
1. Replays PR558.
2. Runs the K-triangle constructor and its controls.
3. Rebuilds the 504-helper shadow chains.
4. Rebuilds each 492-helper provider word through its typed steps (each step's input and output content hash pinned).
5. Localizes each provider word with the generalised native chain and all phase edges.
6. Runs binding, the physical owner audit with its mutation controls, a fresh finite invoice, both exact moment engines, the assembly controls, the phase-timing controls and the generated-identity controls.

Standard library only; assertions are required (no `-O`). The result is conditional on the inherited assumptions listed in NOTICE.md.

### Construction and history

The README of complex-571-cold14-b3 follows unchanged.

# complex-571-cold14-b3: conditional κ 0.001635183729255778

### Definition

The witness `cold14` is the PR558 geometry (112 data columns, h = 9, 504 helpers, 8 centres, 9 stages × 8 replicas = 72 calls) served by 2 provider words, each a pinned base word followed by typed build steps: **jp8** (60 calls) = the frozen PR558 promoted word → `cold_kernel` (PR568 `data/EIGHT-COLD.json`) → `multicut` (PR568 `data/EIGHT-MULTICOLD.json`) → `frozen558_scalar_audits` (inherited static44 and rank-five audits; word unchanged) → `joint_prefix` (PR575, variant `eightcold`) → `hyperplane_end` (46 helpers end at a hyperplane U instead of FULL) → `cold_end` (28 cold helpers end at a dim-4 frame U instead of FULL, after a 550-gate rank-0 premix at the head of A, 104 lower-frame cleanup gates and an exact refactored cleanup); **atm3** (12 calls) = PR571's `frontier-composition/combined-prefix-word/FULL-WORD.json.gz` → `promote` (40 entrance promotions, PR569's constructor) → `greedy_kernels` (12 multi-cut cold kernels, PR568's constructor) → `frame_coalesce` (6 frame coalescences, PR583's constructor) → `gate_move_coalesce` (2 coalescences, each after moving an addition past commuting additions; 2 moves) → `hyperplane_end` (46 helpers end at a hyperplane U instead of FULL) → `cold_end` (28 cold helpers end at a dim-4 frame U instead of FULL, after a 550-gate rank-0 premix at the head of A, 104 lower-frame cleanup gates and an exact refactored cleanup). Each step runs a pinned, unchanged constructor plus its paired omission or negative-control audit; a hyperplane-ended helper starts at its entrance frame E, ends at the hyperplane U, and pays residual width |U| − |E|; a cold-ended helper starts cold (E = ∅) and ends at its low-dimensional frame U, so it pays |U|; every other helper ends at FULL, so its width stays h − |E|. The dispatch (which provider serves each (stage, replica) call), the asynchronous call order and the literal owner map are `data/PLAN.json` (`provider_calls`, `order`) and `data/OWNERS.json.gz`, at the free dispatch jp8 ×60, atm3 ×12 (per-time argmax of the aggregate free-dispatch hosting LP over {ck, atm3, jp8}; ck is never selected); the owner map is an exact per-time-Hall exact-window MIP solution (RINS around the exact-window LP vertex; 240 s time limit, relative gap 1.69e-7) (see `data/cand.json`), and PLAN is the window MIP's PLAN with the provider registry re-derived from the admitted provider locals and `profile`/`assignment_sha256` recomputed from the map (ColdOwner mkplan.py); the resulting paid profile is {1:181848, 2:24770, 3:31778, 4:13728, 5:5040, 6:1008, 7:2, 8:576, 48:2150} with live 7168, physical 7682 and deficit 2560, giving κ = 817591864627889/500000000000000000 = 0.001635183729255778 (conservative model 0.001635183726407116).

### Files

| file | role |
|---|---|
| `data/WITNESS.json` | **inputs only**: geometry, pinned sources, the provider build chains above, dispatch and call order, and PLAN/OWNERS/recipes by SHA-256 |
| `data/EXPECTED.json` | **expected values only**, all derived by recomputation (`spec.py generate`): per-step word hashes and control counts, per-provider artifacts, programs and profiles, global profile and counts, κ. Bound to WITNESS.json by hash |
| `data/PLAN.json`, `data/OWNERS.json.gz` | dispatch, call order and literal owner map (inputs, pinned by WITNESS.json) |
| `data/recipes/` | the package's own step recipes (inputs, pinned by WITNESS.json); `data/recipes/ck-step0-greedy_kernels.json`, `data/recipes/ck-step1-frame_coalesce.json`, `data/recipes/ck-step2-gate_move_coalesce.json`, `data/recipes/ck-step3-hyperplane_end.json`, `data/recipes/ck-step4-cold_end.json.gz` is used only by `data/cand.json` (a menu provider the owner solve did not dispatch), not by the witness |
| `data/cand.json` | the search candidate (schema candidate/1), an input of the search side: the provider chains (PR604's, with ColdBeyond's second-cold-end cold_end recipes), the dispatch rule and the PLAN rule, and the owner search (start map `owners.warm_owners`, solver settings, LP pattern inputs, objective and the solve result), with package-relative and `NAME:` source references. The verifiers do not read it |
| `PROOF-COMMUTING-PREFIX.md` | proof note for the construction (documentation; no verifier reads it) |
| `PROOF-NOTE.md` | proof note for the construction (documentation; no verifier reads it) |
| `data/search/WARM-OWNERS.json.gz` | search input named by `data/cand.json` (`owners.warm_owners`): the E1free map (`data/OWNERS.json.gz` of research/complex-571-cold14-e1, byte for byte), used only to seed the aggregate LP's patterns. The shipped `data/OWNERS.json.gz` is the search's result; the verifiers do not read this file |
| `data/search/DISPATCH.json` | search input named by `data/cand.json` (`owners.search_inputs`): the dispatch {time: provider} = per-time argmax of the aggregate LP selections; the verifiers do not read this file |
| `data/search/LP-PATTERNS-AGG.json` | search input named by `data/cand.json` (`owners.search_inputs`): aggregate free-dispatch LP relaxation over {ck, atm3, jp8} (crossover, tight 3), pattern-seeded from the E1free map; the verifiers do not read this file |
| `data/search/LP-PATTERNS-EX.json` | search input named by `data/cand.json` (`owners.search_inputs`): exact-window LP relaxation (crossover) at that dispatch over the base patterns plus aggregate-LP patterns with weight >= 0.01; the verifiers do not read this file |
| `data/search/TEMPLATE-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): the PLAN of ColdBeyond's working package (PR604's dispatch ck ×44, atm3 ×22, jp8 ×6), whose windows/order/registry template the nominator reuses; the verifiers do not read this file |
| `data/search/WARM-PLAN.json` | search input named by `data/cand.json` (`owners.search_inputs`): the E1free PLAN matching WARM-OWNERS.json.gz (pattern seeding of the aggregate LP); the verifiers do not read this file |
| `data/SPEC.json`, `verify.py`, `verify.sh`, `code/` | the combined spec and package verifier (PR604's verifier and code, byte for byte); they verify the same record |

`data/PLAN.json` carries `"status": "LITERAL_OWNER_NOMINATION_PENDING_ADMISSION"`. That label was written by the owner nominator before admission and is kept unchanged because WITNESS.json pins PLAN by hash; admission is what the verifiers below establish, and the label carries no meaning for them.

`SPEC.expected.entering_helper_roles` corrected from PR604's stale 16344 to the audited 17712 (audit_allcold.py, as pinned in EXPECTED.json); PR604's verify.py does not read this key.

### Verification

The pinned sources are not merged; fetch their pinned commits first:

```sh
git fetch origin pull/568/head:pr568 pull/571/head:pr571 pull/569/head:pr569 pull/575/head:pr575 pull/583/head:pr583
git worktree add --detach ../pr568 71c99ac935a33bb7b59a1b4a7af8725a939b0b90
git worktree add --detach ../pr571 b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3
git worktree add --detach ../pr569 897213a855b7fb8a1b8b0e552a2f5c42e6c1b326
git worktree add --detach ../pr575 eac6f7e378ab622dac50a2fd4b7ef6eab014de44
git worktree add --detach ../pr583 89be768f0157f5a3d8e4db69cf1748768605eac9
```

Generic verifier (`research/witness-spec-tools`, PR587 with the `frame_coalesce`, `gate_move_coalesce`, `hyperplane_end` and `cold_end` step types; its `code/build_hpe.py`, `code/hpe_controls_atc.py`, `code/build_cold_end.py`, `code/cold_end_controls.py`, `code/hpe_audit_and_transport.py` and `code/hpe_*_local.py` must be byte-identical to this package's `code/` copies, which define the hyperplane-end and cold-end constructors, their controls and the generalised native chain). It builds everything from `data/WITNESS.json` and only compares against `data/EXPECTED.json`:

```sh
T=research/witness-spec-tools
python3 $T/spec.py check --package research/complex-571-cold14-b3 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
python3 $T/verify.py --package research/complex-571-cold14-b3 --work /tmp/complex-571-cold14-b3 \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
# kappa 0.001635183729255778
```

`verify.py` checks the package MANIFEST and every source, PLAN, OWNERS and recipe pin; replays PR558; rebuilds each provider word through its build chain (each step's input and output content hash pinned, 12 steps); localizes each word (hyperplane- and cold-ended words through the generalised native chain, with `0:U` wrappers for cold ends); then runs binding, the physical owner audit with 23 controller mutants, a fresh finite invoice, both exact moment engines, 114 assembly controls, the phase-timing controls and the generated-identity controls.

The original package verifier gives the same result from `data/SPEC.json`:

```sh
python3 -B research/complex-571-cold14-b3/verify.py --work /tmp/complex-571-cold14-b3-spec \
  --source multicold=../pr568/research/complex-multicold \
  --source structural_gain=../pr571/research/structural-gain \
  --source larger_gain=../pr569/research/larger-gain \
  --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
```

Both use only the Python standard library and require assertions (no `-O`). The result is conditional on the inherited assumptions listed in NOTICE.md.

### Construction and history (the package README as committed)

This package is PR604's `complex-571-cold14` (DreamingOfClouds) extended by ColdBeyond's second cold low-frame end per factory block (S b.9 at U_b, on top of PR604's S b.10 end) and ColdSupply's E1 entering pair (as in PR615), at a free dispatch (jp8 ×60, atm3 ×12; ck is on the menu but not dispatched) with an exact per-time-Hall owner map from an exact-window MIP. The `cold_end` step's allowlist gains two A-gate primitives (frame-[] target writes from cold helpers and forward absorptions of dead ports at their current frame), in `code/build_cold_end.py` and independently in `verify.py`; see `PROOF-NOTE.md`. `code/cold_end_controls.py` and `code/hpe_audit_and_transport.py` carry the E1 review fixes plus the new controls. The rest of this README is PR604's, with paths and Result numbers updated; its construction sections describe PR604's single cold end per block.

**Build on this at your own risk.** DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. This package awaits independent review.

### Result

κ = **0.001635183729255778** (conservative model 0.001635183726407116). That is **+1.300% over PR601** (0.001614202339036103) on dispatch jp8 ×60, atm3 ×12. The value comes from `ASSEMBLY.json` of the strict `verify.py` run on this package's literal owner map. The paid profile is {1:181848, 2:24770, 3:31778, 4:13728, 5:5040, 6:1008, 7:2, 8:576, 48:2150} (live 7168, deficit 2560).

The complex side binds:

| quantity | value |
|---|---|
| native complex lower bound | 0.001637861934441745021019 |
| bit supplier value (PR543) | 0.0016538 (`bit_lower` 0.001653826988146798944268) |
| κ with the bit cap | 0.001635183729255778 |
| κ without the bit cap | 0.001635183729255778 |

The bit value is above the complex bound, so it does not bind, and κ is the same with or without the cap.

### What changes relative to PR601

PR601 (jeremykothe2) dispatches three provider words: **ck**, **atm3** and **jp8**. In each word, 46 entering helpers per call end at a hyperplane. The mechanism comes from PR591, PR592 and PR601. The Lean side is Lemma A with an arbitrary terminal frame (PR593) and multi-gate tails (PR599).

This package appends one typed build step, `cold_end`, to each of the three chains, after `hyperplane_end`. In every call, 14 **cold** factory-scratch helpers end at a **4-dimensional frame U_b** instead of FULL, so their residual width drops from 9 to 4. These helpers are `S b.10`, one per factory block b: registers 234, 250, …, 442. The step has three parts.

1. **Premix.** 142 rank-0 gates at frame `[]` sit at the head of section A. For each block b, the premix swaps the dirt of `S b.0` and `S b.10`. It then fans the candidate's initial value out into `S b.1 … S b.7` with ±1 coefficients. The premix runs after the entry adapters and paid wrappers, so every gate on a cold-ended helper follows its pre-wrapper R_{0,U}^-1. The compensation reads no cold-ended helper.
2. **Lower-frame cleanup.** For each candidate h, four multi-gate tail gates run right after B at frame U_b:
   - `h += −½·P_a`
   - `h += P_b`
   - `P_c += h`
   - `P_d += h`

   Here P_a … P_d are data ports whose end-of-B frames lie in U_b. After these gates, h's row and column of the state are unit vectors. The 46 inherited hyperplane-end gates follow unchanged.
3. **Exact FULL remainder.** A dyadic Gauss–Jordan refactorisation of the rest of the inverse replaces the literal reversed-inverse cleanup. It touches no helper that ends below FULL.

**Why the premix makes this possible.** A helper h can end at a frame U only if two things hold at the end of B, under every monotone common-frame cleanup:
- the row of h in the inverse state map is supported on registers whose frames lie in U;
- the column of h (every register carrying h's initial dirt) is supported on registers whose frames lie in U.

The premix spreads each candidate's initial dirt over `S b.0 … S b.7`. That collapses its dirt column to three low-frame registers, which is what makes the dim-4 frame reachable.

Effect per call and per provider:
- the paid local profile changes by {1:+28, 5:+14, 6:−28};
- 14 helpers go from width 9 to width 4.

The dispatch and the literal owner map are re-solved for the new widths (`data/PLAN.json`, `data/OWNERS.json.gz`). They come from an annealing search started from PR601's map (relocate, swap, ejection-chain, bin-evacuation and provider-flip moves), followed by an exact owner model that is warm-started from the annealed map and restricted to the patterns of that map and of the LP optimum. The exact model holds one helper per port per call, and its solution is expanded literally by bipartite edge colouring (Kőnig). Every inherited window, family and capacity constraint is kept, and the package's verifier re-admits the map independently.

The approach borrows from the uncomputation literature: Bennett 1989; Gidney 2015 (borrowed dirty ancillas); Häner–Roetteler–Svore 2017.

### Why the cold ends are legitimate

**Labels and realisation.** PR599's `hpe_labels_multi` / `hpe_word_multi` (Lean) cover:
- any number of tail gates per helper, as target or partner;
- interleaved helpers;
- any terminal frame;
- an unrestricted entrance, so the cold case E = ⊥ is included.

`exact_cold` reduces (N) for (⊥, U) to a monomial factorisation of T_U, which is how `canonical_frame` defines T_U.

**(N) for every (0, U_b) pair.** This is checked exactly here. `hpe_adapters_local.py` verifies L^-1 T_U R^-1 = C_[4] ⊗ I, global phase included, for all 14 dim-4 pairs. It rejects these wrapper mutants:
- identity pre or post wrapper;
- no wrappers;
- FULL decode;
- width 9;
- wrong U;
- wrong phase.

PR599's `cold_hyperplane_width` lemma is the dim-8 case. Here the width |U| − |E| = 4 − 0 is the |final| − |start| rule that PR591's verifier already applies at every global site.

**The refactored cleanup is not trusted.** `hpe_audit_and_transport.py` accepts a non-literal cleanup only when the word carries `refactored_cleanup`. Such a cleanup must:
- touch only non-target registers;
- use only dyadic additions and signed binary scales;
- make the arbitrary-dirt endpoint replay of the full reordered program exact in both orientations.

The transport also checks the row and column cone conditions above for every helper that ends below FULL.

**Wrapper order.** Two independent checks enforce it:
- The transport rejects any zero-frame precondition or compensation gate that touches a cold-ended helper.
- The event-level replay (`hpe_audit_local.py`) requires every scalar on a wrapped helper to lie between that helper's pre and post residual adapters. A negative control that hoists a premix gate in front of the pre-wrapper must be rejected.

### Verifier changes (inert for words without cold ends)

- `code/hpe_audit_and_transport.py`:
  - cold helpers may end at a proper subframe U (here dim 4) with `0:U` wrappers;
  - the row/column cone pre-check;
  - the refactored-cleanup switch;
  - the zero-frame wrapper-order assertion.
- `code/hpe_emit_local.py`, `hpe_audit_local.py`, `hpe_adapters_local.py`:
  - `0:U` wrappers for cold low-frame ends;
  - the event-level wrapper-order check;
  - 7 event-level and 7–8 recipe-level cold mutants.
- `code/audit_allcold.py`, `invoice_allcold.py`, `assemble.py`: a cold helper may end below FULL with `0:U` wrappers, and these count as wrappers.
- New step `cold_end`:
  - `code/build_cold_end.py` splices the recipe data and recomputes the profile and widths from the frame chains;
  - `code/cold_end_controls.py` holds 14 raw-word mutants that must be rejected, including a premix moved into the precondition.
- `code/witness.py` adds `WITNESS_RECORD`, used for discovery bookkeeping only.

### Future optimization (results and open headroom)

All LP figures below are first-order bounds. They come from the aggregate hosting LP (the whole-owner model on PR601's windows, objective Σ r·ln(73/r)), calibrated against exact moment-engine prices. On PR601's own dispatch and widths, the LP lies within 0.005% of PR601's literal map.

| quantity | value |
|---|---|
| LP ceiling, fixed dispatch (PR601's ck 45 / atm3 21 / jp8 6, all cold) | ≈ +0.49% |
| LP ceiling, free dispatch over {ck, atm3, jp8} cold | ≈ +0.71% |
| this package's literal map (dispatch jp8 ×60, atm3 ×12) | +1.300% |
| remaining owner-map headroom on this dispatch (exact model's bound = LP) | ≈ 0.06 pt |

- **Free dispatch is jp8-heavy.** The LP puts about 70 calls on jp8 and about 2 on atm3. The LP's idle remainder is pure rank-48 idle children, whereas the literal map still leaves some rank-16 and rank-32 idle children.
- **What limits jp8.** Neither the time windows nor time-refinability bind at the LP level: adding per-pattern, one-helper-per-port-per-call constraints leaves the LP optimum unchanged. The gap to the jp8-heavy ceiling is integrality and search. The first integer aggregate optimum was not refinable per port, and the literal maps found so far for jp8-heavy dispatches are worse than this package's dispatch.
- **Closing the gap.** The exact owner model used here (pattern-restricted, edge-colourable) closes about half of the fixed-dispatch gap; its bound equals the LP. The jp8-heavy dispatch needs the same integer model solved on that dispatch.
- **End dimension (first-order).** Raising a unit's end frame from dim 4 to dim d needs the last tail gate at that frame, which lifts one partner. This adds 2ψ(d−4) + ψ(9−d) − ψ(5) to the local cost per unit, where ψ(r) = r·ln(73/r). That is +6.8, +10.6, +13.0 and +14.1 for d = 5…8. The remaining hosting headroom is about 1–2 per unit, so d = 4 is the best end dimension for these units.
- **Necessary condition, for any cleanup factorisation.** A helper h can end at a frame U only if, at the end of B, the supports of its row in the inverse state map and of its dirt column both lie in Q_U, the registers whose end-of-B frames lie in U. The transport checks this condition for every low-frame end. Choosing which units satisfy it, through the premix, is the supply question. This package uses 14 units per word. Their optimality per word is not certified here.

### Verification

Fetch the pinned sources exactly as for PR601, then run:

```sh
research/complex-571-cold14-b3/verify.sh /tmp/complex-571-cold14-b3 ..
# kappa 0.001635183729255778
```

`verify.py` uses only the standard library and requires assertions. It runs these stages:

1. It checks the MANIFEST and every source, PLAN, OWNERS and recipe pin.
2. It replays PR558.
3. It rebuilds the three provider words through their typed chains. That is 17 steps, each with pinned input and output content hashes and paired controls.
4. It localizes each word through the generalised native chain:
   - exact scalar replay and the cone pre-check;
   - both reflected ledgers;
   - the independent local replay with its mutants;
   - exact wrappers;
   - all phase edges.
5. It runs binding and the physical owner audit with its controller mutants.
6. It runs a fresh finite invoice and both exact moment engines.
7. It runs the assembly controls, the phase-timing controls and the generated-identity controls.

The result is conditional on the inherited assumptions listed in NOTICE.md.

### Credits

- **jeremykothe2**:
  - PR601, PR600, PR596, PR592 and PR591: hyperplane-ended helpers, the HPE verifier, and the packages and owner maps this one starts from;
  - PR593: Lean Lemma A with an arbitrary terminal frame.
- **icekylinx**: PR531 and PR535 (entrance and kernel machinery).
- **DreamingOfClouds**:
  - PR509 and PR516 (the Lemma A / Lemma G Lean line);
  - PR599 (multi-gate and cold hyperplane-end Lean);
  - PR484.
- The pinned PR568, PR569, PR571, PR575 and PR583 packages and their authors, as listed in NOTICE.md.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
