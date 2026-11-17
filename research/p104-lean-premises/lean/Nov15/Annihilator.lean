/-
Annihilator .  See Annihilator.md.  internal notes section 1.

An entry vector's lineage: charts c 0, ..., c n (subspaces of V); step i is a PUBLIC ascent (c i ≤ c (i+1)) or an
OWNED MOVE that is NESTED (either direction; WholeFloorNest / LAT.md).  Owned rank paid = sum of the owned
descents (finrank (c i) - finrank (c (i+1))).  Ports a carry functionals φ a : V → K, and the entry vector's support
vectors u b lie in the start chart.  Each port a has a leaf chart on which φ a vanishes.
THEOREM: rank of the Gram block [φ a (u b)] ≤ owned descending rank.
Corollary: identity Gram block (orthonormal group) on P ⇒ |P| ≤ owned descending rank.
Counterexample: drop nesting (a lateral owned MOVE, rank 0) and the theorem fails.
-/
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Data.ZMod.Basic

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace Annihilator
open Module

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- modular inequality: for A ≤ B, dim(Φ ⊓ B) + dim A ≤ dim(Φ ⊓ A) + dim B. -/
theorem modular_le (Φ A B : Submodule K (Dual K V)) (hAB : A ≤ B) :
    finrank K (Φ ⊓ B : Submodule K (Dual K V)) + finrank K A
      ≤ finrank K (Φ ⊓ A : Submodule K (Dual K V)) + finrank K B := by
  have h := Submodule.finrank_sup_add_finrank_inf_eq (Φ ⊓ B) A
  have h1 : (Φ ⊓ B) ⊓ A = Φ ⊓ A := by
    ext x; simp only [Submodule.mem_inf]; constructor
    · rintro ⟨⟨a, _⟩, c⟩; exact ⟨a, c⟩
    · rintro ⟨a, c⟩; exact ⟨⟨a, hAB c⟩, c⟩
  have h2 : finrank K ((Φ ⊓ B) ⊔ A : Submodule K (Dual K V)) ≤ finrank K B := by
    apply Submodule.finrank_mono
    exact sup_le inf_le_right hAB
  rw [h1] at h
  omega

/-- the K-set of a chart: functionals of Φ vanishing on c. -/
def Kc (Φ : Submodule K (Dual K V)) (c : Submodule K V) : Submodule K (Dual K V) := Φ ⊓ c.dualAnnihilator

theorem finrank_ann (c : Submodule K V) :
    finrank K c.dualAnnihilator + finrank K c = finrank K V := by
  have := Subspace.finrank_add_finrank_dualAnnihilator_eq c
  omega

/-- one step: finrank K(D) ≤ finrank (K(C) ⊓ K(D)) + (descent from C to D), for a public ascent or a nested owned MOVE. -/
theorem step_bound (Φ : Submodule K (Dual K V)) (C D : Submodule K V) (h : D ≤ C ∨ C ≤ D) :
    finrank K (Kc Φ D) ≤ finrank K (Kc Φ C ⊓ Kc Φ D : Submodule K (Dual K V)) + (finrank K C - finrank K D) := by
  rcases h with hDC | hCD
  · have hann : C.dualAnnihilator ≤ D.dualAnnihilator := Submodule.dualAnnihilator_anti hDC
    have hm := modular_le Φ C.dualAnnihilator D.dualAnnihilator hann
    have e : (Kc Φ C ⊓ Kc Φ D : Submodule K (Dual K V)) = Kc Φ C := by
      apply inf_eq_left.mpr
      exact inf_le_inf_left _ hann
    rw [e]
    have a1 := finrank_ann C
    have a2 := finrank_ann D
    have a3 : finrank K D ≤ finrank K C := Submodule.finrank_mono hDC
    unfold Kc
    omega
  · have hann : D.dualAnnihilator ≤ C.dualAnnihilator := Submodule.dualAnnihilator_anti hCD
    have e : (Kc Φ C ⊓ Kc Φ D : Submodule K (Dual K V)) = Kc Φ D := by
      apply inf_eq_right.mpr
      exact inf_le_inf_left _ hann
    rw [e]; omega

/-- step kinds. -/
inductive Kind | pub | own
  deriving DecidableEq

/-- a lineage. Step i goes from `c i` to `c (i+1)` for i < n. -/
structure Lineage (K V : Type*) [Field K] [AddCommGroup V] [Module K V] where
  n : ℕ
  c : ℕ → Submodule K V
  kind : ℕ → Kind

