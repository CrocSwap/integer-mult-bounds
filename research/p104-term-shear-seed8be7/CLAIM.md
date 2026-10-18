# Local claim: P104 two-term basis shear

The initial GraphQL rate-limit response prevented posting this claim at cycle start, so this local card preserved its exact scope. After the endpoint recovered, the completed handoff was posted in [Discussion #1728](https://github.com/CrocSwap/integer-mult-bounds/discussions/1728). The focused artifact is [PR #1726](https://github.com/CrocSwap/integer-mult-bounds/pull/1726).

## CLAIM

- Track: `complex-mechanisms`; accepted OS seed `8be7a2eedea3e46ac14a43b092df843e`; task `complex-new-helper-inventory`; priority revision 3.
- Base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected record: `certificates/selected-result.json`, SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Object and question: the eight exact rank-one terms in PR717's pinned `P104_HIT_flip_3a.txt`. Can one elementary shear or a bounded length-two product on touching term pairs alter supports so that the P104 `cst=56` decoder admits a lower delivery bill while preserving the exact identity?
- Changed assumption: allow two decoder summands to mix by `D' = D(I+λE_ij)`, `T' = T(I−λE_ji)`, instead of keeping the PR717 term basis fixed.
- Bounded method: check all 56 ordered term pairs and `λ ∈ {−2, −1, −1/2, 1/2, 1, 2, 3}`. For the pinned integer vectors, this covers every nonzero rational coefficient ratio that can cancel an entry plus one generic support case. Then check 71,344 length-two sequences where the ordered term-pair edges share at least one index, using the same seven-value alphabet at both steps. Verify exact factorization and all support-pair ranks. Exact rank-profile DP shows cst>=57 fails the 5% ceiling gate even when ranks are optimally redistributed and one term is allowed to vanish.
- Cost gate: the zero-extra-delivery P104 knob has `a=0.001781965481`, 1.05438 times the selected fixed-word ceiling. The 5% target is `a=0.00177455681454345`; at most 21 added rank-one local children fit that target. PR1071's staggered schedule has a 47-copy lower bound on the pinned decoder, so a candidate must lower that bill. All actual frame changes, copies, restoration, hosting, precision and interface costs remain charged before calling a construction viable.
- Predecessors: PR717 head `4a97676294f9fa413b65986e9984fddeda71e4cc`; PR968 frame-pair floor; PR1071 head `ce9531beba1ce115fdcdc44925ded995a29b8bac`; PR1125 head `9f7c0679d64bab954b7161d8586dc626a59b92ee`; PR1619 head `6c96bc1a0e374a713e9ae493228247f49be49dd5`; PR1240 fixed-word ceiling. The last gives a pricing model; PR1071/1125 hold the original term supports fixed. Active Discussion 1693 concerns a different selected-gauge44 rank-two retiming, while Discussions 1671/1674 concern selected-word frame/endpoint changes.
- Result: all 392 one-shears have six rank-7 terms plus two rank-8 terms (cst=58). Of the 71,344 touching two-shear paths, 336 have cst=56 and all are inverse moves on the same ordered pair, restoring the original factorization; 2,744 have cst=58, 32,928 cst=59, and 35,336 cst=60. There are no cst=57 paths. Every nontrivial candidate therefore misses the 5% ceiling target before delivery charges. This is a bounded negative result, not a universal obstruction, new κ or physical supplier.
- Claim expiry: `2026-10-14T09:40:00Z`.

The main REST overlap refresh was completed at `2026-10-14T07:47Z`; it found no open P104 term-basis claim. GitHub Discussion refresh via `scripts/find_overlap.py` failed with the same GraphQL rate-limit response. The one pivot was driven by the exact cst=58 result and the 5% rank-profile screen. Prepared with substantial OpenAI Codex assistance; no subagents.

## Local DONE update

The exact finite replay passed for all 392 one-shears and all 71,344 bounded touching two-shear paths. Certificate and derivation are in `RESULT.json` and `README.md`. PR #1726 is open at head `6498353243328d5e2bf97a8b34e55b0dc4a881f4`; hosted checks were queued at last observation. Discussion #1728 records the completed handoff.
