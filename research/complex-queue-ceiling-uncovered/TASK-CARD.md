# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `complex-new-helper-inventory`, scope key
`5868e5281a1e63d41a22` (chooser track `complex-mechanisms`, OS-random nonce
`03cd0e6ed50226c5f8024d8ad5618d79`), refined to the queue-ceiling census's
uncovered claims.

Base commit; exact predecessor and dependency heads: base `0a201997097b8a89b638f3a2afcb35db4184c8b2`
(origin/main at session start). Predecessors: https://github.com/CrocSwap/integer-mult-bounds/pull/1240
(ceiling model, merged) and https://github.com/CrocSwap/integer-mult-bounds/pull/1264
(`research/complex-queue-ceiling-census`, its "Not covered" list is the domain).

Concrete object and question: the sixteen open complex kappa claims the census
listed as not covered (CrocSwap/integer-mult-bounds#1104, CrocSwap/integer-mult-bounds#1107, CrocSwap/integer-mult-bounds#1111, CrocSwap/integer-mult-bounds#1117, CrocSwap/integer-mult-bounds#1121, CrocSwap/integer-mult-bounds#1150, CrocSwap/integer-mult-bounds#1154, CrocSwap/integer-mult-bounds#1169,
CrocSwap/integer-mult-bounds#1172, CrocSwap/integer-mult-bounds#1175, CrocSwap/integer-mult-bounds#1176, CrocSwap/integer-mult-bounds#1183, CrocSwap/integer-mult-bounds#1192, CrocSwap/integer-mult-bounds#1201, CrocSwap/integer-mult-bounds#1207, CrocSwap/integer-mult-bounds#1218). For each, at its current
head: can the four screening inputs (paid per-call profile matching the title
kappa, idle histogram, live stock W, call count N) be extracted directly, or
bound to a known word through an exact companion-PR identity, and screened with
CrocSwap/integer-mult-bounds#1240's exact relaxation? For each still-unscreenable claim, what exact fields
are missing?

Scope status: refined. Reason: this is the card's "write the candidate per-call
profile and screen it with ceiling.ceiling(); reject routes without headroom"
first experiment, applied to the queue claims the census could not cover. It
implements the second follow-up of the CrocSwap/integer-mult-bounds#1166 handoff ("add
`local_profile_per_call` and `idle_histogram` to the uncovered claims' result
JSON so they can be screened") from the reader side; claim authors still own
their JSON fields.

Existing restriction being changed (or exact claim being audited): the census's
coverage condition, i.e. that a claim is screenable only when profile, idle
histogram and live/call counts are recorded together in one package.

Method; explicit parameter ranges/candidate alphabet: standard-library-only
extraction over each pinned PR head's package files (result JSONs, READMEs,
certificates), quoted exactly; screening via
`research/complex-local-word-ceiling/ceiling.py` at the unchanged model
parameters `ceiling(local, 73, 896, 9, 64)`; fixed domain = exactly those 16 PR
numbers at the heads pinned in the package snapshot.

Nearest overlapping PRs and why this adds something:
- https://github.com/CrocSwap/integer-mult-bounds/pull/1264 screens 14 of 30 claims and lists these 16 as not covered; this fills that list or records why each entry cannot yet be filled.
- https://github.com/CrocSwap/integer-mult-bounds/pull/1262 adds `local_profile_per_call` / `idle_histogram` fields to its own receipt; this is the consuming reader those fields were requested for.
- philippeVV's fork-only `k8-inventory-screens` screens leaver-line words (CrocSwap/integer-mult-bounds#1148/#1005 lineage); it does not cover these 16 claims.
Overlap searches for `local_profile_per_call`, `idle_histogram`, `uncovered`, `queue ceiling`, `screened`, `CrocSwap/integer-mult-bounds#1104`, `CrocSwap/integer-mult-bounds#1169`, `CrocSwap/integer-mult-bounds#1218`, `not covered` found no competing screening of the 16 (find_overlap.py, complete pagination, 723 open PRs / 268 discussion records, 2026-10-14T04:29Z).

Optimistic full cost budget; required observable improvement: review aid, no
kappa claim and no accepted/rejected claim. Observable: a per-claim verdict
table (screened word + cap, or exact missing fields), with at least one newly
screened word or an exact data-gap record for every one of the 16.

Success evidence; falsification test; time/compute cap: `verify.py` rebuilds the
verdict table from pinned blob bytes and rejects mutated snapshot rows (wrong
cap, dropped claim, forged profile match); compute under 2 minutes; one bounded
pivot maximum.

Predecessor authors; intended artifact and reproduction command: Douglas
Colkitt (CrocSwap/integer-mult-bounds#1240, CrocSwap/integer-mult-bounds#1264); the individual claim authors (tomdif, rohanarun,
Rohan Arun, Jeremy Diviney, and others as cited per claim). Artifact:
`research/complex-queue-ceiling-uncovered/`. Reproduce:
`python3 -I -B research/complex-queue-ceiling-uncovered/verify.py`.
