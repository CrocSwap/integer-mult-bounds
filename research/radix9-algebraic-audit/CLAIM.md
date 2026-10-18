# Sprint claim

- Contributor: William Lawyer, with substantial OpenAI Codex assistance.
- Track: adversarial mathematical audit; operating-system assignment seed 73
  (one Python `secrets.randbelow(100)` draw).
- Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Scope: PR628's radix-9 kernel coefficient enclosures and the coefficient-error
  interface of its submitted approximate factor certificate. Pin:
  `0768f97d06c623b8211e651543c66135796b62bf`.
- Method: isolate the real algebraic root of `x^3-3x+1` in `(3/2,8/5)`,
  use a rational square-root enclosure for its positive imaginary component,
  and derive kernel coefficients by division in `Q[X]/(X^6+X^3+1)`.
  This is separate from PR628's Machin-pi/Taylor-exponential enclosure engine.
- Domain: all six primitive embeddings of radix 9, plus every radix-9 row in
  the pinned factor certificate. Seed 73 selects index `73 mod 3 = 1` from
  the candidate radices `[7,9,16]` and will select coefficient mutation sites.
- Deliverable: scoped audit note, independent exact checker, deterministic
  evidence and mathematical negative controls; no new kappa claim.
- Start: 2026-10-13 05:27:13 UTC (2026-10-12 23:27:13 America/Denver).
- Finish deadline: 2026-10-13 06:27:13 UTC. Verification and handoff receive
  at least the final 15 minutes of the 60-minute budget.

## Selection and overlap

Three narrow candidates were inspected: (1) PR628's coefficient enclosure /
factorization interface; (2) PR666's excluded-prime modular lifting interface;
(3) selected cold-helper lifetime / no-later-touch accounting. Candidate (1)
was chosen because the independent closed-coefficient checks in PR628 cover
radices 4 and 8, while radix 9 can use a different exact algebraic method.
PR666 already supplies its own modular witnesses, and PR729 specifically
audits helper lifetimes. Neither rejected candidate is reopened here.

The required contribution guide, selected certificate, status, review ledger,
selected construction/review, retained recurrence note and research index
were inspected. At the recorded base, main selected #626 with #543, conditional
`kappa=0.001635527380375392`; this audit does not modify those sources.

The public inventory contained 597 distinct open PRs across six pages, with
a created-order refresh through #786 immediately before this local claim.
Related #663/#673/#689/#730/#744/#758/#784 concern dirty echoes;
#692 concerns weighted-stride inverses; #764 sharpens scan rounding;
#666/#668/#736 concern cyclic nonvanishing or arithmetic replay.
Their work is distinct from the radix-9 coefficient audit. Pending work is
not treated as accepted. A final overlap refresh is required before handoff.

The open issue search returned only #650 (Discussions), with no pinned sprint
coordination issue visible. The claim is therefore recorded locally, as
permitted by the sprint instructions; no reservation issue is created.

## Result update

Completed a scoped independent audit: all 54 coefficient rectangles across
six primitive radix-9 embeddings contain the independent algebraic enclosures.
Both submitted radix-9 factor rows pass the inherited target budget, and all
15 mathematical controls are rejected. No defect or new kappa is claimed.
See [PROOF.md](PROOF.md), [EXPECTED.json](EXPECTED.json) and
[VALIDATION.md](VALIDATION.md). Attribution is to William Lawyer with the
assistance disclosure and predecessor credits in [NOTICE.md](NOTICE.md).

The initial handoff refresh through #799 found the related #796 p-adic
valuation audit; it is credited and distinguished from this complex-enclosure
check. Main and the pinned PR628 head remained unchanged. Publishing access
was unavailable at that handoff, so a focused clean patch and prepared PR
description were produced. The subsequent publication refresh at
2026-10-13 06:07:46 UTC covered arrivals through #810. Related #803 and #804
were inspected and credited in NOTICE.md; neither checks these complex
coefficient rectangles and submitted factor residuals. Main and PR628
remained at the recorded pins. No remote coordination claim was posted.

The final submission check at 2026-10-13 06:14:25 UTC covered arrivals
through #811 (an unrelated JP8 circuit contribution). Main had advanced to
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; its selected certificate and
current-status note now identify #741 with #589 on #555, conditional
`kappa=0.001661202643272239`. The research base and audited PR628 head
remain pinned above. This audit neither changes nor verifies that new frontier.
