# Sprint claim

- Track: bit supplier. OS-random assignment seed: **17**, drawn with Python
  `secrets.randbelow(100)` on 2026-10-13.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Started: 2026-10-13 05:15 UTC. Planned handoff: **06:15 UTC**;
  reserve 06:00 onward for verification and packaging.
- Object: the four phase-A mini-nodes (frames 506–509) of the reviewed
  PR589 punctured R439 bit word, especially the three-destination frame 506.
- Hypothesis: interleaving external-input injections at different destination
  bases can beat the single injection layer in PR728, with every external
  register read at most once and never changed. Price all basis changes and
  the complete reverse cleanup; retain the exact dirty-input map and frames.
- Method: exact shortest-path search on GL(k,2) times the set of required
  external column patterns, k in {2,3}; seed 17 determines edge tie order and
  rotates the four-node inspection order to 507,508,509,506. This finite
  class permits injections at multiple intermediate bases, unlike PR728's
  single preparation/injection/recombination factorization.
- Deliverable: a circuit and exact replay/cost certificate if successful,
  otherwise a precisely scoped finite-class result; no new kappa claim.
- Stopping rule: complete this finite class once, then verify and hand off;
  at most one evidence-driven pivot, with no new research after 06:00 UTC.

## Selection and overlap

Three candidates considered: (1) these R439 mini-nodes with interleaved
injections, (2) sharing the R439 decoder's common operands, and (3) changing
one R439 phase-B frame schedule. Candidate 1 has a small exact search class
and a directly comparable predecessor. Candidate 2 is close to the crowded
R420 compensation/basis work; candidate 3 repeats mechanisms already searched
to a fixed point by PR589 without a new structural change.

Read CONTRIBUTING.md, selected-result.json, current-status.md, the review
ledger and contribution-review index; followed the selected certificate to
the K492 review and assembly and PR543's actual bit construction. The
selected conditional kappa is 0.001635527380375392 and is complex-bound.
Reviewed the preserved-research exclusions and searched the experiment
archive for this object. No prior interleaved mini-node search was located.

Open-PR metadata and PR728's source were inspected before this claim.
PR728, by Sagar Thakrar, is pinned at
`d454ae19fdd474b4dfa7bd2c28bbe5b0996365fb`; it saves 20 XORs in the same
four-node family but restricts all injections to one basis. We credit that
predecessor and will compare against its result, not claim its savings as new.
R420 PRs 670, 674, 681, 688, 694, 708, 713, 748 and 754 concern different
circuits or composition and are not imported. A fresh open-PR check through
PR764 found no interleaved R439 mini-node claim.

GitHub's pinnedIssues query returned an empty list (checked twice); the
only open issue was #650, about Discussions. Accordingly this is a local
claim, with no separate reservation issue. It will receive one result update
with the PR link or clean-patch handoff.

Prepared for Ryan Haines (@Ryan-Haines) with substantial OpenAI Codex
assistance. Apache-2.0; predecessor attribution is retained.

## Final result update — 2026-10-13 05:40 UTC

Submitted one focused contribution:
[PR792](https://github.com/CrocSwap/integer-mult-bounds/pull/792).
Status: **finite circuit construction with scoped exact optimality; no new
kappa**. All four interleaved mini-nodes attain minima 13, 9, 9 and 8 XORs,
saving 32 XORs including literal cleanup (24,305 -> 24,273), twelve beyond
PR728. The favorable one-read witnesses also attain the minimum in the larger
class allowing repeated reads; both reachable graphs were fully exhausted.

Verification: 866 states, 5,168 potential edges, 4,096 local Boolean inputs,
all 661 dirty-input columns, all frame paths, original H1-H5, unchanged C++
5/9/11-stage native replay on both words and 96 stock bridge controls. Native
payload remains 93 bits. Minimal-source relocation, corruption controls,
optimized Python, selected-record binding, Ruff and whitespace checks pass.
Hosted-parent/recursive invoices and a changed outer assembly remain outside
this contribution. Exact evidence and limitations are in VALIDATION.json.

Immediately before submission, the refreshed queue through PR790 still had
only PR728 in this mini-node scope. Its pinned head and main's base were
unchanged. No pinned coordination issue existed, so this is the single local
claim update. A clean base-relative patch and a short local handoff are also
retained in the session workspace. Research was complete before the final
verification/handoff period; the handoff precedes the user's cutoff.
