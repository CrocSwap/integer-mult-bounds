# Claim and handoff — six-source atomic TRIO

**Track / assignment:** `recursive-interfaces`, OS seed
`87a1691b537e8b9bdc20798d6f9f341d`, task `connector-alphabet-change`, priority
revision 4, scope key `0c9f43f3c7d61edb36fe`.

**Pins:** base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected-record
SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`;
catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.

**Question / changed expense:** With six read-only sources, can one atomic
three-source operation `TRIO_{j,k,l}` plus thirteen singleton operations
produce a closed 14-call path whose paired boundary differences cover all 63
nonzero masks, while keeping each total source-map count even and at least two?
The TRIO combines three source-map applications in one root source call; it is
charged for every added access, arithmetic, frame, precision, restoration,
copying, and routing expense. No map application is treated as free.

**Completed domain:** The initial candidate was limited to distinct prefixes.
One bounded pivot removed that simple-path restriction and included both
possible restored 16-map multiplicity profiles. The exact search exhausts all
13-letter restricted-growth words on six labels with singleton profiles
`(1,2,2,2,3,3)` or `(1,1,2,2,2,5)`, including repeated prefix states. It checks
all pairwise XORs of `p0..p13`; the final TRIO closes at `p14=p0`.

**Result:** 2,342,340 profile words among 9,321,312 complete six-label RGS
words. Python incremental coverage and independent C++ direct pairwise XOR
coverage agree on the full histogram. Maximum coverage is 61/63, attained by
88 words; none covers 62 or 63. The exhibited maximum has missing masks 11 and
40, each repairable with four readouts. It costs 144 root calls versus the
incumbent's 142 at unit prices; the source-map multiplicity multiset matches
the incumbent. In general, candidate minus incumbent is `-2*f + 4*g + rho`.
This is a scoped construction negative, not a universal obstruction or a new
kappa.

**Predecessors / overlap:** The pinned six-source singleton result gives the
142-query incumbent. The local review of PR #1518 describes its proved domain
as a ten-call, one-TRIO, twelve-map census, distinct from this fourteen-call,
sixteen-map domain. The nearest active connector claim in the 2026-10-14
19:58 UTC complete snapshot was a six-source DUO search (Discussion #1166,
comment `18932952`); it changes a different call family. A full paginated
refresh completed at 2026-10-14 20:22:44 UTC and the exact terms were searched
again at 20:23 UTC; no same-domain claim appeared. The original comment could
not be posted when first claimed because GitHub GraphQL was rate-limited. The
completed claim/result update was posted afterward to Discussion #1163,
comment `18933586`:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18933586

**Reproduction:** From repository root, run
`python3 -B research/six-source-trio-path-seed87a169/verify.py` and the
independent C++ command in the package README. The certificate records the
histogram, witness, missing-mask repair indices, and exact-record digest.

**Claim expiry:** `2026-10-14T21:23:00Z`. The post was made at 20:23 UTC with
the completed evidence because the initial API attempt failed. The Discussion
comment has since been updated with the PR link.

**Submission:** [PR #2134](https://github.com/CrocSwap/integer-mult-bounds/pull/2134)
was opened after the fresh overlap check. At initial status inspection it was
open and mergeable; repository checks were queued. The Discussion comment was
updated with the PR link.
