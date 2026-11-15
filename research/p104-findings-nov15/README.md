# P104 findings (Nov 15): caller dying-role proofs, native lock laws, spec ledger (no κ)

This package collects the proofs and laws our lanes logged on Nov 15, after #7606, #7607 and #7609 (the follow-up findings package). It builds on
the P104 frontier words of the same day: our #7615 and #7617, whose lineage runs through Clear1nsight's #7612 (the 902/1091 rechart) and SYLforge's
#7616 (39 stationary auxiliary owned lifetimes). The funded-return/courier conventions used when pricing edits come from the crowd chain
#7480/#7481, and the chart-tag move family (retag plus slide) goes back to #7277's block recharts and #7612. The pricer is PRICEKIT (#7607).
Nothing already in #7606, #7607 or #7609 is repeated. Where a result extends one of them, it says so.

It makes **no κ claim** and ships no word.

Credit: DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

Tags:

- **[P]** proved in [PROOF.md](PROOF.md) (or argued in the text, where stated).
- **[C]** exact computation, re-run by a checker in this package (see "How to verify").
- **[C-param]** priced with PRICEKIT (`code/pricekit.py`, vendored from #7607; its control reproduces #7546's κ and S = 1424).
- **[C-lane]** exact computation by our lane code on a frontier word. The code is shipped under `code/`, but CI does not re-run it
  (the words are other PRs' data, and some scripts need our lane's private helper modules; see "Lane scripts").
- **[N]** numerical (float solver). Reported, never claimed.

## Summary

| # | result | tag |
|---|---|---|
| 1 | **DYINGPAIR.** No root of the ρ = 2 two-arm caller has a dying role pair (or single) entering left stage k and absent from stage d+1 (d ≤ nl−3), under the tight counts T1/T2. The Floor matrix is nonsingular without nesting; the triangular recursion has no eigenvalue 2. Kills every dying layout the pricer had marked as +1.1% to +2.4% | [P, C-param] |
| 2 | **SLACK.** The interval-capped line price (a line is one op, so N(I) ≤ \|Z_I\| − rank on every interval) corrects the pricer; nested B is unchanged, lone extra roles price ≤ 0 and are closed [P]; extended Crossing Lemma; any rank drop across a death forces b_K > 0 on both sides | [P, C-param] |
| 3 | **GAPLEMMA.** The Δ-Floor lemma (P1) kills every pair layout and every k = 0 layout (102 of the 117 survivors). 15 single-role layouts remain, with a proved ceiling of **+1.15%**; one open lemma (HANDOFF) decides them | [P, C, C-param] |
| 4 | **Native laws** on #7615/#7617: RELAY-DIAMOND, lattice lock, the dim-8 non-nesting (tails) law, and the three compiler laws JOINT-SUPPLY, FRAME-FANOUT and ROUTE-DEMAND-IS-UNIT-LEVEL | [P, C-lane] |
| 5 | **Bounds on the native.** Exact single-main reroute bound (= actual on 400/400 mains, forced D 1,811 of 3,950 D0/call), helper-layer floor 944 (1,366 with the endpoint census), zero-need relay census, and the D ledger by bucket | [P, C-lane, C-param] |
| 6 | **Spec ledger.** Which contract clauses are SPEC and which are verifier-only; new public registers are legal and a one-hop new helper costs 0 κ; the fresh-register "meet twice" (Sandwich) rule; S = 2·(104·16 − 17·56); mains are S-neutral | [P, C, C-param] |

## How to verify

```
python3 -I -B research/p104-findings-nov15/code/gaplemma/dfloor_count.py   # §3  Δ-Floor kill counts        PASS_DFLOOR_COUNT
python3 -I -B research/p104-findings-nov15/code/slack/icap_check.py        # §2  interval-cap correction    PASS_ICAP
python3 -I -B research/p104-findings-nov15/code/dyingpair/step1.py         # §1  priced menu, pass count    PASS_DYINGPAIR_PRICE
python3 -I -B research/p104-findings-nov15/code/spec/shuttle.py            # §6  one-hop helper is κ-free   PASS_SHUTTLE
python3 scripts/research_package.py --package research/p104-findings-nov15
```

All four checkers use the standard library plus the vendored `code/pricekit.py`. They read only `data/w7546.json.gz` (the #7546 word) and
`data/7113_CALLER.json.gz` (the #7113 caller), both as data, as vendored in #7606/#7607. Each has controls, listed in [VERIFY.json](VERIFY.json).

---

## 1. DYINGPAIR: dying role pairs are impossible (PROOF Part I)

Setting: ρ = 2 two-arm caller root (stages = pairs of adjacent isotropic units, t_s ≠ −1, prefix commutation, two arms meeting in the hubs H).
A set D of roles enters left stage k, is present on Z_k..Z_d, and is absent from Z_K with K = d+1 ≤ nl−2 (so stage K+1 is still in the left arm).

**Theorem [P].** If (T1) no extra role enters at stages k+1..d, and (T2) |Z_K| ≤ 2K+3 (for example the B count 2K+4 minus the dying roles, plus at most
|D|−1 extra roles), then no root exists. This covers singles and pairs, any entry stage k, any death stage d ≤ nl−3, and one dying group per arm.

Proof outline (full proof in PROOF Part I). The Floor matrix (rows Y_0..Y_{j+1} against columns X_0..X_j, X_r|H) is nonsingular **without** nesting, so
the nesting hypothesis H of #7609's NESTPROOF is automatic. Counting dimensions at K forces a nonzero D-supported vector v in C(P_K − I); Lemma S gives
sum-zero coefficients; the Floor dimension count puts its top index at k; and the triangular recursion (2I − Q_c)A_c + Q_c A_{c−1} = 0 kills it, because
Q_a has eigenvalues 1 ± √(t/(1+t)), never 2.

What it kills: every dying layout in the pricer's menu with T1/T2: k = 0, d = 3 (priced +1.31%); k = 1, d = 4 (+1.08%); one pair per arm (+2.4%); and
the L = 6, nl = 4 stage-0 test (B_2 = 0).

Scope. Not covered: an extra role entering inside (k, d] or at least |D| extra roles at the death stage (handled in §2 and §3); one arm with dying roles of
different entry stages; death at the innermost stage d = nl−2 (#7609's conditional kill stands there); t = −1 stages, ρ ≠ 2, non-two-arm callers.

Checks. `step1.py` [C-param] reprices the 63 single-arm dying layouts and the per-arm pairs (B control 1.0950 / 1.0031 / 0.9773; 35 of 63 pass the +0.5% screen,
all now excluded by the theorem). `qcheck.py` (needs scipy through `rs2.py`; not run in CI) checks Step 0 on the exact nested L = 4 root: K has rank 2 and
Q_a has eigenvalues 1 ± i at t = −1/2, matching the prediction. `code/dyingpair/` also holds the Block Rank Bound scripts (`step2.py`, `o_s2_*.txt`).

## 2. SLACK: pricing correction, lone roles, extended Crossing Lemma (PROOF Part II)

| statement | tag |
|---|---|
| **A. True cap.** An idle line is one op covering stages a..b, so with I = [a, b] and Z_I = ∩Z: N(I) ≤ \|Z_I\| − max(rank Y_I\|Z_I, rank X_I\|Z_I). Per boundary the rank is ≤ 4, so "\|S\|−4" is the tightest per-boundary cap, never too generous. The pricer's error was elsewhere: it capped only two-stage lines, so a role that dies (or a lone extra role) inflated the two-stage caps while the long lines the greedy keeps must live in the smaller Z_I | [P] A |
| **Corrected prices.** With every interval capped at rank 4, nested B is unchanged (1.0950 / 1.0031 / 0.9773); "B plus one lone extra role" drops from +0.20..+0.59% to −0.03..−0.05%; the best pair+slack layout (k = 0, d = 4, slack 1..4) drops from +1.56% to +0.20% | [C-param] `icap_check.py` |
| **B. Extended Crossing Lemma.** With a witness, rank(Y_k, Y_{k+1}\|S′) = rank(X_k, X_{k+1}\|S′) = 4 if any of X_k, X_{k+1}, Y_k, Y_{k+1} is supported in S′ | [P] B |
| **C. Refined DYINGPAIR Step 3 / generalised kill.** An extra role entering exactly at d is killed; a whole dying set entering at one stage with no earlier slack role is impossible (Step 1 on Δ, top index, recursion at the entry stage) | [P] C, H.2 |
| **D. Rank drop ⇒ reflection block.** A rank drop of Y_I\|Z_I or X_I\|Z_I across a death forces b_K = dim(V_K ∩ R^Δ) > 0 on **both** sides, and forces X_a, Y_a to touch the extra role while X_j, Y_j (j < a) do not | [P] D, H.3 |
| **E. Lone extra roles are closed.** For a lone role e on [j_e, e_e], max(rank_X, rank_Y) = 4 on every interval across its death, for any window length (even with b_K > 0). Every lone role prices ≤ 0 | [P] E |
| **F/H. Pair + slack.** For a pair entering at k ≥ 1, intervals starting at k have rank exactly 2 on U_{k−1}, so the proved-cap ceiling was +2.19% (pair k = 1, d = 3, slack 0..3; 74 of 117 survivors ≥ +0.5%). This is the number §3 then cuts to +1.15% | [P] F, H |
| Side check: for a two-stage window block, every sum-zero vector of the window x's is a −1 eigenvector of the block, so b_K > 0 costs nothing at the Gram level; the obstruction is the coordinate support | [C] `win.py` (sympy; not run in CI) |

Scope. ρ = 2, t ≠ −1, two-arm roots in the NESTPROOF model (prefix commutation, product −I). Numbers are model prices [C-param]; no root of any slack layout has been built.
The float solver fails even the lone-role control at L = 4, so no counterexample exists either.

## 3. GAPLEMMA: the Δ-Floor lemma and the standalone open question (PROOF Part III)

Notation: Δ = roles of U_d absent from Z_K (K = d+1 ≤ nl−2), B = V_K ∩ R^Δ, b = dim B.

| statement | tag |
|---|---|
| **P1. Δ-Floor Lemma.** For every 0 ≤ i ≤ d: W_i = B_{≤i}, dim B_{≤i} ≤ \|Δ_{i−1}\|, and dim B_{≤i} ≥ 2i+4 − \|U_i \ Δ\|. So a root needs \|Δ_{i−1}\| ≥ 2i+4 − \|U_i \ Δ\| for every i. Corollaries: every layout whose outermost entry stage dies completely (k = 0) fails at i = 0; every pair (c = 2) layout fails at i = 1 | [P] P1, [C] `dfloor_count.py` |
| **Menu count.** Of the 140 pair/single + slack layouts, 117 survive the generalised kill; P1 kills 102 of them (all pairs, all k = 0). The 15 left are all c = 1, k = 1 | [C] `dfloor_count.py` |
| **P2.** rank X_{<K}[Δ] ≤ b and rank Y_{<K}[Δ] ≤ b; if no thin unit touches Δ, b = \|Δ\| | [P] P2 |
| **P3. Family A** (single D entering stage 1, slack s on 0..d, both dead at K): with b = 1, D is a phantom (no left-arm content) and the layout prices ≤ +0.37% | [P] P3, [C-param] `phantom_price.py` |
| **P4. Family A, b = 2** (needs d ≥ 2): rank ≥ 3 on every interval; priced +1.11 / +1.15 / +1.08 / +0.90% for d = 2..5. Family A′ (slack survives): ≤ +0.97%. **Proved ceiling +1.15%** | [P] P4, [C-param] |
| **P5.** The b = 2 left arm is locally consistent: Lemma S + masks + P_3\|Δ = −I_2 + F1 on both sides + t ≠ −1 solves to 8.7e-15 with D not a phantom (`loc_A2b2_7.npy`). So no argument confined to stages < K plus F1 can close the case | [N] `locgen.py` |
| **P6. Reduction.** Stages ≥ K, the right arm and (if b = \|Δ\|) the thin block never touch Δ, and P_K = diag(M, −I_Δ). A family-A root exists iff some root of the non-dying layout L′ (B plus one surviving extra role, one stage shorter, same thin count) has a first-two-stage prefix equal to an M reachable by the dying 3-stage left arm. The reachable set has codimension ≈ 7 among rank-4 prefixes on R^7 (tangent dimension 33) | [P] P6, [N] `codim.py` |

**Open question (standalone, from PROOF "HANDOFF").** Family A = a single role D entering left stage 1, plus a slack role s on stages 0..d, both dead at K = d+1
(d ≥ 2), with b_K = 2. Let M = P_K restricted to U_d \ Δ. Does some root of L′ have a first-two-stage prefix M′ in the reachable set R = {M : the masked dying left arm has
P_K = diag(M, −I_2)}? Yes: family A exists (then price it, apply the Block Rank Bound, PRICEKIT). No: the caller closes at ≤ +0.97% (≤ +0.37% if A′ also dies).
A proof must use stages ≥ K, the thin block or the right arm. Suggested first step: build an exact L′ root (B + 1 extra surviving role) through the exact-root pipeline of #7609, compute
the dimension of its prefix family and test transversality against R, or find an invariant of M that every L′ prefix satisfies and R violates.

## 4. Native-side laws (frontier words #7615/#7617) [C-lane unless stated]

All census numbers below are exact runs of the scripts under `code/` on the word of #7615 (or #7617, where stated), priced by PRICEKIT.

**4.1 RELAY-DIAMOND** (`code/relay/`). A relay frame is a small linear coding node among helpers parked there: 375 frames carry interior helper stops that no fixed register touches
(1,571 stops, 3,219.2 D0/call if all were removed). They are network-coding butterflies: two parallel butterflies ×103 (e.g. F253), single pair butterflies ×39 (e.g. F463), one-way chains ×71.
*Law* [P + C]: for a transfer j→i at F, any meeting of i and j between j's last pick and i's first read lies in the lattice interval [a_i + a_j, b_i ∧ b_j] of both chains. In 759 of
1,131 pinned no-path pairs that interval is the single frame F. Of 2,033 F-transfers, 1,777 are pinned, 1,468 have no time-respecting path from j to i through helpers other than at F, and every one of the 375 frames
contains at least one such transfer. So with paths, picks and reads fixed, F is forced; removing it needs new co-residence (a courier stop) for each such pair, and a courier must also cancel its own token
(a 2×2 invariant on (i, D)). Exact shear transport (a k-register conjugation, `mover.py`) is validated by a positive control that moves four unpinned F-ops with all final rows equal to the base.
Joint relabel F→G for every register touching F: 12 frames have any legal G, all cost more (+2.36 to +21.3 D0/call). The only escape adds courier stops: each costs ≥ 2 ln 2, and one per
distinct (a_j, b_i) pair gives a ceiling of 2,402.6 D0/call (~10% of D0) on 336 frames, which ignores token cleanup.

**4.2 Lattice lock** (`code/jointedit/`). Model: tag-sequence word (`jl.py`); an ADD d += s commutes past everything except reads of d, writes of s and SCALE/COPY/INIT/CLEAR of d or s.
*Law* [C]: a contact at chart G between a main P→G→N and a partner A→G→B can move to a chart C only if join(P, A) ≤ C ≤ meet(N, B). Dropping G needs C = P (so A ≤ P) or C = N (so N ≤ B).
Of 3,218 main contacts at interior stops: 1,475 are free, 974 are forced (G is the only legal chart), 323 are join-locked, 413 meet-locked, 33 have room, 61 are owned. Every one of the 1,281 interior main stops has at least one contact with
no legal host (691 have exactly one, 590 at least two); the 134 stops with no geometric lock are held only by commutation windows or main-side order. The lock is hereditary: of 1,081 partner neighbour stops, 1,067 are locked by the
same law one level down, 14 are editable, and none of those releases the main's stop. Positive control: an injected stop (main 1, ADD 37589 retagged 383 → 615) replays exactly and the scan removes it.

**4.3 Dim-8 non-nesting / tails law** (`code/tails/`). Census of the 302 rank-1 stays (295 single + 13 strict, `census.py`; the census files are lane data and not shipped). Junk of a dropped stay arrives on the main at its dim-8 final chart G,
so cancellation must happen at G. *Law* [P + C]: (L1) every helper tail visits at most one dim-8 chart (public moves strictly ascend and distinct dim-8 subspaces of F₂⁹ are incomparable, so dim-8 charts do not nest);
the junk of a rank-1 lost row is broadcast over k mains in k distinct dim-8 groups (median 2, up to 53) with shared helper support, so k ≥ 2 is infeasible for any tail assignment. (L2) 503 helpers' last working chart is itself a dim-8 hub, so serving
another group moves a hub delivery. (L3) a waypoint costs about 0.0023% (an exact one-hop split) and the median stay is worth about 0.01%, so a stay needing more than 4 new waypoints is net negative even when legal.
Classes: 243 stays carry junk on input columns of mains whose final chart does not contain G; 40 have no dirty main (V127 only); 59 are helper-only, of which 52 need one helper at two incomparable dim-8 charts.
Bound: the best tail-consistent set, with helper re-homing assumed free, is +0.0456% (4 stays); the only fully legal stay (73@245) is net −0.0196% after waypoints. The loose model that ignores main-column junk (+0.82%) is not a tail bound.

**4.4 Compiler laws** (`code/netc9/`, `code/netc17/`, `code/netc19/`). Setting: recompiling the helper layer from requirements, compared with the native (#7546's 1,101 helpers; D0 9,975.448/call).
- **JOINT-SUPPLY** (NETC9) [P + C]. A joint end-frame mix is exactly the rank condition over P ∪ J at the end frame E, so it is bounded by supplier picks at frames F ≤ E. The optimistic gain is ≤ 23% (≤ 9,396 D0/call);
  the compiled word has ~5.8k chains where the native has 1,101 helpers. The gap is chain count, not who supplies the span. The native is hub-and-spoke (249 of 1,101 helpers end below V on 97 end frames; 76% of their 215 supply edges come
  from helpers that end at V or are not low), not a clique of ending helpers.
- **FRAME-FANOUT** (NETC17) [P + C]. Distinct delivered π-contents: compiled 1,536 vs native 1,656, so the content set is not the problem. But the compiled word delivers them at ~4 frames each
  ((content, frame) pairs 6,293 vs 1,955, 3.2×); native helpers carry 1.79 (content, frame) pairs each against 1.13. The 5.1× helper gap is frame fan-out, not content multiplicity; CSE alone covered only ~17% of native adds.
- **ROUTE-DEMAND-IS-UNIT-LEVEL** (NETC19) [C]. The "hot content with 2,953 gives" of NETC17 is the settled word's 53 V-mix helpers at frame 127 (tail ops), not deliveries. At unit level (5,790 plan helpers, one give each) there are 5,705 distinct (content, G)
  pairs, so there is no frame fan-out to close. Exact route constraint: t₁ strictly ascending and nested frame span. Exact builds: all 96 positive q = 1 chains (205 units → 96) settle and pay exactly the plan saving, 4.066× → 4.011× native (−548 D0, −1.35%, accxfast PASS);
  the plan ceiling over all 305 projective chains is 1,757 D0 (4.3%). The remaining gap is the unit-helper count (5,790 vs the native's 1,656 contents): it needs token-sharing helper synthesis.

## 5. Bounds on the native and the D ledger [C-lane / C-param]

**5.1 Mains: exact single-main bound and forced D** (`code/mainsgap/`, base #7617: S 1424, κ .00365760025222, D0 392,264.18). Public charts strictly ascend (6,212 of 6,212 MOVEs). The mains earn 2,704.2 D0/call
(X 664.4, X2 611.3, Y 760.8, Y2 667.7); one rank-8 hop each would earn 6,654.2, a gap of 3,950/call (×1.20928). Exact max-value chain per main, other registers fixed, same ADD multiset (g(r) = r ln r superadditive, so extra stops never help):
- B2 (partners' timed chart paths fixed, one contact per partner, contact time free): forced gap 1,810.6 D0/call, κ ceiling **.00403595 (×1.10344)**; time order never binds (B1 equal).
- B3w (+ partner-side commutation windows): 2,773.8 (×1.00307). B3o (+ main-side block order): 4,041.0 (×1.06218).
- **B3 (windows and order together, the exact single-main reroute relaxation) = actual on 400 of 400 mains (×1.00000).** No reroute of a single main exists with partners fixed.
- B0 (free network) forces 0: a main can be a pure source at its start chart and a pure sink at its final chart with helpers relaying, so a real cap needs a joint mains+helper token bound.
- Where the B2 slack sits: 2,139.5/call, diffuse (max 12.48 per main). 579 of the 886 droppable stops are pinned by exactly one partner ADD (165 by two, 96 by three or more).

**5.2 Helper-layer lower bound** (`code/helperlb/`, base #7615). Per-frame pass-through need ΣB_G = 681 on 530 frames. *Sound floor* **944.07 D0/call** (681 forced stops × f(2); 9.5% of the 9,961.92 paid) [P + C]; a helper layer meeting it
gives exact κ .0060418 (×1.653). With the endpoint census (22 (start, end) dimension classes fixed): **1,365.97** (LP value equals its dual, 4 dp) [C, conditional]. The floor is validated against the native on all 977 single-frame slices and all 8 per-dimension slices (0 violations).
The previously listed laws add nothing to the floor: under free endpoints the min-cost cover is single-stop helpers p−1 → G → p+1, and that cover satisfies every law. A floor above ~1.4–2.1k must track helper tokens.
*Zero-need relay census.* Of the 8.6k paid above the 1,366 floor, 4,467 are routing of need stops and **4,129 are 1,616 stops on 447 frames with B_G = 0**; 375 of those frames never hold a fixed register (pure helper↔helper meeting points).
By dimension (stops / need): dim 6 623/49, dim 3 609/83, dim 7 468/96, dim 1 514/123, dim 2 431/142. Zero-need hop families: (1,1,1,3,1,1,1) ×89 (315 stops), (1,1,1,1) ×154 (252), (5,1,1,1,1) ×36 (100), (3,3,3) ×59 (88), (3,3,1,1,1) ×29 (71).

**5.3 D ledger by bucket** (`code/dledger/`, PRICEKIT-exact, hist-exact; base #7615 κ .00365455370060, S 1424, D0 392,588.64 = 23,093.45/call × 17; table in `LEDGER.tsv`, with the #7616 column).
Caller 15,930.17 + native 7,163.28 per call. Buckets: native helper layer net 9,961.9 (43%; gross 616 {0}→V helpers 12,181.4 T, other helper births 3,328.9, helper MOVEs −5,548.4); caller arm tops 7,152.0 (A 6,601.9 + B 550.2; hubs 8,247.1);
native mains MOVEs −2,680.6 (Y −737.0, Y2 −670.2, X −662.2, X2 −611.3); arm interiors and idle lines net +47; owned registers −118.0; singles 484. Hubs plus arm tops are 66.7% of D0.
The #7616 move is entirely in MOVE hop spectra: −13.0 D0/call (Y mains −23.8, helper MOVEs +10.5, Y2 +2.5, X −2.3); the caller and all helper T buckets are bit-identical.

## 6. Spec ledger (rounds 1 to 3) [P, C, C-param]

Base #7617. Full clause table with sources: `code/spec/` scripts and the table below. SPEC = fixed by the retained specification text; verifier = a convention of `linear.py` / `pricekit` that the spec does not impose.

| clause | SPEC or verifier | relaxation sound? | prize on #7617 |
|---|---|---|---|
| public rows end exactly expected (L:170-187) | SPEC (exact product; helper inputs arbitrary) | no (counterexample: dropping 680@1049 leaves a live-Y row off by T₁₆₄(x₆₈₂ − x₆₈₃ + x₆₈₄ + x₆₈₆)) | n/a |
| mains keep initial/final charts (L:69-75) | contract (finals = gauge of the fixed operator) | a sink change needs a rank-2 non-nested transition per main | ≤ 0 |
| public MOVE strictly ascends (L:120-122) | verifier only (SPEC prices descents at rank) | yes, priced | ≤ 0 (each added hop mass costs 17–18 S) |
| MOVE endpoints nested (L:116-117, :121) | verifier only: SPEC makes a transition a→b one rank-d child, d = dim a + dim b − 2 dim(a ∩ b) | yes, but mass-neutral (the nested route through meet or join has the same mass d); fuses only op-free turns | 0 (0 op-free intermediate stops in 1,614 lifetimes) |
| strict productive helper (L:189-192) | verifier only (SPEC credit T[d(S,T)]) | yes | ≤ 0 (lateral end raises the credit rank: +1.75 to +3.14 D0/call vs ~2.44 per stay) |
| public count ≥ source (L:90) | verifier **allows new public registers** | already legal | see below |
| no deleting helpers (same line) | verifier only | yes | 0 (the 14 op-free-end helpers are all 1-hop) |
| owned inventory 68 (L:76) | verifier pin | yes | 0 |
| owned MOVE paid P[\|d\|], no owned credit (L:124) | SPEC | no | n/a |
| dyadic alphabet (L:147-155) | verifier | yes (#6931/#6932) | 0 |
| ordinary < 1e9 | package constant | yes with the written substitution | 0 (781M used) |
| QUERY P[1] per port, ρ = 2 | the **first** unit is SPEC in radix 2; the second (ρ 2 → 1) is the t = −1 core, not SPEC | no | +6.8% (A) / +7.36% (A+B) if free; capped +2.98% at the BIT pin |
| two-arm caller, nesting | construction family, not SPEC | open sub-class only | §1–§3 |
| c = 56 (owned mass 112/word) | proof-backed for 8-term decoders | r = 9..12 open | 34 S/unit; +2.41% per unit of c |
| credit = one whole rank-d target | SPEC | no (per-hop credit overcredits, ×1.776) | n/a |
| one slot per child | SPEC | no | n/a |
| per-stage mask-restricted natives | allowed, but no idle mains (equal slots at all 17 stages) | n/a | 0 |
| mains per port 4 A / 2 B | convention | yes | S exactly 0 |
| native_all_columns, owned_erasure, compiler / precision_tape / analytic_recovery | SPEC usage / A29 / proof obligations | weaker forms change no invoice | 0 |

**New public registers are legal and priced** [C `shuttle.py`; P]. The verifier requires only n ≥ source public (L:90), not a fixed 1,501. A new helper with hops h₁..h_k costs exactly f(Σh) − Σf(h_i) D0/call (f = r ln r) and S 0.
A **one-hop** new helper is κ-free: the κ of the word with a 1-hop shuttle 4 → 9 equals the base κ to 34 digits, with S and D0 unchanged; the 0 → 4 → 9 helper adds exactly 17·(f(9) − f(4) − f(5)) = 105.105 D0.
Parking (owned INIT, no MOVE, dirty CLEAR) costs 0 κ.

**Fresh-register "meet twice" (Sandwich) rule** [P]. Split every row into old-column and fresh-column parts. Fresh registers are clean ancillas that must end at 0 (their final row is e_h); internal ancilla ops are invertible and ancillas only ascend.
The set of ancillas at charts ≥ u after t is closed (nobody descends into it), so its state modulo the rows injected into it afterward can never reach 0 unless it was 0 at t; dually before t. Hence **any content a network of fresh registers, of any size and hop
count, delivers to a register at (u, t) lies in Down(u, t) ∩ Up(u, t)**: rows at charts ≤ u before t intersected with rows at charts ≥ u after t. The receiver must also be met before and after t while its column is fixed, so one meeting never suffices.
Owned forward parks need only rows at the same chart before t. Consequence: a fresh courier D serving a stay S must ride a → X → b, costing exactly the merge it enables, and a multi-stop D serving two stays nets ≤ 0 because f is convex.

**S decomposition** [C `inv.py`, `anat.py`]. S = caller 57,728 (T mass 166,816 − P mass 109,088) − 17 × (mains 3,200 + owned 112) = 1,424. Helpers are exactly S-neutral (their whole cost is D, 9,966 D0/call). Per port, both types: T = 1604 = 8 × header 1568 + 36 phase units;
the 8 per mask incidence is paid exactly once, by a main or by an idle, so **mains are S-neutral** (ledger law, `check_slots`). The S money is only
S = 104·(36 − 4 sign units) − 17·112 = 3,328 − 1,904 = 1,424 = **2·(104·16 − 17·56)**, that is o·[P(L−1) − L·c] with o = 2 odd directions per port, P = 104 ports, L = 17 calls, c = 56 [accounting identity; "c per direction" is not claimed causal].
Sign ledger per port (SIGNCAP lemma): n + ρ ≤ 17·o + Q (A: 36 + 2 = 34 + 4; B: 36 + 2 = 34 + 4 IDLE_ODD). Queries are not the loss; ρ = 2 is. Mains' 3,200/call is pure D: one rank-8 move each would give D-side ×1.209, but X and Y never share a chart
(X starts on ⟨q_p⟩ in 104/104 cases, Y ends on q_p^⊥ in 104/104, q_p·q_p = 1, direct X↔Y ADDs 0), so their contacts are relayed; the forced share of that gap is not separated.

**The SPEC root of every contract wall** [Q + C]. The port line is anisotropic: q_p·q_p = 1 is SPEC in radix 2 (03-motifs:203, :512-525, :586-600), so every S lever reduces to this one fact.

## Open next questions

1. The GAPLEMMA HANDOFF in §3: does a non-dying L′ root have a first-two-stage prefix in the codimension-≈7 set R reachable by the dying family-A left arm? Decides +1.15% against ≤ +0.97% for the caller.
2. Are interior stages of two-arm callers nested (b_k = 0 for 1 < k < nl−1)? §2 shows that any rank drop across a death needs b_K > 0 on both sides; an unconditional nesting theorem would close the slack class.
3. Is there a token-flow lower bound for the helper layer (per-frame span equality on full contents, including helper tokens) above the sound 944/1,366 floor, or a tightness theorem? The relay and zero-need census locates 4,129 D0/call at zero-need frames.
4. How much of the 1,811-of-3,950 D0/call forced mains gap (B2) is forced by anisotropy once helper tokens are counted (a joint mains+helper bound)?

## Lane scripts (not re-run in CI)

`code/relay`, `code/jointedit`, `code/tails`, `code/mainsgap`, `code/helperlb`, `code/dledger`, `code/netc9`, `code/netc17`, `code/netc19` and `code/spec` (except `shuttle.py`) are our lane code, with absolute paths rewritten
to `inputs/...`. They read frontier words as data: the word of #7615 (`inputs/ATTACK/COURIER226/hit_c226_1.json.gz`), of #7617 (`inputs/ATTACK/STACK7616/best7616.json.gz`), of #7608 (`w7608.json.gz`), of #7616 (`pr7616_word.json.gz`), the #7113 caller
(`inputs/MONOCALLER/7113_CALLER.json`, the vendored `data/7113_CALLER.json.gz` decompressed) and PRICEKIT (`inputs/PRICEKIT/pricekit.py`, a copy of `code/pricekit.py`). Some scripts also import our private lane modules (NETC6/NETC7 compilers, DCUT, SEEDBUILD) that are not shipped.
They are provided so every number above can be traced to code; the claims that CI re-runs are exactly those of "How to verify". Third-party words are used as data only; no other author's code is run.
