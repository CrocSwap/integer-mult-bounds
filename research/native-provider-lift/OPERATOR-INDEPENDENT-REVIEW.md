# Independent native-provider and lift review

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

## Result

The exact round-three word at PR #4610 head `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6` is suitable for the source-bound native lowering, conditional on the explicitly retained native-generator, all-fiber compiler, normalization and analytic contracts. Its decompressed payload SHA-256 is `cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`. This review establishes the finite identities below and checks the informal lift algebra; it does not independently prove every retained contract or certify a full multiplication program.

## Fresh finite checks

A separately written checker read the actual compressed word and used the main-pinned PR #4470 constructor only as predecessor evidence. It checked:

- The complete original frame-registry prefix and every main entrance and exit are preserved.
- Every scalar opcode, coefficient and chronological order is preserved in each orientation; every logical native operator label and its order is preserved.
- Every one of the 72 explicit binary native maps is a permutation of all 512 binary columns: 36,864 image columns were independently evaluated.
- All 180 actual signed warp classes send their declared input subspace onto their declared output subspace, with the direction reversed for an inverse warp.
- All 408 helpers are arbitrary independent inputs with strictly nested whole-job boundaries. Their exact census is `{4:28,7:7,8:47,9:326}`.
- Both retained literal interpreters check all 632 arbitrary-input columns in both orientations, with owned storage restored as required by their checks.
- The complete paid census, including eight rank-eight center jobs, is `{1:2201,2:412,3:510,4:127,5:40,8:8}` in both orientations.

The receipt is `INDEPENDENT-RECEIPT.json`; the separate checker is `review_provider.py`. These local discovery/review files use workspace paths and are not themselves a portable release entry point. The publication package should retain the receipt and use its own source-authenticated dependency closure for replay.

## Absolute phase source review

The exact public round-three `phase_check.py` and its predecessor `research/warp-interface-20261022/verify_candidate.py` were retrieved from the pinned head and read in full. The round-three checker calls the predecessor's phase routine on the actual new word, then explicitly checks every changed helper boundary. The routine constructs the actual physical operator

    C_input.adjoint().then(K_G).then(C_output)

for each actual warp class and requires its exact Fourier rank to be zero. It checks both orientations, absolute phases and reconstructed monomial recipes. Changed native maps are also compared on all 512 columns against two integer formulas. Each new paid frame edge is lowered and its required positive rank checked. Meaningful wrong-map and same-tableau/wrong-global-phase controls are present. The unmodified pinned public phase checker was then run in a separate 29-file, hash-authenticated tree. It passed in 30.09 seconds: 20 changed native maps on all 512 columns, 180 actual warp classes, 105 new paid pairs, 26 changed helpers, both orientations, and the meaningful wrong-map and wrong-global-phase controls. No authenticated input changed. The separate source manifest and run receipt are `PHASE-INPUT-MANIFEST.json` and `PHASE-RUN-RECEIPT.json`; the regenerated mathematical receipt is `PHASE-VALIDATION.json.gz`.

Generator substitution remains a retained model premise: the new maps may replace the old maps consistently with the unchanged symbolic native identity. The verifier does not claim that a changed K_G is the identical physical matrix to its predecessor K_G. That equality is neither needed by the stated generalized contract nor established here.

## Why the quotient headlines were not used

PR #4596 (`477232ced13ec75fa40e0451ad1377db54c9d385`) and PR #4629 (`2cf7d081118f6f702aa317816d231b41ce073579`) supply much larger numerical invoice roots. PR #4604 (`6d4d72885351e01d0a2ce2b20419c0d84cb4949c`) and PR #4627 (`b5d71c724a30fde0e8d2538c09549ce6a4fca756`) correctly identify the endpoint question. Those constructions change main charts, while literal replay compares against the word's own final-frame record and represents native warps by free symbols. They therefore do not establish the unchanged canonical main operator required by the present lift. No numerical quotient root was used as a replacement for that missing identity.

A bounded alternative tested intersection with each of 511 hyperplanes, followed by least anchored closure while preserving main endpoints and warp frames. It found no positive moment gain over the pinned PR #4470 invoice. This is a search report for that restricted family, not an impossibility theorem or the contribution's main result.

## Native lift algebra

The explicit generic lift was checked symbolically. Write c=3/32, Q=min(q_C,c), q=(κ+Q)/2 and choose

    δ=min(1/100,(q−κ)/(4(q+1)),(c−q)/16),
    ε=1−δ, β=1−3δ, r=δ/10, layout=δ/100,
    ξ=ε(1+q)−c+layout.

For every 0<κ<Q, these are strict interior parameters. In particular:

- The complete-group key has exponent β+1−ε=1−2δ<1; all its coefficient/address/classification tables have subpolynomial setup.
- The membership margin is 1−β−2(1−ε)=δ>0.
- The cap margin is ε−ξ=c−εq−layout>0.
- The chirp margin is exactly `1−(β+2ξ−2+r)=2(c−q)+δ(122/25+2q)>0`.
- The transform saving is εq>κ, the fused Gaussian saving is q+δ(1−3q)>q, and the boundary saving is εq+layout. The remaining six paid rows also strictly exceed κ.

The global-word FFT record setup does not introduce a per-record O(p) defect: in the actual caller log r is of order p/d, with d=p^ε and ε<1 fixed. Thus r grows faster than p, so O(p+r) reusable setup is absorbed by O(r log r). Individual coefficients and intermediates occupy a fixed number of global O(log n)-bit words, rather than a newly chosen local word model.

This establishes the assembly algebra once an effective source-bound provider exponent q_C has been admitted. The independently checked finite profile above is a genuine changed paid profile, not an extra decimal of an unchanged raw root. Its finite compiler/critical-majorant arithmetic is a separate obligation checked by the lead's portable verifier.

## Attribution and remaining review

Credit Cao Yifan for PR #4610 and its round-three joint helper/native-map witness; Cinna Davis and the PR #4470 native/helper lineage; Dugongue for the transported warp-frame lemma and PR #4630 native caller; zxv for the native compiler/critical majorant; Jacob Alan Sussman for mixed-target matching; and Pierre-Loic Doulcet for the independently developed PR #4626 helper-621 route. All source-specific attribution and licenses remain applicable.

The exact supplier all-fiber lift, analytic Gaussian decomposition, conditioning, finite matching, prime avoidance and integer recovery remain the pinned source proofs, not conclusions of the finite checker. No Lean kernel verification or independent human acceptance is claimed.
