# INTCALLER IC (Nov 20, Opus; exact integer programming over role-type multiplicities). Code ic1 (full-type IP, k<=26), ic2 (frame soundness),
ic3 (LP colgen + reduced-cost filter; superseded for large k), ic4 (aggregated IP = exact relaxation + disaggregation + Fraction re-verification).
1 proc, threads=1, < 0.5 CPU-h total. Logs: ic1_k5_20.log, ic3_k21_26.log, ic4_k5_71.log, ic4_parity.log.
Why this differs: CC/KA/MP solved the TYPE LP; its escapes were fractional multiplicities. Here multiplicities are integers and the integral
consequence of TRIPLE is added. It changes the question from "fractional chart" to "integer chart".

## 1. Model (CC model: Q=0, n=2k-2, D>=2, parts<=k-2, lambda != -1; objective = role-piece invoice c^(.99))
- Integer x_{D,P} = #roles of type (D, piece multiset P); integer y = #mains on them, 0 <= y <= #ones(P) x.
  MIXED roles (some singletons main, some idle) are allowed. The cc/mp LP had mf in {0,1} (all or none), which EXCLUDES the built frame C1
  (its two 3-roles have 1 main + 2 idle singletons; mains would total 4, 7 or 10, never 6). [C] Allowing mixing changes no LP value
  (ic3 LP = CC certified values: k13 143.2517, k16 142.8088, k71 129.0373), so earlier numbers stand, but the scope note matters.
- Rows (all [P] from earlier lanes, exact Fractions): n, MAINS (=2k), sep, e, ones, wit_l, coord_th, shal, pfix_x, DYADIC_J (masks), RC_l, RC2_l,
  TRIPLE averaged, HALL_l, plus:
- [P] TURAN (new, integral form of TRIPLE). For ANY two roles a,b: sum_{r != a,b} C(D_r,2) >= floor((k-1)^2/4).
  Proof: TRIPLE gives every triple T >= 3 roles with |M_r cap T| >= 2, so >= 1 outside {a,b}. So G = union of cliques K(M_r), r != a,b,
  has independence number <= 2. Then the complement is triangle-free, so e(complement) <= floor(k^2/4) (Mantel), and
  e(G) >= C(k,2) - floor(k^2/4) = floor((k-1)^2/4). Also e(G) <= sum C(D_r,2).
  In the IP it is applied to the two top-degree roles (big-M on degree indicators). HUBPAIR violates it from k = 9 (averaged TRIPLE: k >= 11).
- [P] PARITY (ic4 only): a role of odd degree has an odd piece.
- Soundness [C ic2, exact]: C1 (k3), c33 (k6), c12 (k3), c22 (k4; main split searched) satisfy EVERY row incl. TURAN. Min slack 0 (coord/pfix).
  #7113-type callers are Q>0: not expressible in this model, same as CC/KA.

## 2. Results [C: HiGHS MIP, gap 1e-10; optimum design re-verified row by row in Fractions; invoice in 60-digit Decimal]
ic4's aggregated IP is a relaxation of the type IP. At every k = 5..71 its optimum disaggregates into a real type multiset (with PARITY),
so it is the exact integer optimum. It cross-checks with ic1/ic3 (full type enumeration) at k = 5..26.
| k | LP (all rows, same model) | IP, no TURAN | IP + TURAN | HP(k) |
| 5-8 | = HP | = HP | = HP (133.804, 137.557, 139.867, 141.321) | |
| 9 | 142.2345 | 142.2345 | 142.1906 | 142.2345 |
| 10 | 142.7924 | 142.7924 | 142.7247 | 142.7924 |
| 11 | 143.1043 | - | 143.0257 | 143.1071 |
| 13 | 143.2517 | 143.2211 | **143.1905 (sup over k)** | 143.2731 |
| 16 | 142.8088 | - | 142.8016 | 142.8935 |
| 20 | 141.8182 | - | 141.8088 | 141.8922 |
| 24 | 140.5706 | 140.5612 | 140.5447 | 140.7024 |
| 32 / 40 / 48 / 56 / 64 | | | 138.0828 / 135.8480 / 133.8015 / 131.9864 / 130.3287 | |
| 68 / 69 / 70 / 71 | 71: 129.0373 | | 129.5859 / 129.4053 / 129.2170 / **129.0349** | 71: 129.2982 |
Full list in ic4_k5_71.log. Every k in 5..71 is ABOVE the bar 128.891.
- Integrality + TURAN is worth at most 0.09 at mid k (k13 -0.062 vs the averaged-TRIPLE LP) and 0.0024 at k71. It is nowhere near the ~10% needed.
- => NOT LOUD. There is no per-k closure: the integer optimum is above the bar at every k in 5..71.
- At k <= 8 the integer program EQUALS HP(k). The integral HUBPAIR / nested-split designs satisfy every type row, so integrality alone can never
  close k5..8. Only mask-level laws can (HUBPAIR theorem, MAINPLACE k8 kill, RESCUEBUILD).

