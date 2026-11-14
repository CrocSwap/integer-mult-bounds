# Proofs

Notation is as in README "Model". A row k is w_k u_kᵀ with D_k = supp w_k and S_k = supp u_k, and r_k = rank_F2 Q[D_k,S_k]. A closure is a flag F ⊆ B of F2^h with D̄(B) = {t : q_t ∈ B} and S̄(F) = {s : q_s ⊥ F}; its codim is dim B − dim F.

## 1. Row price

**Lemma 1.** climb ≥ dim B − dim(B ∩ A^⊥) = r(D,S), where B and A are the label spans of D and S. Equality is attained.
- **Lower bound.** Each gather of s happens at some frame f ⊆ q_s^⊥, and f_start ⊆ f. So f_start ⊆ A^⊥. Also f_end ⊇ B. Hence climb ≥ dim(B + f_start) − dim f_start = dim B − dim(B ∩ f_start) ≥ dim B − dim(B ∩ A^⊥).
- **Rank identity.** dim B − dim(B ∩ A^⊥) is the rank of the pairing B × A → F2, which equals rank [q_t·q_s]_{t∈D, s∈S}.
- **Equality.** Take a maximal chain from B ∩ A^⊥ to B: gather at the bottom, deposit at the top.
- **Legality.** Frame legality can only raise the price. ∎

**Lemma 2.** Suppose q_t·q_s = 1. Once f ∋ q_t we have f ⊄ q_s^⊥, so every gather of s precedes every deposit into t. On odd cells and on the diagonal, the chain therefore contributes exactly c_t γ_s (deposit coefficient × final gathered content): one rank-1 term per chain. ∎

**Rigidity of rank-8 rows** (finite facts in `rows.py` (e)).
- Write a rank-8 row's deposit as {t : r_t·v ≠ 0} for a real v ≠ 0.
- Suppose its labels span ≤ 9 − c dims. Then they lie in a codim-c label subspace Y^⊥, so every port outside Y^⊥ has r_t·v = 0. Those ports then have real rank ≤ 7.
- The check shows this happens for no codim-2 Y, even after deleting one port. So dim B ≥ 8, and likewise dim A ≥ 8.
- Then r ≥ dim B + dim A − 9 ≥ 7, because dim(B ∩ A^⊥) ≤ 9 − dim A. ∎

## 2. Partial replacement

**Rectangle-rank lemma.** Let I × J consist of odd or diagonal cells only. Then the replacement rows equal 2T_R there, and each row contributes rank ≤ 1. So the number of rows touching I × J is ≥ rank 2T_R[I,J]. ∎
- `partial.py` finds such a rectangle of rank 4 for every one of the 70 R, so ≤ 3 rows are impossible.

**Propagation lemma.** Suppose 4 rows W′U′ᵀ agree with XYᵀ (X, Y of rank 4) on the allowed cells, and 2T_R[I0,J0] has rank 4.
- Then W′[I0] = X[I0]g and U′[J0] = Y[J0]g^{−T} for a single g ∈ GL4.
- Take a port t whose already-forced allowed partners J′ satisfy rank Y[J′] = 4. Then (W′[t]g^{−1} − X[t]) Y[J′]ᵀ = 0, which forces W′[t] = X[t]g. The U side is symmetric. ∎

**Four rows cost ≥ 28.**
- Propagation reaches all ports for 62 R, and all but one common port t0 for 8 R.
- Row k's deposit is X a_k on the forced set, with a_k = g e_k ≠ 0. Since X_R = [G[·,d_j]]_{j∈R}, we have X a = (r_t·v)_t with v = Σ a_j r_{d_j} ≠ 0.
- By §1 (rigidity with one port free), each row has r ≥ 7, so the total is ≥ 28. ∎

**Five rows (FIVEROW).**
- **Step 1: a cheap row sits in a codim-5 closure.** Suppose Σ_{k≤5} r_k ≤ 27. Then some r_5 ≤ 5.
  - Its row lies in D̄(B0) × S̄(F0) with B0 = span labels(D_5) and F0 = B0 ∩ span(labels S_5)^⊥, which has codim r_5.
  - Enlarge B0 and then shrink F0 until the codim is exactly 5 (or B0 = F2^9). Both steps only grow D̄ and S̄.
- **Step 2: rigidity outside the closure.** Outside D̄ × S̄, rows 1–4 alone equal 2T_R. Start blocks come in three forms:
  - I × J, with I ∩ D̄ = ∅;
  - I × (J ∖ S̄), with rank Y[J ∖ S̄] = 4; X[I] is invertible here;
  - the transpose (J ∖ D̄) × I.
  - Propagation follows the lemma above. The single gauge g is shared by all blocks, and this sharing is what couples the four rows.
- **Step 3: β bounds the four rows.** The zero set of X a_k has rank ≤ 3, so it lies in a hyperplane flat h_x. Hence D_k ⊇ KW ∖ h_x and likewise S_k ⊇ KU ∖ h_y. Then r_k ≥ β := min over (h_x, h_y) of rank_F2 Q[KW ∖ h_x, KU ∖ h_y].
- **Step 4: finite check, monotone cover.** Enlarging the closure only removes allowed cells, so a pass on a larger closure covers all closures inside it. The cover is:

  | f = dim F | dim B | how covered | closures |
  |---|---|---|---|
  | 0 | 5 | exact | 3,309,747 |
  | 4 | 9 | exact | 3,309,747 |
  | 1 | 6 | inside (0, B) | 788,035 |
  | 3 | 8 | inside (F, F2^9) | 788,035 |
  | 2 | 7 | inside (F, hyperplane B8) | 43,435 × 127 |

  - The f = 2 coarse covers with β < 7 were refined to every codim-5 sub-closure: 756 (R0123) and 133,308 (R0135), with 0 failures.
  - Result: β ≥ 7 everywhere, so Σ r_k ≥ 28 + r_5 ≥ 28. ∎
  - Status: [C-pin], `data/fiverow-coarse.txt`; independent spot-check and teeth in `fiverow.py`.

