# Local sprint claim

- Track: adversarial mathematical audit; OS-random assignment seed **69**
  (`secrets.randbelow(100)`, drawn once on 2026-10-13 UTC).
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: the multi-digit carry and exceptional-stream repair interface in
  `notes/compact-control-movement.tex`, as implemented by
  `scripts/audit_compact_controls.py`.
- Method: an independent exact address interpreter; finite exhaustive two-digit
  rectangles with nonempty good sets, including arbitrary dirty front/back
  fields; explicit destination-key/hole permutation verification and adversarial
  carry/repair controls. Seed 69 prioritizes the later-source case and maximal
  selected-bit offset. No new supplier, kappa, or tape-runtime proof is claimed.
- Deliverable: a source-pinned standalone research audit, deterministic receipt,
  reproducible command, mathematical scope and negative controls.
- Planned finish: 2026-10-13 05:36 UTC; reserve final quarter for verification and
  handoff. Stop after the stated finite domains, with at most one evidence-led
  pivot.

## Selection and overlap

The three candidates were (1) compact-control inter-digit carries and repair,
(2) selected-provider helper-frame lifetimes, and (3) balanced Gaussian assembly
constraints. #729 already audits (2); #684 and #701 cover substantial parts of
(3). Candidate (1) adds multi-digit and actual hole-filling evidence beyond the
existing one-segment exhaustive test and multi-segment random samples.

At selection, GraphQL returned no pinned issues. The open issue inventory
contained only #650 (requesting a discussion channel), not a sprint issue.
A live snapshot of 551 open PRs through #730 was inspected for overlap,
including titles and body searches for compact controls, selected-bit,
exceptional sets and guards. No matching carry/repair audit was found.
This local claim follows the sprint's no-coordination-issue fallback.
Delegated review is confined to this same interface.

## Completed result and handoff — 2026-10-13 05:14 UTC

Submitted [PR #763](https://github.com/CrocSwap/integer-mult-bounds/pull/763),
**Research audit: compact interior carries and exact exceptional repair
(no new kappa)**. The result proves the guarded interior-carry formula and
that the highest source-control digit need not be excluded. The finite audit
passes 1,310,720 representative addresses, 3,072 source comparisons and seven
negative controls. The full proof, exact domain, pins, provenance and remaining
obligations are in this package's README and proof; production sources and
selected κ are unchanged.

Verification and handoff occupied the final portion of this bounded run:
optimized-Python replay, 17 relevant existing tests, selected-record check,
clean dependency export, source-drift rejection, and final scoped review all
passed. No full repository suite, supplier cold replay or remote CI result is
claimed. There was no coordination issue to update publicly.

Before submission, 576 open PRs through #756 were refreshed, followed by a
last title/head check through #762. Concurrent #735 at
`8d36139e49add1e55795e283b3bfa45e1cfe1bf0` audits the original wide-slot
primitive, not this compact primitive. Its related guard-envelope result is
credited in README; no source or result from it is consumed.
