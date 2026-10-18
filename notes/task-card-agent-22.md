# Task card (autoresearch.md section 3)

Task ID / proposed scope key: `overlap-receipt` (consolidation track), scope key
757723e3fd38f20fa774, refined with nonce 6bc45fb7886eb99e0494a94781da0e58.

Base commit; exact predecessor and dependency heads: base main
1f7a934975e5eacaf83511c9ac870263bf095e05. Predecessor evidence:
research/community-reconciliation-fourth100-audit/{ARCHIVE.json,REVIEW.json},
docs/research/community-reconciliation-fourth100-review.md,
docs/research/pr-ledger.md (+ pr-ledger.json), CONTRIBUTORS.md. No code
dependency on any open PR head.

Concrete object and question: the seven PRs of the fourth100 reconciliation
whose contributed-package replay fails at the same vendored-witness MANIFEST
pin assertion (`assert sha(root/'MANIFEST.json') == src[...]` in
verify.py line 39): #636, #638, #639, #640, #642, #644 (vectorsss / Chi Zhao)
and #646 (jeremydiviney). For each exact recorded head: (a) is the recorded
replay failure a content defect of the vendored witness package (registered
MANIFEST hash vs actual blob) or a checkout/normalization artifact, and (b)
what exact content of the PR set is already byte-retained in main's tree or in
pinned archives, with complete predecessor credit?

Scope status: refined. The card's question ("what content and credit of a small
named PR set has already been retained") is kept; the concrete set is chosen
because the ledger records one shared, precisely described unresolved question
for it and the fourth100 receipt is the existing receipt to audit.

Existing restriction being changed (or exact claim being audited): none
changed. Auditing the fourth100 disposition receipt's unresolved question for
this family ("Required contributed-package replay has not completed
successfully").

Method; explicit parameter ranges/candidate alphabet: exact git-blob-identity
comparison. Per PR head (git tree via the GitHub git/trees API at the recorded
head SHA) every changed path's blob SHA is matched against local main's tree
(git ls-tree -r 1f7a9349) and against pinned archive inventories; the witness
MANIFEST pin is recomputed from the exact bytes returned by the contents API at
the same head. No heuristics, no floating point; the domain is exactly the
seven recorded heads and their changed-path sets.

Nearest overlapping PRs and why this adds something: PR1572 (receipt for
PR148's 14 unresolved paths) is a different object; the live claim in
discussion 1166#discussioncomment-18915531 covers the selected-replay tooling
family #1101/#1142/#1151/#1277/#1361/#1509/#1646; the PR99->PR103 retention
claim (discussion 1166#discussioncomment-18912011) is another object. A
find_overlap pass with the refined object terms (witness635, "combined cold
ends", vectorsss, pr643-improvement) returned only the PRs themselves and
their downstream credit mentions; no receipt or audit of this family is in
progress.

Optimistic full cost budget; required observable improvement: no kappa claim
and no moment pricing apply (documentation/consolidation). Required
improvement: every one of the seven unresolved ledger questions is replaced by
an exact, checkable status (complete integration / partial retention / changed
head / content defect), and any missing predecessor attribution is named.

Success evidence; falsification test; time/compute cap: offline stdlib checker
recomputing the per-PR blob-retention counts and the MANIFEST pin verdicts from
committed JSON inputs, with omission/substitution rejection controls; the
smallest falsifying instance is one PR head (#636) where the recomputed pin
disagrees with the recorded failure. Compute cap: single-digit minutes of API
fetches plus one local pass; session timebox keeps the final quarter for
verification and handoff.

Predecessor authors; intended artifact and reproduction command: vectorsss /
Chi Zhao (#636/#638/#639/#640/#642/#644), jeremydiviney (#646), the fourth100
reconciliation authors and the ledger maintainers. Artifact:
research/pr636-family-witness-manifest-receipt/ (README with Open next
questions, receipt JSON, offline checker). Reproduce:
`python3 -B scripts/research_package.py --package
research/pr636-family-witness-manifest-receipt` (and its --check-only
validation before submission).

Attribution: Aaron Wang / navinor, with help from opencode.
