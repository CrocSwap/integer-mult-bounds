# PR637 literal owner repair

The exact conditional saving is **κ = 0.001636456810414854**, or `818228405207427/500000000000000000`, exceeding pinned PR637's `0.001636448463297071` by `0.000000008347117783`. The conservative calculation gives `0.001636456807544675`.

This changes twenty literal owner rows from Jeremy Kothe's pinned PR637 (`4edb0dda99c495141cc56ae6e8a74e632a74db8a`). Both provider words, recipes, all 23 core code files and the 71 JP8 / 1 CK dispatch are unchanged. CK remains at chronological time 5, stage 2 / replica 0, forward orientation. Idle dimensions change from one 4 and one 32 to one 1 and one 35, with 2229 dimension 48 rows unchanged. All 35,424 roles retain legal physical owners and intervals. No packing-optimality claim is made.

**The full fresh replay passed all 64 stages without reuse**, followed by every
supplemental check in the wrapper. Both native suppliers, exact phases, physical
owner controller, 23 controller mutations, finite invoice, both moment engines,
and 114 admission controls passed. The independent native/owner/rational check,
five owner mutations, declaration reconstruction, exact owner reproduction with
four mutations, and independent Fraction/GF2 U4 check with six mutations also
passed. The [validation folder](../validation/) preserves complete replay archives,
receipts and the executed snapshot. Pinned PR637 separately passed a full fresh
64-stage replay. These runs were on macOS.

Reproduce with Python 3.10 or newer, a C++ compiler and Boost headers:

```sh
PYTHON=python3 sh research/pr637-improvement-20261013/witness637/verify.sh /tmp/pr637-improvement-fresh
```

The wrapper checks all frozen source manifests, rebuilds both native suppliers, phases, owners, invoice and exact inequalities, then runs independent native/owner/moment checks, five owner mutations, exact declaration reconstruction, the portable owner exporter and its four controls, and an independent Fraction/GF2 check of the four PR637 JP8 ends with six focused mutations. Python admission uses the standard library; solver dependencies are needed only to rerun historical searches.

`PROVENANCE.json` pins the original source and unchanged core code. `owner-search/` records the literal 20-row replacement exporter and search history; `README-UPSTREAM.md` and inherited proof notes preserve the upstream construction explanation, not the current owner-map result. All six external sources are vendored.

Chi Zhao prepared this owner repair and validation with substantial OpenAI Codex assistance. Jeremy Kothe supplied PR637's CarrierBypass native construction and base owner nomination; Jeremy Diviney supplied PR627's factored ends; Jeremy Kothe supplied PR629's h4a lineage; DreamingOfClouds supplied the cold-end framework; Chafik Boukhalfa supplied the independent PR626 interval engine; eumemic supplied the inherited PR543 bit supplier. Original notices and licenses remain in `NOTICE.md`.

This remains a conditional finite certificate. All-size compilation, common labels, mutable-source realization, whole-call hosting, precision/tape/exact recovery, analytic transfer and bit H1–H5 remain inherited premises. The PR543 bit supplier is repriced, not rebuilt. No unconditional theorem, practical speedup, latest-frontier or global optimality claim is made.