/-- legality: public steps ascend; owned steps are nested (either direction). -/
def Lineage.Legal (L : Lineage K V) : Prop :=
  ∀ i < L.n, match L.kind i with
    | Kind.pub => L.c i ≤ L.c (i + 1)
    | Kind.own => L.c (i + 1) ≤ L.c i ∨ L.c i ≤ L.c (i + 1)

/-- owned DESCENDING rank paid: sum over owned steps of (dim c i - dim c (i+1)) (truncated). -/
noncomputable def Lineage.ownRank (L : Lineage K V) : ℕ :=
  ∑ i ∈ Finset.range L.n, if L.kind i = Kind.own then finrank K (L.c i) - finrank K (L.c (i + 1)) else 0

theorem Lineage.legal_step {L : Lineage K V} (hL : L.Legal) {i : ℕ} (hi : i < L.n) :
    L.c (i + 1) ≤ L.c i ∨ L.c i ≤ L.c (i + 1) := by
  have := hL i hi
  cases hk : L.kind i <;> simp only [hk] at this
  · exact Or.inr this
  · exact this

/-- the running sum of K-sets stays within dim K(start) + owned rank so far. -/
theorem run_bound (Φ : Submodule K (Dual K V)) (L : Lineage K V) (hL : L.Legal) :
    ∀ m ≤ L.n, finrank K (((Finset.range (m + 1)).sup fun j => Kc Φ (L.c j) : Submodule K (Dual K V)))
      ≤ finrank K (Kc Φ (L.c 0)) +
        ∑ i ∈ Finset.range m, if L.kind i = Kind.own then finrank K (L.c i) - finrank K (L.c (i + 1)) else 0 := by
  intro m
  induction m with
  | zero => intro _; rw [Finset.range_one, Finset.sup_singleton]; simp
  | succ m ih =>
    intro hm
    have ih := ih (by omega)
    set N : Submodule K (Dual K V) := (Finset.range (m + 1)).sup fun j => Kc Φ (L.c j) with hN
    have hsucc : ((Finset.range (m + 1 + 1)).sup fun j => Kc Φ (L.c j)) = N ⊔ Kc Φ (L.c (m + 1)) := by
      rw [Finset.range_add_one (n := m + 1), Finset.sup_insert, sup_comm]
    rw [hsucc]
    have hlt : m < L.n := by omega
    have hstep := step_bound Φ (L.c m) (L.c (m + 1)) (L.legal_step hL hlt)
    have hKN : Kc Φ (L.c m) ≤ N := Finset.le_sup (f := fun j => Kc Φ (L.c j)) (Finset.mem_range.mpr (by omega))
    have hmono : finrank K (Kc Φ (L.c m) ⊓ Kc Φ (L.c (m + 1)) : Submodule K (Dual K V))
        ≤ finrank K (N ⊓ Kc Φ (L.c (m + 1)) : Submodule K (Dual K V)) :=
      Submodule.finrank_mono (inf_le_inf_right _ hKN)
    have hsi := Submodule.finrank_sup_add_finrank_inf_eq N (Kc Φ (L.c (m + 1)))
    -- cost of step m
    have hcost : (finrank K (L.c m) - finrank K (L.c (m + 1))) ≤
        (if L.kind m = Kind.own then finrank K (L.c m) - finrank K (L.c (m + 1)) else 0) + 0 := by
      cases hk : L.kind m
      · -- public: c m ≤ c (m+1), so truncated difference is 0
        have := L.legal_step hL hlt
        have hl := hL m hlt
        simp only [hk] at hl
        have := Submodule.finrank_mono hl
        simp; omega
      · simp
    rw [Finset.sum_range_succ]
    omega

/-- a delivery instance: ports `P` (functionals φ), support vectors `u`; the support lies in the start chart, each
port has a leaf chart in the lineage on which its functional vanishes. -/
structure Delivery (K V : Type*) [Field K] [AddCommGroup V] [Module K V] (P S : Type*) where
  L : Lineage K V
  φ : P → Dual K V
  u : S → V
  start : ∀ b, u b ∈ L.c 0
  leafIdx : P → ℕ
  leaf_le : ∀ a, leafIdx a ≤ L.n
  leaf : ∀ a, ∀ x ∈ L.c (leafIdx a), φ a x = 0

