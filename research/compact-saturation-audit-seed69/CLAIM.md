# Compact saturation audit claim

Claimed 2026-10-14 01:04 UTC. Track: adversarial mathematical audit.
OS-random assignment seed: 69, drawn with Python `secrets.randbelow(100)`.
Base: `410026dc5513b87db92ae98571d1d5984c69a983`.
Expected finish: 2026-10-14 01:47 UTC; hard session budget ends 01:57 UTC.
Verification and handoff start by 01:42 UTC at the latest.

Question: for the unchanged earlier-source compact-control word, what is the
exact complete-map agreement criterion when temporary digits may saturate,
and what is the largest subset of that agreement set invariant under the
intended selected-bit XOR? Test whether agreement alone suffices for repair.

Dependencies: Douglas Colkitt's retained movement note and physical simulator;
Hanson Sun / bbMisk's PR1219 at
`dfb453c88b03868d346014867a091d36e7b16589`; the adjacent one-digit PR1108 at
`b76bb2853be4e7001508582b10913e32ad7aba9f`. PR1247 at
`392316a45197ef213cff4febd24aa7fd5e16237f` is later-source work outside this scope.

Method: derive target/compact carry recurrences, exact weighted transfer
counts, then compare an independent integer implementation with complete
small permutations and the original physical interpreter. The all-n domain
is n>=1, G>=1, K>=G+1, 0<=rho<K. Finite domains and seed-69 samples will be
recorded separately. Seed69 chooses G=1+(69 mod 2)=2 for the headline fixture.
Stop after the proof, finite-domain checks and one scoped package; do not
search supplier profiles or claim a runtime or kappa improvement.

Three candidates considered: this saturation/invariance boundary; PR1197's
two-total quotient obstruction; PR1367's tangent-to-orbit regularity step.
The latter is already a second audit in a busy rigidity family. The former
changes PR1219's explicit nonsaturation hypothesis and targets multi-digit
compact carries, distinct from PR1108's one-digit law and PR1247's two-pass
later-source guard. It is not another nonsaturated guard census.

No pinned coordination issue exists, so this is the local claim authorized by
the task. The immediately preceding overlap report covered 823 open PRs and
158 discussion records with complete pagination, fetched at 01:01:21 and
01:01:51 UTC. It found PR1108, PR1219 and PR1247 as the relevant predecessors.
The review ledger and local research notes were also inspected. Text search
does not establish novelty. Refresh metadata before submission.

Expected deliverable: written scoped proof, exact counts and counterexamples,
one reproducible standard-library verifier, pinned sources and negative
controls. Prepared by Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0. No subagents or independent human review.

## Completed result, 2026-10-14 01:22 UTC

DONE: [PR1475](https://github.com/CrocSwap/integer-mult-bounds/pull/1475).
Scope released. This is the claim's single result update.

Established an all-n exact complete-map agreement criterion with saturated
temporary digits and the largest XOR-invariant subset of that agreement set.
The invariant guard has exact transfer-matrix density 1499/2048 at
n=2,K=6,G=2, versus PR1219's 567/1024. The larger raw agreement set is not
invariant; the wrong current-address guard fails on 88,156 of the enumerated
states. No defect in the retained construction, runtime gain or new kappa.

All 1,196,544 complete quotient states, 38,080 local transitions, 1,536 physical
samples, sorted repair payloads and seven named controls pass. Eight algorithm,
six source and two receipt corruptions were also rejected. The registered
Python 3.12 replay, optimized Python 3.11 outside the checkout, 17 existing
compact-control tests, five selected-record tests and selected integrity pass.

Final overlap: 828 open PRs, 162 discussion records, 328 local records, complete
remote pagination and no warnings. Relevant predecessor heads are unchanged.
The branch was rebased onto refreshed main
`4040a0f46d67b41c36a472a7cd4af791fd4c36cc`; all consumed files and applicable
rules are unchanged from the research base. No pinned coordination issue or
codex/codex-automation labels exist. Hosted CI success is not asserted.

Review PROOF.md Sections 2-4, particularly the distinction between exact
agreement and an invariant repair guard. Later-source composition and physical,
tape, recursive hosting, precision and analytic admission remain outside
scope. Verification and handoff began by 01:12 UTC, exceeding the final-quarter
reservation. Exactly one focused PR; no merges, closures or scheduling changes.
