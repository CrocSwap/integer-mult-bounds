import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.Order.WellFounded
import Mathlib.Order.Preorder.Finite
import Mathlib.Tactic.LinearCombination
import Nov15.FutureAttr

/-!
NETBOWTIE (lane LEANBOWTIE, part 2).  Kernel-only: no sorry / native_decide / new axioms.

BOWTIE theorem for networks (NA.md sec 2b), over any field `K` (e.g. ℚ).
Network conventions as NetNG / NetDoubling: ports `ι` with labels `q_p ∈ F2^h`, nodes `κ` with a strict
DAG order `lt`, charts `b_k ≤ a_k` (`hba`), gathers `F k p ≠ 0 → q_p ∈ a_k`, deposits
`G s k ≠ 0 → q_s ∈ b_k^⊥`, relays `H k j ≠ 0 → lt j k ∧ b_j ≤ a_k`, `N = 1 + H N`, `M = G N F`.
Drop `d_k = dim a_k - dim b_k`, `D = Σ d_k`.

Bowtie structure (explicit data and hypotheses of `BNet`):
 relay components `comp : κ → γ`, each with a hub; every node is `inn`, `out` or the hub;
 relay edges stay inside a component and are `inn → inn`, `inn → hub`, `hub → out`, `out → out`;
 gathers only at `inn`/hub, deposits only at `out`/hub; every `inn` node has a relay out-edge and every
 `out` node a relay in-edge.  (Uniqueness of the parent, i.e. arborescence, is NOT used.)
Results:
 * `Fact`: `N k j = N k h N h j` for `k` not `inn`, `j` not `out`, `h` the hub of `j`'s component
 * `M_eq`: `M = Σ_components (G N)[:,h] ⊗ (N F)[h,:]`  (one rank-one row per component)
 * `in_tree`, `out_tree`: tree inequalities `dim Σ_in a ≤ dim b_h + Σ_in d`, `dim b_h ≤ dim ⋂_out b + Σ_out d`
 * `comp_price`: the row of a component has price `≤` the component's total drop
 * `bowtie_decoder`: a decoder of `M∘Q` with `Σ price ≤ D`;  `bowtie_D_ge_mass`, `bowtie_D_ge_of_wall`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace NetBowtie
open FutureAttr Module Submodule Finset Function PriceLemma Matrix

inductive Role
  | inn | out | hub
  deriving DecidableEq

/-- bowtie network over a field `K` (conventions of NetNG, with `K` in place of `ZMod 4`). -/
structure BNet (K : Type*) [Field K] (ι κ γ : Type*) [Fintype ι] [Fintype κ] [Fintype γ]
    [DecidableEq ι] [DecidableEq κ] [DecidableEq γ] (h : ℕ) where
  q : ι → Fin h → ZMod 2
  lt : κ → κ → Prop
  ltrans : ∀ a b c, lt a b → lt b c → lt a c
  lirr : ∀ a, ¬ lt a a
  a : κ → Chart h
  b : κ → Chart h
  hba : ∀ k, b k ≤ a k
  F : Matrix κ ι K
  G : Matrix ι κ K
  H : Matrix κ κ K
  N : Matrix κ κ K
  hF : ∀ k p, F k p ≠ 0 → q p ∈ a k
  hG : ∀ s k, G s k ≠ 0 → ∀ y ∈ b k, y ⬝ᵥ q s = 0
  hHlt : ∀ k j, H k j ≠ 0 → lt j k
  hH : ∀ k j, H k j ≠ 0 → b j ≤ a k
  hN1 : N = 1 + H * N
  hN2 : N = 1 + N * H
  -- bowtie structure
  comp : κ → γ
  role : κ → Role
  hub : γ → κ
  hhub : ∀ c, comp (hub c) = c ∧ role (hub c) = Role.hub
  hhub' : ∀ k, role k = Role.hub → k = hub (comp k)
  hcomp : ∀ k j, H k j ≠ 0 → comp k = comp j
  hshape : ∀ k j, H k j ≠ 0 →
    (role j = Role.inn ∧ (role k = Role.inn ∨ role k = Role.hub)) ∨
      (role k = Role.out ∧ (role j = Role.hub ∨ role j = Role.out))
  hgath : ∀ k p, F k p ≠ 0 → role k ≠ Role.out
  hdep : ∀ s k, G s k ≠ 0 → role k ≠ Role.inn
  hinpar : ∀ j, role j = Role.inn → ∃ k, H k j ≠ 0
  houtpar : ∀ k, role k = Role.out → ∃ j, H k j ≠ 0

namespace BNet
variable {K : Type*} [Field K] {ι κ γ : Type*} [Fintype ι] [Fintype κ] [Fintype γ]
  [DecidableEq ι] [DecidableEq κ] [DecidableEq γ] {h : ℕ}
variable (Nt : BNet K ι κ γ h)

noncomputable def drop (k : κ) : ℕ := finrank (ZMod 2) (Nt.a k) - finrank (ZMod 2) (Nt.b k)
noncomputable def D : ℕ := ∑ k, Nt.drop k