/-- the Gram block [φ a (u b)]. -/
def Delivery.gram {P S : Type*} (D : Delivery K V P S) : Matrix P S K := fun a b => D.φ a (D.u b)

/-- **ANNIHILATOR lemma.**  Gram rank ≤ owned descending rank (any number of hops). -/
theorem annihilator {P S : Type*} [Fintype P] [Fintype S] (D : Delivery K V P S) (hL : D.L.Legal) :
    D.gram.rank ≤ D.L.ownRank := by
  classical
  set Φ : Submodule K (Dual K V) := Submodule.span K (Set.range D.φ) with hΦ
  -- Φ is covered by the running sum of K-sets
  have hcover : Φ ≤ (Finset.range (D.L.n + 1)).sup fun j => Kc Φ (D.L.c j) := by
    apply Submodule.span_le.mpr
    rintro _ ⟨a, rfl⟩
    have hmem : D.φ a ∈ Kc Φ (D.L.c (D.leafIdx a)) := by
      refine ⟨Submodule.subset_span ⟨a, rfl⟩, ?_⟩
      exact (Submodule.mem_dualAnnihilator _).mpr (D.leaf a)
    have hle : Kc Φ (D.L.c (D.leafIdx a)) ≤ (Finset.range (D.L.n + 1)).sup fun j => Kc Φ (D.L.c j) :=
      Finset.le_sup (f := fun j => Kc Φ (D.L.c j)) (Finset.mem_range.mpr (by have := D.leaf_le a; omega))
    exact hle hmem
  have h1 : finrank K Φ ≤ finrank K (Kc Φ (D.L.c 0)) + D.L.ownRank := by
    have := run_bound Φ D.L hL D.L.n le_rfl
    have := Submodule.finrank_mono hcover
    unfold Lineage.ownRank
    omega
  -- Gram rank = dim (map E Φ), and dim Φ = dim (map E Φ) + dim (Φ ⊓ ker E) ≥ ...
  let E : Dual K V →ₗ[K] (S → K) := LinearMap.pi fun b => (LinearMap.applyₗ (D.u b))
  have hE : ∀ f b, E f b = f (D.u b) := fun f b => rfl
  have hset : Set.range D.gram.row = E '' Set.range D.φ := by
    ext v; simp only [Set.mem_range, Set.mem_image]
    constructor
    · rintro ⟨a, rfl⟩; exact ⟨D.φ a, ⟨a, rfl⟩, by ext b; simp [hE, Delivery.gram, Matrix.row]⟩
    · rintro ⟨_, ⟨a, rfl⟩, rfl⟩; exact ⟨a, by ext b; simp [hE, Delivery.gram, Matrix.row]⟩
  have hrank : D.gram.rank = finrank K (Φ.map E : Submodule K (S → K)) := by
    rw [Matrix.rank_eq_finrank_span_row, hset, hΦ, Submodule.map_span]
  have hnull : finrank K (Φ.map E : Submodule K (S → K)) + finrank K (Φ ⊓ LinearMap.ker E : Submodule K (Dual K V))
      = finrank K Φ := by
    have := LinearMap.finrank_range_add_finrank_ker (V := Φ) (E.domRestrict Φ)
    have e1 : LinearMap.range (E.domRestrict Φ) = Φ.map E := by
      rw [LinearMap.range_domRestrict]
    have e2 : finrank K (LinearMap.ker (E.domRestrict Φ)) = finrank K (Φ ⊓ LinearMap.ker E : Submodule K (Dual K V)) := by
      have hm : (LinearMap.ker (E.domRestrict Φ)).map Φ.subtype = Φ ⊓ LinearMap.ker E := by
        rw [LinearMap.ker_domRestrict, Submodule.map_comap_subtype]
      rw [← hm]
      exact (Submodule.finrank_map_subtype_eq Φ _).symm
    rw [e1, e2] at this; exact this
  have hK0 : Kc Φ (D.L.c 0) ≤ Φ ⊓ LinearMap.ker E := by
    refine inf_le_inf_left _ ?_
    intro f hf
    ext b
    exact (Submodule.mem_dualAnnihilator _).mp hf _ (D.start b)
  have := Submodule.finrank_mono hK0
  rw [hrank]
  omega

/-! ### Corollary: orthonormal groups (identity Gram block) -/

