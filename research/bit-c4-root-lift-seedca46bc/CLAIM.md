# Cycle 23 claim and finding

The claim was posted in the Ideas category as [Discussion #2185](https://github.com/CrocSwap/integer-mult-bounds/discussions/2185).
The first coordination refresh hit a GraphQL rate limit, then completed
successfully at 22:45:19 UTC. The final pre-submission refresh completed at
2026-10-14 22:49:11 UTC: 431 open PRs and 871 Discussion/comment records, each
with complete pagination and no warnings. The exact query found no remote
matches; its only match was this package's own task card. Discussion #2185 is
the canonical investigation thread.

**Track / assignment:** `bit-mechanisms`; OS seed
`ca46bc53e5dd5aaf9ff33154b9e78646`; task `bit-new-register-model`; scope key
`7f5f4426ef796683c485`; catalogue priority revision 4.

**Exact base:** `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
Selected-record SHA-256:
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

**Question:** In the formal group algebra `F2[C4]` on four registers, is the
minimum number of factors `D_N([g^s]) = I + ([g^s]+[e])N`, for
`s in {1,2,3}` and rank-one idempotent `N in M4(F2)`, needed for
`diag([g^2],[g^2],[g^2],[g^2])` equal to four? The construction attempt asks
whether three order-four-labelled calls can produce the four order-two
outputs.

**Changed premise:** a four-register finite torsion address group `C4`, rather
than the torsion-free rational-frame three-register model. All calls count
one; there are no free register/address transformations. The full proposed
three-call bill is 3 versus 4 direct calls, and an optimistic regular-action
rank screen (9 versus 8) does not reject it.

**Method and bounded domain:** one exact n=3, length-at-most-two pilot, then a
complete augmentation-filtration argument for n=4 and all word lengths at
most three; exhaust all 120 rank-one idempotents and all 39 nonidentity label
patterns. No larger cyclic groups or alternate targets in this cycle.

**Predecessors / nearby scopes:** the torsion-free three-register bound in
`research/bit-three-register-lower-bound/README.md`; the #1974 formal GL3
census and #2027 UT4(F2) mixed-root tariff in the current review. Fresh exact
overlap found no remote matches for C4, order-four roots, four involution
targets or augmentation filtration. The broader task query surfaced #2094
(UT5(Z), four roles), #2102 (GL3(F2), three registers), #2012 (S3, three
registers), and #1999 (binary tetrahedral group), which use different groups
and targets.

**Finding:** the four-register target has exact minimum four calls. The
augmentation-filtration proof excludes every word of length at most three in
the declared alphabet. The exact verifier also checks a direct four-call
word, all finite matrix lemmas and the three-register pilot's 7,056 ordered
two-call words. The local artifact is
`research/bit-c4-root-lift-seedca46bc/`; no physical supplier mapping or kappa
change is established.

**Expected artifact:** this package, with exact proof, source pins, verifier,
positive controls, limits and a named next question.

**Claim expires:** 2026-10-15 00:45 UTC.
