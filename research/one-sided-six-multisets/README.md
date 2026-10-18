# Decoder floors, case (b): the six remaining `d = 8` multisets of #2816 are dead (≥ 64 with ≤ 3 non-full corrections; E8 lifts ≥ 67; no κ claim)

**Status: research note, a follow-up to #2816 (ours). Every claim is a written proof plus exact finite computations that `verify.sh` re-runs (about 30–40 minutes, at most 6 processes, each under `timeout 1200`, no SAT solver). No κ claim, no supplier word.**
Only `research/one-sided-six-multisets/` is added; nothing existing is changed.

Labels: **PROVEN** (written proof in this file, every finite input listed), **CHECKED** (an exact script re-run by `verify.sh`, assertion in `checks/check_logs.py`), **RECORDED** (a log shipped in `evidence/logs`, not re-run),
**INHERITED** (a statement of #2816, cited from its text and not recomputed here), **OPEN**.

## 0. Claims box (scope is part of the claim)

Setting and notation are those of #2816 (P112 = the 112 non-frame lines of E8, dense F2-pairing of rank 9, Gram realisation, **case (b)**: factors `q_j ∈ col M`, factors `p_j` arbitrary; char 0; every number of terms `m`).
`n_nf` = number of non-full corrected terms of the *normalised* decoder, exactly as defined in #2816 §0 / §6. `Δ` = ε-free cost − 64 (decoder level), `Δ = Σ_b w(ρb) − 64` (lift level), as in #2816 §6–7.

| # | Statement | Status |
|---|---|---|
| S1 | **Basis Lemma** (`d = 8`): the fundamental circuits of a λ-basis give **8 linearly independent** codeword directions `h_y`, `Off(h_y) ⊆ U_B ∪ Λ(F_y)` (§2) | PROVEN |
| S2 | **Lemma S66 / S66+t.** For any two 6-dimensional label subspaces `V_1, V_2` (plus, for S66+t, one further free line, chosen separately for each `h`), the directions `h` with `rank ℓ(Off(h) ∖ X) ≤ 7`, `X = Λ(V_1) ∪ Λ(V_2)`, span **at most 3** dimensions of `R^8` (at most 6 directions); control: two 7-dimensional flats reach rank 8 | CHECKED twice by two independent implementations (`s66.c`, `indep.py`), all 159 orbit representatives of `V_1` against all 776,805 line sets of `V_2` |
| S3 | **Theorem 6.** None of `[7^5,6^5,1]`, `[7^6,6^4]`, `[7^8,5,4,1]`, `[7^8,5,5]`, `[7^8,6,3,1]`, `[7^8,6,4]` occurs as the minimum-weight basis of `T = S_{≤7}` with `d = 8` — these are exactly the six OPEN multisets of #2816 §0 / §9 | PROVEN from S1 + S2 (+ INHERITED flat caps `g(1..6)`) |
| S4 | **`Δ ≤ 2 ⇒ n_nf ≤ Δ`** (decoder level) and **`Δ ≤ 2 ⇒ ρ_0 ≤ Δ`** (lift level) | PROVEN from S3 + INHERITED reduction of #2816 §5.3, §9; second, independent route in §5 below  |
| S5 | **One-sided P112 decoders with `n_nf ≤ 3` non-full corrections (any number of full ones) cost ≥ 64**; in general corrected cost `≥ 64` for `n_nf ≤ 3` and `≥ 67 − n_nf` for `n_nf ≥ 3`, i.e. `≥ 64 − max(0, n_nf − 3) ≥ 59` (`n_nf ≤ 8`) — was `≥ 64 − max(0, n_nf − 2) ≥ 58` in #2816 | PROVEN from S4 |
| S6 | **Lift level:** every `S ⊇ 𝒞_{X_I}` has `cost_w(S) ≥ 64 + Δ + max(0, |I| − ρ_0) ≥ 64 + min(|I|, 3)`; every lift of the E8 root code (every E8/P120 decoder) has `cost_w ≥ 67`, and `≥ 72` unless the P112 restriction has `Δ ≥ 3`; gain-law form `|P120| − C(P120) ≤ 53` | PROVEN from S4 |

**Not claimed / OPEN.** `Δ ≥ n_nf` for general `n_nf` is OPEN; S5 is exactly what `Δ ≤ 2 ⇒ n_nf ≤ Δ` gives, and no more (§6). The corrected-cost root-swap family of #2816 is tight at `n_nf ≤ 4`, so a proof for `n_nf ≥ 4` would have to be exact on it. An extension to `Δ = 3` (`n_nf ≤ 4 ⇒ ≥ 64`) is **in progress** on other cards; nothing about it is claimed or used here.
**Not covered** (as in #2816): two-sided decoders; case (c) (see #2784 for the A2 family); P104 and other punctured units; fields of positive characteristic.

## 1. Overlap and credit

Scanned: titles of the pull requests opened after #2816 (#2817–#2825 at the time of writing) and the open or merged decoder-floor titles that mention P112, one-sided decoders, non-full corrections or `Δ`. Nothing proves or kills any of the six multisets, uses a rank condition on the fundamental circuits, or states a floor for `n_nf = 3`. Nearest work: **#2816** (ours; this note closes its stated open residue at `n_nf = 3`), #2724 / #2338 / #2277 (ours), #2784 (ours, case (c)), #1224 (joaqcoo; the model), #1180, #1633, #1815 / #1609 (rigidity of one-sided masked fits), and the COPY-power PRs (different cost model).
Credit: philippeVV (gain law, Discussion #1587 follow-up 6). No file is copied from another contributor.

## 2. Setting, and what is inherited from #2816

Throughout: `T = S_{≤7}` is the span of the codewords of weight ≤ 7 of the lift `S = col P ⊇ 𝒞`, with a minimum-weight basis `q_1..q_a` (weights `w_j ≤ 7`), `D = 𝒞 ∩ T`, `d = dim D`, `e = a − d`, `λ: T → T/D ≅ K^e`, `λ_j = λ(q_j)`, and `weight(p) = rank_F2 ℓ(supp p)` (#2816 §3). The root code is `𝒞 = {p_h}`, `Off(h) = supp p_h`, `p` is injective.
`Λ(V)` = P112 lines whose label lies in the label subspace `V ⊆ F2^9`; `F_b` = label span of `supp q_b`, `dim F_b = w_b`.

**Inherited from #2816 (not recomputed here; they are the CHECKED inputs of its `verify.sh`):**
* `|Off(h)| ≥ 53` for `h ≠ 0`, `= 53` for the 112 roots, `56` for the 8 frame directions, `≥ 70` otherwise (§3.2 there); every codeword has weight ≥ 8 (§3.2 there), so every `λ_j ≠ 0`.
* The flat caps `g(1..8) = 1, 2, 4, 8, 12, 20, 36, 64` (`g78.py`, `gsmall.py` there).
* The **circuit lemma** (§5.3 there): a dependency `Σ_J a_j λ_j = 0` is a codeword in `D` supported in `∪_J supp q_j`.
* The reduction at cost 66 (§5.3, §7, §9 there): `c66.py` and `land.py` leave, for slack ≤ 2, **exactly the six `d = 8` multisets** of §0 above (DP → LP → Pencil → triple rule); and the `d = 0, Δ ≤ 1` cases (`n_nf ≤ 1`, `ρ_0 ≤ 1`).

Everything else is proved in this file or computed by `verify.sh` here.

## 3. The Basis Lemma (PROVEN) and the six bases

Take `d = 8`, so `D = 𝒞`, `a = e + 8`.

**Lemma B.** Let `B` be any set of `e` pieces with `{λ_b : b ∈ B}` a basis of `K^e`, and `U_B := ∪_{b∈B} Λ(F_b)`. Then there are **8 linearly independent** directions `h_y` (one per non-basis piece `y ∉ B`) with `Off(h_y) ⊆ U_B ∪ Λ(F_y)`, `dim F_y = w_y ≤ 7`.
*Proof.* Write `λ_y = Σ_{b∈B} c_b λ_b`; then `v_y := q_y − Σ c_b q_b ∈ ker λ = 𝒞`, so `v_y = p_{h_y}` for a unique `h_y`, and `v_y ≠ 0` because the `q`'s are a basis. `supp p_h = Off(h)`, and `supp v_y ⊆ supp q_y ∪ ∪_B supp q_b`; lines of `supp q_y` have labels in `F_y`, lines of `supp q_b` lie in `Λ(F_b)`. The `v_y` (`y ∉ B`; there are `a − e = 8` of them) have `q_y`-coefficient 1 in `v_y` and 0 in every `v_{y'}`, `y' ≠ y`, so they are linearly independent; `p` is injective, so the `h_y` are independent. ∎
(The Pencil Lemma of #2816 §8 used only "distinct `h_y`"; here the `h_y` form a basis of `K^8`, a rank condition. It holds for every `d` with `d` in place of 8.)

**Corollary (kill criterion).** For label subspaces `V_1..V_k` let `H(V_1..V_k)` be the set of directions `h` with `rank_F2 ℓ(Off(h) ∖ (Λ(V_1) ∪ … ∪ Λ(V_k))) ≤ 7`. If `U_B ⊆ Λ(V_1) ∪ … ∪ Λ(V_k)` then the 8 directions `h_y` lie in `H(V_1..V_k)` (since `ℓ(Off(h_y) ∖ U_B) ⊆ F_y` has rank ≤ 7). So if `dim span H(V_1..V_k) ≤ 7` for all such choices, the multiset is impossible.

**Bases (PROVEN).** Any `e` pieces whose total support has `< 53` lines are λ-independent: a dependency would be a nonzero codeword (the `q`'s are independent) with `Off` inside their supports, but `|Off| ≥ 53`. Take `B` = the `e` smallest pieces:

| multiset | e | B | `|U_B| ≤` | cover by (label subspaces of dim ≤ 6) |
|---|---|---|---|---|
| `[7^8,5,5]` | 2 | {5,5} | 24 | a 5-dim, a 5-dim |
| `[7^8,6,4]` | 2 | {6,4} | 28 | a 6-dim, a 4-dim |
| `[7^8,5,4,1]` | 3 | {5,4,1} | 21 | a 5-dim, span(4-piece, t) of dim ≤ 5 |
| `[7^8,6,3,1]` | 3 | {6,3,1} | 25 | a 6-dim, span(3-piece, t) of dim ≤ 4 |
| `[7^6,6^4]` | 2 | {6,6} | 40 | a 6-dim, a 6-dim |
| `[7^5,6^5,1]` | 3 | {6,6,1} | 41 | a 6-dim, a 6-dim, **one extra line `t`** |

`|U_B| ≤ 41 < 53` in every row (flat caps `g`), so `B` is λ-independent, hence a basis of `K^e`. Enlarging each cover to two 6-dimensional subspaces only enlarges `Λ(·)` (monotone), so the Corollary applies with `V_1, V_2` of dimension 6 (and one free line `t` in the last row).

## 4. Lemma S66 (CHECKED twice) and Theorem 6

**Direction list (PROVEN complete for `|Off| ≤ 80`, finite inputs CHECKED by `gen.py`).** If `|Off(h)| ≤ 80` then at least 32 P112 lines are ⊥ `h`; `Φ_h` = the E8 roots ⊥ `h` is a closed subsystem of rank ≤ 7 with ≥ 32 lines: rank 7 gives E7 (63 lines), D7 (42) or E6+A1 (37) (D6+A1 has 31 and A7 has 28, too few); rank 6 gives E6 (36); rank ≤ 5 gives ≤ 20 lines. Rank 7: `h` is proportional to the primitive normal of `M = h^⊥ ∩ E8`, and `|h|² = det M ≤ det(ℤΦ_h) ∈ {2, 4, 6}` (E8 is unimodular), so `h` is a lattice vector of norm 2, 4 or 6 (theta series 240 / 2160 / 6720, all enumerated). Rank 6 (E6): `P = Φ_h^⊥` is a plane with `det(P ∩ E8) = det M ≤ 3`, an even rank-2 lattice, hence A2: the family is an **A2 pencil**, and all 1120 A2 planes have generic `|Off| ∈ {78, 80}` (`gen.py`: 896 and 224). Values found (`gen.py`, `indep.py`): roots 53 (112), frame 56 (8), D7 70 / 73 / 76 (128 / 896 / 56), E6+A1 77 / 79 / 80 (2688 / 448 / 224), pencils 78 / 80. So `|Off| ≤ 76` gives the **1200 directions** (112 + 8 + 128 + 896 + 56); `≤ 77` adds the 2688 E6+A1 directions (3888 in `data.txt`).
"There is a 7-dimensional `G ⊇ ℓ(R)`" is equivalent to `rank_F2 ℓ(R) ≤ 7`, so no enumeration of `G` is needed.

**Lemma S66 (CHECKED, two implementations).** For every pair of 6-dimensional label subspaces `V_1, V_2` and `X := Λ(V_1) ∪ Λ(V_2)`:
`dim_R span{ h : rank_F2 ℓ(Off(h) ∖ X) ≤ 7 } ≤ 3` (at most 6 such directions).
**Lemma S66+t (CHECKED, two implementations).** The same with one further line removed from `Off(h) ∖ X`, chosen separately for each `h` (a superset of the set needed for the row `[7^5,6^5,1]`): span ≤ 3.
*The 1200-list suffices.* An E6+A1 direction (`|Off| = 77`, every 7-dimensional label subspace holds ≤ 32 of its lines — computed, `gT.py` of #2816 and `cap` in `s66.c`) would need `|Off ∩ (X ∪ {t})| ≥ 45 > 41 ≥ |X ∪ {t}|`, so it never qualifies; `indep.py` uses the 1200-list in both modes, `s66.c` mode 1 the 3888-list (a harmless superset).

* **`checks/s66.c`** (C): 12 generators of a group of order 172,032 acting on the 112 lines (8 frame reflections and 4 permutations of the Hamming [8,4,4] code; checked label-linear in `gen.py`); all 776,805 distinct line sets `Λ(V)` of 6-dimensional label subspaces (dual 3-dimensional subspaces of `F2^9`, 788,035 of them); **159 orbit representatives** for `V_1` against **all** `V_2`; exact F2 ranks; exact fraction-free integer real rank. Output: max real rank 3, max number of directions 6, rank-8 pairs 0, in both modes.
* **`checks/indep.py`** (Python/numpy, written separately): other coordinates (frame coordinates `c_j = ⟨r, f_j⟩`), other labels (Gram mod 2 against a random unimodular root basis), directions rebuilt from sums of 1, 2, 3 pairwise orthogonal roots and checked against the theta counts 240 / 2160 / 6720, subspaces by RREF enumeration (788,035 duals, 776,805 distinct), its own orbit code (159 orbits), vectorised over `V_2`, `Fraction` rank. Run in both modes, **chunked 6 ways (`reps i::6`)**; `check_logs.py` asserts that the six chunks cover each of the 159 representatives exactly once. Result: max real rank 3, max 6 directions, in both modes — agrees with `s66.c`.
* **Control (CHECKED).** `s66 0 7` (two 7-dimensional flats): max real rank **8**, 152 rank-8 pairs. So the test is not vacuous: the bound 3 is a property of 6-dimensional flats.

**Theorem 6 (PROVEN from Lemma B + S66/S66+t).** None of `[7^5,6^5,1]`, `[7^6,6^4]`, `[7^8,5,4,1]`, `[7^8,5,5]`, `[7^8,6,3,1]`, `[7^8,6,4]` occurs as a minimum basis of `T = S_{≤7}` with `d = 8`.
*Proof.* §3 gives a λ-basis `B` with `U_B ⊆ Λ(V_1) ∪ Λ(V_2)` (∪ `{t}` for `[7^5,6^5,1]`), `dim V_i = 6`. Lemma B gives 8 linearly independent directions `h_y` with `ℓ(Off(h_y) ∖ U_B)` of rank ≤ 7, which are 8 independent qualifying directions; Lemma S66 (S66+t for the last multiset) allows span ≤ 3. Contradiction. ∎
**Basis-kill (PROVEN, same proof).** Any multiset with `d ≥ 4` that has `e` pieces packing into two groups of total weight ≤ 6 (plus at most one 1-piece) is impossible: `d` independent qualifying directions are needed and at most 3 exist.
Double implementation by multiset: `[7^6,6^4]`, `[7^8,5,5]`, `[7^8,6,4]`, `[7^8,5,4,1]`, `[7^8,6,3,1]` need S66 (`s66.c` and `indep.py` mode 0); `[7^5,6^5,1]` needs S66+t (`s66.c` and `indep.py` mode 1).

## 5. Consequences and the second route

**Inheritance chain.** #2816 §5.3 / §9: for slack `Δ_w ≤ 2` the only unkilled `d ≥ 1` configurations are the six multisets; the `d = 0` cases at `Δ = 2` are closed there by the SMALL2 §10 root-swap argument (at most 2 root swaps). With Theorem 6, **every `d ≥ 1` configuration of slack ≤ 2 is impossible**, hence:

1. **`Δ ≤ 2 ⇒ n_nf ≤ Δ` (decoder level) and `ρ_0 ≤ Δ` (lift level).** With `Δ ≤ 1` (#2816 §5.2, §7) this reads: `Δ ≥ n_nf` whenever `Δ ≤ 2`; equivalently `n_nf ≥ 3 ⇒ Δ ≥ 3`.
2. **One-sided P112, corrected (S5).** Corrected cost `= 64 + Δ − n_nf`. If `Δ ≤ 2` then `n_nf ≤ Δ` and the cost is `≥ 64`; if `Δ ≥ 3` the cost is `≥ 67 − n_nf`. Hence every decoder with **`n_nf ≤ 3`** costs **`≥ 64`**, and **`≥ 67 − n_nf`** for `n_nf ≥ 3` (the coordinate decoder has `n_nf = 0` and cost 64): in all, **`≥ 64 − max(0, n_nf − 3) ≥ 59`** (`n_nf ≤ 8` after normalisation).
3. **Lift level (S6).** `cost_w(S) = 64 + Δ + D ≥ 64 + Δ + max(0, |I| − ρ_0)` (#2816 §7). For `Δ ≤ 2` (`ρ_0 ≤ Δ`) this is `≥ 64 + max(Δ, |I|) ≥ 64 + |I|`; for `Δ ≥ 3` it is `≥ 64 + Δ ≥ 67`, and `≥ 64 + |I|` when `|I| ≤ 3`. So `cost_w(S) ≥ 64 + min(|I|, 3)` for every `I` and every `S ⊇ 𝒞_{X_I}`.
4. **E8 / P120 (`I = [8]`).** Every lift of the E8 root code has `cost_w ≥ 67`, and `≥ 72` unless the P112 restriction has `Δ ≥ 3` (for `Δ ≤ 2` the bound of item 3 is `64 + max(Δ, 8) = 72`). Gain-law form: `|P120| − C(P120) ≤ 53`. A P120 decoder below 72 would need `ρ_0 > Δ ≥ 3`, i.e. ≥ 4 independent z-carrying restricted basis vectors.

**Second route to item 1 (PROVEN; uses the written Carrier Lemma, the `d ≥ 1` kills above, and nothing from the SMALL2 §10 case split).**

*Parity Lemma (PROVEN; recorded for the `κ = 3` extension, not used below).* Lines are E8 roots `r`; labels `ℓ = (1, r̄)`, `β(ℓ_a, ℓ_b) = 1 + ⟨r_a, r_b⟩ mod 2`. (i) Pairwise non-orthogonal lines have β-orthonormal labels, hence independent labels. (ii) Four pairwise non-orthogonal lines never have `ℓ_a + ℓ_b + ℓ_c + ℓ_d = 0`: that would mean `Σ ±r ∈ 2E8`, but `⟨r_a, Σ⟩ = 2 ± 1 ± 1 ± 1` is odd. (CHECKED, as a search over rank-4 quadruples only: `quad.py` finds 0 pairwise non-orthogonal rank-4 quadruples with label sum 0.)

*`d = 0` Carrier Lemma for `κ ≤ 2` (PROVEN; all that is used).* Let `ρS = 𝒞 ⊕ T` with `T = (ρS)_{≤7}`, `𝒞 ∩ T = 0`, `κ := cost_w(T) ≤ 2`, and `F = {ρb ≠ 0}` a spanning family with `Σ_F w = 64 + Δ`, `Δ ≤ 7`. Then the number of z-carrying members of `F` is `≤ Δ`.
*Proof.* `T` is spanned by ≤ 2 one-pieces or by one 2-piece, so `|supp T| ≤ κ ≤ 2`, and `T` contains no z-carrier (a 1- or 2-dimensional flat spanned by ≤ 2 labels contains no `z`: its affine elements are the labels themselves). Put `F_T := F ∩ T`, `F_8 := F ∖ T`. Every vector of weight ≤ 7 lies in `T`, so members of `F_8` have weight ≥ 8 and are `p_h + τ` with `h ≠ 0`. If `F_T` does not span `T` then `|F_8| ≥ 9` and `Σ_F w ≥ 72`; so `F_T` spans `T`, `|F_8| = 8` (else `Σ ≥ 72`), and `Δ ≥ (Σ_{F_T} w − κ) + κ + c_9 = Σ_{F_T} w + c_9`, with `c_9` the number of weight-9 members of `F_8`. A weight-8 member `v = p_h + τ` (`τ ∈ T`) has `|Off(h)| ≤ 64 + |supp T| ≤ 66`, so `h` is a frame or root direction (the next value is 70). Frame `h`: `N(f_j)` minus ≤ 2 lines has ≥ 54 lines, more than `g(7) = 36`, so its label span is all of `W_j`; the flat is `W_j ∌ z`: not carrying. Root `h = r_t`: `Off(r_t)` has label rank 9 and exactly one coloop (`t`), and no pair of lines other than the coloop lowers the rank (`coloop.py` of #2816, CHECKED there); so `t ∈ supp τ`, and every surviving line of `supp τ` must lie in `W_t`, i.e. `supp τ ⊆ Off(r_t)` (a line ⊥ `r_t` has `p_{r_t} = 0` there and cannot be cancelled): a **root swap at `t`**. The `h`'s of `F_8` form a basis of `(𝒞 ⊕ T)/T`, so the swaps sit at distinct lines `t ∈ supp T`: the number `m` of carriers in `F_8` is at most `|supp T| ≤ κ ≤ Σ_{F_T} w`. Hence carriers `≤ m + c_9 ≤ Σ_{F_T} w + c_9 ≤ Δ`. ∎
(The same statement for `κ = 3` needs the 3-piece cases of the proof; that is part of the `Δ = 3` work in progress and is not claimed here.)

*Pipeline (PROVEN).* Let `Δ ≤ 2`. Peeling (#2816 §3.2 (★)) gives `Σ_b w(ρb) = 64 + Δ ≥ cost_w(ρS) = 64 + (cost(T) − 8d) + 8x + c_8`, so the slack `cost(T) − 8d ≤ Δ ≤ 2`, `8x ≤ 2` i.e. `x = 0`. If `d ≥ 1` the multiset has slack ≤ 2, impossible by Theorem 6 and the inherited survivor list. So `d = 0`, `ρS = 𝒞 ⊕ T` and `κ = cost_w(T) ≤ 2`. The Carrier Lemma bounds the z-carrying members by `Δ`; `ρ_0 ≤ #carriers ≤ Δ`, and at decoder level the corrected terms are carriers of the same family, so `n_nf ≤ Δ`. ∎
This route bypasses the case split (A)/(B)/(C) of OS-CHARGE2 §5 / SMALL2 §10 and uses only the `d ≥ 1` kills at slack ≤ 2 plus the Carrier Lemma; it agrees with item 1.

## 6. What remains OPEN (exactly)

1. **`Δ ≥ n_nf` for general `n_nf`**, i.e. corrected cost `≥ 64` with ≥ 4 non-full corrections. This note gives `Δ ≤ 2 ⇒ n_nf ≤ Δ` only. The root-swap family of #2816 §6 attains corrected cost exactly 64 for `n_nf = 1..4`.
2. Two-sided decoders; case (c); other units; positive characteristic (as in #2816).
3. An extension of the method to `Δ = 3` is in progress; it needs eight further `T`-level multisets killed (single-implementation so far) and is **not** part of this note.

## 7. Reproduction

`bash verify.sh [outdir]` (Python ≥ 3.11 with numpy ≥ 2.0 (`np.bitwise_count`); `cc` with 128-bit integers; `nice -n 10`; stages run one after the other, with at most 6 processes at a time and `timeout 1200` on every process; there are no wait loops). Step 0 checks `MANIFEST.sha256`; step 1 regenerates `data.txt` and `gens.txt` with `gen.py` (~15 s) and compares them byte for byte with `data/`, and runs the Parity-Lemma search; step 2 runs `s66.c` (modes 0 and 1 and the 7+7 control) as three parallel processes; steps 3–4 run `indep.py` in mode 0 and mode 1, six chunks each; step 5 `checks/check_logs.py` prints one PASS/FAIL line per assertion above.
`evidence/logs` holds the logs of the original runs (RECORDED): `s66_m0`, `s66_m1`, `s66_m0_d7` (control), `indep_m0` (one serial run of about 50 minutes), `indep_m1_c0..c5` (the six chunks of mode 1), `gen.log`. `SOURCES.json` pins every shipped script to the working-card file it was copied from.
