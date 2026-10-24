# One bounded joint Clifford chart experiment

Status: implementation and contract ready for independent static review. No joint candidate has been executed. Root authorization is required before the declared run. The construction objective is one favorable complete joint energy; a single-move obstruction does not settle this domain.

## Source and exact domain

Source is Cinna Davis / 1337isnot1337 PR5124, head 0335701859182b7bdf31706b0d969c72f5de41c7, research/independent-clifford-expansion. The predecessor graph is research/general-gaussian-contact-search/model.py, Git blob a69138e4014424235345f3301fbe6b097caa1b8c, SHA256 7cc29edccb3679b2a5c9defeeb0a2ec6bcef9b01b97c2390bebc48f366395f1f. Its round3-word.json.gz is blob 46d929df83817b85a5387bcdb9745e0627d6366e, SHA256 7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05. Both blob bytes were authenticated.

The contracted graph has1,075 groups,800 movable groups and3,938 signed incidences. Its exact encoded SHA256 is f5db08a5814b14b11b93b79207afb1a8d5ec2c5803c1cf6bbc3333cccf0a94af. The uncontracted source has19,197 nodes. Original zero paid edges are contracted; each entire group receives one actual common chart/gauge. Frozen main, owned and adapter groups remain unchanged. Scalar order, coefficients and native logical warp maps remain fixed. This excludes the separately owned PR5125 source/destination scalar-contact splitting work. The monitor cleared only this bounded joint-domain question; no exhaustive novelty is claimed.

Use the retained contracted RESULT zero-polynomial witness: group 499, Pauli axis 7. Its baseline and changed nine-row binary Lagrangian bases are recorded in PIVOT-INVENTORY.json. The original chronological node is11381. Reconstructing the source graph and this ONE retained witness confirms the paid-minus-helper polynomial is identically zero; this was a static source-binding check, not a joint search or a single-neighbor census.

Fix that pivot move. The complete movable adjacent partner set is exactly {172,497,504}. For each partner, independently choose every one of its 1,022 distinct nearest Lagrangian charts relative to its unchanged baseline chart, in the source neighbors() order. This declares exactly 3,066 joint candidates. No other pivot, second-step neighbor, uncontracted move, plateau walk, common-axis restriction, scalar rewrite or graph expansion is in scope.

The three shared incidences are 1193:(172,499),1194:(497,499),1204:(499,504), all paid identity transitions. Complete incident unions have 11, 7 and 7 rows respectively. In this specific domain they contain no helper or warp row; this absence is an authenticated graph fact, not an omitted charge. The generic checker nevertheless implements helper signs, strict productivity, source-side warp action, selfloops and parallel incidences. Group 526 is the fourth neighbor of 499 and is frozen.

A nonadjacent second group cannot improve this fixed-pivot domain: its joint energy equals the pivot's zero polynomial plus its single-move energy, nonnegative on[0,.005] by the retained source certificate. This justifies restricting partners to the complete adjacent set. It does not exclude a different pivot or a move beyond this declared family.

## Chart, owner and rank contract

A chart is a full nine-dimensional isotropic subspace in the 18-dimensional binary symplectic space, represented by the canonical nine-row integer basis used by the source. The pivot chart is T7(L499); each partner chart is one source Hermitian-Pauli-transvection neighbor. Both are actual nearest charts, with distinct-neighbor count checked. Every original node in a contracted group uses that same chosen chart. A future physical witness must specify the common actual Clifford lift and phase, not merely the binary basis.

For an identity transition, rank is d(A,B)=rank(stack(A,B))-9. For a native warp with symplectic action S, rank is d(SA,B): apply S to the SOURCE endpoint before evaluating rank. Replace both endpoints when a selfloop changes. Deduplicate adjacency by incidence ID only; preserve parallel rows and their separate multiplicities. Newly zero ranks are retained in the rank tables and cost H0=0. Original omitted zero identity transitions stay internal to one group and remain free under its common chart.

The baseline paid profile is {1:2201,2:412,3:510,4:127,5:40,8:8}. The eight rank-eight centers remain paid. The 408 independent arbitrary helper owners remain distinct, with baseline productive profile {4:28,7:7,8:47,9:326}. Every helper uses its complete entrance-to-exit relative rank with sign-1 in the energy. All four states of a proposed pair must retain strictly positive helper rank; joint rank zero is invalid, even if both single moves were valid. Main inputs/outputs, owned scratch and explicit adapter boundaries remain fixed and receive no new reward.