/-- An identity block on ports `P`: support vectors `ι a` with φ a (u (ι a')) = δ. -/
theorem identity_block_rank {P S : Type*} [Fintype P] [Fintype S] [DecidableEq P] [DecidableEq S] (G : Matrix P S K)
    (ι : P → S) (hι : Function.Injective ι) (hG : ∀ a a', G a (ι a') = if a = a' then 1 else 0) :
    Fintype.card P ≤ G.rank := by
  classical
  let Sg : Matrix S P K := fun b a' => if b = ι a' then 1 else 0
  have hprod : G * Sg = 1 := by
    ext a a'
    rw [Matrix.mul_apply, Finset.sum_eq_single (ι a')]
    · simp [Sg, hG, Matrix.one_apply]
    · intro b _ hb; simp [Sg, hb]
    · simp
  have := Matrix.rank_mul_le_left G Sg
  rw [hprod, Matrix.rank_one] at this
  exact this

/-- **COROLLARY.** a lineage whose Gram block over its ports is an identity block serves at most
its owned descending rank many ports, with any number of hops. -/
theorem sparse_serves_le {P S : Type*} [Fintype P] [Fintype S] [DecidableEq P] [DecidableEq S] (D : Delivery K V P S)
    (hL : D.L.Legal) (ι : P → S) (hι : Function.Injective ι)
    (hG : ∀ a a', D.φ a (D.u (ι a')) = if a = a' then 1 else 0) :
    Fintype.card P ≤ D.L.ownRank :=
  (identity_block_rank D.gram ι hι hG).trans (annihilator D hL)

/-- Family version: lineages are disjoint in owned MOVEs (each MOVE carries one vector), so their owned
ranks add up to at most the word's total descending owned rank R.  Then the ports served by sparse
(identity-block) entries number at most R. -/
theorem total_sparse_le {ι : Type*} (s : Finset ι) (card : ι → ℕ) (rk : ι → ℕ) (R : ℕ)
    (hc : ∀ i ∈ s, card i ≤ rk i) (hR : ∑ i ∈ s, rk i ≤ R) : ∑ i ∈ s, card i ≤ R :=
  (Finset.sum_le_sum hc).trans hR

/-! ### The NESTING hypothesis is necessary: a lateral owned MOVE of rank 0 breaks the bound -/
section Lateral
/-- V = ℚ^2; chart 0 = span e0, chart 1 = span e1 (incomparable): a lateral owned MOVE. -/
abbrev V2 := Fin 2 → ℚ

def ch0 : Submodule (ℚ) V2 := Submodule.span (ℚ) {Pi.single 0 1}
def ch1 : Submodule (ℚ) V2 := Submodule.span (ℚ) {Pi.single 1 1}

/-- the coordinate-0 functional. -/
def coord0 : Dual (ℚ) V2 := LinearMap.proj 0

theorem lateral_counterexample :
    -- one owned MOVE ch0 → ch1 pays owned descending rank 0 (dims equal), yet the 1x1 Gram block [coord0 e0] = [1] has rank 1.
    finrank (ℚ) ch0 = finrank (ℚ) ch1 ∧ (coord0 (Pi.single 0 1) : ℚ) = 1
      ∧ (∀ x ∈ ch1, coord0 x = 0) ∧ ¬ (ch1 ≤ ch0 ∨ ch0 ≤ ch1) := by
  refine ⟨?_, by simp [coord0], ?_, ?_⟩
  · have h0 : (Pi.single 0 1 : V2) ≠ 0 := by intro h; have := congrFun h 0; simp at this
    have h1 : (Pi.single 1 1 : V2) ≠ 0 := by intro h; have := congrFun h 1; simp at this
    unfold ch0 ch1
    exact (finrank_span_singleton h0).trans (finrank_span_singleton h1).symm
  · intro x hx
    unfold ch1 at hx
    rcases Submodule.mem_span_singleton.mp hx with ⟨a, rfl⟩
    simp [coord0]
  · rintro (h | h)
    · have := h (Submodule.mem_span_singleton_self (Pi.single 1 1 : V2))
      unfold ch0 at this
      rcases Submodule.mem_span_singleton.mp this with ⟨a, ha⟩
      have := congrFun ha 1
      simp at this
    · have := h (Submodule.mem_span_singleton_self (Pi.single 0 1 : V2))
      unfold ch1 at this
      rcases Submodule.mem_span_singleton.mp this with ⟨a, ha⟩
      have := congrFun ha 0
      simp at this

end Lateral

#print axioms annihilator
#print axioms sparse_serves_le
#print axioms lateral_counterexample

end Annihilator