**Cross-pair identity.** Let x_j = 2u_j mod 2 and y_j = w_j mod 2.
- G ≡ Σ_i y_i x_iᵀ (mod 2), and Q = J + G (mod 2) entrywise. Hence (2T_R ∘ Q) ≡ Σ_{j∈R} (y_j x_jᵀ) ∘ (J + Σ_i y_i x_iᵀ).
- Expanding gives three kinds of term:
  - the i = j terms equal y_j x_jᵀ (since x² = x mod 2) and cancel the J term;
  - pairs i ≠ j with both i, j ∈ R appear twice and cancel;
  - what remains is Σ_{j∈R, i∉R} (y_i y_j)(x_i x_j)ᵀ. ∎
- **Half-integer bound.** Scale each replacement row so that w_k and 2u_k are 2-adically integral. Then Σ_k diag(w_k) Q_k diag(2u_k) = 2T_R ∘ Q on the prescribed cells. Reduce mod 2: each term has rank ≤ r_k. So Σ r_k ≥ rank_F2 = |R|(8 − |R|). ∎

**Graded 2-adic bound.** Let row k have denominators dividing 2^{e_k}, and put e = max e_k.
- 2^e I = Σ_k 2^{e−e_k} diag(w_k) Q_k diag(2^{e_k} u_k).
- Replace Q_k by L_k ≡ Q_k mod 2^{e_k+1}, with rank s_k from the Smith form. The sum becomes 2^e(I + 2X) with X 2-adically integral, which has rank n.
- Hence n ≤ Σ s_k.
- For e_k = 1, lift an F2 factorisation Q_k = ΦΨᵀ. The mod-4 correction e_2(φ_t ∘ ψ_s) has rank ≤ C(r_k, 2), so s_k ≤ r_k(r_k+1)/2. ∎

## 3. Certificates

**Certificate lemma.** Z ∘ M = diag(Z_pp), which has rank n, because M = I wherever Z ≠ 0. Also Z ∘ M = Σ_k diag(w_k) Z diag(u_k), and the k-th term has rank ≤ rank Z[D_k,S_k]. Subadditivity gives the claim. ∎
- **Mixtures.** Averaging the lemma over a mixture and using climb ≥ r gives C ≥ n/λ.
- **Closures suffice.** The closure of (D,S) under B = span labels(D) and F = B ∩ A^⊥ contains (D,S) and has the same r. Rank is monotone under submatrices.

**Functional splits.** Z_A = Q ∘ [a·q_t = a·q_s for all a ∈ A]. It is zero on even pairs and 1 on the diagonal, and rank Z_A[D,S] = Σ over A-signature blocks of rank_Q Q[D ∩ P, S ∩ P].
- **Restriction monotonicity.** A split of F2^h restricted to F2^6 is a split of F2^6. Lift a flag (F,B) to (F ⊕ W, B ⊕ W) with W = ⟨e7..eh⟩: the price is the same, S is the same and D is larger. So λ_h ≥ λ_6, and likewise λ_h ≥ λ_7.
- **Integrality.** C is an integer and C ≥ n/λ. If λ < 2n/(n−1) (n odd) or λ < 2n/(n−2) (n even), then C ≥ ⌈n/2⌉.

**Full-flag obstruction.** The full flag (D = S = all labels, price h) is fixed by every isometry. So any mixture needs E rank ≤ λh there, and E rank ≥ the minimum over its members. At h = 7 that minimum is 15 (`halfwall.py` (4)), so λ7 ≥ 15/7 for split mixtures, and by restriction λ9 ≥ 15/7. ∎

**Clique obstruction at h = 9.** A pairwise-odd set of size 16 is 1 + T, with T a maximal totally isotropic even subspace, so it contains the all-ones label. Every other clique has size ≤ 8. A clique partition of the 256 odd labels therefore has ≥ 1 + 240/8 = 31 blocks, against the full-flag budget 2h = 18. ∎

## 4. Six or more rows: reduction (Lemma A)

- **Setup.** Sort r_1 ≥ … ≥ r_m with m ≥ 6 and Σ r ≤ 27. Let A be the top 4 rows and C the rest. Each cheap row lies in a closure U_j of codim exactly r_j (§2, Step 1).
- **Bound.** Outside U = ∪_j U_j only the A rows act. So Steps 2–3 give Σ r ≥ Σ_{i∈A} max(β, r_i) + Σ_{j∈C} r_j.
- **Profiles.** Enumerating every profile C with a feasible top 4-tuple leaves 252 dangerous profiles, each with a least β (need) that rules it out. Their needs are 2:4, 3:38, 4:91, 5:83, 6:33 and 7:3; need 7 occurs only for (1,1), (2,1) and (1,1,1). (This profile count is a lane exact run, not re-run by a checker here.)
- **The missing piece (URL).** It remains open to show that every such union still yields β ≥ need(C). The search evidence is in README §4.