theorem wf : WellFounded Nt.lt := by
  haveI : IsTrans κ Nt.lt := ⟨Nt.ltrans⟩
  haveI : Std.Irrefl Nt.lt := ⟨Nt.lirr⟩
  exact Finite.wellFounded_of_trans_of_irrefl _

theorem Nrec (k j : κ) : Nt.N k j = (if k = j then 1 else 0) + ∑ m, Nt.H k m * Nt.N m j := by
  have := congrFun (congrFun Nt.hN1 k) j
  simpa [Matrix.add_apply, Matrix.one_apply, Matrix.mul_apply] using this

/-- walks never leave a relay component -/
theorem N_cross (j : κ) : ∀ k, Nt.comp k ≠ Nt.comp j → Nt.N k j = 0 := by
  intro k
  induction k using Nt.wf.induction with
  | _ k ih =>
    intro hk
    rw [Nt.Nrec, if_neg (fun e => hk (by rw [e])), zero_add]
    apply Finset.sum_eq_zero
    intro m _
    by_cases hHm : Nt.H k m = 0
    · simp [hHm]
    · have hc := Nt.hcomp k m hHm
      rw [ih m (Nt.hHlt k m hHm) (by rw [← hc]; exact hk), mul_zero]

/-- nothing flows from the hub or the out-part into the in-part -/
theorem N_in_zero (j : κ) (hj : Nt.role j ≠ Role.inn) : ∀ k, Nt.role k = Role.inn → Nt.N k j = 0 := by
  intro k
  induction k using Nt.wf.induction with
  | _ k ih =>
    intro hk
    rw [Nt.Nrec, if_neg (fun e => hj (by rw [← e]; exact hk)), zero_add]
    apply Finset.sum_eq_zero
    intro m _
    by_cases hHm : Nt.H k m = 0
    · simp [hHm]
    · have hs := Nt.hshape k m hHm
      have hm : Nt.role m = Role.inn := by
        rcases hs with ⟨h1, _⟩ | ⟨h1, _⟩
        · exact h1
        · rw [hk] at h1; exact absurd h1 (by decide)
      rw [ih m (Nt.hHlt k m hHm) hm, mul_zero]

theorem N_hub_hub (c : γ) : Nt.N (Nt.hub c) (Nt.hub c) = 1 := by
  have hr := (Nt.hhub c).2
  rw [Nt.Nrec, if_pos rfl]
  have : ∑ m, Nt.H (Nt.hub c) m * Nt.N m (Nt.hub c) = 0 := by
    apply Finset.sum_eq_zero
    intro m _
    by_cases hHm : Nt.H (Nt.hub c) m = 0
    · simp [hHm]
    · have hs := Nt.hshape _ m hHm
      have hm : Nt.role m = Role.inn := by
        rcases hs with ⟨h1, _⟩ | ⟨h1, _⟩
        · exact h1
        · rw [hr] at h1; exact absurd h1 (by decide)
      rw [Nt.N_in_zero (Nt.hub c) (by rw [hr]; decide) m hm, mul_zero]
  rw [this, add_zero]

