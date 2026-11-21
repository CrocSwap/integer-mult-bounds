# PORTGEN PG (Nov 20, Opus, theory + exact arithmetic). Is the universal work stuck at P104? Parametric rung, general vs P104 classification, port-set optimality plan.
Own code: pg1.py (rung + interval cover, retyped from UNIMODEL/runggen/rg1.py), pg2.py/pg3.py/pg4.py sweeps (logs pg2.log pg3.log pg4.log), hrank.py (label ranks of root-line sets). Stdlib Decimal-50, 1 thread, light. No Lean built, no advisor, no push.
Differs from earlier lanes: RG/WR/AS all fix n = 104, h = 9, m = 56. This lane makes (n, h, m_D, m_R, caller, S_spec) parameters and asks which port sets the ceiling protects.

## 1. The rung as a function of the port set [P: reading of the proved rung; C: controls]
Parameters of a legal port set P: n = |P|; h = rank_F2(J + G_P) (label rank, BOARD R-14 rule; u := h - 1 = main climb = caller D-unit, "main8"); m_D = decoder mass per call (D side); m_R = hosted-rise mass per call (R side, the wall on the R sub-pattern, Q96 for P104); k = calls; sigma = S_spec(P)/n (stays per port).
Per port and per call, with psi_h = h^s - u^s, A_u = (2u+1)^s - 2u^s, H_u = 1 + (u-1)^s - u^s (HSContract), p_u = (u - u^s)/(u - 1) (stay price):

  f_P(s) = Gamma(s) - 2*rhobar*psi_h(s) - eta*H_u(s) - sigma*p_u(s),   rhobar = (m_D + m_R)/(2n),   kappa_ceil(P) = 1 - s*, s* = first zero of f_P.

- Gamma = caller budget per port net of mains. Theorem U (any shape, any k): Gamma <= (2 - 2/k)*A_u(s); sup over k is k -> inf (Gamma increases with k, so the ceiling does) [P].
- Specific caller (word_rung_gen): Gamma = (cdat T - cdat P)/(L*n) - (Mn/n)*u^s, Mn = 2n + 2|Q_R| (400 = 2*104 + 2*96).
- The whole rung is HOMOGENEOUS in n: every term is per port. kappa_ceil depends only on (h, rhobar, sigma, caller law). n enters only through the ratios m/n and S_spec/n.
- s = 1 identity (the surplus law, port-general): f_P(1) = 2(1 - 1/k) - 2*rhobar, i.e. per k calls S = 2[(k-1)n - k*(m_D+m_R)/2]. This is the memory identity S = (k-1)p - kc on each side (c = 56, p = 104), now with n, m as parameters.
- Controls reproduced exactly [C pg1, covers OK]: h = 9, rhobar = 56/104: k->inf X+HS .0338671 (RG), S_spec .0207429 (RG headline), k=17 S .0187394, k=4 S .0111307; 7113-shaped caller .0093453741 (= Lean word_rung).

Where P104 numbers enter (replace by parameters):
| number | meaning | parameter |
|---|---|---|
| 104 | ports (caller counts 416 = 4n, 208 = 2n; Theorem U prefactor; HS 104) | n |
| 56, 56 | D wall (P104), R wall (Wall56@Q96) | m_D(P), m_R(Q_R(P)) |
| 8, 9, 7, 17 | u, h = u+1, u-1, 2u+1 (radices 8d+1 / 8l, psi, HS, Theorem U split) | h(P) |
| 400 | mains = 2n + 2|Q_R| | n, |Q_R| |
| 96 (Q96, R96) | R-side sub-pattern (half-diagonal ports) | Q_R(P) |
| 865.58 | S_spec: rank-8 sector DP on U104 geometry | sigma(P) = S_spec(P)/n, P104-DATA (unknown elsewhere; port-general rung uses sigma = 0) |
| 13 frames, 1152 / 136 blockings, Aut 384, price-7 orbits 96 | decoder-wall-at-P104 data | none: only inside Wall56@P104 |
| 17 calls, Tcal/Pcal | #7113 caller | caller block |

