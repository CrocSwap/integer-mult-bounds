# R420 exterior frame audit

Status: completed on 2026-10-13. GitHub returned no pinned issues; the claim
was recorded locally before implementation.

- Track: independent verification; OS-random assignment seed 83.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: every rational frame of eumemic's selected PR543 R420 bit word,
  including its closed root-line set and the nested moves used by that word.
- Method: primitive exterior coordinates and contraction projectors over exact
  integers, with seed-83 input ordering. No import of the predecessor rank,
  Hermite-normal-form, determinant or geometry routines.
- Deliverable: standard-library verifier, exact receipt, mathematical explanation,
  source pins and negative controls. No new kappa or full theorem claim.
- Expected finish: 2026-10-13 05:25 UTC. Final 12 minutes reserved for checks
  and handoff.

Three candidates were considered. PR543 moment verification overlaps #678;
selected cold-wrapper verification overlaps #702 and #712. This frame audit
instead supplies a separate algebraic method for the finite geometry obligation.
The initial scan covered 535 open PRs through #716. #707 accelerates the existing
Gram checker; #709 caches the existing geometry checker; #612 formalizes literal
boundary and scalar interfaces. Their results are credited but are not code
dependencies. No exterior-coordinate projector audit was found in that scan.

Acceptance requires exact checks for all frames and all distinct ordered frame
transitions in D/A/scatter/B/C/finalization, dyadic projector denominators,
closed line sets, expected source/target endpoints, and rejection of deliberately
broken geometry. Scalar XOR semantics, hosted invoices, analytic bounds and
all-size realization remain outside this contribution. Existing sources,
`upstream/` and the selected frontier remain unchanged.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, Apache-2.0.

## Result update

All 672 frames passed the independent exterior audit, including 2,460 distinct
nested pairs, 66,240 nonincidences and dyadic basis/Gram witnesses. The complete
certificate reproduces with 258 positive oracles and 11 rejected controls.
The selected kappa is unchanged. The final overlap scan covered 549 open PRs
through #730, followed by the new #731/#732 heads immediately before submission.
No duplicate rational-projector audit was found. Verification and its limits
are recorded in the README. No issue or PR belonging to another contributor
was modified.

The reviewable result is on
[the contribution branch](https://github.com/thakrarsagar/integer-mult-bounds/tree/research/r420-exterior-frame-audit/research/r420-exterior-audit).
One focused upstream PR will carry this branch; no merge is requested.
