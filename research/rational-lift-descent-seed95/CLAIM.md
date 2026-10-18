# Local cycle claim

Claimed 2026-10-13 18:34 UTC. Finish by 19:07:23 UTC, with verification and
handoff beginning no later than 18:57:23 UTC.

- OS-random seed 95, research consolidation.
- Base `ba82555c64e1879e4b7decce28186f208fcb8262`.
- Branch `research/cycle06-seed95-rational-lift-descent`.
- Exact object: the fixed-reader single-lift identity for a rational matrix X,
  and the attainable supports of its original and added rank-one terms.
- Hypothesis: every lift over a characteristic-zero extension of Q has a
  rational lift preserving each term's support pair, hence every support-only
  copy cost. A finite-field example should show why descent needs a field-size
  condition.
- Method: consolidate the reciprocal-projection proof in the retained
  `p112-complex-single-lift` package into a finite-dimensional linear-functional
  argument over an infinite base field. Check exact quadratic-extension
  witnesses and a minimal F4-to-F2 failure independently of predecessor code.
- Deliverable: written theorem and boundaries, exact runnable certificates,
  source pins, negative controls, and a concise cycle handoff. No new kappa,
  supplier implementation, global regeneration, or selected-frontier edits.

Three candidates were considered. U8 terminal-cone cleanup is already covered
by PR988 and its reviewed package. The selected PR1042 invoice is covered by
PR1112, with cell semantics covered by PR1049 and owner maps by PR1091. Rational
descent of support patterns is distinct from these and from PR1098's label-free
Gram spectra. No reservation issue is opened. The immediately preceding scan
covered all 774 open PRs through #1120 and recent issue comments; the repository
has no pinned sprint issue. The claim therefore stays local.

Acceptance: a proof valid for every finite X over the stated field, exact
support equality for the finite examples, explicit rejection of wrong direct
projection and missing support constraints, and a valid finite-field boundary
counterexample. Finite examples alone will not be described as the theorem.
This is a support-only consolidation, so there is no optimistic paid supplier
to implement or cost improvement to claim. Precision, restoration, hosting,
tape, and compiler costs remain outside the theorem.

## Completed result, one claim update

2026-10-13 18:53 UTC. Published
[PR1133](https://github.com/CrocSwap/integer-mult-bounds/pull/1133).
The written infinite-field theorem proves rational representatives with
identical term supports for rational X. Nine exact examples, 162 scalar
lifts, five mathematical controls, the F4-to-F2 boundary, and relocated CLI
controls pass on CPython 3.11.15 and 3.14.8. The separate integer-coordinate
premise check passes for all 896 P112 entries. No new kappa is claimed.

The final overlap refresh covered all 747 open PRs through #1132, then the
twelve latest PRs again immediately before publication, plus recent comments
and the absence of pinned sprint issues. PR845 and PR998 retain their reviewed
heads. The source dependency files remain unchanged at refreshed main
`ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, which now selects PR1094 at
`836330098538459/500000000000000000`. The original base is retained.
Neither `codex` nor `codex-automation` is an available repository label.
No other contributor's PR was changed.

Verification and handoff began by 18:42 UTC, leaving more than ten minutes
before publication and final handoff. The declared finite checks are complete;
no coefficient-height, multiple-total, paid-supplier or new decoder search
was started. Full `make verify`, selected cold replay, Linux and formal proof
were not run. The code and mathematical certificate were committed as
`0d4fda24e060b3c14e5df5aa4526fdc5cbea79f5`; this result update adds only the
publication and coordination record.
