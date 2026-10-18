Task ID / scope key: `bit-new-register-model` / `D8-reflection-rank1-W3-inverse-rotation-length3`
Track and accepted seed: `bit-mechanisms` / `df1e67db401c155561180b9d7f1a77f8`
Priority revision / catalogue SHA-256: 4 / `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`
Exact research base / selected-record SHA-256: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` / `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`
Scope status: refined. The catalogue question concerns escaping the abelian three-register obstruction. This fixes a nonabelian D8 group algebra, three arbitrary dirty roles, reflection labels `{s,t}`, and the exact noncentral endpoint `diag([r],[r^-1],1)` where `r=st` has order four.

Question: can a fully restored three-role word of at most three paid factors reach this endpoint over the full formal algebra `F2[D8]`?

Changed hypothesis/expense: use the nonabelian group-algebra operation alphabet and allow one arbitrary dirty role that must return exactly unchanged. Charge every rank-one factor once; allow no extra roles, COPY, discarded outputs, or unpriced address operations. Arbitrary free scalar `GL3(F2)` mixing is normalized into the complete idempotent alphabet, with the residual free map forced to identity by augmentation.

Predecessors / nearest overlap: PR #1881, exact source commit `5a51deaaab2746d42eddb454bbb968bda3af02cc`, proves the two-role noncentral inverse-pair minimum is four; its README suggests testing a third dirty role. Discussion #1738 / PR #1742 cover a different D8 endpoint, the central pair `diag([z],[z],[1])`, and a seven-call search. The new endpoint has a four-call direct word and a three-call target. The refreshed overlap scan covered 388 open PRs and 796 Discussion records; exact-term cached intersection had no matches.

Optimistic complete budget: one call is the entire new paid rank-one factor. The direct baseline is four calls,
`F_s(E11) F_t(E11) F_t(E22) F_s(E22) = diag([r],[r^-1],1)`.
The proposed three-call word would save one of four factors (25%) in this formal block. Physical hosting/recursive charges and native bit-supplier realization are outside the model and remain necessary for any supplier or kappa claim.

Method/domain: over `D8=<r,s | r^4=s^2=1, srs=r^-1>`, put `t=r^-1s`; enumerate all `56^3=175,616` ordered triples from the two labels and 28 rank-one idempotents in `M3(F2)`. First use the exact regular-representation rank floor (the target difference has rank 12 and each call difference rank 4), then compare the complete formal 3x3 group-algebra product with the target. Length 0--2 is excluded by rank; length 3 is fully enumerated. Stop after this exact domain and direct length-four replay.

Success evidence: either one exact three-call word with all three arbitrary inputs restored, or zero matching words in the complete named domain and the resulting exact minimum-four statement. Require an independent full-coefficient replay, a direct four-call positive control, and endpoint / label / call-omission negative controls.

Intended artifact and reproduction: package under this directory; `python3 -I -B research/d8-inverse-pair-third-role-seeddf1e67/verify.py` and `python3 scripts/research_package.py --package research/d8-inverse-pair-third-role-seeddf1e67 --check-only`.

Claim location/expiry: Discussion #1738, 2026-10-14 22:20 UTC. Substantial OpenAI Codex assistance; no independent human review claimed.
