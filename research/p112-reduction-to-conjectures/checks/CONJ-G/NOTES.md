# CONJ-G — Conjecture G (K1-T2 §3) at tight m: proven for Δ_D <= 2 (Δ_D = 3 conditional); residue = corrected-cost-64 one-sided decoders with >= 4 corrections (Oct 16)
Labels PROVEN / CHECKED / CONDITIONAL / OPEN. python = W/venv/bin/python. Script: f1.py (< 10 s).
Imports: K1-T2 §0–2 (setting, Theorem L, converse), #2816 (peeling (★), Thm 1, U′, Δ1, survivor lists), #2826 = kpr17 one-sided-six-multisets (Theorem 6, pipeline §5, d=0 Carrier Lemma κ<=2),
SIX/THEORY.md §5 (Carrier Lemma κ<=3, Parity Lemma (iii), slack-3 landscape; slack-3 kills SINGLE implementation), catalogue/L3.1 (Off(x) spans F2^9 unless x ∝ f_i).

## STATE
- CONJ-G: read K1-T2, O4-2, LC, BUDGET, MAP-DRAFT, #2816 README, #2826 README, SIX §4–7.
- CONJ-G: PROVEN Theorem G≤2 (tight m, Δ_D <= 2 ⇒ cost(D) >= 64); Δ_D = 3 CONDITIONAL on SIX slack-3 runs (e = t multisets only). f1.py CHECKED.
- CONJ-G: cells (1,2) m=11 / (1,3) m=12 NOT closed: residue Δ_D >= 4 (>= 3 unconditionally) with n_c >= Δ_D, i.e. D′ itself a one-sided decoder of corrected cost <= 64 with >= 4 corrections. No counterexample built.
- CONJ-G: lift.py re-run: cost(D′) = Σw(A_j) − n_c exactly on all designs; every tight design has Δ_D >= 4 (theorem vacuous on the data, consistent).

## 0. Setting (tight m)
The cells have m = 9 + t, so D′ = {(C′x_j, q_j)}_{j≠π} has 8 + t terms and its columns F := {q_j} are a BASIS of S = col Q (dim 8 + t, L4). Dual functionals φ_j (s = Σ φ_j(s) q_j).
(*) gives φ_j|_𝒞 = x_j (φ_j(C′h) = <x_j,h>). All x_j ≠ 0 (x_j = 0 ⇒ p_j ∝ p_π, Lemma D). Write Δ_D := Σ_{j≠π} w(A_j) − 64 (>= 2 for t >= 2, L4),
n_c := #{j : x_j ∝ f_i, z_i ∈ U_{A_j}} (raw corrected frame rows), ε_k := [l_v ∈ U_{A_k}].
**Ledger (PROVEN; = advisor's pen formula).** cost(D′) = Σ_j w(A_j) − n_c (L3.1 transposed). Passing D′ → D changes rows only at v: rows losing v keep U_R (Off(x)∖v spans F2^9 unless x ∝ c_v
[only k, by Lemma D], Off(f_i)∖v spans W_i), k drops to W_v (−ε_k), rows gaining v can only gain. So **cost(D) >= 64 + Δ_D − n_c − ε_k** (pen >= 0 dropped). CHECKED: lift.py identity on all designs.
Hypothesis of G in these terms: φ_k|_𝒞 = γ ev_v (x_k = γ c_v), and some g ∈ S_v := {s ∈ S : s|O_{l_v} = 0} has φ_k(g) ≠ 0.

## 1. F1 (CHECKED f1.py, exact)
For every line v: Off(c_v) ∩ O_{l_v} = {v}, N(v) = Off(c_v)∖{v}; and |Off(h) ∩ O_{l_v}| >= 26 for every root c_t (t ≠ v) and every frame f_j.
With #2816 §3.2 (|Off(h)| >= 70 unless h is a root or frame direction): if p_h + τ vanishes on O_{l_v} with |supp τ| <= 17 (so |Off(h)| <= 69: root/frame only) and h ≠ 0, then h ∝ c_v. [18..25 would need the D7/E6+A1 directions, NOT checked.]

