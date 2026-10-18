# Historical local sprint claim

- Track: adversarial mathematical audit; OS-random assignment seed **60**.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Started: 2026-10-13T05:50:00Z. Planned finish: 2026-10-13T06:25:00Z.
- Precise object: the Fourier coefficient l1 estimate in the incorporated
  `research/prime-power-cyclic-inverse/PROOF.md`, section "An inverse bound
  from Fourier coefficients" (PR621).
- Hypothesis: splitting low/high Fourier frequencies before Cauchy-Schwarz
  improves the dependence on the circle separation delta from inverse-square
  to inverse-three-halves, while preserving all cyclic lengths, integer
  strides and unit scalar gauges. This audits an overestimate, not an alleged
  defect in the accepted theorem.
- Deliverable: one standalone proof/audit package, exact rational budget
  comparisons, independently computed finite cyclic inverses, negative controls,
  pinned source provenance and a focused PR or clean patch. No new kappa.
- Three candidates considered: (1) Fourier transfer accounting in #621;
  (2) early-ended helper lifetime checks in #626; (3) generalized R/R0 assembly
  accounting. Candidates 2 and 3 overlap #729 and #724/#766 respectively.
  Seed 60 selects candidate index 0 modulo 3 and seeds deterministic finite
  fixture ordering. Initial method was a frequency split; the completed
  derivation uses periodic total variation of finite Fourier polynomials
  for a stronger constant. Method diversity is this analytic estimate,
  not the seed itself. This refines the same claimed transfer step.
- Initial overlap review: selected certificate/review, central review ledger,
  all open issue search (only #650, no pinned sprint coordination issue),
  45 recently updated PRs through #795, and targeted cold audit, cyclic,
  Fourier bound, rounding and Sobolev queries. #668 and #666 concern
  resultant certification/composite lifting; #764 concerns rounded scan
  execution and does not refine #621's Fourier transfer estimate.
- Claim recorded locally because there is no pinned coordination issue.
- Delegated work stays within this Fourier transfer audit: independent proof
  scrutiny and a finite inverse oracle. Reserve the final quarter for
  verification and handoff. Do not change the selected frontier or upstream/.

## Completed result

The same scoped transfer admits the stronger rational square bound
`delta^-2 + (44/7) M delta^-3`; a periodic total-variation argument improves
the initially proposed frequency-split constant. Independent derivation and
adversarial review found no mathematical defect. Exact evidence includes
648 generic finite inverses, 200 Fourier sequences, all 26 prime-power
parameter substitutions through 64, and explicit negative controls.

Final overlap refresh on 2026-10-13: recent queue through #802, targeted
Fourier-title search, and the newly arrived #796 body. #796 proves p-adic
root valuations, explicitly not sharper complex conditioning; this work
addresses a different step. Main remained at the pinned base.

No pinned coordination issue exists, so this is the one local claim update.
Prepared as a clean patch because the connected account has read-only
upstream access, no existing fork, and no exposed fork-creation operation.
No issue/PR was created or modified; no merge or frontier selection occurred.
The reviewable package and handoff identify the exact base and commands.

## Publication preparation (2026-10-13)

The preceding claim and access limitations record the original research run.
A fork is now available under ThiagoCAltoe. Publication uses upstream main
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. The four predecessor source hashes
are unchanged; only the selected-result context pin advances with main.
The queue refresh through PR824 identified Rafael Guevara's PR803 on the same
conditioning step, proposing the stronger degree-controlled bound
`(1+4 degree(P))^2 / delta`. It is credited in the README, source record and
notice. This submission is an independently prepared Sobolev-based audit,
not a strongest-current-bound or priority claim. PR820 concerns separate
radix-9 coefficient/factor certificates. No concurrent implementation is
imported, and no selected frontier or upstream file is modified.