/-- FACTORISATION through the hub of the component of `j`. -/
theorem Fact (j : κ) (hj : Nt.role j ≠ Role.out) (k : κ) (hk : Nt.role k ≠ Role.inn) :
    Nt.N k j = Nt.N k (Nt.hub (Nt.comp j)) * Nt.N (Nt.hub (Nt.comp j)) j := by
  set hj' := Nt.hub (Nt.comp j) with hhj
  have hch : Nt.comp hj' = Nt.comp j := (Nt.hhub _).1
  have key : ∀ k, Nt.role k ≠ Role.inn → Nt.comp k = Nt.comp j →
      Nt.N k j = Nt.N k hj' * Nt.N hj' j := by
    intro k
    induction k using Nt.wf.induction with
    | _ k ih =>
      intro hk hc
      by_cases hr : Nt.role k = Role.hub
      · have hkh : k = hj' := by rw [Nt.hhub' k hr, hc]
        rw [hkh, hhj, Nt.N_hub_hub, one_mul]
      · have hro : Nt.role k = Role.out := by
          cases hh : Nt.role k
          · exact absurd hh hk
          · rfl
          · exact absurd hh hr
        have hne1 : k ≠ j := fun e => hj (by rw [← e]; exact hro)
        have hne2 : k ≠ hj' := fun e => hr (by rw [e]; exact (Nt.hhub _).2)
        rw [Nt.Nrec k j, if_neg hne1, zero_add, Nt.Nrec k hj', if_neg hne2, zero_add,
          Finset.sum_mul]
        apply Finset.sum_congr rfl
        intro m _
        by_cases hHm : Nt.H k m = 0
        · simp [hHm]
        · have hs := Nt.hshape k m hHm
          have hmn : Nt.role m ≠ Role.inn := by
            rcases hs with ⟨_, h2⟩ | ⟨_, h2⟩
            · rcases h2 with h2 | h2 <;> (rw [hro] at h2; exact absurd h2 (by decide))
            · rcases h2 with h2 | h2 <;> (rw [h2]; decide)
          have hcm : Nt.comp m = Nt.comp j := by rw [← Nt.hcomp k m hHm]; exact hc
          rw [ih m (Nt.hHlt k m hHm) hmn hcm]; ring
  by_cases hc : Nt.comp k = Nt.comp j
  · exact key k hk hc
  · rw [Nt.N_cross j k hc, Nt.N_cross hj' k (by rw [hch]; exact hc), zero_mul]


/-! ## one rank-one row per component -/

/-- the decoder row of component `c`: `w = (G N)[:,hub]`, `u = (N F)[hub,:]` -/
noncomputable def row (c : γ) : DRow K ι :=
  ⟨fun s => (Nt.G * Nt.N) s (Nt.hub c), fun p => (Nt.N * Nt.F) (Nt.hub c) p⟩

theorem GN_fact (s : ι) (j : κ) (hj : Nt.role j ≠ Role.out) :
    (Nt.G * Nt.N) s j = (Nt.G * Nt.N) s (Nt.hub (Nt.comp j)) * Nt.N (Nt.hub (Nt.comp j)) j := by
  simp only [Matrix.mul_apply, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro k _
  by_cases hG : Nt.G s k = 0
  · simp [hG]
  · rw [Nt.Fact j hj k (Nt.hdep s k hG)]; ring

/-- DECOMPOSITION: `M = Σ_components (G N)[:,h] ⊗ (N F)[h,:]` (exactly, on every cell) -/
theorem M_eq (s p : ι) :
    (Nt.G * Nt.N * Nt.F) s p = ∑ c, (Nt.row c).w s * (Nt.row c).u p := by
  have hterm : ∀ j : κ, (Nt.G * Nt.N) s j * Nt.F j p =
      (Nt.G * Nt.N) s (Nt.hub (Nt.comp j)) * (Nt.N (Nt.hub (Nt.comp j)) j * Nt.F j p) := by
    intro j
    by_cases hF : Nt.F j p = 0
    · simp [hF]
    · rw [Nt.GN_fact s j (Nt.hgath j p hF)]; ring
  have hsingle : ∀ j : κ, ∑ c, (Nt.G * Nt.N) s (Nt.hub c) * (Nt.N (Nt.hub c) j * Nt.F j p) =
      (Nt.G * Nt.N) s (Nt.hub (Nt.comp j)) * (Nt.N (Nt.hub (Nt.comp j)) j * Nt.F j p) := by
    intro j
    apply Finset.sum_eq_single (Nt.comp j)
    · intro c _ hc
      rw [Nt.N_cross j (Nt.hub c) (by rw [(Nt.hhub c).1]; exact hc)]; simp
    · intro h; exact absurd (Finset.mem_univ _) h
  calc (Nt.G * Nt.N * Nt.F) s p = ∑ j, (Nt.G * Nt.N) s j * Nt.F j p := by rw [Matrix.mul_apply]
    _ = ∑ j, ∑ c, (Nt.G * Nt.N) s (Nt.hub c) * (Nt.N (Nt.hub c) j * Nt.F j p) := by
        apply Finset.sum_congr rfl; intro j _; rw [hsingle j, hterm j]
    _ = ∑ c, ∑ j, (Nt.G * Nt.N) s (Nt.hub c) * (Nt.N (Nt.hub c) j * Nt.F j p) := Finset.sum_comm
    _ = ∑ c, (Nt.row c).w s * (Nt.row c).u p := by
        apply Finset.sum_congr rfl; intro c _
        simp only [row, Matrix.mul_apply, Finset.mul_sum]

/-! ## tree inequalities -/

theorem wf_flip : WellFounded (fun a b => Nt.lt b a) := by
  haveI : IsTrans κ (fun a b => Nt.lt b a) := ⟨fun a b c hab hbc => Nt.ltrans c b a hbc hab⟩
  haveI : Std.Irrefl (fun a b => Nt.lt b a) := ⟨fun a => Nt.lirr a⟩
  exact Finite.wellFounded_of_trans_of_irrefl _

/-- IN-TREE: `dim (Σ_{j∈S} a_j) ≤ dim b_hub + Σ_{j∈S} d_j` for a parent-closed set of in-nodes. -/
theorem in_tree_aux (c : γ) : ∀ (n : ℕ) (S : Finset κ), S.card = n → Nt.hub c ∈ S →
    (∀ j ∈ S, j ≠ Nt.hub c → Nt.role j = Role.inn) →
    (∀ j ∈ S, j ≠ Nt.hub c → ∃ k ∈ S, Nt.H k j ≠ 0) →
    finrank (ZMod 2) (S.sup Nt.a : Chart h) ≤
      finrank (ZMod 2) (Nt.b (Nt.hub c)) + ∑ j ∈ S, Nt.drop j := by
  intro n
  induction n with
  | zero =>
    intro S hS hhub
    rw [Finset.card_eq_zero] at hS; subst hS; simp at hhub
  | succ n ih =>
    intro S hS hhub hrole hpar
    by_cases hne : (S.erase (Nt.hub c)).Nonempty
    · obtain ⟨j, hjS, hmin⟩ := Nt.wf.has_min (↑(S.erase (Nt.hub c)) : Set κ) hne
      have hj1 : j ≠ Nt.hub c := (Finset.mem_erase.1 (Finset.mem_coe.1 hjS)).1
      have hj2 : j ∈ S := (Finset.mem_erase.1 (Finset.mem_coe.1 hjS)).2
      have hcard : (S.erase j).card = n := by rw [Finset.card_erase_of_mem hj2]; omega
      have hhub'' : Nt.hub c ∈ S.erase j := Finset.mem_erase.2 ⟨Ne.symm hj1, hhub⟩
      have hrole'' : ∀ i ∈ S.erase j, i ≠ Nt.hub c → Nt.role i = Role.inn :=
        fun i hi hne => hrole i (Finset.mem_of_mem_erase hi) hne
      have hpar'' : ∀ i ∈ S.erase j, i ≠ Nt.hub c → ∃ k ∈ S.erase j, Nt.H k i ≠ 0 := by
        intro i hi hne
        obtain ⟨k, hkS, hHk⟩ := hpar i (Finset.mem_of_mem_erase hi) hne
        refine ⟨k, Finset.mem_erase.2 ⟨?_, hkS⟩, hHk⟩
        rintro rfl
        exact hmin i (Finset.mem_coe.2 (Finset.mem_erase.2 ⟨hne, Finset.mem_of_mem_erase hi⟩))
          (Nt.hHlt _ _ hHk)
      have IH := ih (S.erase j) hcard hhub'' hrole'' hpar''
      obtain ⟨k, hkS, hHk⟩ := hpar j hj2 hj1
      have hkj : k ≠ j := fun e => Nt.lirr j (e ▸ Nt.hHlt k j hHk)
      have hbj : Nt.b j ≤ ((S.erase j).sup Nt.a) ⊓ Nt.a j :=
        le_inf (le_trans (Nt.hH k j hHk) (Finset.le_sup (f := Nt.a) (Finset.mem_erase.2 ⟨hkj, hkS⟩)))
          (Nt.hba j)
      have e : S.sup Nt.a = Nt.a j ⊔ (S.erase j).sup Nt.a := by
        conv_lhs => rw [← Finset.insert_erase hj2]
        exact Finset.sup_insert
      have hsum : ∑ i ∈ S, Nt.drop i = Nt.drop j + ∑ i ∈ S.erase j, Nt.drop i :=
        (Finset.add_sum_erase S _ hj2).symm
      have d1 := Submodule.finrank_sup_add_finrank_inf_eq ((S.erase j).sup Nt.a) (Nt.a j)
      have d2 : finrank (ZMod 2) (Nt.b j) ≤
          finrank (ZMod 2) (((S.erase j).sup Nt.a) ⊓ Nt.a j : Chart h) := Submodule.finrank_mono hbj
      have d3 : finrank (ZMod 2) (Nt.b j) ≤ finrank (ZMod 2) (Nt.a j) :=
        Submodule.finrank_mono (Nt.hba j)
      have hdj : Nt.drop j = finrank (ZMod 2) (Nt.a j) - finrank (ZMod 2) (Nt.b j) := rfl
      rw [e, sup_comm]
      omega
    · have h0 : S.erase (Nt.hub c) = ∅ := Finset.not_nonempty_iff_eq_empty.1 hne
      rcases (Finset.erase_eq_empty_iff _ _).1 h0 with h1 | h1
      · rw [h1] at hhub; simp at hhub
      · rw [h1]
        have d3 : finrank (ZMod 2) (Nt.b (Nt.hub c)) ≤ finrank (ZMod 2) (Nt.a (Nt.hub c)) :=
          Submodule.finrank_mono (Nt.hba _)
        have e1 : ({Nt.hub c} : Finset κ).sup Nt.a = Nt.a (Nt.hub c) := Finset.sup_singleton
        rw [e1, Finset.sum_singleton]
        unfold drop
        omega

/-- OUT-TREE: `dim b_hub ≤ dim (⋂_{j∈S} b_j) + Σ_{j∈S, j≠hub} d_j` for a parent-closed set of out-nodes. -/
theorem out_tree_aux (c : γ) : ∀ (n : ℕ) (S : Finset κ), S.card = n → Nt.hub c ∈ S →
    (∀ j ∈ S, j ≠ Nt.hub c → Nt.role j = Role.out) →
    (∀ j ∈ S, j ≠ Nt.hub c → ∃ k ∈ S, Nt.H j k ≠ 0) →
    finrank (ZMod 2) (Nt.b (Nt.hub c)) ≤
      finrank (ZMod 2) (S.inf Nt.b : Chart h) + ∑ j ∈ S.erase (Nt.hub c), Nt.drop j := by
  intro n
  induction n with
  | zero =>
    intro S hS hhub
    rw [Finset.card_eq_zero] at hS; subst hS; simp at hhub
  | succ n ih =>
    intro S hS hhub hrole hpar
    by_cases hne : (S.erase (Nt.hub c)).Nonempty
    · obtain ⟨j, hjS, hmax⟩ := Nt.wf_flip.has_min (↑(S.erase (Nt.hub c)) : Set κ) hne
      have hj1 : j ≠ Nt.hub c := (Finset.mem_erase.1 (Finset.mem_coe.1 hjS)).1
      have hj2 : j ∈ S := (Finset.mem_erase.1 (Finset.mem_coe.1 hjS)).2
      have hcard : (S.erase j).card = n := by rw [Finset.card_erase_of_mem hj2]; omega
      have hhub'' : Nt.hub c ∈ S.erase j := Finset.mem_erase.2 ⟨Ne.symm hj1, hhub⟩
      have hrole'' : ∀ i ∈ S.erase j, i ≠ Nt.hub c → Nt.role i = Role.out :=
        fun i hi hne => hrole i (Finset.mem_of_mem_erase hi) hne
      have hpar'' : ∀ i ∈ S.erase j, i ≠ Nt.hub c → ∃ k ∈ S.erase j, Nt.H i k ≠ 0 := by
        intro i hi hne
        obtain ⟨k, hkS, hHk⟩ := hpar i (Finset.mem_of_mem_erase hi) hne
        refine ⟨k, Finset.mem_erase.2 ⟨?_, hkS⟩, hHk⟩
        rintro rfl
        exact hmax i (Finset.mem_coe.2 (Finset.mem_erase.2 ⟨hne, Finset.mem_of_mem_erase hi⟩))
          (Nt.hHlt _ _ hHk)
      have IH := ih (S.erase j) hcard hhub'' hrole'' hpar''
      obtain ⟨k, hkS, hHk⟩ := hpar j hj2 hj1
      have hkj : k ≠ j := fun e => Nt.lirr j (e ▸ Nt.hHlt j k hHk)
      have hIk : (S.erase j).inf Nt.b ≤ Nt.a j :=
        le_trans (Finset.inf_le (f := Nt.b) (Finset.mem_erase.2 ⟨hkj, hkS⟩)) (Nt.hH j k hHk)
      have hle : (S.erase j).inf Nt.b ⊔ Nt.b j ≤ Nt.a j := sup_le hIk (Nt.hba j)
      have e : S.inf Nt.b = Nt.b j ⊓ (S.erase j).inf Nt.b := by
        conv_lhs => rw [← Finset.insert_erase hj2]
        exact Finset.inf_insert
      have hsum : ∑ i ∈ S.erase (Nt.hub c), Nt.drop i =
          Nt.drop j + ∑ i ∈ (S.erase j).erase (Nt.hub c), Nt.drop i := by
        rw [Finset.erase_right_comm]
        exact (Finset.add_sum_erase _ _ (Finset.mem_erase.2 ⟨hj1, hj2⟩)).symm
      have d1 := Submodule.finrank_sup_add_finrank_inf_eq ((S.erase j).inf Nt.b) (Nt.b j)
      have d2 : finrank (ZMod 2) (((S.erase j).inf Nt.b ⊔ Nt.b j : Chart h)) ≤
          finrank (ZMod 2) (Nt.a j) := Submodule.finrank_mono hle
      have d3 : finrank (ZMod 2) (Nt.b j) ≤ finrank (ZMod 2) (Nt.a j) :=
        Submodule.finrank_mono (Nt.hba j)
      have hdj : Nt.drop j = finrank (ZMod 2) (Nt.a j) - finrank (ZMod 2) (Nt.b j) := rfl
      rw [e, inf_comm, hsum]
      omega
    · have h0 : S.erase (Nt.hub c) = ∅ := Finset.not_nonempty_iff_eq_empty.1 hne
      rcases (Finset.erase_eq_empty_iff _ _).1 h0 with h1 | h1
      · rw [h1] at hhub; simp at hhub
      · rw [h1]
        have e1 : ({Nt.hub c} : Finset κ).inf Nt.b = Nt.b (Nt.hub c) := Finset.inf_singleton
        rw [e1]; simp
/-! ## price of a component's row -/

/-- in-nodes of component `c` (the in-part and the hub) -/
def Sin (c : γ) : Finset κ := univ.filter (fun j => Nt.comp j = c ∧ Nt.role j ≠ Role.out)
/-- out-nodes of component `c` (the out-part and the hub) -/
def Sout (c : γ) : Finset κ := univ.filter (fun j => Nt.comp j = c ∧ Nt.role j ≠ Role.inn)

theorem mem_Sin {c : γ} {j : κ} : j ∈ Nt.Sin c ↔ Nt.comp j = c ∧ Nt.role j ≠ Role.out := by
  simp [Sin]

theorem mem_Sout {c : γ} {j : κ} : j ∈ Nt.Sout c ↔ Nt.comp j = c ∧ Nt.role j ≠ Role.inn := by
  simp [Sout]

/-- COMPONENT PRICE: the rank-one row of component `c` costs at most the component's total drop. -/
theorem comp_price (c : γ) :
    price Nt.q (Nt.row c) ≤ ∑ k ∈ univ.filter (fun k => Nt.comp k = c), Nt.drop k := by
  classical
  have hubc := Nt.hhub c
  have hhubIn : Nt.hub c ∈ Nt.Sin c := Nt.mem_Sin.2 ⟨hubc.1, by rw [hubc.2]; decide⟩
  have hhubOut : Nt.hub c ∈ Nt.Sout c := Nt.mem_Sout.2 ⟨hubc.1, by rw [hubc.2]; decide⟩
  have hnothub : ∀ j, Nt.comp j = c → Nt.role j = Role.hub → j = Nt.hub c := by
    intro j hj hr; rw [Nt.hhub' j hr, hj]
  -- tree inequalities
  have T1 := Nt.in_tree_aux c _ (Nt.Sin c) rfl hhubIn
    (by
      intro j hj hne
      obtain ⟨hc, hr⟩ := Nt.mem_Sin.1 hj
      cases hh : Nt.role j
      · rfl
      · exact absurd hh hr
      · exact absurd (hnothub j hc hh) hne)
    (by
      intro j hj hne
      obtain ⟨hc, hr⟩ := Nt.mem_Sin.1 hj
      have hinn : Nt.role j = Role.inn := by
        cases hh : Nt.role j
        · rfl
        · exact absurd hh hr
        · exact absurd (hnothub j hc hh) hne
      obtain ⟨k, hk⟩ := Nt.hinpar j hinn
      refine ⟨k, Nt.mem_Sin.2 ⟨by rw [Nt.hcomp k j hk]; exact hc, ?_⟩, hk⟩
      rcases Nt.hshape k j hk with ⟨_, h2⟩ | ⟨_, h2⟩
      · rcases h2 with h2 | h2 <;> (rw [h2]; decide)
      · rcases h2 with h2 | h2 <;> (rw [hinn] at h2; exact absurd h2 (by decide)))
  have T2 := Nt.out_tree_aux c _ (Nt.Sout c) rfl hhubOut
    (by
      intro j hj hne
      obtain ⟨hc, hr⟩ := Nt.mem_Sout.1 hj
      cases hh : Nt.role j
      · exact absurd hh hr
      · rfl
      · exact absurd (hnothub j hc hh) hne)
    (by
      intro j hj hne
      obtain ⟨hc, hr⟩ := Nt.mem_Sout.1 hj
      have hout : Nt.role j = Role.out := by
        cases hh : Nt.role j
        · exact absurd hh hr
        · rfl
        · exact absurd (hnothub j hc hh) hne
      obtain ⟨k, hk⟩ := Nt.houtpar j hout
      refine ⟨k, Nt.mem_Sout.2 ⟨by rw [← Nt.hcomp j k hk]; exact hc, ?_⟩, hk⟩
      rcases Nt.hshape j k hk with ⟨_, h2⟩ | ⟨_, h2⟩
      · rcases h2 with h2 | h2 <;> (rw [hout] at h2; exact absurd h2 (by decide))
      · rcases h2 with h2 | h2 <;> (rw [h2]; decide))
  -- the pair (M, N) = (I^⊥, V)
  set V : Chart h := (Nt.Sin c).sup Nt.a with hV
  set I : Chart h := (Nt.Sout c).inf Nt.b with hI
  have hIV : I ≤ V := le_trans (Finset.inf_le (f := Nt.b) hhubOut)
    (le_trans (Nt.hba _) (Finset.le_sup (f := Nt.a) hhubIn))
  unfold price
  refine le_trans ((pair_price _ _).2 ⟨perp I, V, ?_, ?_, ?_, rfl⟩) ?_
  · apply Submodule.span_le.2
    rintro _ ⟨t, rfl⟩
    show Nt.q t.1 ∈ perp I
    rw [mem_perp]; intro y hy
    have hw : (Nt.G * Nt.N) t.1 (Nt.hub c) ≠ 0 := t.2
    have hex : ∃ k, Nt.G t.1 k * Nt.N k (Nt.hub c) ≠ 0 := by
      by_contra hcon; push Not at hcon
      apply hw; simp [Matrix.mul_apply, hcon]
    obtain ⟨k, hk⟩ := hex
    obtain ⟨hGk, hNk⟩ := mul_ne_zero_iff.1 hk
    have hck : Nt.comp k = c := by
      by_contra hcne
      exact hNk (Nt.N_cross (Nt.hub c) k (by rw [hubc.1]; exact hcne))
    have hkS : k ∈ Nt.Sout c := Nt.mem_Sout.2 ⟨hck, Nt.hdep _ _ hGk⟩
    have hyb : y ∈ Nt.b k := (Finset.inf_le (f := Nt.b) hkS : (Nt.Sout c).inf Nt.b ≤ Nt.b k) hy
    exact Nt.hG t.1 k hGk y hyb
  · apply Submodule.span_le.2
    rintro _ ⟨p, rfl⟩
    show Nt.q p.1 ∈ V
    have hu : (Nt.N * Nt.F) (Nt.hub c) p.1 ≠ 0 := p.2
    have hex : ∃ j, Nt.N (Nt.hub c) j * Nt.F j p.1 ≠ 0 := by
      by_contra hcon; push Not at hcon
      apply hu; simp [Matrix.mul_apply, hcon]
    obtain ⟨j, hj⟩ := hex
    obtain ⟨hNj, hFj⟩ := mul_ne_zero_iff.1 hj
    have hcj : Nt.comp j = c := by
      by_contra hcne
      exact hNj (Nt.N_cross j (Nt.hub c) (by rw [hubc.1]; exact fun e => hcne e.symm))
    have hjS : j ∈ Nt.Sin c := Nt.mem_Sin.2 ⟨hcj, Nt.hgath _ _ hFj⟩
    exact (Finset.le_sup (f := Nt.a) hjS : Nt.a j ≤ V) (Nt.hF j p.1 hFj)
  · exact perp_anti (K := ZMod 2) hIV
  -- arithmetic
  have hd1 : finrank (ZMod 2) (perp I : Chart h) = h - finrank (ZMod 2) I := finrank_perp I
  have hI1 := finrank_le_n (K := ZMod 2) (n := h) I
  have hV1 := finrank_le_n (K := ZMod 2) (n := h) V
  have hdisj : Disjoint (Nt.Sin c) ((Nt.Sout c).erase (Nt.hub c)) := by
    rw [Finset.disjoint_left]
    intro j hj1 hj2
    obtain ⟨hc, hr⟩ := Nt.mem_Sin.1 hj1
    obtain ⟨hne, hj2'⟩ := Finset.mem_erase.1 hj2
    obtain ⟨_, hr2⟩ := Nt.mem_Sout.1 hj2'
    cases hh : Nt.role j
    · exact hr2 hh
    · exact hr hh
    · exact hne (hnothub j hc hh)
  have hsub : Nt.Sin c ∪ (Nt.Sout c).erase (Nt.hub c) ⊆ univ.filter (fun k => Nt.comp k = c) := by
    intro j hj
    rcases Finset.mem_union.1 hj with hj | hj
    · simp [(Nt.mem_Sin.1 hj).1]
    · simp [(Nt.mem_Sout.1 (Finset.mem_of_mem_erase hj)).1]
  have hsum := Finset.sum_le_sum_of_subset (f := Nt.drop) hsub
  rw [Finset.sum_union hdisj] at hsum
  omega

/-! ## the BOWTIE theorem -/

/-- BOWTIE THEOREM: a decoder of `M∘Q` (one rank-one row per relay component) with total price `≤ D`. -/
theorem bowtie_decoder :
    ∃ rows : List (DRow K ι),
      IsDec Nt.q (fun s p => (Nt.G * Nt.N * Nt.F) s p) rows ∧
        (rows.map (price Nt.q)).sum ≤ Nt.D := by
  classical
  refine ⟨(univ : Finset γ).toList.map Nt.row, ?_, ?_⟩
  · intro t s _
    simp only [List.map_map, Function.comp_def, Finset.sum_map_toList]
    exact (Nt.M_eq t s).symm
  · simp only [List.map_map, Function.comp_def, Finset.sum_map_toList]
    calc ∑ c, price Nt.q (Nt.row c)
        ≤ ∑ c, ∑ k ∈ univ.filter (fun k => Nt.comp k = c), Nt.drop k :=
          Finset.sum_le_sum (fun c _ => Nt.comp_price c)
      _ = Nt.D := Finset.sum_fiberwise univ Nt.comp Nt.drop

/-- `D ≥ m(P)`: the network drop is at least the decoder mass of the realised pattern. -/
theorem bowtie_D_ge_mass (Rec : ι → ι → K)
    (hM : ∀ s p, Nt.q s ⬝ᵥ Nt.q p = 1 → (Nt.G * Nt.N * Nt.F) s p = Rec s p) :
    mass Nt.q Rec ≤ Nt.D := by
  obtain ⟨rows, hd, hle⟩ := Nt.bowtie_decoder
  have hd' : IsDec Nt.q Rec rows := fun t s hts => (hd t s hts).trans (hM t s hts)
  exact le_trans (mass_le hd') hle

/-- with the decoder wall as an explicit hypothesis (e.g. `N = 56` at Q96): `D ≥ N` for bowtie networks. -/
theorem bowtie_D_ge_of_wall (N : ℕ) (Rec : ι → ι → K)
    (hM : ∀ s p, Nt.q s ⬝ᵥ Nt.q p = 1 → (Nt.G * Nt.N * Nt.F) s p = Rec s p)
    (hwall : Wall Nt.q Rec N) : N ≤ Nt.D := by
  obtain ⟨rows, hd, hle⟩ := Nt.bowtie_decoder
  have hd' : IsDec Nt.q Rec rows := fun t s hts => (hd t s hts).trans (hM t s hts)
  exact le_trans (hwall rows hd') hle

end BNet
/-! ## Non-vacuity: a 3-node bowtie over ℚ (in-node → hub → out-node, relay scalars 2 and 1), one port.
`h = 1`, all charts ⊤ except the out-node's `b = ⊥`, so `D = 1`; `M = G N F = 2`; one row of price 1. -/
namespace Toy

def Hm : Matrix (Fin 3) (Fin 3) ℚ := !![0, 0, 0; 2, 0, 0; 0, 1, 0]
def Nm : Matrix (Fin 3) (Fin 3) ℚ := !![1, 0, 0; 2, 1, 0; 2, 1, 1]
def Fm : Matrix (Fin 3) (Fin 1) ℚ := !![1; 0; 0]
def Gm : Matrix (Fin 1) (Fin 3) ℚ := !![0, 0, 1]
def roleT : Fin 3 → Role := ![Role.inn, Role.hub, Role.out]

noncomputable def bchart : Fin 3 → Chart 1 := fun k => if k = 2 then ⊥ else ⊤

noncomputable def toy : BNet ℚ (Fin 1) (Fin 3) Unit 1 where
  q := fun _ _ => 1
  lt := fun a b => a < b
  ltrans := fun a b c h1 h2 => lt_trans h1 h2
  lirr := fun a => lt_irrefl a
  a := fun _ => ⊤
  b := bchart
  hba := fun k => le_top
  F := Fm
  G := Gm
  H := Hm
  N := Nm
  hF := fun _ _ _ => Submodule.mem_top
  hG := by
    intro s k hk y hy
    fin_cases k
    · simp [Gm] at hk
    · simp [Gm] at hk
    · simp [bchart] at hy; subst hy; simp
  hHlt := by
    intro k j hk
    fin_cases k <;> fin_cases j <;> simp [Hm] at hk ⊢
  hH := fun _ _ _ => le_top
  hN1 := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [Hm, Nm, Matrix.mul_apply, Fin.sum_univ_three, Matrix.one_apply]
  hN2 := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [Hm, Nm, Matrix.mul_apply, Fin.sum_univ_three, Matrix.one_apply]
  comp := fun _ => ()
  role := roleT
  hub := fun _ => 1
  hhub := fun c => ⟨rfl, rfl⟩
  hhub' := by
    intro k hk
    fin_cases k <;> simp [roleT] at hk ⊢
  hcomp := fun _ _ _ => rfl
  hshape := by
    intro k j hk
    fin_cases k <;> fin_cases j <;> simp [Hm, roleT] at hk ⊢
  hgath := by
    intro k p hk
    fin_cases k <;> simp [Fm, roleT] at hk ⊢
  hdep := by
    intro s k hk
    fin_cases k <;> simp [Gm, roleT] at hk ⊢
  hinpar := by
    intro j hj
    fin_cases j <;> simp [roleT] at hj
    exact ⟨1, by simp [Hm]⟩
  houtpar := by
    intro k hk
    fin_cases k <;> simp [roleT] at hk
    exact ⟨1, by simp [Hm]⟩

theorem toy_drop_top (k : Fin 3) (hk : k ≠ 2) : toy.drop k = 0 := by
  have hb : toy.b k = ⊤ := by simp [toy, bchart, hk]
  unfold BNet.drop
  rw [hb]
  exact Nat.sub_self _

theorem toy_drop_two : toy.drop 2 = 1 := by
  have hb : toy.b 2 = ⊥ := by simp [toy, bchart]
  unfold BNet.drop
  rw [hb]
  show finrank (ZMod 2) (⊤ : Chart 1) - finrank (ZMod 2) (⊥ : Chart 1) = 1
  simp

theorem toy_D : toy.D = 1 := by
  simp only [BNet.D, Fin.sum_univ_three]
  rw [toy_drop_top 0 (by decide), toy_drop_top 1 (by decide), toy_drop_two]

theorem toy_M : (toy.G * toy.N * toy.F) 0 0 = 2 := by
  simp [toy, Gm, Nm, Fm, Matrix.mul_apply, Fin.sum_univ_three]

/-- the bowtie theorem on the toy: `mass ≤ D = 1` for the pattern `M∘Q = diag(2)`. -/
theorem toy_headline :
    toy.D = 1 ∧ mass toy.q (fun s p => if s = p then (2 : ℚ) else 0) ≤ 1 := by
  refine ⟨toy_D, ?_⟩
  have := toy.bowtie_D_ge_mass (fun s p => if s = p then (2 : ℚ) else 0) (by
    intro s p _
    have hs : s = 0 := Subsingleton.elim _ _
    have hp : p = 0 := Subsingleton.elim _ _
    subst hs; subst hp
    simpa using toy_M)
  rwa [toy_D] at this

end Toy

#print axioms BNet.Fact
#print axioms BNet.M_eq
#print axioms BNet.in_tree_aux
#print axioms BNet.out_tree_aux
#print axioms BNet.comp_price
#print axioms BNet.bowtie_decoder
#print axioms BNet.bowtie_D_ge_mass
#print axioms BNet.bowtie_D_ge_of_wall
#print axioms Toy.toy_headline

end NetBowtie
