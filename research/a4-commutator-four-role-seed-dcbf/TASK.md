# Cycle 20 task card

- **Selector assignment:** fresh seed `dcbf94d85fe6d264c5345f44ec8ac7ce`; track `bit-mechanisms`; task `bit-new-register-model`; priority revision 4; catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`; selector scope key `7084092dd726e7ba1f2f`; exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- **Refined scope key:** `01f9a05fb9dd53d99ba1`.
- **Claim:** https://github.com/CrocSwap/integer-mult-bounds/discussions/2095; expires `2026-10-14T21:10:00Z`; root title/body updated for the pivot at 19:22 UTC, with the old hub pointer corrected.
- **Final live overlap:** refreshed `2026-10-14T19:36:34Z`; 375 open PRs and 769 Discussion records, complete pagination and no warnings. No separate exact A4 four-output commutator/product target was found. Nearby S3, D8, free-group, UT5, Dic3, and additive rational-frame scopes are pinned in `OVERLAP.json`.
- **Scope status:** changed. The selector chose a target-specific relaxation bound in the old family. Per the session's construction-only constraint, this became an exact nonabelian construction question.

## First candidate and correction

The first target was `diag([a],[b],[c],1)`, where `a=(123)`, `b=(124)` in A4 and `c=aba^-1b^-1=(12)(34)`. The initial eight-call baseline was wrong: `c=ab^-1a` in this presentation, so this first target has a six-call direct word. Its direct control passes and matches the corrected shortest separate-role cost. No complete search was run for this first target; it gives no saving. This exact control triggered the one allowed pivot.

## Pivoted construction question

Work in the full group algebra `F2[A4]` on four arbitrary input registers. The paid factor is `D_N(g)=I+([g]+1)N`, where `g` is `a` or `b`, `N=xy^T` is a rank-one idempotent in `M4(F2)`, and `y^T x=1`. The alphabet has 120 idempotents and 240 paid factors. Put `c=aba^-1b^-1=(12)(34)` and `d=ab=(13)(24)`. The pivot target is `diag([a],[b],[c],[d])`.

- **Changed premise:** the additive abelian address model becomes nonabelian A4; all four roles carry nontrivial outputs. No inverse label is free: `a^-1=a^2`, `b^-1=b^2`.
- **Direct baseline:** 8 calls: one `a`, one `b`, four for `c=abba` in execution order, and two for `d=ab`. The direct word acts on all 48 register/address basis vectors.
- **Optimistic improvement screen:** a six-call word would save two calls (25%) within the formal alphabet. Address/compiler conversion, physical source access, copies, stream routing, hosting, precision and selected-supplier adoption remain unpriced; no kappa follows from this formal result alone.
- **Method and stop rule:** exact 3+3 meet-in-the-middle over every word of length 0–3 on each side of the 240-factor alphabet. Compare exact coefficient matrices in all 16 register entries and all 12 A4 basis elements. Each side has 13,881,841 raw prefixes before deduplication. First screen the `A4/V4 ~= C3` determinant character. Stop at a verified exact construction or after the complete length-at-most-six domain; do not extend to seven calls this cycle.
- **Evidence:** exact word or a complete no-six receipt; direct eight-call positive control; planted six-call join control; wrong-target and omitted-factor controls; exact regular action on all 48 basis columns. A negative result excludes only six-call words for this target and alphabet.

## Completed result

The complete join reports `PASS_A4_NO_WORD_THROUGH_SIX`. It checks all
13,881,841 left prefixes and 13,881,841 raw right prefixes through length
three, deduplicating the right side to 6,697,991 full coefficient states.
The planted six-call join and direct eight-call target controls pass. The
independent Python replay reconstructs A4, checks the exact 4-by-4 formal
matrix and all 48 regular basis inputs, rejects all eight direct-call
omissions, and verifies the prior three-output six-call control (zero saving).
The search ran in 3 seconds locally; no length-seven search was run.

Reproduce from the repository root with
`python3 -I -B research/a4-commutator-four-role-seed-dcbf/verify.py`, then run
`python3 scripts/research_package.py --package research/a4-commutator-four-role-seed-dcbf --check-only`.

## Candidate scopes and overlap

- Rejected: four-role mixed S3 target through six calls (active Discussion #2023); third-dirty-register GL3 search at length 8 (only an extension of the #1974 bounded census); generic helper-star H2/K replacement (covered by multiple predecessor packages and PRs).
- Adjacent active work: #2023 (four-role S3), #1999 (binary tetrahedral order-24 group), #2094 (four-role UT5 target), #1763 (repeated even-order-3 targets in GL2(F2)), #2069 (three-role Dic3). Completed #2012 is a three-role S3 target. Merged #2027 is a UT4(F2) mixed-root tariff. The A4 group and heterogeneous four-output commutator/product target differ in group structure and endpoint; no exact pivot-target overlap was found in the live refresh.

Expected package path: this directory. Credit the nonabelian-register predecessors and disclose substantial AI assistance.