## 2. Theorem G≤2 (PROVEN mod imports + F1)
**Statement.** Single-entry self-paired row pivot, (1,t), t >= 2, tight m (D′ columns a basis of S). If Δ_D <= 2 then cost(D) >= 64. (For t = 2 this is the case Δ_D = 2; for t = 3 it is vacuous.)
**Proof.** Peeling with the family F: 64 + Δ_D = Σ_F w >= cost_w(S) = 64 + (cost(T) − 8d) + 8x + c_8, so slack <= 2 and x = 0; Theorem 6 (#2826) + #2816 lists kill d >= 1, so
S = 𝒞 ⊕ T, T = S_{<=7}, κ = cost_w(T) <= 2. As in the Carrier Lemma: F_T := F ∩ T is a basis of T, F_8 := F∖T has 8 members p_{h_l} + τ_l (τ_l ∈ T, {h_l} a basis of K^8),
weight 8 or 9, Δ_D = Σ_{F_T} w + c_9; weight-8 members are frame members (flat W_j, not z-carrying) or root swaps at lines t ∈ R ⊆ supp T (τ_l(t) ≠ 0, supp τ_l ⊆ Off(c_t), flat W_t);
z-carrying members: root swaps, carriers in T (m_T; none for κ <= 2), weight-9 members. Corrected rows are z-carrying and k is not corrected (c_v has 4 nonzero frame coordinates), so
n_c <= |R| + m_T + c_9' (c_9' = corrected weight-9 members) and **|R| + m_T <= Σ_{F_T} w** (swap lines are distinct lines of supp T; |supp T| <= κ <= Σ_{F_T} w).
Hence cost(D) >= 64 + (Σ_{F_T} w − |R| − m_T) + (c_9 − c_9') − ε_k, and it suffices to find one unit of slack or a contradiction when ε_k = 1.
Duality facts: for l ∈ F_8, φ_l(p_h) = μ_l(h) (μ = dual basis of {h_l}; the τ-parts lie in T = span F_T), and φ_l(T) = 0.
 (W9) k of weight 9: k is not corrected, so c_9 − c_9' >= 1. Done.
 (A) k ∈ F_8 of weight 8. Write g = p_h + τ (τ ∈ T). φ_k(g) = μ_k(h) = γ p_h(v) = −γ τ(v) (g(v) = 0, v ∈ O_{l_v}). So τ(v) ≠ 0, h ≠ 0, and p_h vanishes on O_{l_v} ∖ supp T:
 F1 ⇒ h ∝ c_v, and τ vanishes on O_{l_v}∖{v}, i.e. supp τ ⊆ Off(c_v): **v is a swap line of T** (g/ν is a root-swap vector at v). ε_k = 1 ⇒ k is not the root swap at v (flat W_v ∌ l_v).
 If v ∈ R: the swap member s_v has h = c_v ≠ h_k, so μ_k(c_v) = 0, but μ_k(c_v) = γ<c_v,c_v> ≠ 0. Contradiction.
 If v ∉ R: R ∪ {v} are distinct lines of supp T, so |R| + 1 <= |supp T| <= Σ_{F_T} w: one unit of slack. Done.
 (B) k ∈ F_T. If g = p_h + τ with h ≠ 0 then h ∝ c_v (F1) and v is a swap line; if v ∉ R, slack as in (A). Otherwise (h = 0, or v ∈ R) put u := g (h = 0) or u := g − ν q_{s_v}
 (q_{s_v} vanishes on O_{l_v}, as supp τ_{s_v} ⊆ Off(c_v) and q_{s_v}(v) = 0): then u ∈ T, u|O_{l_v} = 0 and φ_k(u) = φ_k(g) ≠ 0. So supp u ⊆ N(v), U(supp u) ⊆ W_v ∌ l_v.
 If supp q_k is disjoint from the other members of F_T, u|supp q_k = φ_k(u) q_k gives A_k ⊆ N(v), so l_v ∉ U_{A_k}: contradicts ε_k = 1. With Σ_{F_T} w <= 2 the members are
 {δ_a}, {δ_a, δ_b}, or one 2-piece: always disjoint. ∎
**Δ_D = 3 (CONDITIONAL).** Same proof with κ <= 3, using SIX §5's κ = 3 Carrier Lemma (cases: <= 3 one-pieces / {1,2} disjoint or overlapping / one 3-piece with 4 lines (no swap line at all,
parity) / 3 lines carrying z (<= 1 swap line, Parity (iii)) / 3 lines non-carrying), plus: overlapping {δ_a, 2-piece on {a,b}} has Σ_{F_T} w = 3 > 2 = |supp T| (slack). The only
non-hand input is the d >= 1 kill at slack 3 with e = t (x = 0): t = 2: [7^9,4]; t = 3: [7^3,6^6,2], [7^4,6^6,3], [7^5,6^5,2], [7^9,3,1] — SIX §6, single implementation (s6y/s6r).

## 3. What this gives for the LC cells (single-entry row pivot) and the exact residue
- (1,2) m=11: cost <= 63 forces n_c + ε_k >= Δ_D + 1 and cost(D′) <= 64, with **n_c >= Δ_D >= 3 (PROVEN)**.
  CONDITIONAL (SIX slack-3, single implementation): Δ_D >= 4, hence n_c >= 4.
- (1,3) m=12: Δ_D >= 3 automatically (PROVEN, n_c >= 3); Δ_D >= 4 only CONDITIONAL as above.
- Sanity tie-in: the k = 3 root-swap family (tight t = 3, Δ_D = 3 = n_c, cost(D′) = 64, frame member k with ε_k = 1, T = <δ_a,δ_b,δ_c>, R = supp T) falls under (A) with
  v ∈ R ⇒ contradiction, matching rslift.py's exact 'nullspace dim 0'.
**Residue (OPEN; = G at tight m).** A one-sided P112 decoder D′ with 8+t terms (t = 2, 3), corrected cost <= 64 and >= 4 raw corrections, carrying a c_v-row k with l_v ∈ U_{A_k}
and g ∈ S_v with φ_k(g) ≠ 0. Since cost(D′) <= 63 would already break the one-sided Δ >= n_nf conjecture (#2816 §9), the live case is corrected cost exactly 64 with n_c >= 4,
where the only known decoders are the root-swap family (k = 4: t = 4, outside both cells; no (k,g), rslift.py). Data: every tight design has Δ_D >= 4 and cost(D′) >= 65.
**Mechanism to reuse (PROVEN above, any κ, given the d = 0 structure "weight-8 members are frames / root swaps", which holds when |supp T| <= 4, the range of the checked root-coloop / frame-span facts):** the pair (k, g) either is
contradictory or exhibits ONE MORE swap line v ∉ R. So at d = 0, G follows from the Swap Conjecture (SIX §7) applied to R ∪ {v}, plus the T_v-coefficient step of (B)
(automatic when supp q_k is disjoint from the other T-members). G is therefore no harder than Δ >= n_nf itself at d = 0.
