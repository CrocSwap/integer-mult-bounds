# Optional native discovery archive

These sources preserve the discovery route used for the accepted witness. They are not invoked by the fixed-witness verifier, and their floating search scores are not κ bounds. Build with GNU C++17 and the package `code/` include directory, for example:

    g++ -O3 -std=c++17 -Iresearch/e8-signed-lift/code research/e8-signed-lift/discovery/signed-response-v2.cpp -o signed-response-v2

` signed-response-v2 BASE OUTPREFIX ` extracts exact transported total/READ response arrays. For the decoder tools use prefix `response351-v2` in a chosen response directory. The dense arrays require roughly 150 MB and are intentionally not shipped. The extraction and optional search may be rerun on the replay's decompressed `native351` source.

`suffix_matroid351_multi INPUT RESPONSE-DIR SECONDS OUT` performs bounded integer shared-cap nomination. `disjoint_suffix_lift_groups MULTI RESPONSE SINK-RECEIPT OUT` selects disjoint groups with all shared donors charged. `audit_signed_lift_union INPUT RESPONSE-DIR GROUPS OUT` checks exact signed relations and term omission/sign controls.

`compose-selection-lift ORIGINAL SUNK RESPONSEPREFIX GROUPS SINGLES SELECTION FRAMES` remaps stable physical roles and actual cuts onto the sunk source. `signed-single TARGET RESPONSEPREFIX SECONDS OUT` produces the additional exact single-donor nominations used by that composition. The canonical fixed selection already supplied in `data/` avoids rerunning time-bounded nomination or relying on platform-specific floating tie order. Every accepted fixed witness is still independently admitted by `verify.py`.

The original signed groups use original compact-source role IDs. The literal selected instruction data uses the remapped sunk source and expands coefficients into unit additions. Never import original role IDs directly into a changed word.
