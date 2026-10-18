# Decoder floors, case (b): excess 3 is paid (≥ 64 with ≤ 4 non-full corrections; E8 lifts ≥ 68; no κ claim)

**Scope: a research note, the follow-up to #2816 and #2826 (both ours). Every claim is a written proof plus exact finite computations that `verify.sh` re-runs (about 35–45 minutes, at most 3 processes at a time, each under `timeout 1200`, no SAT solver). No κ claim, no supplier word.**
Only `research/one-sided-excess-three/` is added; nothing existing is changed.

Labels: **PROVEN** (written proof in this file, every finite input listed), **CHECKED** (an exact script re-run by `verify.sh`, assertion in `checks/check_logs.py`), **RECORDED** (a log shipped in `evidence/logs`, not re-run),
**INHERITED** (a statement of #2816 or #2826, cited from its text and not recomputed here), **OPEN**.

## 0. Claims box (scope is part of the claim)

Setting and notation are those of #2816 (P112 = the 112 non-frame lines of E8, dense F2-pairing of rank 9, Gram realisation, **case (b)**: factors `q_j ∈ col M`, factors `p_j` arbitrary; char 0; every number of terms `m`) and of #2826. `n_nf` = number of non-full corrected terms of the *normalised* decoder, as in #2816 §0 / §6. `Δ` = ε-free cost − 64 (decoder level), `Δ = Σ_b w(ρb) − 64` (lift level), as in #2816 §6–7.

| # | Statement | Status |
|---|---|---|
| E1 | **The eight slack-3 multisets are dead.** None of `[7^5,6^5,2]`, `[7^5,6^5,1,1]`, `[7^4,6^6,3]`, `[7^4,6^6,1^3]`, `[7^9,4]`, `[7^9,3,1]` (all `d = 8`) and `[7^3,6^6,2]`, `[7^3,6^6,1,1]` (`d = 7`) occurs as the minimum-weight basis of `T = S_{≤7}`; with #2816 and #2826, **no `d ≥ 1` multiset of slack `cost(T) − 8d ≤ 3` occurs** | PROVEN from Lemma B + the finite statements E1a–E1c; **CHECKED by two independent implementations** (§3) |
| E1a | Two 6-dimensional label flats plus `s ≤ 2` lines: the qualifying directions span **≤ 4** dimensions of `R^8` (hence `< 7`) | CHECKED twice (§3.3) |
| E1b | Two 6-dimensional label flats plus a 3-dimensional label flat: span **≤ 7 < 8** (relaxed to four free lines; ≤ 7 on all pairs except 6), and on the 6 pairs where the relaxed span reaches 8 the exact third-flat refinement over all 161,420 three-dimensional label subspaces gives **≤ 4**. Both E1b multisets have `d = 8`, so `< 8` suffices. | CHECKED twice (§3.3) |
| E1c | A 7-dimensional and a 4-dimensional label flat: span **≤ 4** | CHECKED twice (§3.3) |
| E2 | **`d = 0` Carrier Lemma for `κ ≤ 3`.** If `ρS = 𝒞 ⊕ T`, `T = (ρS)_{≤7}`, `κ = cost_w(T) ≤ 3`, and `F` is a spanning family of nonzero vectors with `Σ_F w = 64 + Δ`, `Δ ≤ 7`, then at most `Δ` members of `F` are z-carrying | PROVEN (§4); finite inputs CHECKED (`carrier3.py`) |
| E3 | **`Δ ≤ 3 ⇒ n_nf ≤ Δ` (decoder level) and `Δ ≤ 3 ⇒ ρ_0 ≤ Δ` (lift level)** | PROVEN from E1 + E2 + INHERITED (§5) |
| E4 | **One-sided P112 decoders with `n_nf ≤ 4` non-full corrections (any number of full ones) cost ≥ 64**; in general corrected cost `≥ 64` for `n_nf ≤ 4` and `≥ 68 − n_nf` for `n_nf ≥ 4`, i.e. `≥ 64 − max(0, n_nf − 4) ≥ 60` (`n_nf ≤ 8`) — was `≥ 64 − max(0, n_nf − 3) ≥ 59` in #2826 | PROVEN from E3 |
| E5 | **Lift level:** every `S ⊇ 𝒞_{X_I}` has `cost_w(S) ≥ 64 + Δ + max(0, |I| − ρ_0) ≥ 64 + min(|I|, 4)`; every lift of the E8 root code (every E8/P120 decoder) has `cost_w ≥ 68`, and `≥ 72` unless the P112 restriction has `Δ ≥ 4`; gain-law form `|P120| − C(P120) ≤ 52` | PROVEN from E3 |

**Tightness.** The root-swap family of #2816 §6 (exact `P·Y = C`, `rootswap.py` there) attains corrected cost exactly 64 for `n_nf = 1, 2, 3, 4`, so E4 (`≥ 64` for `n_nf ≤ 4`) cannot be improved at `n_nf = 4`.
**Not claimed / OPEN.** `Δ ≥ n_nf` for `n_nf ≥ 5` (equivalently the cases `Δ ≥ 4`); slack 4 at the `T`-level and `κ = 4` in the Carrier Lemma are not treated here. Two-sided decoders; case (c) (see #2784 for the A2 family); P104 and other punctured units; fields of positive characteristic (as in #2816).

## 1. Overlap and credit

Builds directly on **#2816** (setting, peeling, DP/LP/Pencil/triple rules, root-swap family) and **#2826** (Basis Lemma, direction list, Lemma S66, Parity Lemma, the `κ ≤ 2` Carrier Lemma), both ours; also on #2724 / #2338 / #2277 (ours), #2784 (ours, case (c)), #1224 (joaqcoo; the model). Credit: philippeVV (gain law, Discussion #1587 follow-up 6). No file is copied from another contributor.

## 2. Setting, and what is inherited

Notation of #2826 §2: `T = S_{≤7}`, minimum-weight basis `q_1..q_a` (weights `w_j ≤ 7`), `D = 𝒞 ∩ T`, `d = dim D`, `e = a − d`, `λ: T → T/D ≅ K^e`, `λ_j = λ(q_j)`; `Λ(V)` = P112 lines with label in the label subspace `V ⊆ F2^9`; `weight(p) = rank_F2 ℓ(supp p)`; `Off(h) = supp p_h`; `z_i = (1, f̄_i)`, `W_i = z_i^⊥`; a vector is **z-carrying** if the label span of its support contains some `z_i`.

**INHERITED (cited, not recomputed here).**
* (#2816 §3.2) `|Off(h)| ≥ 53` for `h ≠ 0`, `= 53` for the 112 roots, `56` for the 8 frame directions, `≥ 70` otherwise; every codeword has weight ≥ 8, so every `λ_j ≠ 0`; weight 8 for `p_h` exactly when `h ∝ f_i`.
* (#2816 §3.3) flat caps `g(1..8) = 1, 2, 4, 8, 12, 20, 36, 64`.
* (#2816 §3.2) **Peeling**: `cost_w(S) = 8(s − a_7) + cost_w(T) + c_8`, `s − a_7 = (8 − d) + x`, `x ≥ 0`, so `Δ_w = (cost(T) − 8d) + 8x + c_8` with every term `≥ 0` (#2816 Theorem 1: `cost_w(T) ≥ 8d`).
* (#2816 §4 (C1)–(C3), (LP); §5.3; §8) the necessary conditions on the weight multiset of `T`: DP rules, quotient LP, **Pencil Lemma** (`e − 1` anchor pieces on ≤ 4 lines force `d ≤ 2`), the `e = 2` triple rule; circuit lemma.
* (#2826 §3–§4) **Lemma B** (Basis Lemma; its proof is repeated in §3.1 below), the **direction list** for `|Off| ≤ 80` (complete; rank-7 `E7/D7/E6+A1` directions of norm 2, 4, 6 and the 1120 `A2` pencils with generic `|Off| ∈ {78, 80}`), **Lemma S66 / S66+t** (two 6-flats: span ≤ 3), and the **Parity Lemma** (i), (ii).
* (#2816 §6) Lemma P, normalisation and Theorem A: corrected cost `= 64 + Δ − n_nf`; (#2816 §7) the lift-level identity `cost_w(S) = 64 + Δ + D`, the frame-rank bound `|I| ≤ ρ_0 + |B_+|`, and the definitions of `B_0`, `ρ_0`.

## 3. The eight slack-3 multisets (E1)

### 3.1 Lemma B and the kill criterion (PROVEN; as in #2826 §3, any `d`)

**Lemma B.** Let `B` be any set of `e` pieces with `{λ_b : b ∈ B}` a basis of `K^e`, and `U_B := ∪_{b∈B} Λ(F_b)` (`F_b` = label span of `supp q_b`, `dim F_b = w_b`). Then there are **`d` linearly independent** directions `h_y` (one per non-basis piece `y ∉ B`) with `Off(h_y) ⊆ U_B ∪ Λ(F_y)`, `dim F_y = w_y ≤ 7`.
*Proof.* Write `λ_y = Σ_{b∈B} c_b λ_b`; then `v_y := q_y − Σ c_b q_b ∈ ker λ = D ⊆ 𝒞`, so `v_y = p_{h_y}` for a unique `h_y`, and `v_y ≠ 0` because the `q`'s are independent. `supp v_y ⊆ supp q_y ∪ ∪_B supp q_b`; lines of `supp q_y` have labels in `F_y`, lines of `supp q_b` lie in `Λ(F_b)`. The `v_y` (`y ∉ B`; there are `a − e = d` of them) have `q_y`-coefficient 1 in `v_y` and 0 in every `v_{y'}`, `y' ≠ y`, so they are linearly independent, and `p` is injective. ∎

**Kill criterion.** If `U_B ⊆ X ∪ L` (`X` a union of `Λ(·)` of label flats, `L` a set of `s` lines), the `d` directions `h_y` lie in `H := {h : rank_F2 ℓ(Off(h) ∖ (X ∪ L)) ≤ 7}`, since `ℓ(Off(h_y) ∖ U_B) ⊆ F_y` has rank ≤ 7. So if `dim span H < d` for every admissible `(X, L)`, the multiset is impossible. Replacing "one `L` for all `h`" by "an `L_h` with `|L_h| ≤ s` chosen separately for each `h`" only enlarges `H` (sound for a kill).

**λ-independence of `B` (PROVEN).** Any `e` pieces whose total support has `< 53` lines are λ-independent: a dependency would give a nonzero codeword with `Off` inside their supports, but `|Off| ≥ 53` (#2816; the circuit lemma).

### 3.2 The reduction to eight multisets (CHECKED once: `land3.py 3`)

`checks/land3.py K` enumerates, for `d = 1..8` and slack `k = cost(T) − 8d ≤ K`, the weight multisets passing the DP rules (`dpX.py`, #2816 (C1)–(C3)), then applies in order: the quotient LP (`symlp.py`, #2816 (LP)); **Basis-kill** (`d ≥ 4` and some `e` pieces pack into two groups of total weight ≤ 6, plus at most one further 1-piece: #2826 §4, S66 / S66+t); **Pencil** (`d ≥ 3`, the `e − 1` smallest pieces have `Σ g ≤ 4`: #2816 §8); **E2-triple** (`e = 2` and at least 5 pieces of weight ≤ 6: #2816 §5.3). At `K = 3` it prints: no survivor at slack ≤ 2 (the six `d = 8` multisets of #2816 §9 are among the Basis-killed ones, #2826), and at slack 3 exactly

| multiset | `d` | `e` | `B` (the `e` smallest pieces) | `\|X\| ≤` | cover `X ⊇ U_B` | `\|Off(h_y)\| ≤` | span needed `<` |
|---|---|---|---|---|---|---|---|
| `[7^5,6^5,2]` | 8 | 3 | {2,6,6} | 42 | 6-flat, 6-flat, 2 lines | 78 | 8 |
| `[7^5,6^5,1,1]` | 8 | 4 | {1,1,6,6} | 42 | 6-flat, 6-flat, 2 lines | 78 | 8 |
| `[7^3,6^6,2]` | 7 | 3 | {2,6,6} | 42 | 6-flat, 6-flat, 2 lines | 78 | 7 |
| `[7^3,6^6,1,1]` | 7 | 4 | {1,1,6,6} | 42 | 6-flat, 6-flat, 2 lines | 78 | 7 |
| `[7^4,6^6,3]` | 8 | 3 | {3,6,6} | 44 | 6-flat, 6-flat, 3-flat | 80 | 8 |
| `[7^4,6^6,1^3]` | 8 | 5 | {1,1,1,6,6} | 44 | 6-flat, 6-flat, 3-flat (spanned by the 3 lines) | 80 | 8 |
| `[7^9,4]` | 8 | 2 | {4,7} | 44 | 7-flat, 4-flat | 80 | 8 |
| `[7^9,3,1]` | 8 | 3 | {1,3,7} | 44 | 7-flat, 4-flat (spanned by the 3-piece and the line) | 80 | 8 |

(`X` is the union of the `Λ(·)` of the covering flats; `|X|` is bounded by the flat caps `20 + 20 + 2`, `20 + 20 + 4`, `36 + 8`. Since `U_B ⊆ X` and `|X| ≤ 44 < 53`, `B` is λ-independent (§3.1). The bound on `|Off(h_y)|` is `|X| + g(7) = |X| + 36`.)
**What each stage rests on.** DP, LP, Pencil, triple rule: the written proofs and the finite inputs of #2816 (the code is that of #2816's `c66.py`/`land.py`, run with slack ≤ 3 and with the Basis-kill stage added); Basis-kill: S66 / S66+t of #2826. The **landscape itself is one implementation** (the DP/LP stages are the shared code of #2816); an error there could only keep a dead multiset in the list or remove a live one, and the removed ones are justified stage by stage by the cited statements. The independence below concerns the finite kills of the eight survivors.

### 3.3 The finite statements E1a–E1c (CHECKED twice)

For label flats `V_1, V_2` (dimension 6 or 7, 4), a set `X = Λ(V_1) ∪ Λ(V_2)` and `s ≥ 0`, let `H_s(V_1, V_2)` be the directions `h` of the list with `|Off(h)| ≤ lim` for which some set of at most `s` lines, chosen separately for each `h`, satisfies `rank_F2 ℓ(Off(h) ∖ X ∖ L_h) ≤ 7`; a pencil of directions (an `A2` plane, all members sharing one `Off` set) counts as 2 dimensions, correctly, because every direction with `|Off| ≤ 80` whose root system is `E6` is a member of exactly one pencil and has that pencil's generic `Off` (#2826 §4; all other members of the plane are among the finite directions), so it qualifies iff the generic set does. For the relaxed three-flat case the third flat is then enumerated exactly (below).

| statement | multisets | what is run | bound (needed `<`) |
|---|---|---|---|
| E1a | `[7^5,6^5,2]`, `[7^5,6^5,1,1]` (`<8`); `[7^3,6^6,2]`, `[7^3,6^6,1,1]` (`<7`) | `(6,6)`, `s = 2`, `lim = 78`, all 159 orbit representatives of `V_1` against all 776,805 line sets of `V_2` | span **≤ 4**, ≤ 10 directions; rank histogram `1:14024 2:15950 3:1108 4:65` |
| E1b | `[7^4,6^6,3]`, `[7^4,6^6,1^3]` (`<8`) | `(6,6)`, `s = 4`, `lim = 80`, relaxed; on every pair with relaxed rank 8 (6 pairs) the third flat `V_3` over **all 161,420** three-dimensional label subspaces | relaxed histogram `1:319084 2:592591 3:24565 4:3405 5:543 6:144 7:36 8:6`; exact refinement **≤ 4** on all 6; hence span ≤ 7 < 8 everywhere |
| E1c | `[7^9,4]`, `[7^9,3,1]` (`<8`) | `(7,4)`, `s = 0`, `lim = 80`, 51 orbit representatives of the 7-flat | span **≤ 4**, ≤ 12 directions; `3:6 4:2` |
| controls | — | `(6,6)`, `s = 0`, `lim = 76`: span 3, 6 directions (= S66 of #2826); `(7,7)`, `s = 0`, `lim = 76`: **rank 8 on 152 pairs** | the test is not vacuous |

(For E1b the pairs with relaxed rank ≤ 7 already give `< 8`, and the exact set is a subset of the relaxed one.)

* **Implementation A** (`checks/s6x.c`, with `gen.py 80`, the generator of #2826): labels from the Bourbaki simple-root basis, directions = the primitive E8 vectors of norm ≤ 8 with `|Off| ≤ lim`, plus the 1120 A2 pencils, 12 generators of the group of order 172,032 (8 frame reflections and 4 permutations of the Hamming [8,4,4] code), orbit representatives by union–find over all flats, exact fraction-free integer real rank. A different program from `s66.c` of #2826: it adds the relaxed `s`-line test, pencil handling and the exact third-flat refinement.
* **Implementation B** (`checks/k3.c`, with `checks/gen3.py`; written separately by another card): standard `D8+` coordinates (doubled), labels = coordinates in its own `Z`-basis mod 2, its own direction/pencil derivation (120 / 1080 / 3360 finite directions and 1120 pencils, matching the theta series), its own group (derived, order 172,032, direction list verified invariant), its own flat enumeration (greedy-minimal dual bases), its own qualifier test (dual-pair counting: some `⟨w_1, w_2⟩` with `|R ∩ Z[w_1] ∩ Z[w_2]| ≥ |R| − s`), its own 128-bit exact rational rank, and its own third-flat refinement. The author of B had read the first card's theory notes and kernel before writing it, so what is shared is the mathematical reduction (Lemma B, the direction-list statement, the kill criterion), not code or coordinates.
* The two implementations agree on **every** histogram above, and on both controls; `check_logs.py` asserts the merged chunk results of both against the numbers in the table.

**Proof of E1 (PROVEN).** For each row of §3.2: `B` is λ-independent (§3.1), so a basis of `K^e`; the cover of `U_B` is as in the table (a weight-`w` piece has its label span of dimension `w`, so its support lies in a `w`-flat; a `w`-flat is contained in a 6- or 7-flat, and `Λ` is monotone); Lemma B gives `d` independent directions in `H` with `|Off| ≤ lim`; E1a–E1c give `dim span H ≤ 7 < d` (≤ 4 for E1a and E1c, where `d` may be 7). Contradiction. ∎

### 3.4 What neither implementation re-audits

Lemma B (proved in §3.1; its use for `d < 8` is the same proof), the completeness of the direction list for `|Off| ≤ 80` (proved in #2826 §4, finite inputs `gen.py` there; the pencil remark above is the only addition), the bookkeeping of `land3.py` (one implementation, §3.2), and the Parity and Carrier proofs (§4, written here; their finite inputs are re-run by `carrier3.py`). A reader who wants a second check of the landscape can read `land3.py` (45 lines) against the stage list in §3.2.

## 4. The `d = 0` Carrier Lemma for `κ ≤ 3` (E2, PROVEN)

**Parity Lemma (PROVEN; (i) as in #2826; (ii) in the form needed here, which is stronger than #2826's statement for pairwise non-orthogonal quadruples; (iii) is new).** Lines are E8 roots `r`; labels `ℓ = (1, r̄)`, `β(ℓ_a, ℓ_b) = 1 + ⟨r_a, r_b⟩ mod 2`; distinct lines have `⟨r_a, r_b⟩ ∈ {0, ±1}`, and `Q(x̄) := |x|²/2 mod 2` is well defined on `E8/2E8` with `Q(r̄) = Q(f̄_i) = 1`.
(i) Pairwise non-orthogonal lines have β-orthonormal labels, hence independent labels.
(ii) Four lines `a, b, c, d` with `ℓ_a + ℓ_b + ℓ_c + ℓ_d = 0` have `Σ ±r ∈ 2E8` for every choice of signs, so `⟨r_a, Σ⟩` is even; if `b, c, d` are non-orthogonal to `a` then `⟨r_a, Σ⟩ = 2 ± 1 ± 1 ± 1` is odd: contradiction.
(iii) Three pairwise non-orthogonal lines never have `ℓ_a + ℓ_b + ℓ_c = z_i`: that means `r̄_a + r̄_b + r̄_c = f̄_i`, but `Q(r̄_a + r̄_b + r̄_c) = (6 + 2(±1 ± 1 ± 1))/2 = 3 ± 1 ± 1 ± 1 ≡ 0 ≠ 1 = Q(f̄_i)`.
(CHECKED, `carrier3.py`: 25,088 pairwise non-orthogonal triples, none with label sum in `{z_i}`; 88,704 pairwise non-orthogonal quadruples, none with label sum 0; 24,276 quadruples of lines with label sum 0, none of which has a line non-orthogonal to the other three; control: 7,168 triples with label sum in `{z_i}` exist.)

**Finite inputs of §4 (CHECKED, `carrier3.py`).** (a) `β(ℓ_s, ℓ_t) = 1 + ⟨r_s, r_t⟩ mod 2` on all 112 × 112 pairs, so `ℓ_s ∈ ℓ_t^⊥ ⇔ ⟨r_s, r_t⟩ = ±1`; the `z_i` are not labels of P112 lines and `β(z_i, z_j) = 1` for all `i, j` (so no `z` lies in a flat `W_j`). (b) For every root `r_t` (all 112): `|Off(r_t)| = 53`, label rank 9, `t` is a coloop, `span ℓ(Off(r_t) ∖ t) = W_t := ℓ_t^⊥` (rank 8), and every cocircuit of the 52 lines `Off(r_t) ∖ t` has size ≥ 5 (the minimum is 20): deleting at most 4 lines never lowers the rank. (c) For every frame direction `f_j` (all 8): `|Off| = 56`, label rank 8, label span `W_j`, every cocircuit of size ≥ 5 (minimum 24).

**Lemma (κ ≤ 3).** Let `S'` be a space with `𝒞 ⊆ S'`, `S' = 𝒞 ⊕ T`, `T = S'_{≤7}`, `κ := cost_w(T) ≤ 3`, and `F` a family of nonzero vectors spanning `S'` with `Σ_F w = 64 + Δ`, `Δ ≤ 7`. Then the number of z-carrying members of `F` is at most `Δ`.

*Proof.* **Step 0 (counts).** Every vector of weight ≤ 7 lies in `T`. Put `F_T := F ∩ T`, `F_8 := F ∖ T`; members of `F_8` have weight 8 or 9 (weights are ≤ 9) and are `p_h + τ` with `h ≠ 0`, `τ ∈ T`. `F_8` spans `S'/T ≅ 𝒞`, so `|F_8| ≥ 8`; if `F_T` does not span `T`, then `|F_8| ≥ 9`, `Σ_F w ≥ 72`, `Δ ≥ 8`. So `F_T` spans `T`, `|F_8| = 8`, and `Δ = Σ_{F_T} w + c_9`, `c_9` the number of weight-9 members of `F_8`. The 8 members of `F_8` are a basis of `S'/T`, so their directions `h` are independent. Also `Σ_{F_T} w ≥ κ` (a spanning set contains a basis).

**Step 1 (weight-8 members are frame or root swaps).** `T` has a basis of pieces with weights summing to `κ ≤ 3`; by `g(1), g(2), g(3) = 1, 2, 4` we have `|supp T| ≤ 4`, with `|supp T| ≤ 3` unless `T = ⟨q⟩` for a 3-piece `q` with four lines (§ below). Let `v = p_h + τ ∈ F_8` have weight 8. `Off(h) ∖ supp τ ⊆ supp v`, which lies in a label flat of rank 8 (≤ 64 lines), so `|Off(h)| ≤ 68 < 70`: `h` is a root or a frame direction.
*Frame `h = f_j`.* `Off(f_j) ∖ supp τ` has rank 8 (c: deleting ≤ 4 lines keeps rank 8), so the flat of `v` is `W_j`, which contains no `z_i` (a): `v` is not z-carrying.
*Root `h = r_t`.* If `t ∉ supp τ`, `Off(r_t) ∖ supp τ` contains the coloop `t` and the rank-8 remainder (b), so `v` has weight 9: contradiction. So `t ∈ supp τ`, and `Off(r_t) ∖ supp τ ⊇ Off(r_t) ∖ ({t} ∪ L)` with `|L| ≤ 3` has rank 8 and spans `W_t` (b), so the flat of `v` is `W_t`. A line `s ∈ supp τ`, `s ≠ t`, either has `v(s) ≠ 0`, so `ℓ_s ∈ W_t`, i.e. `⟨r_s, r_t⟩ = ±1` (a); or `v(s) = 0`, so `p_h(s) ≠ 0` and `s ∈ Off(r_t)`, again `⟨r_s, r_t⟩ = ±1`. Hence: **a weight-8 root member is a *swap at `t`*: `t ∈ supp τ` and every other line of `supp τ` is non-orthogonal to `t`.** The directions `h` of the members of `F_8` are independent, so the swaps sit at distinct lines `t ∈ supp T`: their number `m` satisfies `m ≤ |supp T|`.

**Step 2 (counting).** z-carrying members: `m_T` in `F_T`, at most `m` among the weight-8 members of `F_8`, at most `c_9` weight-9 members. Since `Δ = Σ_{F_T} w + c_9`, it is enough to show **`m_T + m ≤ Σ_{F_T} w`**. A z-carrying vector in `T` has weight ≥ 3: a flat spanned by ≤ 2 labels has as affine points (first coordinate 1) only those labels, and `z_i` is not a label (a); for weight 3 its support is three lines with `ℓ_a + ℓ_b + ℓ_c = z_i`.
* `κ ≤ 2`: `T` is spanned by ≤ 2 one-pieces or one 2-piece, `|supp T| ≤ κ`, `m_T = 0`, `m ≤ κ ≤ Σ_{F_T} w`.
* `κ = 3`, `dim T ≥ 2` (pieces `(2,1)` or `(1,1,1)`, so `|supp T| = 3`, `m ≤ 3`): if `m_T = 0`, `m ≤ 3 = κ ≤ Σ`. If `m_T ≥ 1`: either some member of `F_T` is not z-carrying, then `Σ ≥ 3 m_T + 1 ≥ m_T + m` (as `m ≤ 3 ≤ 2m_T + 1`), or all members are z-carrying, `m_T ≥ dim T ≥ 2` and `Σ ≥ 3 m_T ≥ m_T + 4 ≥ m_T + m`.
* `κ = 3`, `T = ⟨q⟩`, `q` of weight 3, all members of `F_T` multiples of `q`, each of weight 3. `supp q` has 3 or 4 lines (`g(3) = 4`).
 - **4 lines**: the labels are the four affine points of a 3-dimensional label space, so they sum to 0 and no `z_i` is among its points: `q` is not z-carrying, `m_T = 0`. A swap at `a ∈ supp q` needs the other three lines non-orthogonal to `a`, which Parity (ii) forbids: `m = 0`.
 - **3 lines, `q` z-carrying** (`ℓ_a + ℓ_b + ℓ_c = z_i`): `m_T = |F_T| ≥ 1`. Two swaps among `{a, b, c}` make them pairwise non-orthogonal (each swap makes the other two lines non-orthogonal to its own), contradicting Parity (iii): `m ≤ 1`, so `m_T + m ≤ 1 + m_T ≤ 3 m_T = Σ_{F_T} w`.
 - **3 lines, not z-carrying**: `m_T = 0`, `m ≤ 3 = κ ≤ Σ`. ∎

(For `κ ≤ 2` this is the Carrier Lemma of #2826 §5; the extra cases `κ = 3` are the ones above.)

## 5. Consequences (E3–E5)

**Theorem Δ3 (PROVEN from E1 + E2 + INHERITED).** Let `S'` be the span of a family `F` of nonzero vectors with `Σ_F w = 64 + Δ`, `Δ ≤ 3`, such that `S' ⊇ 𝒞`; for a decoder `F` = the nonzero columns of `P`, `S' = col P`, `Σ_F w` = the ε-free cost; for a lift `F = {ρb ≠ 0}`, `S' = ρS`. Then at most `Δ` members of `F` are z-carrying.
*Proof.* `cost_w(S') ≤ Σ_F w`, so peeling gives `Δ ≥ (cost(T) − 8d) + 8x + c_8` with `T = S'_{≤7}`, `d = dim(𝒞 ∩ T)`. Hence the slack of `T` is ≤ 3 and `x = 0`. If `d ≥ 1` the weight multiset of a minimum basis of `T` has slack ≤ 3 and satisfies the necessary conditions of #2816, and is impossible: for slack ≤ 2 by #2816 and #2826, for slack 3 by E1. So `d = 0`, `cost_w(T) = κ ≤ 3`, `s' − a_7 = 8` and `S' = 𝒞 ⊕ T`. Apply the Lemma of §4. ∎

1. **E3, lift level.** The members of `B_0` (#2816 §7: drop 0 and `π_F b ≠ 0`) are z-carrying members of `F`, so `ρ_0 ≤ |B_0| ≤ Δ` when `Δ ≤ 3`.
2. **E3, decoder level.** The non-full corrected terms of the normalised decoder are columns `(f_i, U)` with `z_i ∈ U = ℓ-span of their support`, at most one per `i`: z-carrying members of `F`, so `n_nf ≤ Δ` when `Δ ≤ 3`. Equivalently `n_nf ≥ 4 ⇒ Δ ≥ 4`.
3. **E4 (one-sided P112 decoders).** Corrected cost `= 64 + Δ − n_nf` (#2816). If `Δ ≤ 3` then `n_nf ≤ Δ` and the cost is `≥ 64`; if `Δ ≥ 4` the cost is `≥ 68 − n_nf`. So `n_nf ≤ 4` gives `≥ 64`, and in all `≥ 64 − max(0, n_nf − 4) ≥ 60`.
4. **E5 (lift level).** `cost_w(S) = 64 + Δ + D ≥ 64 + Δ + max(0, |I| − ρ_0)` (#2816 §7). For `Δ ≤ 3` this is `≥ 64 + |I|`; for `Δ ≥ 4` it is `≥ 64 + Δ ≥ 68`. So `cost_w(S) ≥ 64 + min(|I|, 4)` for every `I`. For `I = [8]` (every lift of the E8 root code): `≥ 64 + 8 = 72` when `Δ ≤ 3`, and `≥ 68` when `Δ ≥ 4`; so `cost_w ≥ 68` always and `≥ 72` unless `Δ ≥ 4`; gain-law form `|P120| − C(P120) ≤ 120 − 68 = 52`.

## 6. What remains OPEN (exactly)

1. **`Δ ≥ n_nf` for `n_nf ≥ 5`**, i.e. corrected cost `≥ 64` with ≥ 5 non-full corrections; the root-swap family of #2816 §6 reaches exactly 64 for `n_nf ≤ 4` and has no member with `n_nf = 5`, so a proof for `n_nf = 5` would have to be exact on whatever replaces it. This note gives `Δ ≤ 3 ⇒ n_nf ≤ Δ` only.
2. Two-sided decoders; case (c); other units; positive characteristic (as in #2816).

## 7. Reproduction

`bash verify.sh [outdir]` (Python ≥ 3.11 with numpy ≥ 2.0 and scipy; `cc` with 128-bit integers; `nice -n 10`; at most 3 processes at a time, `timeout 1200` on every process, three fixed lanes for the chunked stages (one `wait` on the lanes), no wait loops). Step 0 checks `MANIFEST.sha256`; step 1 regenerates `data80.txt`, `gens.txt` (`gen.py 80`) and `data3.txt` (`gen3.py`) and compares them byte for byte with `data/`, runs `land3.py 3` and `carrier3.py`; step 2 compiles `s6x.c` and `k3.c`; step 3 runs the kills and controls of §3.3 in both implementations (implementation A: 24 chunks of reps for `(6,6)`, `s = 4` with the refinement, 3 chunks for `s = 2`; implementation B: 4 chunks for `s = 4`, 2 for `s = 2`); step 4 `checks/check_logs.py` prints one PASS/FAIL line per assertion above, including that the chunks of every run cover each orbit representative exactly once.
`evidence/logs` holds the logs of the run that produced the numbers above (RECORDED; 2300 s on a heavily loaded machine; `evidence/all.out.txt` is its assertion output: 25 PASS, 0 FAIL); `SOURCES.json` pins every shipped script to the working-card file it was copied from.
