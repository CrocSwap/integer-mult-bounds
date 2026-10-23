# CONJG2 — Conjecture G remaining branch (K1 (1,t>=2) wide pivot)
## STATE
- CONJG2: started; reading CONJ-G, TWOSIDE §3, AUDIT-TS, K1-T2, #2816, SIX §5-7.
- CONJG2 (~75k): x>=1 branch CLOSED (§1: n_c<=8 forces x=1, slack 0, U'-kill). d=0 forces dim T = t, F_T spans T, |F_8| = 8 (§2). Working on d=0 with dim T<=3.
- CONJG2 (~110k): d>=1 branch reduced to a finite T-level list: x = 0 forced, e = t; e=2: 35 multisets (slack 3..8), e=3: 280 (single impl, land_e23.py). d=0 reduced to dim T = t <= 3, κ <= 8. Card ends here (token cap); G NOT closed, no counterexample.

Labels PROVEN / CHECKED-1 (one implementation) / OPEN. python = W/venv/bin/python. Setting and notation: CONJ-G §0, #2816 §3.2 (peeling (★): dim S = 8+t, T = S_{<=7}, d = dim(𝒞∩T), dim T = d+e, x = t − e).
Residue being attacked (TWOSIDE §3): D′ one-sided, 8+t terms (t = 2, 3), column family F a basis of S, Σ_F w = 64 + n_c − δ (δ := 64 − cost(D′) >= 0; cost(D′) <= 64 since cost(D) <= 63 forces it, CONJ-G §0),
n_c = raw corrected rows, plus (k, g) with x_k = γ c_v, l_v ∈ U_{A_k}, g ∈ S_v, φ_k(g) ≠ 0.

## §0 Two counting facts used throughout (PROVEN)
(N8) n_c <= 8: a corrected row has x_j ∝ f_i; two rows ∝ the same f_i are proportional, excluded by Lemma D (normalised). So distinct corrected rows use distinct frames.
(SL) Peeling: n_c − δ = Σ_F w − 64 >= cost_w(S) − 64 = (cost(T) − 8d) + 8x + c_8, all three terms >= 0 (#2816 Thm 1: cost(T) >= 8d). Hence (cost(T) − 8d) + 8x + c_8 <= 8.

## §1 Branch x >= 1 is EMPTY (PROVEN mod the #2816 U′ T-level kill)
By (SL) 8x <= 8, so x = 1 and n_c = 8, δ = 0, cost(T) = 8d, c_8 = 0.
- d = 0: cost(T) = 0 ⇒ T = 0 ⇒ e = 0 ⇒ x = t >= 2, contradicting x = 1.
- d >= 1: cost(T) = 8d exactly is impossible for every d >= 1 — this is the T-level part of #2816 §5.1 (Theorem U′ proof: DP for d <= 5; enum.py d 8d+1 + quotient LP + Pencil
  for d = 6, 7, 8). Those kills use only (T, D = 𝒞∩T) (rules C1–C3, LP (a)–(c), Pencil), not x, so they apply verbatim. [Control is partial: land_e23 slack-0 rows (e∈{2,3}) give 0 survivors; the x=1 branch has e = t−1 ∈ {1,2}, and e=1 rests on U′'s T-level kill (+ C3 for d>=2) alone. U′'s Pencil step not re-read for x-freeness: keep 'mod import'.]
So **x = 0, e = t** in every remaining branch.

## §2 Branch d = 0: rigid shape (PROVEN)
x = 0 and d = 0 ⇒ S = 𝒞 ⊕ T with **dim T = t ∈ {2, 3}**. Let F_T := F ∩ T (f members), F_8 := F ∖ T (weights 8, 9; Σ = Σ_{F_T} w + 8(8+t−f) + c_9).
If f < t then |F_8| = 8 + t − f >= 9 and Σ_F w >= Σ_{F_T} w + 72, and Σ_F w <= 64 + n_c <= 72 forces Σ_{F_T} w = 0, i.e. f = 0, |F_8| = 8 + t >= 10, Σ_F w >= 80 > 72. Contradiction. (Members outside T have weight >= 8: every weight-<=7 vector of S lies in T.)
Hence **F_T is a basis of T, |F_8| = 8, κ := cost_w(T) <= Σ_{F_T} w <= n_c − δ − c_9 <= 8**, and the h-parts {h_l} of F_8 form a basis of K^8 with dual rows x_l = μ_l (CONJ-G §2 duality).
So |supp T| <= 37 for t=2 ((7,1)) and <= 22 for t=3 ((6,1,1)/(6,2)). κ <= 2 ⇒ |supp T| <= 2 and CONJ-G §2 (A)/(B) applies verbatim, so κ >= 3 below. Need (as CONJ-G §2): **n_T + n_8 + ε_k <= Σ_{F_T} w** (n_T = corrected F_T members, n_8 = corrected weight-8 members; weight-9 handled by c_9 >= c_9').
Consequences: the Swap Conjecture is needed **only for dim T <= 3** (dim 1 PROVEN, SIX §7); carriers in T: n_T <= ⌊Σ_{F_T} w / 3⌋ (carrier weight >= 3) and n_T <= t.
Still OPEN at d = 0: (i) Swap(+carrier) inequality for dim T ∈ {2,3}, κ ∈ [3, 8]; (ii) weight-8 members with h of D7/E6 type (possible once |supp T| >= 5, up to 37 lines);
(iii) the F1 step (p_h + τ vanishing on O_{l_v} ⇒ h ∝ c_v) for |supp τ| in 18..37 (t=2) / 18..22 (t=3) (F1 CHECKED only to 17; roots/frames already meet O_{l_v} in >= 26, so the gap is 26..37 for roots/frames plus D7/E6 directions).

## §3 Branch d >= 1: finite T-level residue (CHECKED-1)
By §1, e = t and slack s := cost(T) − 8d <= n_c − δ − c_8 <= 8. land_e23.py = SIX/land3.py (DP → symmetric LP → Basis-kill S66+t → Pencil → e=2 triple rule) restricted to e ∈ {2,3}, slack <= 8
(out: land_e23_k8.out; e=2 full list: land_e2.py → land_e2_k8.out). Control: the slack-3 survivors with e ∈ {2,3} are exactly SIX §5's five ([7^3,6^6,2] d=7; [7^4,6^6,3], [7^5,6^5,2], [7^9,3,1], [7^9,4] d=8).
- t = 2 (cell (1,2) m=11, e = 2): **35 multisets**: d=1 [7,6,2],[7,7,1] (s7), [7,6,3],[7,7,2] (s8); d=2 [7,7,6,2],[7,7,7,1] (s6), [7,7,6,3],[7,7,7,2] (s7), [6^4],[7,7,5,5],[7,7,6,4],[7,7,7,3] (s8);
  d=3 [7,6^4],[7^3,5,5],[7^3,6,4] (s7), [7,7,6,6,6],[7^3,6,5],[7^4,4] (s8); and the chain **[7^{d+1}, w]** (one 7-piece per D-dimension plus one small piece): d=4 w=4,5; d=5 w=4,5,6; d=6 w=4..7; d=7 w=4..7 (=[7^9] at w=7); d=8 w=4..7 (slack = 7 + w − d).
- t = 3 (cell (1,3) m=12, e = 3): 280 multisets (by d = 1..8: 3, 7, 13, 24, 45, 56, 65, 67; slack >= 3; e∈{2,3} total 315; full list: land_e3.py → land_e3_k8.out, 280 CHECKED-1).
These lists are necessary conditions on T only (no use yet of the corrections, of k, or of g). Each needs either a T-level kill or a carrier bound n_c <= slack − 1 + ...
**Idea for the [7^{d+1}, w] chain (OPEN, untried):** with e = 2 every λ-basis is d 7-pieces; BK7/F7 (TWOSIDE §1) gives b <= 2 when ρ pieces with Σ w <= 7 exist — here they do not (pieces are 7s), so the needed tool is TWOSIDE's F7+P (one 7-flat + <= 4 lines).

## §4 Status of Conjecture G after this card
PROVEN: x >= 1 impossible; d = 0 ⇒ dim T = t, F_T basis, |F_8| = 8, κ <= 8. OPEN (exact): d = 0 items (i)–(iii) of §2; d >= 1 with T one of the 35 (t=2) / 280 (t=3) CHECKED-1 survivor multisets.
No counterexample: every candidate needs n_c >= slack + 1 − ε_k corrected rows on top of a surviving T; none constructed.
