# Local sprint claim

Track: complex supplier. OS assignment seed **22**, drawn once with Python
`secrets.randbelow(100)` at 2026-10-13 15:03:42 UTC.
Base: `007664306fff84fbb1c9a1b4053b69f439764034`.
Contributor: Lauren, with substantial OpenAI Codex assistance, including
separate AI implementations and proof review. New work is Apache-2.0.

Claim: investigate arbitrary dyadic parent coefficients for the historical
PR626 CK compensation panel and PR816 one-parent target-forest class.
Use exact coefficient pricing, PR961's all-dyadic tail reduction and
same-parent exchange argument, applied to the different CK matrix. Check
all 1,086 coefficients n/8, 0<|n|<=543, and 12,432 directed target pairs.
Deliver a concrete checked improvement or a scoped negative result with
reproducer, source pins, adverse controls and independently computed census.
Expected finish: 2026-10-13 15:43 UTC (11:43 America/New_York).
Budget: 40 minutes, final 10 minutes reserved for verification/handoff.

Three candidates considered: (1) fixed factory diagonal scaling, already
covered by PR949; (2) U8 owner packing beyond T21, overlapping PR942/962;
(3) CK non-power-of-two dyadic parent weights, the explicit remaining gap
in PR964. Candidate 3 is chosen. Seed22 fixes equal-cost MST tie order;
it does not restrict the coefficient/pair domain or create novelty by itself.

Overlap inspected: required contribution/status/ledger files, selected PR890
construction and review, latest 100 updated open PRs, plus targeted Horner
and signed-digit PR searches. PR964 head
`7a3bf8460cf6ca16a2bf008ff51fdb06df1af938` closes only signed powers of two
on CK; PR961 head `4257ddf4b755cd0ac3bd3b0f6281cc5b2b1f72ad` closes all
dyadics on X4. This contribution deliberately transports PR961's mathematical
method to the distinct CK matrix; it claims neither that method nor PR816's
original savings as new. No pending executable implementation is imported.

At initial public API inspection the only open issues were #650 (Discussions)
and #913 (all-size/compiler). No open coordination issue existed. The GitHub
connector returned USER_NOT_LOGGED_IN, so the claim is recorded here. No
separate reservation issue was opened. The checkout needed its local Git
long-path option enabled before the complete Windows checkout could succeed.

Stopping rule: complete the entire declared finite core once per implementation
and prove the tails. If domination fails, report the explicit improving edge;
do not infer a full forest improvement without a valid complete forest.
No expanded search or new exponent model is planned.

## Result update

Completed the full 13,501,152-case census with two separately written checkers.
They agree on every ordered edge cost via digest
`8419c238a791375dd846ba7558aeea9185af8b776f148731c377ad21fe311e6d`.
All dyadic forests in the declared class retain floor 16364; the finite
nonunit margin is 63. A total of 941 nonunit edges beat a root, so same-parent unit
replacement is necessary. See [the result and reproducer](README.md).

The final refresh after resumption found Adam Gall's PR1220 already reporting
the same result, so this is labeled **independent corroboration**, with no
priority claim. Our two scalar-arithmetic implementations do not use its
packed lanes or executable code. Its pinned receipt agrees on the quantitative
claims. Main advanced to `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; both CK
inputs remain identical. No posting credentials were available at that handoff,
so a clean patch and ready-to-submit description were delivered locally.

Publication resumed after the user connected GitHub. The mathematical scope
is unchanged; the contribution remains independent corroboration of PR1220.
The publication refresh and its coverage limits are recorded in OVERLAP.json.
The scoped result and claim are complete; the pull request is the review route.
