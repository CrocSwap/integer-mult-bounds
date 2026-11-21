import Nov15.LevelCutRelay
import Nov15.CFChain
import Mathlib.Data.Fin.Tuple.Sort

/-!
CFRELAY (lane LEANCF, Nov 20).  Kernel-only.  CARRIER8 on top of CFChain / LevelCutRelay / FutureAttr.
 (2) HOT INTAKES AS RELAYS, class CF.
   `hot_relay_legal`  : taker epoch `j` first-intake chart `K`, hot pickup of a public `P` at time `τ`
        (ADD legality `K <= chart P τ`), publics only ascend (`chartP` monotone), an owned output event of epoch `i` writes into
        `P` at time `σ >= τ` from chart `C_e` (ADD legality `chart P σ <= C_e`): then `A'_j <= B_i` (a LEGAL relay; the epoch
        meet `A'` is below every intake chart and `B` above every output chart: `CFChain.Tr.intake_le / output_le`).
   `same_register_legal` : the same on one register (virtual first intake at the previous epoch's last output).
   `relay_acyclic`, `cf_time_hot` : CF = every referenced event belongs to an epoch whose last intake is before the pickup, so
        last-intake time `lam` strictly increases along relays and the relay graph has no cycle.
 (3) LEVEL CUT FOR CF RUNS.  `Mnode_reindex` (relabelling by any permutation does not change `M_l`), `cf_level_cut`:
        for ANY labelling with injective `lam` increasing along relays,  Σ_l rank M_l <= Σ_k (da k - db k)
        (LevelCutRelay's `abstract_level_D_ge` applied to the `lam`-sorted network).
 (4) RENDEZVOUS LEMMA A (rank-8 facts as hypotheses): `rendezvous_lemma_A`   Σ drops >= 56;
        `rendezvous_lemma_A_run`  R >= 56 for registers whose lives are `CFChain.Life`.
-/

open Module Submodule Finset FutureAttr CFChain Matrix

namespace CFRelay

variable {n : ℕ}

/-! ### (2) relays -/

theorem hot_relay_legal {chartP : ℕ → Chart n} (hmono : Monotone chartP) {τ σ : ℕ} (hτσ : τ ≤ σ)
    {sj0 sj : ES n} {cj : ℕ} {pre post : List (Ev n)}
    (hj : Tr sj0 (pre ++ Ev.intake :: post) sj cj)
    {si0 si : ES n} {ci : ℕ} {pre' post' : List (Ev n)}
    (hi : Tr si0 (pre' ++ Ev.output :: post') si ci)
    (hpick : ∀ t c, Tr sj0 pre t c → t.Z ≤ chartP τ)
    (hwrite : ∀ t c, Tr si0 pre' t c → chartP σ ≤ t.Z) :
    sj.A ≤ si.B := by
  obtain ⟨t, c1, ht, hle⟩ := hj.intake_le pre post rfl
  obtain ⟨u, c2, hu, hle'⟩ := hi.output_le pre' post' rfl
  exact hle.trans ((hpick t c1 ht).trans ((hmono hτσ).trans ((hwrite u c2 hu).trans hle')))

/-- relay on the same register: the next epoch starts with a virtual intake at (a chart below) the chart at the previous
epoch's last output. -/
theorem same_register_legal {A0 Z : Chart n} {sj sj' si0 si : ES n} {cj ci : ℕ} {body pre' post' : List (Ev n)}
    (hj : Tr ⟨A0, ⊥, Z⟩ body sj cj)
    (hi : Tr si0 (pre' ++ Ev.output :: post') si ci)
    (hA0 : ∀ t c, Tr si0 pre' t c → A0 ≤ t.Z) : sj.A ≤ si.B := by
  obtain ⟨u, c2, hu, hle'⟩ := hi.output_le pre' post' rfl
  exact (hj.A_le : sj.A ≤ A0).trans ((hA0 u c2 hu).trans hle')

theorem Step.det {s s1 s2 : ES n} {e : Ev n} {c c' : ℕ} (h1 : Step s e s1 c) (h2 : Step s e s2 c') :
    s1 = s2 ∧ c = c' := by
  cases h1 <;> cases h2 <;> exact ⟨rfl, rfl⟩

theorem Tr.det {s t t' : ES n} {es : List (Ev n)} {c c' : ℕ} (h1 : Tr s es t c) (h2 : Tr s es t' c') :
    t = t' ∧ c = c' := by
  induction h1 generalizing t' c' with
  | nil s => cases h2; exact ⟨rfl, rfl⟩
  | cons hs _ ih =>
    cases h2 with
    | cons hs' h2' =>
      obtain ⟨e1, e2⟩ := Step.det hs hs'
      subst e1; subst e2
      obtain ⟨e3, e4⟩ := ih h2'
      exact ⟨e3, by omega⟩

/-- CF: a hot edge `i → j` has `lam i < τ <= lam j` (`lam` = time of the last intake). -/
theorem cf_time_hot {lami lamj τ : ℕ} (h1 : lami < τ) (h2 : τ ≤ lamj) : lami < lamj := lt_of_lt_of_le h1 h2

theorem relay_acyclic {m : ℕ} (R : Fin m → Fin m → Prop) (lam : Fin m → ℕ)
    (h : ∀ k j, R k j → lam j < lam k) : ∀ k, ¬ Relation.TransGen R k k := by
  have key : ∀ a b, Relation.TransGen R a b → lam b < lam a := by
    intro a b hab
    induction hab with
    | single h' => exact h _ _ h'
    | tail _ h' ih => exact (h _ _ h').trans ih
  intro k hk
  exact lt_irrefl _ (key k k hk)

/-! ### (3) the level cut for CF runs -/

theorem Nmat_submatrix {m : ℕ} (σ : Equiv.Perm (Fin m)) (H : Matrix (Fin m) (Fin m) ℚ) :
    N8.Nmat (H.submatrix σ σ) = (N8.Nmat H).submatrix σ σ := by
  have hp : ∀ i : ℕ, (H.submatrix σ σ) ^ i = (H ^ i).submatrix σ σ := by
    intro i
    induction i with
    | zero => simp
    | succ i ih => rw [pow_succ, ih, pow_succ, Matrix.submatrix_mul_equiv]
  unfold N8.Nmat
  ext a b
  simp [Matrix.sum_apply, hp]

theorem Mnode_reindex {ι κ : Type} [Fintype ι] [Fintype κ] {m : ℕ} (σ : Equiv.Perm (Fin m))
    (G : Matrix ι (Fin m) ℚ) (H : Matrix (Fin m) (Fin m) ℚ) (F : Matrix (Fin m) κ ℚ)
    (da db : Fin m → ℕ) (l : ℕ) :
    N8.Mnode (G.submatrix id σ) (H.submatrix σ σ) (F.submatrix σ id) (da ∘ σ) (db ∘ σ) l =
      N8.Mnode G H F da db l := by
  classical
  have hlow : N8.lowD (db ∘ σ) l = (N8.lowD db l).submatrix σ σ := by
    unfold N8.lowD; rw [Matrix.submatrix_diagonal_equiv]; rfl
  have hhigh : N8.highD (da ∘ σ) l = (N8.highD da l).submatrix σ σ := by
    unfold N8.highD; rw [Matrix.submatrix_diagonal_equiv]; rfl
  unfold N8.Mnode
  rw [hlow, hhigh, Nmat_submatrix]
  simp only [Matrix.submatrix_mul_equiv, Matrix.submatrix_id_id]

/-- **LEVEL CUT FOR CF RUNS.**  Nodes = epochs; `H k j ≠ 0` = relay from epoch `j` into epoch `k` (any slack, the carrier
being free); the relay graph only has to go strictly up in the last-intake time `lam` (distinct epochs have distinct
last-intake events).  Then `Σ_{l ∈ L} rank M_l <= Σ_k (da k - db k)`. -/
theorem cf_level_cut {ι κ : Type} [Fintype ι] [Fintype κ] {m : ℕ}
    (G : Matrix ι (Fin m) ℚ) (H : Matrix (Fin m) (Fin m) ℚ) (F : Matrix (Fin m) κ ℚ)
    (da db : Fin m → ℕ) (lam : Fin m → ℕ) (hlam : Function.Injective lam)
    (hHlam : ∀ k j, H k j ≠ 0 → lam j < lam k) (hH : ∀ k j, H k j ≠ 0 → db j ≤ da k)
    (L : Finset ℕ) :
    ∑ l ∈ L, (N8.Mnode G H F da db l).rank ≤ ∑ k, (da k - db k) := by
  set σ := Tuple.sort lam with hσ
  have hmono : Monotone (lam ∘ σ) := Tuple.monotone_sort lam
  have hlt : ∀ i j : Fin m, lam (σ i) < lam (σ j) → i < j := by
    intro i j h
    by_contra hij
    exact absurd (hmono (not_lt.1 hij)) (not_le.2 h)
  have hHlt : ∀ k j, (H.submatrix σ σ) k j ≠ 0 → j < k := by
    intro k j h
    exact hlt j k (hHlam _ _ h)
  have hH' : ∀ k j, (H.submatrix σ σ) k j ≠ 0 → (db ∘ σ) j ≤ (da ∘ σ) k := fun k j h => hH _ _ h
  have key := N8.abstract_level_D_ge (G.submatrix id σ) (H.submatrix σ σ) (F.submatrix σ id)
    (da ∘ σ) (db ∘ σ) hHlt hH' L
  simp only [Mnode_reindex] at key
  have hs : ∑ k, ((da ∘ σ) k - (db ∘ σ) k) = ∑ k, (da k - db k) :=
    Equiv.sum_comp σ (fun k => da k - db k)
  rw [hs] at key
  exact key

/-! ### (4) Rendezvous Lemma A -/

theorem finrank_le9 (N : Chart 9) : finrank (ZMod 2) N ≤ 9 := by
  simpa using Submodule.finrank_le N

/-- **RENDEZVOUS LEMMA A** (CARRIER8 sec 3).  Epoch factors of rank 8 on both sides, expressed through the three rank-8 facts
(`hF`: every nonzero cold increment has `dim A' <= 1`; `hG`: every nonzero output weight has `dim B >= 8`;
`hM`: `rank (G N F) >= 8`), relay legality `A'_k <= B_j` and CF acyclicity (`lam`): `Σ_k drop_k >= 56`. -/
theorem rendezvous_lemma_A {ι κ : Type} [Fintype ι] [Fintype κ] {m : ℕ}
    (Ap B : Fin m → Chart 9) (G : Matrix ι (Fin m) ℚ) (H : Matrix (Fin m) (Fin m) ℚ)
    (F : Matrix (Fin m) κ ℚ) (lam : Fin m → ℕ) (hlam : Function.Injective lam)
    (hHlam : ∀ k j, H k j ≠ 0 → lam j < lam k)
    (hleg : ∀ k j, H k j ≠ 0 → Ap k ≤ B j)
    (hF : ∀ k p, F k p ≠ 0 → finrank (ZMod 2) (Ap k) ≤ 1)
    (hG : ∀ s k, G s k ≠ 0 → 8 ≤ finrank (ZMod 2) (B k))
    (hM : 8 ≤ (G * N8.Nmat H * F).rank) :
    56 ≤ ∑ k, (finrank (ZMod 2) (Ap k ⊔ B k : Chart 9) - finrank (ZMod 2) (Ap k)) := by
  classical
  set da : Fin m → ℕ := fun k => 9 - finrank (ZMod 2) (Ap k) with hda
  set db : Fin m → ℕ := fun k => 9 - finrank (ZMod 2) (Ap k ⊔ B k : Chart 9) with hdb
  have hAB : ∀ k, finrank (ZMod 2) (Ap k) ≤ finrank (ZMod 2) (Ap k ⊔ B k : Chart 9) :=
    fun k => Submodule.finrank_mono le_sup_left
  have hBB : ∀ k, finrank (ZMod 2) (B k) ≤ finrank (ZMod 2) (Ap k ⊔ B k : Chart 9) :=
    fun k => Submodule.finrank_mono le_sup_right
  have hH : ∀ k j, H k j ≠ 0 → db j ≤ da k := by
    intro k j h
    have h1 : finrank (ZMod 2) (Ap k) ≤ finrank (ZMod 2) (Ap j ⊔ B j : Chart 9) :=
      Submodule.finrank_mono ((hleg k j h).trans le_sup_right)
    have := finrank_le9 (Ap j ⊔ B j)
    simp only [hda, hdb]
    omega
  have hlev := cf_level_cut G H F da db lam hlam hHlam hH (Finset.Icc 2 8)
  have hrk : ∀ l ∈ Finset.Icc 2 8, 8 ≤ (N8.Mnode G H F da db l).rank := by
    intro l hl
    have hl' := Finset.mem_Icc.1 hl
    have hGl : G * N8.lowD db l = G := by
      ext s d
      rw [N8.lowD, Matrix.mul_diagonal]
      by_cases h0 : G s d = 0
      · simp [h0]
      · have h8 := hG s d h0
        have := hBB d
        have : db d < l := by simp only [hdb]; omega
        simp [this]
    have hFl : N8.highD da l * F = F := by
      ext g p
      rw [N8.highD, Matrix.diagonal_mul]
      by_cases h0 : F g p = 0
      · simp [h0]
      · have h1 := hF g p h0
        have : l ≤ da g := by
          have := finrank_le9 (Ap g)
          simp only [hda]; omega
        simp [this]
    have : N8.Mnode G H F da db l = G * N8.Nmat H * F := by
      unfold N8.Mnode
      rw [hGl, hFl]
    rw [this]; exact hM
  have hsum : ∑ _l ∈ Finset.Icc 2 8, 8 ≤ ∑ l ∈ Finset.Icc 2 8, (N8.Mnode G H F da db l).rank :=
    Finset.sum_le_sum hrk
  have h56 : ∑ _l ∈ Finset.Icc 2 8, 8 = 56 := by simp
  have hdrop : ∑ k, (da k - db k) =
      ∑ k, (finrank (ZMod 2) (Ap k ⊔ B k : Chart 9) - finrank (ZMod 2) (Ap k)) := by
    refine Finset.sum_congr rfl fun k _ => ?_
    have := finrank_le9 (Ap k ⊔ B k)
    have := hAB k
    simp only [hda, hdb]
    omega
  rw [← hdrop]
  omega

/-- RENDEZVOUS LEMMA A for runs: registers whose lives are `CFChain.Life` (cold-intake epochs), epochs enumerated as
`nodes`, the carriers giving relays `H`.  Then `R = Σ_r c_r >= 56`. -/
theorem rendezvous_lemma_A_run {ρ m : ℕ} {τ : Type} [Fintype τ] (q : τ → Fin 9 → ZMod 2)
    (Z : Fin ρ → Chart 9) (eps : Fin ρ → List (Epoch ℚ τ 9)) (c : Fin ρ → ℕ)
    (hl : ∀ r, Life q (Z r) (eps r) (c r))
    (nodes : Fin m → Epoch ℚ τ 9)
    (hsum : ∀ f : Epoch ℚ τ 9 → ℕ, ∑ k, f (nodes k) = ∑ r, ((eps r).map f).sum)
    (H : Matrix (Fin m) (Fin m) ℚ) (lam : Fin m → ℕ) (hlam : Function.Injective lam)
    (hHlam : ∀ k j, H k j ≠ 0 → lam j < lam k)
    (hleg : ∀ k j, H k j ≠ 0 → (nodes k).A ≤ (nodes j).B)
    (hF : ∀ k p, (nodes k).u p ≠ 0 → finrank (ZMod 2) (nodes k).A ≤ 1)
    (hG : ∀ s k, (nodes k).w s ≠ 0 → 8 ≤ finrank (ZMod 2) (nodes k).B)
    (hM : 8 ≤ (Matrix.of (fun (s : τ) (k : Fin m) => (nodes k).w s) * N8.Nmat H *
      Matrix.of (fun (k : Fin m) (p : τ) => (nodes k).u p)).rank) :
    56 ≤ ∑ r, c r := by
  have h1 := rendezvous_lemma_A (fun k => (nodes k).A) (fun k => (nodes k).B)
    (Matrix.of (fun (s : τ) (k : Fin m) => (nodes k).w s)) H
    (Matrix.of (fun (k : Fin m) (p : τ) => (nodes k).u p)) lam hlam hHlam hleg
    (fun k p h => hF k p h) (fun s k h => hG s k h) hM
  have h2 := total_drop_le hl nodes hsum
  have h3 : ∑ k, (nodes k).drop =
      ∑ k, (finrank (ZMod 2) ((nodes k).A ⊔ (nodes k).B : Chart 9) - finrank (ZMod 2) (nodes k).A) :=
    rfl
  omega

end CFRelay

#print axioms CFRelay.hot_relay_legal
#print axioms CFRelay.same_register_legal
#print axioms CFRelay.Tr.det
#print axioms CFRelay.relay_acyclic
#print axioms CFRelay.Mnode_reindex
#print axioms CFRelay.cf_level_cut
#print axioms CFRelay.rendezvous_lemma_A
#print axioms CFRelay.rendezvous_lemma_A_run
