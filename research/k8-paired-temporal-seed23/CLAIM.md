# Paired temporal gauges with zero nonscalar boundaries

Claimed 2026-10-13 23:32 UTC by Sagar Thakrar, with substantial OpenAI Codex
assistance. Apache-2.0. Track: complex supplier. OS-random assignment seed: 23.
Exact base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Branch: `research/cycle15-seed23-paired-temporal`.
Expected finish: 2026-10-14 00:07 UTC; verification/handoff starts by 23:57 UTC.

## Candidate tasks and choice

1. Another constant multihelper gauge. Declined: PR1263, PR1310 and PR1322
   already cover coordinate, pair and coherent-triple moves.
2. Another single-helper temporal gauge or independent composition. Declined:
   PR1259, PR1270, PR1350 and PR1353 cover that mechanism; fresh Discussion1163
   claims cover zero-static helpers and L248/L253 composition.
3. Jointly optimize *interacting* temporal gauges with zero at every nonscalar
   boundary. Selected. Shared ADDs depend on the difference of the two gauges,
   so independent minima need not compose. This changes the optimization class.

## Exact scope and method

The selected PR1094 provider is the byte-identical seven-slot k8 provider in
the retained PR1042 archive. The eligible inventory has 237 cold/FULL,
unwrapped, non-center helpers without COPY/CLEAR. Its forward ADD interaction
graph has 2,414 unordered pairs. Seed23 selects sorted pairs [23:39]:
`(225,342), (225,347), (225,348), (225,350), (225,351), (225,352), (225,356),
(225,367), (225,379), (225,384), (225,388), (225,391), (225,395), (225,399),
(225,400), (225,401)`.

For each pair and both orientations, optimize both exponents in [-4,4] before
every incident ADD. Both gauges must be zero at every nonscalar event and at
entry/exit. All other gauges are zero. Keep every original event, SCALE,
operand, frame, and recursive child. Charge changed ADD lowering, every
transition SCALE, and every reset. Use an exact two-dimensional shortest-path
recurrence and a separate dense transition oracle. Complete all 32 cases;
no enlarged box or further pair search is planned. This is a finite-domain
experiment, not an all-integer or global optimum claim.

An optimistic complete scalar budget is the sum of all original macro prices,
changed ADD prices, and L1 variation of both exponent paths, including resets.
Only a negative complete delta is an improvement. A useful paired result must
also explain shared-ADD coupling relative to the independently optimized paths.
Paid recursive profiles stay fixed, so no new kappa follows from scalar savings.

Expected artifact: one source-pinned finite construction or scoped negative
result, deterministic verifier/certificate, meaningful adverse controls, full
712-column scalar replay, and explicit local precision/frame limits.

## Coordination and predecessors

No pinned sprint issue exists, so this is the local claim requested by the
donor. At entry, 838 open PRs and all 38 discussion bodies were inspected;
Discussion1163's seven comments were read, including its two active temporal
claims. The overlap helper is refreshed before substantial work and submission.
Nearest sources: woklerx PR1161, Hanson Sun/bbMisk PR1214, Sagar Thakrar PR1259,
Philipp/mightyOil PR1263/1270/1310/1322 and Cinna Davis/1337isnot1337
PR1350/1353. PR1350's L253/L254 follow-up is a different pair and background.
Existing k8 supplier and lowerer attribution is retained in the final note.

The selected conditional kappa remains `836330098538459/500000000000000000`.
Inherited compiler, common-label/mutable-source, hosting, precision/tape,
analytic and bit H1-H5 obligations remain. No selected/frontier or upstream/
files will change.

## Completed result, 2026-10-13 23:49 UTC

Submitted [PR1380](https://github.com/CrocSwap/integer-mult-bounds/pull/1380),
research commit `094204c9689a0185855b8c7ba35763d1a6598995`.
All 16 selected pairs and both orientations are complete, with no box expansion
or pivot. Five pairs have a strict coupling gap. L225/L350 has the largest:
-237 real primitives jointly versus -234 for the best composition of every
tied independent optimum. Complete scalar bills become 148,528/148,544, saving
474 per complex invocation in each orientation. The six-primitive coupling
advantage is isolated to one block and one shared ADD, with an exact 9-by-9
conditional-cost witness. No new kappa or physical supplier invoice is claimed.

Two optimization implementations agree on 49,693,014 transition candidates;
all 712 scalar columns, all changed frames and nonscalar boundaries, full
literal prices, unchanged paid profiles, local precision, 729 tiny paths and
twelve rejection controls pass. CPython3.14.8 and optimized3.11.15 pass, including
outside-checkout execution and an external saved-certificate corruption check.
Seven source/context Git blobs and selected-record integrity pass. The saved
certificate SHA256 is `3c59f72bcd0768bf0740edebcb09427bcd48659b8bcbba762a0e30ca53aa2afc`.

The final overlap refresh covered 850 open PRs after the complete 94-record
discussion refresh at23:44. New PR1369 and PR1376 are credited with exact heads.
PR1376's disjoint objectives separate; this result proves a strict interaction
for a different pair and background. The source main remained at the same base
on the final fetch. No pinned issue existed, so this local claim receives its
single result update and is now released. Neither `codex` nor
`codex-automation` label exists in the target repository.

Verification/handoff began before23:43, well before the23:57 cutoff. Native and
hosted admission, full cold replay, unbounded exponent optimization and formal
or human review remain unrun. Review the small coupling witness and the
scalar-cost versus complete-physical-cost boundary first.
