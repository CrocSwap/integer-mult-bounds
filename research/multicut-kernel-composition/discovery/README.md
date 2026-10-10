# Discovery (not run by the verifier)

Pure-Python replay of PR #249's word, the censuses that produced the 387 added kernel families, and the chain that
rebinds the two published retiming selections (Chafik Boukhalfa, Anthropic Claude assistance). Inputs are the
package's own `inputs/` files, decompressed into a data directory.

    twins.py  <data> twins.pkl                  census of twin dirty helpers at PR #254's cut (record 727,593)
    chrono2.py <data> twins.pkl chrono.pkl <cut> the same census at any cut (at 676,560: 985 pairs, 24 size-9 classes)
    gain.py                                     log-weighted gain phi(r) = r ln(120/r) per pair and exact-grid price
    gen_candidates.py, compare259.py, merge259.py   round 1: candidates in PR #259's schema, the pairs disjoint from its helpers, the merge
    census2.py, merge2.py                       round 2: every response class at twelve cuts, pairs and XOR triples, greedy packing
    census3.py, census3b.py                     round 3: shared-donor families (partner = an existing donor, nested entrance chain)
    retime.py                                   the chain cohort -> descent (PR #263) -> plateau (PR #270) with the sha rebinding
    rebind_target.py                            PR #273's 209 squares rebound to this transcript (post-cut scalar alignment)
    scan_sandwich.py                            the cleanup-sandwich scan (pivots with the three-gate cleanup shape, joint dimension 4)
    chain_swap.py, finalize_swap.py             the pivot-role swap in 83 families, the full stage chain and the packaging

Diff of this package against PR #259's (everything else byte for byte):

    inputs/candidates.json.gz      518 items of PR #259 (26 dissolved) + 387 appended (rounds union-early-cut, headroom-2, shared-donor; 83 with the pivot role swapped)
    inputs/target-selection.json   PR #273's 209 squares, rebound (core_binding block)
    inputs/sandwich-selection.json the 126 retired helpers (128 scanned)
    code/target_prefix.py          PR #273's stage, verbatim
    code/cleanup_sandwich.py, code/sandwich_endpoints.py, code/sandwich/price-histogram.cpp   PR #271's mechanism, ported
    inputs/descent-selection.json  PR #263's 25 gates, rebound to this transcript (input sha gate)
    inputs/plateau-selection.json  PR #270's 29 blocks, rebound to the descent transcript
    code/descent_retiming.py, code/plateau_retiming.py, code/verify_frames.py, code/verify_plateau_spans.py, code/verify_frame_tables.py
                                   PR #263's and PR #270's stages, verbatim
    code/cohort-transform.cpp      std::sort -> std::stable_sort on the gauge order (platform-independent transcript)
    verify.py                      stages 02b-02f and 09-17 inserted with sha gates; 'containment_pairs_checked' dropped from compared fields; normalize() on both sides
    expected/*.json, expected-sandwich/*.json, RESULT.json   regenerated receipts (twelve + eight) and result (890 pivots, rank 1719, kappa 7.12005174354669e-4 native, 7.14026746429965e-4 with sandwiches)
    README.md, PROOF.md, NOTICE.md this package's notes; PR #259's README/PROOF kept as README-PR259.md, PROOF-PR259.md
    MANIFEST.json                  regenerated
