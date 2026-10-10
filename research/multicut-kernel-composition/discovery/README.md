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

Diff of this package against PR #259's (everything else byte for byte):

    inputs/candidates.json.gz      518 items of PR #259 (26 dissolved) + 387 appended (rounds union-early-cut, headroom-2, shared-donor)
    inputs/descent-selection.json  PR #263's 25 gates, rebound to this transcript (input sha gate)
    inputs/plateau-selection.json  PR #270's 29 blocks, rebound to the descent transcript
    code/descent_retiming.py, code/plateau_retiming.py, code/verify_frames.py, code/verify_plateau_spans.py, code/verify_frame_tables.py
                                   PR #263's and PR #270's stages, verbatim
    code/cohort-transform.cpp      std::sort -> std::stable_sort on the gauge order (platform-independent transcript)
    verify.py                      stages 02b-02e inserted with three sha gates; 'containment_pairs_checked' dropped from compared fields; normalize() on both sides
    expected/*.json, RESULT.json   regenerated receipts (eleven) and result (890 pivots, entrance rank 1719, kappa 7.11482139228173e-4)
    README.md, PROOF.md, NOTICE.md this package's notes; PR #259's README/PROOF kept as README-PR259.md, PROOF-PR259.md
    MANIFEST.json                  regenerated
