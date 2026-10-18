# Scope selection and overlap

Seed 21, complex-supplier track, base ba82555c64e1879e4b7decce28186f208fcb8262. Three candidates were considered before the experiment:

1. Sharp fixed-endpoint positive-lift minimum for the 21-ADD mutable-leaver cells: selected.
2. Rank-seven helper endpoints on k8: rejected because [PR1090](https://github.com/CrocSwap/integer-mult-bounds/pull/1090) already covers that mechanism.
3. Seven-slot T16 owner packing: rejected because PR1050,1053,1055,1061,1065,1068,1074,1087 already develop it.

Live Curiosity Bot GitHub-provider queries on 2026-10-13 included `"k8" "slot"`, `"mutable" "leaver"`, `"leaver" "21"`, `"leaver" "optimal"`, and `"monotone" "leaver"`, restricted to this repository's PRs. The optimality query returned no results; that is a targeted overlap check, not a claim of exhaustive novelty. The monotone query returned PR1049,683,622.

The text of [PR1049](https://github.com/CrocSwap/integer-mult-bounds/pull/1049) was read live. It independently verifies the PR1005/1018 local endpoint, inverse compensation criterion, frame profiles, literal cell locations and leaver premise, and corrects a raw profile description. It does not establish a 21-ADD lower bound. We preserve its limits and do not claim its audit as new work.

[PR1005](https://github.com/CrocSwap/integer-mult-bounds/pull/1005) supplies the eight mutable-leaver cells; [PR1018](https://github.com/CrocSwap/integer-mult-bounds/pull/1018) supplies the seven-slot word; [PR1042](https://github.com/CrocSwap/integer-mult-bounds/pull/1042) changes T16 owner packing while retaining that local word. The present bound does not re-optimize owners or slots. PR683's partial K/M face-bypass carrier result concerns a different interface; PR622 supplies the preceding K-triangle skeleton.

Concurrent round22 analyzes PR917 determinant-two helper-matching butterflies; this package does not touch that circuit. Previous bit-frame positive-transfer results concern different endpoint matrices and registers. The new proof uses the three disjoint source pairs and the asymmetric donor/recipient projection types of the twelve-wire mutable-leaver endpoint, rather than transferring a bit-frame enumeration.

A final fresh metadata check reached PR1120 at 18:36 UTC: PR1115 describes U8 B-stage shear rewrites, PR1116/1118 CK butterfly/grid constructions, PR1117 helper ends plus owner packing, PR1119 U8 cleanup refactorization, and PR1120 mixed-rank block splitting. None of these titles states this restricted leaver-cell lower bound. This last check is metadata-only and is not presented as a full review of those packages.