## 2. Classification of the proved laws
PORT-GENERAL (any n, h, labels; field or ring generic):
- TensorPot.lean (R >= dim(S0+T) - dim S0 - public climbs; toy R >= rank(Q o M), any field/relays). HalvingLaw.lean (R + n*k >= rank_F2(Q o Mbar), Z/4). Doubling.lean (C >= rank[[Y,E],[0,Z]] >= rank_F2(I+X); split decoders C >= n). NetDoubling.lean (network D >= rhoB + rhoA; torsion form D >= rank(I + X_walk); split D >= n). FutureAttr.lean (attribution decoder, mass <= R, R >= N given Wall N: wall value is a hypothesis). LemmaT.lean (any triangle-containing port set, Z/4 rows). AllOrNothing.lean (abstract, frame hypothesis named). PriceLemma.lean / Price7 general part (exact price, pair price dim M + dim N - n, any field). SplitBound.lean (n <= 2C). CallerSGram.lean, CallerAdj.lean (callers over any field, any k). NetNG.lean ng_fwd/ng_mir/ng_sum (2n <= (h+1)D, general n, h).
- Paper results (not Lean): ADICWALL graded 2-adic bound n <= sum_k s_k (C >= n for odd denominators or one (1+i); C >= 2n/(h+1) for halves); h = 3 => C >= n; tensor multiplicativity; Theorem U (per port, u-generic); RG budget form; OMEGA48 trace identity (any Gram design).
P104-DATA (or P104-typed):
- NetNG.ng_P104 (D >= 21: instance of ng_sum). FrameCert.lean, BlockComplete.lean, BlockLaw.lean, BlockLaw2*.lean (Fin 104 labels, 1152/136 blockings, dim <= 6 blocking excluded). Price7 headline (8 rows, total 55 needs a price <= 6 row: P104 wall reduction). AllOrNothing instantiation (all_or_nothing_real).
- The WordRung chain: WordRung, WordRungGen, WordRungPD*, WordRungLat, WordRungLadder, UniOwnedBank (excess_ge_112_halves, 56 literals), Uni.Chart := Submodule (Fin 9 -> ZMod 2), Ports7113 / DCount (U104 interface), kappa_of_cert_dep with the 400/112/104 invoice literal. The fold/Theorem-K/invoice machinery is generic in shape, but every headline is typed at h = 9 and n = 104 through Ports7113 and the invoice polynomial.
- S_spec 865.58 (LANDSPAN: U104 geometry, rank-8 sector). OMEGA48 T3 census (E8 only). #968 max(72-p, 56) (E8 punctures, p <= 24).
So Uni.word_rung_gen is caller-universal but not port-universal: porting it means re-typing Chart at Fin h, Ports/DCount at n, and the invoice at (n, |Q_R|, u, m_D + m_R). The proofs use no P104 fact beyond those literals, except where the D and R halves cite the P104 walls.

## 3. What P104 optimises, and the optimality inequality [P structure; C numbers]
- Monotonicity [P]: f_P is pointwise decreasing in rhobar (psi_h > 0) and in sigma, increasing in k (A_u > 0 on the crossing range) => kappa_ceil decreases in rhobar, sigma; increases in k (sup over callers = k -> inf).
- Monotonicity in h [C pg5]: kappa_ceil(h, rho) strictly decreasing in h on h = 4..40, 48..729 for rho in {0, 7/13, 0.8}, no violation. Mechanism: the caller's per-role split value is A_u, whose slope at s = 1 is (2u+1)ln(2u+1) - 2u ln u ~ 2u ln 2, linear in h, while the native psi slope is only ~ ln h + 1. First order: kappa ~ (2 - 2 rhobar)/(2a - 2 rhobar b + c), a = (2u+1)ln(2u+1) - 2u ln u, b = h ln h - u ln u, c = u ln u - (u-1)ln(u-1) (h = 9: .03138 vs exact .03387). This is the swarm's screen proxy "X ~ 1/h" (e8-decoder-floors README, x = c h / v), now derived from the rung.
- So the quantity P104 optimises is the per-port pair (h, rhobar), traded along the iso-ceiling curve rho_eq(h). P104 OPTIMAL (in the rung) <=> for every legal P: rhobar(P) >= rho_eq(h(P)) [and sigma(P) >= sigma(P104) if S_spec is used on the P104 side].

rho_eq(h) = smallest rhobar with kappa_ceil(h, rhobar) <= kappa_ceil(P104), U k->inf caller; and rho needed for < .01 [C pg2/pg4, 40-step bisection, rounding 1e-5]:
| h | rho_eq, X+HS (P104 = .0338671) | rho_eq, both sides S_spec/n = 8.323 (P104 = .0207429) | rho for X+HS <= .0207429 | rho for < .01 (X+HS, U k->inf) | NG floor 2/(h+1) |
|---|---|---|---|---|---|
| 3 | .85860 | .80558 | .91436 | .95908 | .50000 (but h=3: C >= n proved) |
| 4 | .80024 | .75206 | .87899 | .94218 | .40000 |
| 5 | .74553 | .70427 | .84584 | .92633 | .33333 |
| 6 | .69255 | .65992 | .81374 | .91099 | .28571 |
| 7 | .64059 | .61788 | .78224 | .89593 | .25000 |
| 8 | .58929 | .57753 | .75115 | .88107 | .22222 |
| 9 | .53846 = 7/13 | .53846 | .72034 | .86634 | .20000 |
| 10 | .48799 | .50040 | .68974 | .85171 | .18182 |
| 12 | .38780 | .42657 | .62900 | .82266 | .15385 |
| 13 | .33799 | .39056 | - | .80822 | .14286 |
| 16 | .18936 | .28518 | .50867 | .76512 | .11765 |
| 17 | .14002 | .25076 | - | .75081 | .11111 |
| 18 | .09076 | - | .44888 | - | .10526 |
| 19 | .04158 | - | .41905 | - | .10000 |
| 20+ | 0 (h0 = 20: rho = 0 gives .0336201 [C cover]) | 0 by h = 25 | .38926 (h=20) | 0 from h0(.01) = 71 (rho = 0: .0098949 [C cover]) | |
Almost linear: rho_eq(h) ~ 7/13 - 0.0505 (h - 9) for 4 <= h <= 19.
Under the U k=4 caller the curve is flatter (h=8 .56128, h=12 .47104, h=25 .18609; pg2.log), but sup_k is k -> inf, so the k->inf column is the comparison.

