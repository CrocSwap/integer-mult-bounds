# Selective raw249 cold-end dispatch

The exact conditional saving is **κ = 0.001636472098484378**, or
`818236049242189/500000000000000000`. This exceeds PR640's CK-u4 result
`0.001636464689763295` by `0.000000007408721083`; the conservative calculation
is `0.001636472095614052`.

A new supplier, `j249`, adds one dimension-eight cold end to PR637's JP8 word.
Its raw helper 249 (helper index 25) has residual width 8 instead of 9. The
construction uses 17 rank-zero premix gates, an eight-gate factored tail and an
exact regenerated FULL cleanup. `PROOF-END249.md` derives the cancellation and
checks all 69 ended rows and columns. Its exact local profile is
`{1:2528,2:397,3:448,4:169,5:63,6:4,8:8}`.

The literal dispatch uses **59 JP8, 12 j249 and 1 CK** calls. The j249 calls
occur at chronological times `[7,9,12,13,15,20,31,32,40,46,53,61]`; CK remains
at time 5. Original JP8 and CK are the unchanged PR637 suppliers; this package
does not use PR640's altered CK supplier. Selective use releases exactly 12
rank units into PR639's 36-unit idle remainder. The literal owner map packs
all slack into 2,230 dimension-48 idle rows, with 35,424 checked roles.

**The full fresh replay passed all 82 stages without reuse**, followed by
every supplemental wrapper check, in 425.33 seconds for the core stages.
All 63 receipt artifacts and 82 stage logs were independently hash-checked.
The [validation folder](../validation/) preserves the full replay archive,
receipts, exact reconstruction and mutation-control results, and executed input
snapshots. Execution was on macOS; no Linux replay is claimed.

Reproduce with Python 3.10 or newer, a C++ compiler and Boost headers:

```sh
PYTHON=python3 sh research/selective249-improvement-20261013/witness/verify.sh /tmp/selective249-fresh
```

The wrapper rebuilds the baseline, all three native suppliers and exact global
certificate. It then runs independent native/owner/moment checks and five
mutations, declaration reconstruction, the exact owner exporter and four
mutations, the inherited U4 independent proof and six mutations, the new raw249
proof and eight mutations, and exact recipe reconstruction. All 23 core
verification files remain unchanged from PR637. Python admission uses the
standard library; solver packages are needed only for historical search.

Chi Zhao prepared the new end, selective dispatch, packing and validation with
substantial OpenAI Codex assistance. Jeremy Kothe supplied PR637's CarrierBypass
construction and PR629's h4a lineage; Jeremy Diviney supplied PR627's factored
ends; DreamingOfClouds supplied the cold-end framework; Chafik Boukhalfa supplied
the PR626 interval engine; eumemic supplied the inherited PR543 bit supplier.
Original notices and licenses remain in `NOTICE.md`. Pinned source roles are
recorded in `PROVENANCE.json`; `owner-search/` reconstructs the literal map from
pinned PR639 using 235 recorded row replacements.

This remains a conditional finite certificate. All-size compilation, common
labels, mutable-source realization, whole-call hosting, precision/tape/exact
recovery, analytic transfer and bit H1–H5 remain inherited premises. PR543 is
repriced, not rebuilt. No unconditional theorem, practical speedup, or
unrestricted global optimality claim is made.
