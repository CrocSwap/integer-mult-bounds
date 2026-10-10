# Discovery (not run by the verifier)

Census of collective response-kernel families on the gen4 word and their composition onto PR #283 (Chafik Boukhalfa,
Anthropic Claude assistance). Inputs: the gen4 transcript dumped from PR #276's package; PR #283's package for the
overlap and the pin-generating driver.

    load.py, linalg.py                 per-helper table (responses, first frames, reads, touches); exact rational Gram / nondegeneracy
    families.py, fameval.py            low-weight F2 circuits of the responses (twins, triangles, quadruples), common-frame filter, phi-gain
    allpairs.py, quint.py, quint_eval.py   first-frame intersection screen; size-5 circuits (never net-positive)
    pack.py                            greedy packing with nested shared-donor chains and the deficit-fixed ledger (reproduces #276's and #283's prices)
    replay_families.py                 in-process F2 replay of a selection with per-family omitted-setup / omitted-restore controls
    overlap283.py                      overlap of a selection with #283's kernel roles, sinks and transported candidates
    gen283.py                          pin-generating twin of #283's verify.py (records every sha and receipt, rewrites RESULT.json, inputs/kernel-remapped.json, expected/, MANIFEST.json)
    selA_alone.selection.json          the 695-entry selection on the bare gen4 word (416 pairs, 24 e = 16 pairs, 255 families), model kappa 7.24029e-4
    selD_disjoint283.selection.json    the 91 families disjoint from #283 (this package); families283_rows.json: the same in #283's row schema
    families283_subset_rows.json       the 25 families that fit #283's rank-4 filler pool without the allocator change (7.26226544e-4)

Diff of this package against PR #283's (everything else byte for byte): inputs/kernel-original.json (+91 rows),
inputs/kernel-remapped.json, code/banks.cpp (rank-3 filler block), PROOF-PR283.md (one sentence on the tiling),
expected/*.json and RESULT.json (regenerated), MANIFEST.json, this package's README/PROOF/NOTICE, discovery/.