## 4. Port-general reductions (what is already proved per class) [P unless marked]
| class of P / decoders | proved floor | covers rhobar >= rho_eq(h)? |
|---|---|---|
| h >= 20, any labels, any decoder | none needed (rho = 0 already below P104) [C pg3/pg5] | YES, unconditional in the rung |
| h >= 71 | none needed even for kappa < .01 (U k->inf, X+HS) [C] | YES for .01 |
| half-integer networks, D side (NetNG ng_sum, Lean, general h): D >= 2n/(h+1) | rhobar >= 1/(h+1) (R >= 0) | YES for h >= 19 (rho_eq(19) = .0416 < .05) |
| same, if R obeys the same NG floor | rhobar >= 2/(h+1) | YES for h >= 18 (.0908 < .1053) |
| h = 3 (ADICWALL sec 4) | C >= n | YES |
| odd-denominator or single-(1+i) decoders (ADICWALL sec 2, e = 0) | C >= n on that side | YES if on both sides; one side gives rhobar >= 1/2 => YES for h >= 10 only |
| split decoders (Doubling / NetDoubling, Lean) | C >= n | as above |
| E8 subsets at h = 9, v >= 104 (OMEGA48 T0, general model) | c >= v - 48 <=> C(P120) >= 72 | YES: 1 - 48/v >= 7/13 iff v >= 104; Gram class proved (p <= 16) |
| E8 subsets, 96 <= v <= 103 | Gram class c >= 56 (#968/OMEGA48 T3) | YES in Gram class (56/v >= 7/13) |
| E8 subsets, v <= 95 at h = 9 | Gram class only p in 32..36; else open | OPEN (need c >= 7v/13) |
| 4 <= h <= 17, general labels | only 2/(h+1) (halves) | NO: this is the real gap |

## 5. Known port sets vs P104 (dangerous = rhobar possibly < rho_eq(h)). h by hrank.py [C] (rank_F2(J+G)), c from OMEGA48/ADICWALL tables [Q]
| P | n | h | c (status) | rhobar | rho_eq(h) | verdict |
|---|---|---|---|---|---|---|
| P120 | 120 | 9 | 72 (F, D) | .600 | .538 | safe |
| P112 | 112 | 9 | 64 (F, D, W) | .571 | .538 | safe |
| P111 | 111 | 9 | 63 (F, D) | .568 | .538 | safe |
| P104 | 104 | 9 | 56 | .538 | .538 | the optimum (tight) |
| P103, E8 p = 17..24 | 103..96 | 9 | >= 56 (F Gram) | >= .544 | .538 | safe in Gram class |
| E8 random 16-deletion | 104 | 9 | 63, 60 | .606, .577 | .538 | safe |
| E8 subsets v <= 95 with h = 9 | <= 95 | 9 | open (Gram: p 32..36 only) | ? | .538 | OPEN, needs c >= 7v/13 |
| half-spin 64 (P120 - D8) | 64 | 8 | <= 54 (U, design only) | <= .844 | .589 | OPEN: beats P104 iff c <= 37 (no floor known) |
| E7 | 63 | 7 | 49 (D, floor #2228) | .778 | .641 | safe (floor quoted) |
| E7 - frame | 56 | <= 7 | 42 (D) | .750 | >= .641 | safe if 42 is a floor (only design quoted) |
| E7 + A1 | 64 | <= 8 | <= 50 (U) | <= .78 | >= .589 | OPEN (needs c >= 38) |
| E6 | 36 | 7 | 36 (D, floor) | 1 | .641 | safe |
| D_n, D8 | n(n-1) | 7 (D8) | = v (floor #2719) | 1 | - | safe (ceiling 0) |
| Eisenstein 40 | 40 | ? | 40 (Q) | 1 | - | safe (ceiling 0), different contract |
| Gaussian E8 60 | 60 | ? | 60 design, floor window 40..60 | >= .667 | .641 at h = 7 | safe if h >= 7; LOUD only if h <= 6 and c <= 41 |
| A_n (HALFWALL) | - | - | 1.33-1.78 per port | > 1 | - | safe |
| P104 (x) P104 tensor | 10816 | 81 | <= 3136 | <= .290 | 0 | safe: h >= 20 (h = 81: .00403 at rho = 7/13, below P104 at any rho) |
| P104 (x) h=3 set | 416 | 27 | <= 224 | .538 | 0 | safe (h >= 20) |
| P104 labels at h = 8 (bit-type) | 104 | 8 | 56 | .538 | .589 | ceiling .03793 > .03387: BEATS P104 in the rung. Not a complex port set (complex E8 labels have h = 9, BOARD R-14); it is the BIT side, out of scope (owner: ignore BIT). |
NO known complex port set beats P104. Nothing LOUD. Open entries: E8 subsets with v <= 95 at h = 9, half-spin 64 and E7+A1 at h = 8 (floors needed: 7v/13, 38, 38).

## 6. The port-general premise needed (decoder statements only)
**PORTWALL(h)** [CONJ; the only new premise]: for every legal label set P of label rank h = rank_F2(J + G_P) (distinct odd labels) and every exact decoder M of P (M o Q_P = I over the SPEC scalars), C(M) = sum_k rank_F2 Q[D_k, S_k] >= rho_eq(h) |P|. The same applies to the R sub-pattern Q_R(P) (Wall56@Q96 is its P104 case), normalised so that m_R >= rho_eq(h) n.
- It is needed only for 4 <= h <= 19. h = 3 is proved (C >= n). h >= 20 needs nothing. h >= 18/19 follows from NetNG for half-integer networks.
- At h = 9 it reads C(P) >= 7|P|/13 for every rank-9 label set: Wall56 in per-port form, quantified over port sets. Inside E8 with v >= 104 it is equivalent to C(P120) >= 72 (OMEGA48 T0).
- Its slope: about -0.0505 per unit of h. A rank-8 port set must pay 0.589 per port and a rank-7 one 0.641, so smaller label spaces need more than 7/13, not less.
**Theorem shape (PORT-OPT)** [P given monotonicity, C for the h-curve]: under the rung premises (Theorem U with u = h - 1, HSContract, Theorem K pricing), PORTWALL(h(P)) for all P implies kappa_ceil(P) <= kappa_ceil(P104) for every legal P. Unconditional parts today: all h >= 20; half-integer h >= 19; h = 3; odd-denominator/split decoders on both sides; E8 subsets with 96 <= v (Gram class).
**Universal kappa < .01.** Port generality is not the binding gap. Even P104 needs rhobar >= .86634 under bare Theorem U, so < .01 needs a caller law as well. In the per-port form of the #7113 caller (radices 8 -> u, counts per port, control .0093453741 at h = 9) [MODEL for h != 9; C pg3], the requirement is:
| h | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 17 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rho for < .01 | .76568 | .71380 | .66251 | .61156 | .56085 | .51029 | .45985 | .40951 | .35924 | .30903 | .10861 |
| rho_eq to .0093454 | .77716 | .72867 | .68073 | .63312 | .58571 | .53846 | .49132 | .44426 | .39728 | .35035 | .16303 |
So the premise for a truly universal kappa < .01 is: CALLER(u): every caller's per-port budget Gamma <= the #7113 per-port budget at the same u. That is the open caller gap of RG sec 6, now stated per port. It comes with **PORTWALL01(h)**: C >= rho01(h) n on both sides, with rho01(9) = .51029 (P104 pays .53846: slack 2.9 mass units per side per call), roughly .51 - .0505(h - 9), needed for h <= ~19.

## 7. Verdict
- Not stuck at P104 in the arithmetic: the rung is homogeneous in n and depends on P only through (h, rhobar, sigma). Every ceiling transfers to any P once its walls are stated per port.
- The Lean chain is typed at P104 (Fin 9 charts, Ports7113, invoice literals). The laws (tensor, halving, doubling, NG, net doubling, FA, Lemma T, price, CallerSGram/Adj, SplitBound) are port-general.
- P104 optimality = PORTWALL(h) for 4 <= h <= 19. No known complex port set violates it. Open data points: E8 subsets with v <= 95 at h = 9, and half-spin 64 / E7+A1 at h = 8 (need c >= 38).
- Next: (1) a floor c >= 38 for half-spin 64 (h = 8; design 54), which is the cheapest open check. (2) Prove the h-monotonicity of kappa_ceil (now [C]) analytically. (3) Re-type WordRungGen at (n, h, Q_R) as Uni.word_rung_port (mechanical, Sonnet). (4) PORTWALL at h = 8 on the h = 8 E8 sub-systems.
