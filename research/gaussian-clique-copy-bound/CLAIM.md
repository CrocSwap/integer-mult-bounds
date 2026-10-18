# Sprint claim

- Track: structural decoder research. OS assignment seed: **46**, drawn with
  Python `secrets.randbelow(100)` on 2026-10-13.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Object: the 60 Gaussian E8 lines in PR620's extension-ring notes, with scalar
  binary totals and arbitrary asymmetric fitting decoders.
- Method: exact nonorthogonal-clique rank inequalities, averaged over a finite
  clique family, with geometric flat enumeration to bound each total's charge.
  The even seed selects Gaussian rather than Eisenstein geometry. No randomized
  search or extension of the predecessor's timed CP-SAT search is planned.
- Deliverable: one scoped copy-cost bound or exact limitation of this method,
  a written argument, source pins, and a standard-library replay with controls.
- Time budget: 40 minutes from 04:42 UTC; selection ends by 04:50 UTC,
  verification and handoff start by 05:12 UTC; finish by 05:22 UTC.
- Coordination: no pinned issue exists as of 04:43 UTC. Open PR metadata and
  recent comments were checked. PR703 resolves Hurwitz E8 using averaged rank
  inequalities; this contribution credits that method and investigates the
  distinct rank-four Gaussian geometry. PR631 covers real E8 punctures,
  PR669 hypercube stars, and PR715 minimal mixed-port extension saturation.

Candidates considered: higher-rank ordinary E8 fitting-matrix perturbations;
Gaussian E8 asymmetric copy costs; Eisenstein E8 asymmetric copy costs. The
Gaussian task has a small exact geometric domain and a predecessor lower bound
that does not close the copy-cost question. Workers are restricted to this scope.

Prepared for @thakrarsagar with substantial OpenAI Codex assistance.

## Result update

Completed the [reviewable contribution](README.md): every decoder in the
claimed class costs at least 40 Gaussian / 80 rational rank units. All
2,579,856 nonempty unordered flat pairs are covered. The uniform maximum-clique
weight is sharp, witnessed by a rank-two/rank-three flat pair of pairing rank
one. The true optimum remains in [40,60]. Under the inherited Dfc formula,
three stages cannot give positive deficit; five or more stages remain open.

The exact certificate, six controls, selected-record integrity and relocated
Python 3.11 replay pass; Python 3.14 also passes. Source/certificate corruption
and optimized execution are rejected. Sources, attribution and limits are
recorded with the result. No new kappa or physical supplier is claimed.

Final overlap refresh at 04:58 UTC covered 551 open PRs through #732. Main
remained at the recorded base after fetch, and there was still no pinned
coordination issue. #703 remains credited for the weighted clique method;
#717 concerns complex P112 decoders and schedule/accounting notes, not this
Gaussian copy-floor census. Its schedule erratum does not alter the Dfc
premise used here. No overlapping Gaussian result was found.

Public branch package after submission:
https://github.com/thakrarsagar/integer-mult-bounds/tree/research/seed46-extension-decoder/research/gaussian-clique-copy-bound
