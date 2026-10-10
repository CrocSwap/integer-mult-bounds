# Discovery (not run by the verifier)

Pure-Python replay of PR #249's word and the censuses that produced the 365 added families (Chafik Boukhalfa,
Anthropic Claude assistance). Inputs are the package's own `inputs/` files, decompressed into a data directory.

    twins.py  <data> twins.pkl                  census of twin dirty helpers at PR #254's cut (record 727,593)
    chrono2.py <data> twins.pkl chrono.pkl <cut> the same census at any cut (used at 676,560: 985 pairs, 24 size-9 classes)
    gain.py                                     log-weighted gain phi(r) = r ln(120/r) per pair and exact-grid price
    gen_candidates.py                           candidate records (basis, first frames, entrance line) in PR #259's schema
    compare259.py                               the pairs disjoint from PR #259's 1,194 helpers (free259.json)
    merge259.py                                 PR #259's 518 items + the 333 free net-positive pairs (round 1)
    census2.py                                  second census: every response class at twelve cuts, pairs and XOR triples, greedy packing
    merge2.py                                   + the 32 families of the second round -> inputs/candidates.json.gz

Diff of this package against PR #259's (everything else byte for byte):

    inputs/candidates.json.gz      518 items unchanged + 333 appended (round "union-early-cut") + 32 (round "headroom-2"), all at cut 676559
    expected/*.json, RESULT.json   regenerated receipts and result (883 pivots, entrance rank 1710, kappa 7.11421336565136e-4)
    code/cohort-transform.cpp      std::sort -> std::stable_sort on the gauge order (platform-independent transcript)
    verify.py                      'containment_pairs_checked' added to the dropped fields; normalize() on both receipt sides
    README.md, PROOF.md, NOTICE.md this package's notes; PR #259's README/PROOF kept as README-PR259.md, PROOF-PR259.md
    MANIFEST.json                  regenerated
