# UNIFY (Nov 20, Opus, theory + small exact). Own code: r2perp.py (R2 run as a ⊥-network), zigzag.py + zz_level.py (exact ZIGZAG test; imports NETATTR's exact.py read-only). 1 proc, threads=1.
Why not a retread: YC proved the D-side level cut, REV the R-side tensor rank, SK/RB the caller cut laws, each on its own side. This lane shows the three are ONE object, with one floor and one gap, and it locates the sharing currency.

## 0. One-line answer
SHARING IS FREE UP TO RANK, AND NEVER BEYOND.
- All three costs count crossings of a graded cut.
- Every proved sharing-proof floor is a CUT-RANK: rank of what crosses ≤ number of paid crossings.
- Mass-type accounting (one row per piece, priced alone) is ROUTING. It overcharges sharing on the D and R sides.
- The caller's type LP undercharges sharing: one relay rescuing many pieces is more sharing than rank allows.
- The tight walls (E8 = 56, the R2 run, aligned caller cells) are exactly the objects whose cut-rank equals their crossing count at EVERY level. Sharing has nothing to save there.
- In network-coding terms: mass = routing cost, cost floor = cut-set bound, and sharing defect = coding gain.

## 1. Dictionary: every side is a graded relay network (NetW) [P]
- **D side (calls).** YC §1 maps any Legal call onto a NetW with total drop = D.
  - Owned descents are nodes (gather at a, deposit ⊥ b).
  - Relays are ascents: owned ones are paid in R; public ones are free.
- **R side (runs).** Read every chart through ⊥.
  - An owned ascent c → c' with cold intake is a NetW node with a = c^⊥, b = c'^⊥ and drop dim c' − dim c. Intake labels q_s ∈ c^⊥ = a means cold intake; reader labels q_t ∈ c' means q_t ⊥ b.
  - A relay j → k needs b_j ⊆ a_k, i.e. c_k ⊆ c'_j. That is an owned DESCENT, paid in D, and its slack is e = dim c'_j − dim c_k (JD: "R-side relays are descents").
  - Publics never descend, so R-side relays are never free.
  - Public ascents enter the ⊥ picture as free NODES. This is the known hot-intake / K-jump residual, which REV's tensor potential handles in the toy.
- **Caller.**
  - Roles crossing a stage cut (X, Y) are the paid crossings.
  - The transfer is Ghat_XY, of rank 2c.
  - CROSS reads #{r meets X and Y} ≥ rank G_XY: a cut-rank law.
  - DYADIC_J is that law summed over a dyadic tree of cuts: the caller's LEVEL SUM.
  - ONE-RELAY / capacity reads dim A + dim B ≤ |C| + #nonzero: the stage-local cut-rank of a relay set C.
- **Decoders** are the relay-free networks (row (w, v) = one node, a = span labels(v), b = a ∩ labels(w)^⊥, drop = price). So mass = Σ_l n_l, where n_l = #rows crossing level l.

## 2. The unified floor (CUT-RANK LAW) and the sharing defect
For any realisation Γ (call, ⊥-run, or caller) with paid crossings c_l at level l and level-l transfer M_l(Γ):
  **cost(Γ) = Σ_l c_l ≥ Σ_l rank M_l(Γ)**,
and the inequality does not depend on the relays (YC §2 proof: first node below level l on every walk).
- D: [P] YC, Lean LevelCutRelay.lean (node-restricted).
- R, for cold-intake runs: [P] by the ⊥ dictionary plus YC. This is new as a level-filtered statement. REV's single tensor rank is its top-level shadow and also covers public nodes in the toy.
- Caller: [P] CROSS / DYADIC_J (SK §2), ONE-RELAY (RB §2).

Define the SHARING DEFECT of a relay-free object as δ = mass − Σ_l rank M_l = Σ_l (n_l − rank M_l) ≥ 0. Its per-level summand is the MULTIPLICITY: the number of crossing rows that are dependent at level l. In Stepanov's sense, sharing can only spend that multiplicity:
- if a network shares one crossing between two rows, those rows must be dependent at that level;
- a level with zero multiplicity cannot be shared.

Exact evidence:

