# Sprint claim

- Track: structural decoder research; OS assignment seed **48**, drawn with
  `secrets.randbelow(100)` at 2026-10-13 05:22:15 UTC.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: scalar binary asymmetric decoders on the **40 Eisenstein E8 lines**
  of PR620, charged by rational pairing rank divided by two.
- Method: reconstruct the rational order-three geometry, enumerate its
  maximum nonorthogonality cliques and all line-matroid flats, then certify
  the strongest uniform clique weight on every flat pair. Use the weighted
  clique argument credited to PR703 and PR738, in this different geometry.
- Deliverable: a scoped copy-charge bound or exact limitation of this
  method, a complete finite certificate, negative controls and a paid-format
  optimistic screen. No new kappa is promised.
- Three candidates considered: (0) Eisenstein asymmetric copy cost;
  (1) the remaining Gaussian decoder gap; (2) P112 decoders beyond frame
  partitions. Recent Gaussian/P111 work makes (0) less crowded. Seed 48
  fixes the independent rank-control samples and distinguishes line 8
  (48 modulo 40) for the saturated-singleton dual rejection obligations.
- Prior work: PR620's extension-ring solver reports leave the asymmetric
  Eisenstein cost unresolved. This changes the proof method and covers any
  finite number of totals, rather than extending a timed-out solver run.
  PR703 handles ten Hurwitz lines; PR738 handles 60 Gaussian lines; PR767
  handles Gaussian subclasses. None supplies the Eisenstein certificate.
- Coordination: no pinned issue existed at the fresh pre-claim check;
  no separate reservation issue was opened. Open PR metadata through #769
  and the review ledger were inspected, including PR620's partial status
  and PR446's unreviewed status. No matching Eisenstein/Witting claim was
  found in the open PR search.
- Budget: 45 minutes from 05:22:15 UTC; stop investigation by 05:56 UTC
  and reserve the final quarter for verification and handoff. Expected
  finish: **2026-10-13 06:07 UTC**. Stop after the complete finite clique/flat
  domain; do not broaden to other geometries or claim decoder optimality.
- Contributor: Jonathan Lam (@jonathanlam), with substantial OpenAI Codex
  assistance in research, implementation and verification; Apache-2.0.

## One result update — 2026-10-13 05:48 UTC

Completed: **C ≥ 22 Eisenstein rank units**, and an exact matching dual proves
that *all* nonnegative clique-weight certificates have optimum 22. The actual
decoder optimum remains in [22,40]; no new κ is claimed. The same finite
domain gave one refinement: the maximum-clique-only bound 280/13 saturated,
so singleton inequalities were added, and the resulting all-clique dual
closed this proof method at 22. No other geometry or supplier was searched.

Coverage: 772 flats, 298,378 unordered flat pairs, 40,054 cliques, eight
mathematical controls, and an independent modular/Fraction arithmetic check.
Python 3.11/3.12 replay, three packaging tests and selected-record integrity
passed. Final PR metadata covered 614 open PRs through #795 with no matching
Eisenstein contribution. Origin/main remains at the claimed base.

Deliverable: [proof and reproduction](README.md), [validation](VALIDATION.md),
and the [focused contribution branch](https://github.com/jonathanlam/integer-mult-bounds/tree/research/eisenstein-clique-bound-seed48/research/eisenstein-clique-copy-bound).
One research-note PR is the intended handoff; no frontier edit or merge.