## 3. Integer argmax designs (next build/kill targets). The argmax is a big tie face (chi(2)=0: 2-piece <-> singleton/main trades are free).
- k5-8: HP / nested-split charts, e.g. k8 2x(8:2|2|2|2) + 8 main chords + 4 pure pairs (already DEAD in every order, MP §4), k5 2 all-main hubs + 6 pure pairs (HUBPAIR-dead).
- k9-~20: "2 hubs + ONE third role of degree d ~ k/2 + 2k-5 degree-2 roles". TURAN is TIGHT: k13 C(6,2)+21 = 36 = floor(12^2/4).
  [P] TURAN-TIGHT FORCES THE PLACEMENT. Equality in Mantel gives complement = K_{6,7}, so G = K_6 ⊔ K_7:
  the third role's mask is the 6-side, and the 21 degree-2 roles are exactly the 21 pairs of the 7-set W.
  [P] Kill of the ic1/ic4 reported k13 design (2x 13:2^6|1 m1, 6:6 pure, 12 chords 1|1 m2, 9 pure pairs): all degree-2 roles lie in W
  and the 6-role is pure. So the 6 stages of M_R get mains only from the hubs' 2 singletons. Per-stage MAINS needs 12. DEAD.
  The rest of the k13 face (e.g. 13:2|2|1^9 + 13:6|1^7 + 6:1^6 all-main + 2 chords + 19 pure) has the same forced K_6 ⊔ K_7 placement.
  - Lemma A (CC §6) with S = pure pairs in W gives #pure <= sum_{t != f} rank A_t|S <= 2|W| = 14, which kills every face member with > 14 pure pairs (incl. the 19-pure one).
  - STAR-PURE (relays of a W-pair are only H1,H2) caps rank at 1 where >= 3 pure pairs meet.
  - Members with <= 14 pure pairs AND mixed (1 main + 1 idle) chords are NOT killed here. They are a fully placed mask problem for MAINPLACE/RESCUEBUILD.
- k >= ~25: the argmax goes DYADIC (pieces 32|32, 16|16, 8:8, 16:2^8; see ic4 log). Example k71 (129.0349): 71:16|16|1^39 m39 + 71:32|32|1^7 m7
  + 32:8|8|8|6|2 + 32:16|16 + 4x 16:2^8 + 3x 8:2^4 + 6:2|2|2 + 48 main chords + 80 pure pairs.
  DYADIC_J and RC2 are binding there. It is 0.144 above the bar; the next row needed near k ~ 65-71 is small (~0.1-1.2).

## 4. What it unlocks / next
- Integrality is closed as a route: the caller gap in k5..71 is NOT a fractional-multiplicity artefact (it is <= 0.09). Any closing law is mask-level or a new type row.
- TURAN is a new valid integral row (sound on all frames). It also turns TRIPLE into a placement statement, which is useful for MAINPLACE:
  every Turán-tight design has forced masks (two cliques), so its kill is a finite mask check.
- Cheapest targets: (a) k66-71 need only 0.14-1.07; a row of ~1% at large k (e.g. a dyadic-piece relay row) would close k >= ~66.
  (b) The k13 face kill for mixed-chord members (MAINS per stage + Lemma A + STAR on the forced K_6 ⊔ K_7 placement).
