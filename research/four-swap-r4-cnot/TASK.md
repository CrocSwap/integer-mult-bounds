# Local task card (autoresearch.md section 3)

Task ID / proposed scope key: `bit-new-register-model` / `7f5f4426ef796683c485`,
refined to `F2[GL2(F2)]/four-SWAP-targets/exactly-four-registers/rank-one-idempotent-calls/free-GL4-mixing`.
Chooser: OS-random nonce `b5ce6390976f7388a9834b2418b70942`, track `bit-mechanisms`,
priority revision 3, base `1f7a934975e5eacaf83511c9ac870263bf095e05`
(origin/main at session start).

Base commit; exact predecessor and dependency heads:
base `1f7a934975e5eacaf83511c9ac870263bf095e05`; no code dependency. Lineage
(model and questions, read-only): Gareth Davidson PR1333
`7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`, commdata2338 PR1414
`9e1640094f649ba6db9742796825a8d6c238989b`, PR1491
`69638b36c691d3e1b8463526fd68c849e8d1aef9`, PR1495
`d5f8745962597a2e5d5bf2deeb7925705c37db8e`, Cinna Davis / 1337isnot1337 PR1541
`194724d87505ec2517fdca1c1884da12398f4c33` (all currently open PR heads; no
predecessor executable is imported).

Concrete object and question:
Formal group algebra F2[GL2(F2)], G = S3 = <a,b | a^2 = b^2 = (ab)^3 = 1>,
S = aba = bab. Paid call C(g,N) = I + ([g]+1)N for g in {a,b} and N any binary
rank-one idempotent over F2^4 (120 of them). Free scalar GL4(F2) basis changes
cost zero and may be interleaved anywhere (strongest convention: reachable
values at q calls are GL4 * Ball_q). Target T = diag([S],[S],[S],[S]) on
exactly r = 4 registers, every register an arbitrary formal dirty input, fully
restored (exact matrix equality in M_4(F2[G]) is the acceptance test, so
restoration is included). Question: is the exact paid-call minimum 12 (four
disjoint aba words), or can free mixing / cross-target sharing give 10 or 8
calls? The written sign-quotient invariant leaves only q in {8,10} below 12.

Scope status: refined. The card allows "a fixed larger register count or a
specified nonabelian operation family". This is the same nonabelian
coordinate-CNOT family as PR1414/1491/1541 at the target count those papers'
own boundary statements leave open ("Four or more targets remain open",
PR1541 body; PR1491 is t=3 at exactly three registers; PR1541 is t=3 at any
finite workspace).

Existing restriction being changed (or exact claim being audited):
target count t <= 3 becomes t = 4; register count fixed at r = 4 (the minimum
where four SWAP targets fit). Not the excluded three-register abelian model.

Method; explicit parameter ranges/candidate alphabet:
Complete finite word search in a necessary natural-matrix representation
(entrywise 2-dimensional F2-representation of S3, states as 8x8 binary
matrices), filtered by two exact written invariants proved in the README
(det-parity q = t mod 2 over F2[epsilon]/(epsilon^2); sign-quotient idempotent
sum with the free-mixing factor forced to the identity), with every candidate
re-verified exactly in the full formal algebra M_4(F2[G]). Two independently
written search implementations cross-check ball sizes and the meet result.
Ranges: r = 4, t = 4, q in {8,10}, g in {a,b}, N over all 120 binary rank-one
idempotents of F2^4, U over GL4(F2) reduced by the stated invariant.

Nearest overlapping PRs and why this adds something:
PR1414 (t=2, any finite workspace, min 6), PR1491 (t=3, r=3, min 9), PR1495
(t=2 with the six GL3(F2) coordinate CNOTs at r=2,3), PR1496 (two order-four
GL3(F2) targets at r=2), PR1541 (t=3, any finite workspace, min 9). A final
find_overlap refresh with the concrete object terms found no four-target
coordinate-CNOT claim. This adds the first t=4 case.

Optimistic full cost budget; required observable improvement:
Unit-price rank-one calls (the family's price rule). No paid-moment or kappa
claim: the bit supplier is nonbinding and no selected-supplier profile is
touched. Required observable: either a verified word with q < 12 (escape of
the 3-per-SWAP tariff) or a complete exclusion of q in {8,10} at r = 4
(floor evidence for the first open case), each with exact receipts.

Success evidence; falsification test; time/compute cap:
Success = exact search receipt (ball counts, meet emptiness or witness),
second-implementation agreement, attaining 12-call word checked in the full
formal algebra on all dirty roles, mutation controls. Falsification = any
q < 12 word found and exactly verified in M_4(F2[G]) with restoration.
Compute cap about 40 minutes; kill and record the measured ball-growth
obstruction if the complete exclusion does not close.

Predecessor authors; intended artifact and reproduction command:
Credit Gareth Davidson (@bitplane, PR1333), commdata2338 (PR1414, PR1491,
PR1495, PR1496), Cinna Davis (1337isnot1337, PR1541), Ali Romman (PR468),
eumemic (PR288) and the retained register-model lineage. Artifact:
`research/four-swap-r4-cnot/` with README (model, invariants, boundary),
verify.py (stdlib only) and structured metadata; reproduce with
`python3 -I -B research/four-swap-r4-cnot/verify.py`.