| object | cost | Σ rank | mass | δ | how |
|---|---|---|---|---|---|
| E8 / NET8 / asc56 | 56 | 56 (8 at each l = 2..8) | 56 | 0 | [C] LEVELTEST; NET8 Lean |
| NETATTR §3(ii), 2-node, 1-relay | D = 2 | 2 | 3 | sharing saved 1 | [P] NA, level sum by hand: both nodes cross l = 2, rank M = 2 |
| R2TEST run as ⊥-NetW | R = 2 | 2 | 3 | sharing saved 1 | [C] r2perp.py |
| controls: relay rule off / ADD from lower chart | — | violate the floor | — | — | [C] YC 50–59 violations per 400; REV ctl 8567 per 1500 |

★ [C, r2perp.py] **The R2 run IS the NETATTR network, read through ⊥.** Every check passes:
- Its two epochs are two nodes:
  - epoch 1: <13> → <1,12>, giving a, b of dims 3, 2;
  - epoch 2: <12> → <7,12>, giving dims 3, 2.
- The owned descent <1,12> → <12> is a legal relay of slack e = 1, and e equals the descent's D-cost.
- Cold intakes and reader legality all hold.
- The odd pattern equals R2's Rec.
- D_⊥ = 2 = R, the level sum is 2, and the mass is 3.

