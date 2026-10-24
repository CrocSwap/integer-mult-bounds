# One exact three-group star gate

Status: code and contract for independent static review. No star candidate has been evaluated. Execute only once after independent acceptance and root GO, with an external hard 60-second cap and internal cooperative 58-second cap.

The concrete question is whether two interactions with retained zero-cost leaf moves can jointly overcome one bridge move's full cost. The accepted two-site result does not answer this question. The separate 43-zero-chart result does not move the bridge.

## Source and exact domain

Use Cinna Davis's PR5124 at head 0335701859182b7bdf31706b0d969c72f5de41c7, research/independent-clifford-expansion. The contracted graph has 1,075 groups and 3,938 signed incidences; SHA256 f5db08a5814b14b11b93b79207afb1a8d5ec2c5803c1cf6bbc3333cccf0a94af. The predecessor model is Git blob a69138e4014424235345f3301fbe6b097caa1b8c, SHA256 7cc29edccb3679b2a5c9defeeb0a2ec6bcef9b01b97c2390bebc48f366395f1f. The literal word is blob 46d929df83817b85a5387bcdb9745e0627d6366e, SHA256 7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05. AUTH-MANIFEST.json binds every copied input and retained receipt.

The bridge is group 172. Its active chart ranges over exactly the 1,022 distinct nearest charts of its unchanged baseline, in the source neighbors() order. The leaves are group 499 with retained axis 7 and group 572 with retained axis 25. Each leaf has two choices: its unchanged baseline or that one retained changed chart. Both leaf moves occur in the source DISCOVERY.json contracted plateau row 1, round 0. The pinned connector capture, raw text hash, and one-final-LF copy normalization are documented in retained/CAPTURE.json.

This gives exactly 1,022 bridge charts and four active-bridge leaf assignments per chart: 4,088 active candidates. Four bridge-off states are repeated controls, not new distinct candidate credit. No other bridge, leaf, farther chart, axis, scalar rewrite, source word, native map, uncontracted move or graph expansion is in scope. This is the final fixed-graph round absent a favorable complete-cost result or explicit new direction.

The complete incident union consists of IDs 130, 131, 1181, 1187, 1193, 1194, 1204, 1212, 1399, 1405, 1411, 1412, 1422 and 1430. All 14 are paid identity transitions. The only internal rows are 1193:(172,499) and 1411:(172,572). Rows 1181 and 1399 are separate parallel transitions (119,172), both charged. Frozen groups 526 and 592 remain fixed. There is no leaf-leaf row. Absence of helper and warp rows is checked against the full graph, not treated as free work.

## Eight states and complete profiles

State order is lexicographic in (bridge, leaf499, leaf572): 000, 001, 010, 011, 100, 101, 110, 111. For each bridge chart emit every incidence ID, ordered endpoint, operator, sign and all eight ranks, plus eight complete paid/helper profiles and paid-minus-helper delta polynomials. State 100 is bridge alone, 101 adds leaf 572, 110 adds leaf 499, and 111 adds both.

The baseline paid profile is {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}; the eight rank-eight centres remain paid. All 408 independent arbitrary helper owners remain distinct, with profile {4:28, 7:7, 8:47, 9:326}. No new input or reward is granted. Each contracted group retains a common actual chart. Original internal zero contacts remain internal to that group.

For an identity contact use d(A,B)=rank(stack(A,B))-9. A native symplectic warp S acts on the source endpoint: d(SA,B). Both endpoints of a self-loop would require substitution. Parallel rows retain separate incidence IDs. Zero helper rank is invalid in any state. The fixed union has neither helper nor warp rows, but the generic rank and sign formulas remain correct.

The accepted pair receipt is retained/SEARCH-RESULT.json, SHA256 d2ea1bd88173a46d8fa59c2958ef234ae9811e44c677aadf012423e77cbf78a9. Each actual bridge chart must match its retained pair chart. New states (000,010,100,110) must reproduce the old four-state polynomials and every overlapping rank exactly. This authenticates E172 and the first interaction, rather than silently recomputing a different pair experiment.

Let E172=E100, R499=E110-E100-E010+E000, and R572=E101-E100-E001+E000. Require the exact polynomial identity E111=E172+R499+R572. The full model is

E(b,x,y)=b E172 + b x R499 + b y R572.

Conditional on activating the bridge, the best leaf cost is E172+min(0,R499)+min(0,R572). The global optimum additionally takes min(0, ...). The checker directly evaluates all four active states; no floating choice of minima is used. A negative KZ cross-difference alone does not imply savings.

All profiles are assembled from the complete baseline and every changed row. The complete source invoice is additionally evaluated for each new polynomial bucket, every favorable candidate and all active states of the final bridge option. Independent review must reconstruct all 8,176 state profiles and 114,464 rank entries.

## Exact test, coverage and cap

Use Hr(C)=r^(1-C), H0=0, and energy paid cost minus productive helper reward. The exact primary point is C*=15108879/5000000000=.0030217758. Success requires a strict outward upper bound below zero for complete active-state energy. A zero polynomial, regular interaction, floating negative value or unresolved sign is not success.

The checker uses 128-bit outward integer log/exp bounds. Equal complete polynomials are grouped losslessly. Full-domain nonnegativity on [0,1/200] is attempted by concave dominance or 16/128 direct/derivative interval cells. Any unproved sign stays unresolved. Candidate coverage, processing completion and full-domain certificates are separate fields. No min-cut solver is used.

Held command after independent static acceptance and root GO:

    timeout --signal=KILL 60s python3 -I -B outputs/joint-clifford-three-group-star-20261023/check_star.py --max-seconds 58 --output outputs/joint-clifford-three-group-star-20261023/STAR-RESULT.json

Record all input, code and contract hashes before and after the run, exit status and elapsed time. The checker refuses to overwrite an output. A timeout preserves any available partial receipt and does not authorize a retry or domain expansion. No source census, optimizer, random plateau walk, native emitter, compiler, Lean process or public write is invoked.

If no favorable complete energy appears, stop this fixed star domain. If a favorable witness appears, freeze both leaf charts, bridge chart, all eight-state rows, complete profiles, exact intervals and source pins for independent verification.

## Remaining physical admission

A favorable geometric invoice would still require exact physical Clifford lifts/phases, common gauges, all-column telescoping, native warp/adapter realization, helper and owned restoration, and raw inverse transpose F_out^(-T) M_old^(-T) F_in^T. Moving helper entrance gauges requires a direct-sum/zero-transfer binding; none moves here. Do not import PR4654's typed seven-axis invoice into this nine-axis word. Finite coefficient, precision, ordinary-BIT, tape, compiler-tail, reserve, endpoint/next-grid and outer-transfer obligations remain. A local saving does not establish an admitted kappa improvement.

Credit Cinna Davis for the source geometry, alphabet, census and retained discovery; Cao Yifan for the native word; Dugongue for inverse-chart phase geometry; and the retained construction, scalar, Clifford, precision and outer contributors. The bounded star contract and implementation were developed with OpenAI Codex assistance.
