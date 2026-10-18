# Complex-supplier research claim: coupled read exchanges

Prepared for Jason Willems (@at1as) with substantial OpenAI Codex assistance.

- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Separate branch: `research/complex-kappa-seed21`; completed PR #666 is unchanged.
- Track: complex-supplier improvement, deliberately selected following the user's
  request to try improving kappa. Diversification seed **21** was drawn once from
  20..39 using operating-system randomness, not from the gist's unrestricted
  0..99 track lottery. This choice is recorded explicitly.
- Claim recorded: 2026-10-13 04:58 UTC (2026-10-12 America/Los_Angeles).
- Initial bounded session: aim to finish by 06:15 UTC, reserving at least the final
  quarter for validation and handoff; do not assume an improvement exists.
- Object: two simultaneous partial entering-copy read-set exchanges on the
  promoted P6k4 input to PR #699, retaining its fixed helper boundaries and
  owner map. Compare with its four-exchange output, not merely with old #626.
- Dependency: #699 at `03e8d7ca494a083e5053cd6b1228f66b98414479`, plus its
  pinned #635 source. The main selected result remains #626/#543. #699 and
  #589 are pending/conditional dependencies, not newly accepted frontiers.
- Hypothesis: moves individually rejected by target-frame containment might
  become legal together because one shrinks a frame needed by the other.
  A complete paid-profile reduction at unchanged widths can improve the complex
  moment while preserving the owner assignment and unchanged #589 bit headroom.
- Method: enumerate entering-copy candidates from the literal word, test
  simultaneous choices with exact binary frame arithmetic, and check arbitrary
  input scalar equality for legal candidates. Price the full paid profile,
  including sources, targets, centers, tails, helper ends and idle owners.
- Deliverable: a verified improving construction if found; otherwise a precisely
  bounded completed search and reproducible evidence, with no impossibility claim
  outside its enumerated class. No unsupported new kappa claim.

## Candidate selection and overlap

Three narrow candidates: (0) coupled partial entering-copy exchanges;
(1) mixed-beta nine-term decoders on P112; (2) joint A/cleanup regrouping.
Seed 21 modulo 3 selects candidate 0, after checking that its scope is open.
Candidate 1 has larger potential but requires a new decoder/factory interface;
candidate 2 is less sharply bounded and borders earlier failed regrouping searches.

Read CONTRIBUTING.md, the selected certificate, current status, PR ledger,
#626 construction/review, and retained negative-search summaries. Refreshed **551
open PRs through #732**. No pinned coordination issue exists, so this claim is local.
#699's `construction/sw4/NOTES.md` explicitly reports 602 single-pair candidates
and says cross-pair partial combinations were not enumerated. #698 fixes the
scalar word and gate order, #687 moves one read in one raw K-triangle, and #651
fixes role and delivery rules; these do not close the present simultaneous class.
Owner packing, existing entrance promotions and single-pair exchanges are not
claimed as new work. Scalar primitive reductions alone do not improve kappa.

Search domain, stopping rule, source hashes, completed coverage and any pivot
will be recorded with the experiment. Delegated work is limited to reproducing
this pinned baseline and reviewing this specific rewrite and its complete cost.

## Evidence-driven follow-up

The complete two-pair domain contained 175,456 joint choices across all 1,431
pairs, requiring both selected masks to be nonempty and at least one partial.
All were rejected by target caps. A preceding shared-direct-target subdomain
covered 5,840 of those choices. The direct-target overlap graph on the 54 eligible
pairs has 16 connected components of size three and six isolated vertices.
One bounded follow-up therefore tests all simultaneous nonempty choices in
those 16 three-pair components, still requiring at least one partial and keeping
known SW4 moves on untouched pairs. This tests a possible three-way repair
without reopening arbitrary gate permutations or unrestricted multi-pair search.

## Completed result and handoff

Completed this claim in [PR #775](https://github.com/CrocSwap/integer-mult-bounds/pull/775).
The two-pair domain rejected all 175,456 parameterized cases; the bounded
three-pair follow-up rejected all 27,344 cases in the 16 connected triples.
These are case counts, not counts of distinct completed rewrites. Both independent
engines agreed on every first-refusal digest and the finite coverage. The public
optimized Python 3.13 replay passed, including the exact 728-column SW4 scalar
control and all 13 focused tests; Python 3.11 checks also passed.

No legal improving candidate was found and no kappa improvement is claimed.
The exclusion applies only to the pinned word and the documented eligibility,
insertion, boundary and frame-floor rules. The direct-target graph does not prove
circuit independence, and arbitrary triples and larger combinations remain open.
The final overlap refresh covered 586 open PRs through #767; #741's frame-growth
construction is credited as a separate approach. This bounded experiment is
complete. Further search classes belong in a separate research claim.