So the D-side and R-side counterexamples are the same 2-node, 1-slack-relay object. CTCOVER's overcount dim B2 − dim(B1∩B2) and NETATTR's xb = dim(B+B') − dim B' are the same modular quantity, one read on charts and the other on their ⊥.

## 3. Who pays for sharing (the "other currency") [P + C] — CORRECTED by REUSE96 §4, see §7
[P] Sharing below mass needs a NON-TIGHT relay. BOWTIE plus tight-chain contraction (NA §2, Lean NetBowtie/NetContract) gives mass ≤ cost whenever every relay is tight. Tight relays share nothing; slack e is what makes sharing possible.
- In the opposite currency, a slack relay of slack e is a zigzag move:
  - D side: an ascent of e. Owned, it is paid in R. Public, it is FREE (JD y-carrier).
  - R side: a descent of e. It is always owned (publics never descend), so it is always paid in D.
- [ZIGZAG — REFUTED in §11] mass(pattern) ≤ cost + Σ_relays e (NA C3(a)). Tight on both canonical examples:
  - NA(ii): 3 = 2 + 1;
  - R2: 3 = 2 + 1, i.e. R2's D + R = 3 = mass.
  - So the R2 run does NOT beat mass in owned movement D + R.
  - Exact test: see §6.
- Consequences if ZIGZAG holds:
  - R side: mass_R ≤ R + (owned descents used as R-relays). CLIMB-SHARING IS PAID IN D, unit for unit.
  - D side: mass_D ≤ D + (owned ascent relays) + (public-carried slack). The ONLY free sharing anywhere is public-carried D-relays. By YC §3 these carry only content inside one port hyperplane (48 ports); rigid E8 content is uncarriable [C].
- Joint ledger (rung uses only D + R, WordRungJoint): OWN = D + R ≥ m_D + m_R − (double use) − (public-carried D slack). Double use means one owned move that is both a node on one side and a relay on the other. t7669 has neither kind of move: every lifetime is monotone [C, JD lt.log], so no owned move is ever a relay there.

## 4. What it gives
- **LEVEL-WALL** [FALSE as stated — see §12 (NOGAIN); kept for history] [CONJ, the unified target]: every realisation of −I@Q96 / P104 (call, run, network) has Σ_l rank M_l ≥ 56.
  - This gives D ≥ 56 and R ≥ 56 (for cold-intake runs) at once.
  - It is relay-blind, hence sharing-proof.
  - It is implied by NET-D56 and implies Wall56's conclusion for every shared object.
  - Evidence: [C] ~1400 P104 decoders all ≥ 56 (LEVELTEST), E8 tight, half-spin S = 48 = D.
  - It is STRONGER than Wall56: it needs the level ranks, not the mass. Within the owner rules it is an open target, not a premise.
- **Under Wall56 alone**, ZIGZAG would give:
  - R + D_relay ≥ 56 and D + R_relay + P ≥ 56, where P is public-carried slack, which cannot touch rigid content.
  - On monotone words (t7669-type, no owned zigzags) this means R ≥ 56 exactly when the run has no hot-intake public nodes, and D ≥ 56 − P.
- **Caller:** the cut-rank law summed over the dyadic tree (DYADIC_J) is already proved and stops at k64 153.48 (SK). So the sharing-blind floor alone CANNOT reach 128.891. The caller bar needs a finer filtration than dyadic cuts:
  - stage-local relay cuts (RB capacity) summed coherently over stages, i.e. a level sum whose cuts are relay sets C_t rather than stage sets;
  - the missing piece is RB §5's relay-incidence row. Not proved.
- **Fourth face: helpers** (coordinator's SPECHELPER note). Copy-couriers and helper fan-out are sharing of ONE content vector. Cut-rank prices crossings by the RANK of what crosses, so fan-out of identical content is free under this law. That is consistent with S ≈ 61 ≪ HS.
  - A helper-side gain can only come from a helper level cut: helper stops crossing level l ≥ rank of DISTINCT content delivered across l, which is nearly independent across the 104 P_t.
  - [CONJ, untested] Whether that rank sum exceeds 104h is the right next test. The law gives nothing on copies.

## 5. Status of labels
- [P] the dictionary (§1);
- [P] the cut-rank floor on D (YC), on cold-intake R (⊥ + YC) and on the caller (SK, RB);
- [P] tight relays never beat mass (NA + Lean);
- [C] R2 ≅ NA via ⊥;
- [C] E8 zero defect;
- [CONJ] ZIGZAG (§6);
- [CONJ] LEVEL-WALL;
- [CONJ] helper level cut.

## 6. ZIGZAG exact test [C, weak]
- h=4, random legal 3-node DAGs, D ≤ 4, diagonal-free (zz_h4dag.log): 20/20 have a decoder of mass ≤ D + Σe; 0 refutations.
  - This is WEAK: budgets with large Σe are easy to meet.
- The informative regime is 2-node chains with min(xf, xb) > e, which the NA row maps do not cover.
  - It does not occur at h=4 for D ≤ 5 (generator found 0 instances).
  - At h=5 (D ≤ 6) the exact cover + Singular tool did not finish one instance in 15 min.
  - So ZIGZAG is UNTESTED where it matters.
- NEXT:
  - (a) prove or refute ZIGZAG on 2-node chains by hand: split f_j by ports in A∩A' versus A∖A', and price against the k-readers;
  - (b) a faster exact mass routine (F2 covers first, GB only on survivors) at h=5, e=1, xf=xb=2.

## 7. Update after REUSE96 (cards/WILD/NOVEL/reuse96/RU.md)
CORRECTION to §3.
- RU §4 [C, kissat + independent replay] found a MONOTONE run on Q5: 0 owned descents, D + R = 2, mass 3.
- It works as a Y-carrier rendezvous: one owned register deposits into a public Y, the Y climbs, and a second owned register born at <12> takes the content with a hot intake.
- So "R-side sharing is always paid in D" is FALSE. In the ⊥ dictionary that run is a free PUBLIC NODE, not a relay. That is the caveat in §1 (public ascents are free ⊥-nodes); it is not an exception to it.
- ZIGZAG (mass ≤ cost + Σ relay slack) is untouched by this run, because it has no slack owned relay. But OWN112-per-cluster fails on R as well as on D.
- The only free sharing on both sides is PUBLIC: a free relay on D (JD) and a free node on R (RU §4).

The unified invariant, sharpened: OWN-PRICE / CHAIN MASS [P].
- For any legal relay network (any slack), define m_net = Σ over nodes k of rank_F2 Q[supp(own deposits g_k), supp(own gathers f_k)].
- Node k's deposit labels are ⊥ b_k and its gather labels are in a_k, so each summand is ≤ dim a_k − dim b_k (PriceLemma). Hence **cost ≥ m_net** for every network, independent of the relays.
  - On D this holds for every Legal call (YC bridge) [P, one line].
  - On R it is exactly RU's CHAIN LAW: chain-F runs read through ⊥ are relay CHAINS, the epochs are nodes, and the own output and own intake are (w_j, c_j) [P, RU §1 + §1 here].
- Values on the test objects:
  - R2 run: 1 + 1 = 2 = R, tight.
  - NETATTR §3(ii): j gives rank Q[{7},{1,4}] = 1 and k gives rank Q[{11,14},{2}] = 1, so 2 = D, tight.
  - E8: 8 × 7 = 56, tight.
- Sharing defect = decoder mass − own-price. It is 1 on NA and R2, and 0 on E8.
- So the same epoch / own-price decomposition DOES price D-side slack relays. Both sides then rest on ONE network wall:
  **NETWALL [CONJ]: every legal relay network realising −I@Q96 / P104 has Σ_nodes own-price ≥ 56.**
  - On D it is NET-D56.
  - On R (⊥ chains) it is ChainWall56.
  - **ChainWall56 and NET-D56 are the same conjecture read through ⊥.**
- Known cases:
  - the rank-8 sector on both sides: Chain Lemma A on R [P, RU §2]; NET8 / the level cut on D [P, YC];
  - the open core on both sides is factor rank ≥ 9.
- Owner rules: NetWall56 is NOT an allowed premise. So this is a target, not a ship.
- Own-price and the level sum (§2) are two different bounds that both ignore relays. Each is ≤ cost, both are tight on NA, R2 and E8, and neither is known to dominate the other.

Caller: the own-price form does not transfer naturally.
- The caller's proved laws (CROSS, DYADIC, ONE-RELAY, CELL-RANK) are all of cut-rank form (§2), not own-price form.
- A role's own price would need a per-role invoice that relays cannot share. RB's capacity law (dim A + dim B ≤ |C| + #nonzero) is the nearest analogue, and it is a cut.
- So for the caller the unification stays at the cut-rank level, and the dyadic cut sum stops at 153.48.

Outside every relay-blind invariant: hot intake / public nodes.
- RU §4's rendezvous and the G2C residual both fall here.
- [CONJ, next] a Rendezvous Lemma A in the rank-8 sector: price cleaner + carrier + hot taker as one cluster, at ≥ 7 per cluster output.

## 8. Restated law, R-side carriers, ZIGZAG regime (coordinator round 2)
THE LAW, restated. For every realisation Γ:
- (i) cost ≥ Σ_l rank M_l and cost ≥ own-price m_net [P, both relay-blind];
- (ii) cost ≥ mass − σ_pub − Z, where:
  - Z = Σ slack of OWNED relays [CONJ ZIGZAG]; it is paid in the opposite currency;
  - σ_pub = the saving bought by PUBLIC carriers: free relays on D (JD y-carrier) and free nodes on R (RU §4 rendezvous).
- Reading of the examples:
  - R2 run: σ_pub = 0, Z = 1.
  - g2run (RU §4): Z = 0, σ_pub = 1.
  - NA + port 8 (JD): Z = 0, σ_pub = 1.
- The question therefore becomes: HOW MUCH CAN PUBLIC CARRIERS ABSORB ON P104/Q96?

R-side carrier geometry [P, port-general; read off g2run's moves].
- The engine requires ADD d += s to have chart(d) ⊆ chart(s).
- In g2run: O0 loads into Y1 at {0}; Y1 climbs inside q_1^⊥ (<12>, then <1,12,13>, both ⊥ 2); O1 is born at <12> and takes the content hot; O0 later cleans Y1 at <1,12,13>.
- In general a carrier Y_t keeps every chart inside q_t^⊥ (pinned y charts). So:
  - the hand-over chart C satisfies C ⊆ q_t^⊥;
  - the cleaner's chart at cleaning is ⊇ chart(Y_t) ⊇ C;
  - the taker's output chart is B_1 ⊇ C.
- (H1) Taker cost ≥ dim B_1 − dim C ≥ dim B_1 − dim(B_1 ∩ q_t^⊥). So a taker rides for FREE only if its output labels lie in the port hyperplane q_t^⊥.
  - This is the same hyperplane obstruction as YC §3 on D. There it applies to carried content; here it applies to the taker's output support.
  - If the taker's output label span is ≥ 8 (the rank-8 sector, q96(c)), a free taker needs span(labels supp w_1) = q_t^⊥ exactly, i.e. a port hyperplane.
- (H2) The taker's OWN increment must be cold at C. With C = q_t^⊥ it lies in <q_t>, i.e. it is ∝ y_t. So a cleaner with m takers on one carrier Y_t contributes contents in span{c_0, y_t}: rank ≤ 2 per carrier.
- (H3) Cleaner + taker cluster cost ≥ (dim C − dim A_0) + (dim B_1 − dim C) = dim B_1 − dim A_0, which is ≥ 7 in the rank-8 sector (dim A_0 ≤ 1).
  - BUT the cleaner's climb also serves its own output, so one cluster can carry TWO outputs for about 7.
  - Naive counting therefore gives only R ≥ 7·⌈8/2⌉ = 28 in the rank-8 sector. 56 needs H1 + H2:
    - takers pay ≥ 1 each unless their outputs sit in a port hyperplane;
    - takers' fresh content is rank ≤ 1 per carrier.
  - [CONJ sketch, RENDEZVOUS LEMMA A] Price the cleaner row (w_0 + Σ w_i, c_0) with overflow ≤ dim(B_0 + Σ B_i) − dim B_0. That overflow is ≤ 1 in F2^9 when dim B_0 ≥ 8. So in the rank-8 sector the carrier saving is ≤ 1 per cleaner, giving R ≥ 56 − #cleaners. Not proved: the cluster rows need not be the R96-reduced rows.
  - Handed to CARRIER8. No carrier8/ notes existed when this was written.
  - Q96 data test: does any col(M) vector of the E8 sector have support inside a port hyperplane q_t^⊥? If none does, H1 makes every R-side taker pay ≥ 1, and the rank count must close the rest.

ZIGZAG regime lemma [P]. For a 2-node chain j → k, the row maps of NA §2a give mass ≤ D + min(xf, xb). The uncovered case min(xf, xb) > e needs h ≥ 5 and D ≥ 4.
- Proof:
  - xb = dim B − dim(B∩B') ≤ dim B. Also dim(B∩B') ≥ dim B' − e because B, B' ⊆ A' and dim A' = dim B + e. So xb ≤ d_k.
  - xf ≤ dim A − dim B = d_j, since B ⊆ A ∩ A'.
  - So xf, xb ≥ e+1 ≥ 2 forces d_j, d_k ≥ 2 and dim B ≥ 2.
  - At h = 4: dim A' = dim B + e ≥ 3, so xf ≤ 4 − dim A' ≤ 1 ≤ e. Contradiction. ∎
- So NA's 2-node counterexample (D = 2, e = 1, mass 3) sits on the boundary of the covered regime, and the first real test is h = 5, dim B = 2, e = 1, xf = xb = 2, D = 4.
- Targeted instances: zz5.py → zz5.log (results below).
- Hand proof NOT obtained. Chart-level pricing cannot beat D + min(xf, xb): the k-readers versus A∖A' labels can pair at full rank, so any proof must use port-level rectangle structure.

## 9. THE UNIFIED STATEMENT (final form, after CARRIER8, cards/WILD/NOVEL/carrier8/C8.md)
Corrections:
- §7 is SUPERSEDED. A hot intake is a FREE LEGAL RELAY between owned epochs, not a free public node (C8 §1, past-attribution identity).
- The own-price / NETWALL / ChainWall forms are FALSE as invariants. C8's asc56 carrier-split is a pinned run with R = 56 and own-price 0: an E8 row splits into a gather-only node and a deposit-only node joined by one relay.
- So the only relay-proof invariant is the drop / level-cut form.

**ONE OBJECT.** Every side is a legal graded relay network over F2-charts (NetW).
- D side: owned descents are nodes; relays are owned ascents (paid in R) or public ascents (free).
- R side, read through ⊥: owned epochs are nodes; relays are owned descents (paid in D) or hot intakes via carriers (free).
- In both, cost ≥ Σ drops ≥ Σ_l rank M_l (level cut, relay-blind):
  - D: [P] YC + Lean LevelCutRelay;
  - R: [P] C8 §2, class CF (acyclic relays); outside CF it is open, and 0 cyclic runs were seen in 18.6k.
- Caller: the same cut-rank law on role networks (CROSS, DYADIC_J, ONE-RELAY) [P]. Its dyadic level sum stops at 153.48, so the caller needs a finer cut family. It is NOT reduced to the D/R core.

**ONE CORE.** [CORRECTED in §12: LEVEL-WALL is FALSE; the core is NET-D56 in DROP form.] Both of these ⇐ LEVEL-WALL(Q96/P104): every legal network realising −I has Σ_l rank M_l ≥ 56.
- D ≥ 56 for every network (= NET-D56);
- R ≥ 56 for every CF run (= NETR56; NET-D56 read through ⊥).

What is known on the core:
- Relay-free networks are decoders. There LEVEL-WALL is STRONGER than Wall56, because level sum ≤ mass. [C] ~1400 decoders all ≥ 56.
- Rank-8 sector on both sides [P]: NET8 / YC Cor A on D; Rendezvous Lemma A on R (C8 §3).
- Gap = network-coding gain = min network drop − min decoder mass. It is 1 on Q5 / NETATTR, at factor rank = rank M = 2 [C]. So any NoGain lemma at rank ≥ 9 MUST use Q96/P104 rigidity, not rank-minimality.

Sharing currencies: owned relays cost slack in the opposite currency, and carriers make relays free on BOTH sides. So "who pays" arguments are dead (§3 superseded). Only the level ranks remain.

## 10. The core: why could relays not gain on Q96 at rank ≥ 9? [L1/L2/direct per-level rank-8 targets are FALSE on Q96 itself — §12] (lemma map; nothing below is proved unless labelled)
Necessary shape of a sub-56 network [P, YC Cor B / C8 per-level form]:
- some level l ∈ [2,8] has rank M_l ≤ 7;
- equivalently, part of M is carried only by walks that start at a LOW source (dim a < l, so its column labels span < l) or end at a HIGH sink (dim b ≥ l, so its row labels lie in b^⊥, dim ≤ 9 − l).

Three rigidity inputs, and how each would enter:
- (R1) q96(c): every vector of col M / col M^T has label span ≥ 8.
  - A low source's contribution X_g = G N[:,g] f_g^T has columns in col M only if it is not cancelled.
  - So any low-source content that survives to the target must be cancelled by other low-source or high-sink content. Relays create exactly that cancellation: NA's failing cell is a cancellation in the ascent block.
  - Lemma target L1: at each level l, (M − M_l) restricted to the odd cells has rank ≤ Σ over low/high pieces of (their level-l-invisible drop). Combined with clique8 (rank of −I on the odd graph ≥ 8 at every level), this would give rank M_l ≥ 8 − (cancelling pieces).
- (R2) Port hyperplanes (YC §3). Free carriage needs content span ≤ 8 lying inside a port hyperplane (48 ports).
  - At rank ≥ 9 the danger rows are non-rigid (span ≤ 8) by YC Cor B.
  - Lemma target L2: low-span pieces that cancel at a level must sit inside a common hyperplane v^⊥, and the odd graph of Q96 restricted to one hyperplane has min-rank ≥ 8. If true, each level keeps rank ≥ 8 for l = 2..8, giving 7 × 8 = 56.
  - Test: min-rank of the Q96 odd graph inside each of its hyperplane port sets. GF(2) is easy (it is rank_F2 of Q restricted); over Q it is the hard part. This is the half-integer question again.
- (R3) R96 / frame laws: the rank-8 factorisation M = Λ Ah (Λ^{-1} Ah/4)^T is unique up to GL8.
  - At rank ≥ 9 the extra factor directions are ker-cancelling (MERGEROWS normal form: saturated rows refactor by GL at no cost).
  - Lemma target L3: a network normal form. Relays between nodes whose contents are in the same saturated class can be contracted (as tight chains are, NA §2c), at no drop increase. The surviving slack relays then join rigid content, which YC shows cannot be carried.

Honest assessment:
- L2 is the most concrete: it is a finite statement about Q96 hyperplane sections.
- L1 is the most general: a cancellation-counting lemma per level.
- None is proved. Q5 shows the gain is real when content can cancel inside a low-dim chart, so every route must show that Q96's odd graph leaves no room for such cancellation at any level 2..8.

## 11. ★ ZIGZAG is FALSE [P + C exact] (zz5.py, zzcx.py → zzcx.log)
Instance: h=5, a 0/1 network with 2 nodes and 1 relay.
- j: A = <3,5,8,16> (dim 4), B = <13,21> (dim 2). Gathers {8,11,14,21,22}, deposits {25,28}.
- k: A' = B + <7> (dim 3), B' = <18> (dim 1). Gathers {7,13,31}, deposits {1,4,19,22,26,31}.
- e = 1, xf = xb = 2, D = 4, level sum 4, own-price 4.
- Legality is asserted in code.

Result:
- The exact decoder search finds NO decoder of mass ≤ 5 = D + e, even over C:
  - a complete F2 cover enumeration finds a single cover within budget;
  - its Singular GB is <1>.
- So m ≥ 6. Since m ≤ D + min(xf, xb) = 6 by NA §2a backward rows, **m = 6 = D + 2 = D + 2e.**

Consequences:
- Sharing through ONE relay of slack 1 saves 2 > e. The saving is bounded by the modular quantity min(xf, xb), not by the relay slack.
- Hence no "pay e in the other currency" law exists even for owned relays. This confirms §9: only level ranks survive.
- A second instance in zz5_0.8.log #5 also has NONE at budget 5. It was not re-verified separately.
- Rate: 2 of 205 instances in this regime. The rest have mass ≤ 5 over Q̄; that direction is not certified over Q.
- [P, regime lemma §8] h = 5, D = 4 is the smallest size where this can happen.

## 12. CORRECTION (NOGAIN, Nov 20; cards/WILD/NOVEL/nogain/NG.md) — LEVEL-WALL is FALSE; unified picture restated
- [P + C, nogain/lwcx.py] LEVELRANK's (d56dir/levelrank, Nov 19) routed-E8 network, rechecked on Q96: 96 one-port gatherers (a = <q_t>, b = 0) → 8 kernel-line hubs (a dim 2, b dim 1).
  - It is legal, realises −I with M = G/2 (RIGID, rank 8), and has D = 104 (P104: 112).
  - Its YC level sum is **0**.
  - So "every legal network has Σ_l rank M_l ≥ 56" is false. LEVEL-WALL is only sufficient for D ≥ 56; it is not a valid core. Restricted to D ≤ 55 it is NET-D56 itself.
- [P] DX (downward-crossing level cut): D ≥ Σ_l rank M*_l, where M*_l sums the walks with some dim a ≥ l before some dim b < l. It equals YC on decoders, gives 16 (vs YC 0) on the counterexample, and is 56 = D (tight) on E8 / asc56-split. It carries over to D and to CF runs on R (same walk proof through ⊥, §9). The caller keeps its own cut-rank laws (CROSS/DYADIC/ONE-RELAY).
- [P] Zero-drop contraction: WLOG every node has drop ≥ 1, so ≤ D nodes.
- Why the per-level route fails [P]: q96(c)/R96 only constrain vectors in col M / col M^T, and cut contents lie there only in the factor-rank-8 sector (Lemma A). On the counterexample, M*_l = 0 for l ≥ 3.
- UNIFIED PICTURE (restated):
  - cost ≥ DX level sum on D and CF-R (relay-blind, proved); the caller stays at cut-rank level (§9);
  - the WALL is NET-D56 / NETR56 in DROP form (no legal −I@Q96 network with Σ drops ≤ 55);
  - relay-free case = Wall56; gap = network-coding gain in drop terms.
- Plain-rank JUNK-PAYS is FALSE (L2TEST: free zero-drop hubs inflate rank M*_l on EVEN cells at fixed D).
- Repaired INVARIANT form. Let μ_l = the odd-pattern min-rank of M*_l, i.e. the min rank over even-cell completions.
  - DX-inv [P]: D ≥ Σ_l μ_l. It is tight at E8 (μ = 8 at l = 2..8).
  - JUNK-PAYS-inv [CONJ]: Σ_{l=2..8}(8 − μ_l)_+ ≤ Σ_l(|C_l| − μ_l). It implies NET-D56.
  - Details in nogain/NG.md §4.