## Four-state invoice and exact success criterion

For each candidate emit every incidence in the complete union with its row ID, ordered endpoints, warp operator, sign, and ranks in the order00,10,01,11. State10 is the fixed pivot only, state01 the partner only, state11 both. Emit all four paid-minus-helper DELTA polynomials relative to the complete source baseline. In particular E00=E10=0 as exact integer polynomials. Emit the complete changed paid and helper profiles for state11.

Use Hr(C)=r^(1-C), H0=0 and energy E=paid cost minus productive helper reward. Main reward and unchanged controller terms cancel in this local comparison. The exact primary test point is C*=15108879/5000000000=.0030217758; the declared saving domain is[0,1/200]=[0,.005]. Strict improvement requires an outward-certified upper bound E11(C*)<0. A floating negative number, a nonpositive interval with unresolved sign, or an unchanged polynomial is not success.

The cross-difference R=E11-E10-E01+E00 includes every jointly dependent signed incidence. The KZ regularity convention for minimized energy is R<=0; it is not an improvement certificate, which still requires E11<0. One pair needs exact four-state enumeration, so no min-cut solver is used. All parallel rows must be aggregated before any later regularity claim. The existing sole literature worker confirmed these conventions from the already reviewed published binary-cut note; no second literature search occurred.

The checker uses the source 128-bit outward integer log/exp bounds at the exact rational C*. It groups equal joint delta polynomials losslessly, then attempts a complete-domain nonnegativity certificate by exact concave dominance or outward direct/derivative intervals with 16 and 128 subdivisions. Derivative certificates start from the exact rank-mass value at C=0. Any unproved full-domain sign is reported unresolved, not silently excluded. A positive point witness does not become a complete-domain or new-kappa claim.

## Implementation, coverage and run cap

Implementation: check_joint.py. It authenticates AUTH-MANIFEST.json, reconstructs the exact graph and retained pivot, enumerates the declared 3,066 candidates, and writes every candidate's complete rank table and exact polynomials. It checks a full global invoice for the first witness of every joint polynomial bucket, every certified favorable candidate, and the final neighbor of each partner. Independent verification must separately reconstruct the raw-source graph and all candidate tables before accepting either a positive result or a complete negative certificate.

Proposed first command, held until root GO:

    python3 -I -B outputs/joint-clifford-design-20261023/check_joint.py --max-seconds 60 --output outputs/joint-clifford-design-20261023/SEARCH-RESULT.json

The anticipated cap is 60 seconds. The checker permits at most 120 seconds only for a separately authorized retry; there is no automatic escalation, larger-domain continuation or fallback random walk. A deadline writes partial coverage and unresolved status. Candidate coverage, certificate-processing completion and full-domain coverage are separate fields. No full native program, C++ census, compiler, Lean process or external write is invoked. The source's 19 million single-move census and optional plateau discovery are not run.

## Stop and later admission

If no favorable exact joint energy appears, preserve only this declared domain's outcome and stop. Do not widen the pivot/partner/neighbor set or repack an unchanged invoice without root review. If a favorable point witness appears, freeze both chart bases and axes, source-node mapping, all affected rank rows, complete paid/helper profiles, exact interval evidence and original source hashes. Then independent physical Clifford/phase, native warp/adapter, common-gauge telescoping, all-column, helper/owned restoration, inverse-transpose/caller and complete compiler/precision/ordinary-BIT/outer gates remain. A negative local E is a changed geometric invoice, not an admitted kappa improvement.

Credit Cinna Davis for5124's source geometry, exact alphabet, zero witness and finite single-move certificate; Cao Yifan/4610 for the native word; Dugongue/4654 for inverse-chart phase geometry; the retained4470, zxv, Jacob Alan Sussman, E8, Clifford, native, scalar, precision and outer contributors. The bounded fixed-pivot joint experiment was designed with OpenAI Codex assistance.

The separate admission map records an additional primary-source requirement: PR4654's all-column telescoping cannot be invoked across changed helper entrance gauges without an independent direct-sum/zero-transfer statement. This declared pair domain does not touch a helper incidence, but helper autonomy and full-source telescoping must still be authenticated for any physical emission. A dual must use the actual formula F_out^(-T) M_old^(-T) F_in^T. No typed seven-axis invoice from PR4654 is imported. See outputs/joint-chart-admission-map-20261023/ADMISSION-MAP.md.
