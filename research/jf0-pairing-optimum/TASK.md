# Independent jf0 pairing-cost audit

Task: portable-replay; scope status changed. The selector drew verifier-engineering
with nonce 05def5c4e1ed792501eda6cba1f2a576, scope key 831cc1a3c8f9ff01b197.
Override: take DreamingOfClouds explicit independent-check handoff, item 4 in
Discussion1166 comment18934590, rather than repairing a generic portability issue.
This is an exact finite decoder-rank audit with a dependency-free certificate.
Base: 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2, priority revision4.
Predecessor: PR2162 113a718265c62aec301c5695f4bfb9c421bef7ab,
research/char2-jets/data/jf0.json. Exact object: eleven rational P,Q line pairs;
all binary 11x11 B with diagonal1 and off-diagonal entries supported only on
P_i dot Q_j=0. Objective: sum of three F2 ranks B[R_j,A_j].
Method: universal triangular-minor lower bounds plus an explicit admissible
upper witness; no SAT assertion accepted without independently checked evidence.
Domain: all 2^41 binary pairings from41 rational incidences. All41 entries
belong to at least one charged block; none are omitted. Arbitrary asymmetry
is allowed. The domain is covered by proof, not exhaustive enumeration.
Completed result: coordinate minors of sizes6,6,7 give universal lower19;
the identity plus both directions of (2,8),(3,4),(9,10) attains19.
Required improvement: close exact minimum or report rigorously improved interval.
Falsification: a bad order, missing support, nonzero rational incidence or rank
miscount invalidates certificate. Exact independent elimination and semantic mutants.
Cap: remaining 45 minutes, reserve final15 for verification/publication/cleanup.
Credit: DreamingOfClouds with Claude Opus5.5 for the configuration, prior >=16
SAT result and requested audit; prior decoder framework #1590/#2111. No kappa,
physical supplier, polynomial-time universal minrank or formal kernel claim.
Worktree owned only by this automation run; specialists share disjoint files.

Nearest overlap: PR2162 at the head above, and its explicit handoff item4.
Fresh entry helper:418 open PRs,850 Discussion records, full pagination;
only the source/request match jf0/char2-jets. Source data belong to the
predecessor; this adds a solver-free exact minimum, independently checked.
Current selected sources remained unchanged and their integrity check passed.
