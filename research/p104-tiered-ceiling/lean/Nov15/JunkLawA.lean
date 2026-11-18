import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.Perm
import Mathlib.Tactic

/-!
JUNKLAW Law A: the index-coding / acyclic-subset bound with NO junk-count assumption.  See JunkLawA.md.

Abstract model (`LawAModel`).  Rows `t : Fin P` are the owned lifetimes (P = 104 on the natives); `M t` is the X-part `alpha_t . arr_t` of the row `v_t`.
  * `arr : Fin D → (Fin P → K)`: the arrival X-vectors, ONE PER OWNED DESCENDING MOVE.
  * `hspan`: every `v_t` is a combination of arrivals (premise: SP + nested owned moves, JL1 s.1).
  * `hdiag`: `M t t ≠ 0` (premise: the Y_t odd part is `c_t e_t`, `c_t ≠ 0`).
  * `Ev`, `hodd`: off-diagonal entries live only on `Ev`-related (even) partners (premise: odd part of `Y_t` is `c_t e_t`).
  * `hpart`: each `t` has at most 48 even partners (premise: the 48-law universe; used only for the bound `j t ≤ 48`).
`j t` = number of off-diagonal nonzeros of row `t` (the junk of the arrival row).  `J := Σ_t j t` is `|J^arr|`.

Results: `lawA` (`Σ_t 1/(j_t+1) ≤ rank M ≤ D`), `lawA_cs` (`P² ≤ D (J + P)`, i.e. `J ≥ P²/D - P`), `lawA_lin` (`J ≥ 2 (P - D)`), `lawA_96`
(`P = 104`, `D ≤ 56 ⇒ 96 ≤ J`), `junkSet_card` (the junk cells as a `Finset (ℕ × ℕ)` have cardinality `J`), `single_arrival_clique` (core of Theorem S).
-/
namespace JunkLawA
open Finset
open scoped Classical

variable {K : Type*} [Field K] {P : ℕ}

/-- the junk partners of row `t`: off-diagonal nonzeros -/
noncomputable def outN (M : Matrix (Fin P) (Fin P) K) (t : Fin P) : Finset (Fin P) :=
  univ.filter fun s => s ≠ t ∧ M t s ≠ 0

/-- junk count `j_t` of row `t` -/
noncomputable def jc (M : Matrix (Fin P) (Fin P) K) (t : Fin P) : ℕ := (outN M t).card

/-! ### 1. counting permutations (Caro-Wei / MAIS expectation) -/

/-- the permutations ranking `x` strictly below every other element of `B` -/
noncomputable def firstSet (B : Finset (Fin P)) (x : Fin P) : Finset (Equiv.Perm (Fin P)) :=
  univ.filter fun σ => ∀ c ∈ B, c ≠ x → σ x < σ c

theorem firstSet_swap (B : Finset (Fin P)) (x y : Fin P) (hy : y ∈ B) (σ : Equiv.Perm (Fin P)) (hσ : σ ∈ firstSet B x) :
    σ * Equiv.swap x y ∈ firstSet B y := by
  simp only [firstSet, mem_filter, mem_univ, true_and] at hσ ⊢
  intro c hc hcy
  simp only [Equiv.Perm.coe_mul, Function.comp_apply, Equiv.swap_apply_right]
  by_cases hcx : c = x
  · subst hcx
    have hxy : c ≠ y := hcy
    rw [Equiv.swap_apply_left]
    have := hσ y hy (Ne.symm hxy)
    exact this
  · rw [Equiv.swap_apply_of_ne_of_ne hcx hcy]
    exact hσ c hc hcx

theorem card_firstSet_eq (B : Finset (Fin P)) (x y : Fin P) (hx : x ∈ B) (hy : y ∈ B) :
    (firstSet B y).card = (firstSet B x).card := by
  symm
  refine Finset.card_nbij' (fun σ => σ * Equiv.swap x y) (fun σ => σ * Equiv.swap x y) ?_ ?_ ?_ ?_
  · intro σ hσ; exact firstSet_swap B x y hy σ hσ
  · intro σ hσ
    have := firstSet_swap B y x hx σ hσ
    rwa [Equiv.swap_comm] at this
  · intro σ _; simp [mul_assoc]
  · intro σ _; simp [mul_assoc]

theorem sum_card_firstSet (B : Finset (Fin P)) :
    ∑ b ∈ B, (firstSet B b).card = if B.Nonempty then P.factorial else 0 := by
  split_ifs with hB
  · have e : ∀ b, (firstSet B b).card = ∑ σ : Equiv.Perm (Fin P), if σ ∈ firstSet B b then 1 else 0 := by
      intro b; rw [Finset.sum_boole]; simp
    have e' : ∀ σ : Equiv.Perm (Fin P), (B.filter fun b => σ ∈ firstSet B b).card = ∑ b ∈ B, if σ ∈ firstSet B b then 1 else 0 := by
      intro σ; rw [Finset.sum_boole]; simp
    have h1 : ∑ b ∈ B, (firstSet B b).card = ∑ σ : Equiv.Perm (Fin P), (B.filter fun b => σ ∈ firstSet B b).card := by
      calc ∑ b ∈ B, (firstSet B b).card = ∑ b ∈ B, ∑ σ : Equiv.Perm (Fin P), if σ ∈ firstSet B b then 1 else 0 :=
            Finset.sum_congr rfl (fun b _ => e b)
        _ = ∑ σ : Equiv.Perm (Fin P), ∑ b ∈ B, if σ ∈ firstSet B b then 1 else 0 := Finset.sum_comm
        _ = _ := Finset.sum_congr rfl (fun σ _ => (e' σ).symm)
    have h2 : ∀ σ : Equiv.Perm (Fin P), (B.filter fun b => σ ∈ firstSet B b).card = 1 := by
      intro σ
      obtain ⟨b0, hb0, hmin⟩ := Finset.exists_min_image B σ hB
      rw [Finset.card_eq_one]
      refine ⟨b0, ?_⟩
      ext b
      simp only [mem_filter, firstSet, mem_univ, true_and, mem_singleton]
      constructor
      · rintro ⟨hb, hall⟩
        by_contra hne
        have h1 := hall b0 hb0 (Ne.symm hne)
        have h2 := hmin b hb
        exact absurd h1 (not_lt.mpr h2)
      · rintro rfl
        refine ⟨hb0, fun c hc hcb => ?_⟩
        exact lt_of_le_of_ne (hmin c hc) (fun h => hcb (σ.injective h).symm)
    rw [h1]
    simp [h2, Fintype.card_perm]
  · rw [Finset.not_nonempty_iff_eq_empty.mp hB]; simp

/-- the key count: `(|B|) * #{σ | x first in B} = P!` -/
theorem card_mul_firstSet (B : Finset (Fin P)) (x : Fin P) (hx : x ∈ B) :
    B.card * (firstSet B x).card = P.factorial := by
  have h := sum_card_firstSet B
  rw [if_pos ⟨x, hx⟩] at h
  rw [← h, Finset.card_eq_sum_ones, Finset.sum_mul]
  exact Finset.sum_congr rfl fun b hb => by rw [one_mul, card_firstSet_eq B x b hx hb]

/-- the MAIS set of a ranking: rows ranked before all of their junk partners -/
noncomputable def mais (M : Matrix (Fin P) (Fin P) K) (σ : Equiv.Perm (Fin P)) : Finset (Fin P) :=
  univ.filter fun t => ∀ s ∈ outN M t, σ t < σ s

theorem mem_firstSet_insert (M : Matrix (Fin P) (Fin P) K) (t : Fin P) (σ : Equiv.Perm (Fin P)) :
    σ ∈ firstSet (insert t (outN M t)) t ↔ t ∈ mais M σ := by
  simp only [firstSet, mais, mem_filter, mem_univ, true_and, mem_insert]
  constructor
  · intro h s hs
    exact h s (Or.inr hs) (by simp only [outN, mem_filter] at hs; exact hs.2.1)
  · intro h c hc hct
    rcases hc with rfl | hc
    · exact absurd rfl hct
    · exact h c hc

theorem t_not_mem_outN (M : Matrix (Fin P) (Fin P) K) (t : Fin P) : t ∉ outN M t := by simp [outN]

/-- average count: `Σ_σ |mais σ| = P! Σ_t 1/(j_t+1)` -/
theorem sum_mais (M : Matrix (Fin P) (Fin P) K) :
    (∑ σ : Equiv.Perm (Fin P), ((mais M σ).card : ℝ)) = (P.factorial : ℝ) * ∑ t, (1 : ℝ) / (jc M t + 1) := by
  have h1 : (∑ σ : Equiv.Perm (Fin P), ((mais M σ).card : ℝ)) = ∑ t, ((firstSet (insert t (outN M t)) t).card : ℝ) := by
    simp only [Finset.card_eq_sum_ones, Nat.cast_sum, Nat.cast_one, mais]
    simp only [Finset.sum_filter]
    rw [Finset.sum_comm]
    refine Finset.sum_congr rfl fun t _ => ?_
    simp only [firstSet, Finset.sum_filter]
    refine Finset.sum_congr rfl fun σ _ => ?_
    have := mem_firstSet_insert M t σ
    simp only [firstSet, mais, mem_filter, mem_univ, true_and] at this
    by_cases h : ∀ s ∈ outN M t, σ t < σ s
    · rw [if_pos h, if_pos (this.mpr h)]
    · rw [if_neg h, if_neg (fun h' => h (this.mp h'))]
  rw [h1, Finset.mul_sum]
  refine Finset.sum_congr rfl fun t _ => ?_
  have hc := card_mul_firstSet (insert t (outN M t)) t (mem_insert_self _ _)
  rw [Finset.card_insert_of_notMem (t_not_mem_outN M t)] at hc
  have hc' : ((jc M t : ℝ) + 1) * ((firstSet (insert t (outN M t)) t).card : ℝ) = P.factorial := by
    have := congrArg (fun n : ℕ => (n : ℝ)) hc
    simpa [jc] using this
  have hpos : (0 : ℝ) < (jc M t : ℝ) + 1 := by positivity
  field_simp
  linarith

/-! ### 2. triangular rows are independent -/

theorem mais_linIndep (M : Matrix (Fin P) (Fin P) K) (hdiag : ∀ t, M t t ≠ 0) (σ : Equiv.Perm (Fin P)) :
    LinearIndependent K (fun t : mais M σ => M.row (t : Fin P)) := by
  rw [Fintype.linearIndependent_iff]
  intro g hg
  by_contra hne
  push Not at hne
  obtain ⟨i1, hi1⟩ := hne
  have hne' : (univ.filter fun i : mais M σ => g i ≠ 0).Nonempty := ⟨i1, by simpa using hi1⟩
  obtain ⟨i0, hi0, hmin⟩ := Finset.exists_min_image _ (fun i : mais M σ => σ (i : Fin P)) hne'
  have hg0 : g i0 ≠ 0 := by simpa using hi0
  have hcoord := congrFun hg (i0 : Fin P)
  simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at hcoord
  have hterm : ∀ i : mais M σ, i ≠ i0 → g i * M.row (i : Fin P) (i0 : Fin P) = 0 := by
    intro i hi
    by_cases hgi : g i = 0
    · simp [hgi]
    · have hle := hmin i (by simpa using hgi)
      have hne2 : (i : Fin P) ≠ (i0 : Fin P) := fun h => hi (Subtype.ext h)
      have hlt : σ (i0 : Fin P) < σ (i : Fin P) := lt_of_le_of_ne hle (fun h => hne2 (σ.injective h).symm)
      have hzero : M (i : Fin P) (i0 : Fin P) = 0 := by
        by_contra hM
        have hmem : (i0 : Fin P) ∈ outN M (i : Fin P) := by simp [outN, mem_filter, Ne.symm hne2, hM]
        have := (Finset.mem_filter.mp i.2).2 _ hmem
        exact absurd hlt (not_lt.mpr this.le)
      simp [Matrix.row, hzero]
  rw [Finset.sum_eq_single i0 (fun i _ hi => hterm i hi) (by simp)] at hcoord
  exact mul_ne_zero hg0 (hdiag _) hcoord

/-- `|mais σ| ≤ rank M` for every ranking -/
theorem mais_card_le_rank (M : Matrix (Fin P) (Fin P) K) (hdiag : ∀ t, M t t ≠ 0) (σ : Equiv.Perm (Fin P)) :
    (mais M σ).card ≤ M.rank := by
  have hli := mais_linIndep M hdiag σ
  have h1 : Module.finrank K (Submodule.span K (Set.range fun t : mais M σ => M.row (t : Fin P))) = Fintype.card (mais M σ) :=
    finrank_span_eq_card hli
  have h2 : Submodule.span K (Set.range fun t : mais M σ => M.row (t : Fin P)) ≤ Submodule.span K (Set.range M.row) :=
    Submodule.span_mono (by rintro _ ⟨t, rfl⟩; exact ⟨t, rfl⟩)
  rw [Matrix.rank_eq_finrank_span_row]
  have := Submodule.finrank_mono h2
  rw [h1] at this
  simpa using this

/-- **MAIS bound**: `Σ_t 1/(j_t+1) ≤ rank M` (diagonal nonzero; `j_t` = off-diagonal nonzeros of row t). -/
theorem maisBound (M : Matrix (Fin P) (Fin P) K) (hdiag : ∀ t, M t t ≠ 0) :
    ∑ t, (1 : ℝ) / (jc M t + 1) ≤ M.rank := by
  rcases Nat.eq_zero_or_pos P with h0 | hP
  · subst h0; simp
  have hfac : (0 : ℝ) < P.factorial := by exact_mod_cast Nat.factorial_pos P
  have hsum := sum_mais M
  by_contra hlt
  push Not at hlt
  have hall : ∀ σ ∈ (univ : Finset (Equiv.Perm (Fin P))), ((mais M σ).card : ℝ) ≤ M.rank := fun σ _ => by
    exact_mod_cast mais_card_le_rank M hdiag σ
  have := Finset.sum_le_sum hall
  rw [hsum, Finset.sum_const, Finset.card_univ, Fintype.card_perm, Fintype.card_fin, nsmul_eq_mul] at this
  nlinarith

/-! ### 3. the abstract model and Law A -/

/-- Law A model: P rows, D arrival vectors; every premise is a field. -/
structure LawAModel (K : Type*) [Field K] (P D : ℕ) where
  M : Matrix (Fin P) (Fin P) K
  arr : Fin D → (Fin P → K)
  /-- every row `v_t` is a combination of arrivals: one arrival vector per owned descending move -/
  hspan : ∀ t, M t ∈ Submodule.span K (Set.range arr)
  /-- Y_t odd spec: the diagonal coefficient `c_t ≠ 0` -/
  hdiag : ∀ t, M t t ≠ 0
  /-- `Ev t s`: `s` is an even partner of `t` -/
  Ev : Fin P → Fin P → Prop
  /-- odd off-diagonals vanish -/
  hodd : ∀ t s, s ≠ t → M t s ≠ 0 → Ev t s
  /-- 48 even partners -/
  hpart : ∀ t, (univ.filter fun s => s ≠ t ∧ Ev t s).card ≤ 48

namespace LawAModel
variable {D : ℕ} (m : LawAModel K P D)

noncomputable def j (t : Fin P) : ℕ := jc m.M t
/-- the arrival junk `|J^arr|` -/
noncomputable def J : ℕ := ∑ t, m.j t

theorem rank_le : m.M.rank ≤ D := by
  classical
  rw [Matrix.rank_eq_finrank_span_row]
  have h : Submodule.span K (Set.range m.M.row) ≤ Submodule.span K (Set.range m.arr) :=
    Submodule.span_le.mpr (by rintro _ ⟨t, rfl⟩; exact m.hspan t)
  refine le_trans (Submodule.finrank_mono h) ?_
  have h' := finrank_range_le_card (R := K) m.arr
  rw [Fintype.card_fin] at h'
  exact h'

/-- `j t ≤ 48` -/
theorem j_le (t : Fin P) : m.j t ≤ 48 := by
  show (outN m.M t).card ≤ 48
  refine le_trans (Finset.card_le_card ?_) (m.hpart t)
  intro s hs
  simp only [outN, mem_filter, mem_univ, true_and] at hs ⊢
  exact ⟨hs.1, m.hodd t s hs.1 hs.2⟩

/-- **Law A**: `Σ_t 1/(j_t+1) ≤ rank M ≤ D`. -/
theorem lawA : ∑ t, (1 : ℝ) / (m.j t + 1) ≤ D := by
  have h1 := maisBound m.M m.hdiag
  have h2 : (m.M.rank : ℝ) ≤ D := by exact_mod_cast m.rank_le
  exact le_trans h1 h2

/-- Cauchy-Schwarz form: `P² ≤ D (J + P)`, i.e. `J ≥ P²/D - P`. -/
theorem lawA_cs : (P : ℝ) ^ 2 ≤ D * (m.J + P) := by
  have h := Finset.sq_sum_div_le_sum_sq_div (s := (univ : Finset (Fin P))) (fun _ => (1 : ℝ)) (g := fun t => (m.j t : ℝ) + 1)
    (fun t _ => by positivity)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul, mul_one, one_pow] at h
  have hA := m.lawA
  have hs : ∑ t, ((m.j t : ℝ) + 1) = m.J + P := by
    simp [J, Finset.sum_add_distrib]
  rw [hs] at h
  have hpos : (0 : ℝ) < m.J + P ∨ P = 0 := by
    rcases Nat.eq_zero_or_pos P with h0 | h0
    · exact Or.inr h0
    · left; have : (0 : ℝ) < P := by exact_mod_cast h0
      have : (0 : ℝ) ≤ m.J := by positivity
      linarith
  rcases hpos with hp | h0
  · rw [div_le_iff₀ hp] at h
    have h2 : (P : ℝ) ^ 2 ≤ (∑ t, (1 : ℝ) / (m.j t + 1)) * (m.J + P) := by
      simpa using h
    exact le_trans h2 (mul_le_mul_of_nonneg_right hA hp.le)
  · subst h0
    have : (0 : ℝ) ≤ D * m.J := by positivity
    simpa using this

/-- integer tangent: `1 - j/2 ≤ 1/(j+1)` -/
theorem tangent (j : ℕ) : 1 - (j : ℝ) / 2 ≤ 1 / ((j : ℝ) + 1) := by
  rcases Nat.lt_or_ge j 2 with h | h
  · interval_cases j <;> norm_num
  · have hj : (2 : ℝ) ≤ j := by exact_mod_cast h
    have : (0 : ℝ) < 1 / ((j : ℝ) + 1) := by positivity
    linarith

/-- linear form: `J ≥ 2 (P - D)` (reals) -/
theorem lawA_lin : 2 * ((P : ℝ) - D) ≤ m.J := by
  have h := m.lawA
  have h2 : ∑ t, (1 - (m.j t : ℝ) / 2) ≤ ∑ t, (1 : ℝ) / (m.j t + 1) := Finset.sum_le_sum fun t _ => tangent _
  have h3 : ∑ t, (1 - (m.j t : ℝ) / 2) = P - (m.J : ℝ) / 2 := by
    simp [J, Finset.sum_sub_distrib, ← Finset.sum_div, Nat.cast_sum]
  linarith

/-- **the number used by the ceiling**: 104 rows and at most 56 descending moves force `96 ≤ J`. -/
theorem lawA_96 (m : LawAModel K 104 D) (hD : D ≤ 56) : 96 ≤ m.J := by
  have h := m.lawA_lin
  have hD' : (D : ℝ) ≤ 56 := by exact_mod_cast hD
  have : (96 : ℝ) ≤ m.J := by push_cast at h; linarith
  exact_mod_cast this

end LawAModel

/-! ### 4. the junk cells as a `Finset (ℕ × ℕ)` -/

/-- junk cells `(t, s)`, `s ≠ t`, `M t s ≠ 0`, as natural-number pairs -/
noncomputable def junkSet (M : Matrix (Fin P) (Fin P) K) : Finset (ℕ × ℕ) :=
  (univ.filter fun p : Fin P × Fin P => p.1 ≠ p.2 ∧ M p.1 p.2 ≠ 0).image fun p => ((p.1 : ℕ), (p.2 : ℕ))

theorem junkSet_card (M : Matrix (Fin P) (Fin P) K) : (junkSet M).card = ∑ t, jc M t := by
  unfold junkSet
  rw [Finset.card_image_of_injective _ (by
    intro p q h
    simp only [Prod.mk.injEq] at h
    exact Prod.ext (Fin.ext h.1) (Fin.ext h.2))]
  rw [Finset.card_filter, Fintype.sum_prod_type]
  refine Finset.sum_congr rfl fun t _ => ?_
  rw [jc, outN, Finset.card_filter]
  refine Finset.sum_congr rfl fun s _ => ?_
  by_cases h : s ≠ t ∧ M t s ≠ 0
  · rw [if_pos h, if_pos ⟨Ne.symm h.1, h.2⟩]
  · rw [if_neg h, if_neg (fun h' => h ⟨Ne.symm h'.1, h'.2⟩)]

theorem LawAModel.junkSet_card {D : ℕ} (m : LawAModel K P D) : (junkSet m.M).card = m.J := JunkLawA.junkSet_card m.M

/-- Law A in cardinality form for the ceiling: `D ≤ 56` descending moves over 104 rows force `96 ≤ |junkSet|`. -/
theorem junkSet_card_ge_96 {D : ℕ} (m : LawAModel K 104 D) (hD : D ≤ 56) : 96 ≤ (junkSet m.M).card := by
  rw [m.junkSet_card]; exact m.lawA_96 hD

/-! ### 5. Theorem S, core (clique form) -/

/-- Rows served by ONE arrival vector `a` (`M t = c t • a`) are pairwise junk partners (so pairwise even). -/
theorem single_arrival_clique (M : Matrix (Fin P) (Fin P) K) (hdiag : ∀ t, M t t ≠ 0) (a : Fin P → K) (c : Fin P → K)
    (G : Finset (Fin P)) (hrow : ∀ t ∈ G, M t = c t • a) :
    ∀ t ∈ G, ∀ s ∈ G, t ≠ s → M t s ≠ 0 := by
  intro t ht s hs hts
  have hct : c t ≠ 0 := by
    intro h; have := hdiag t; rw [hrow t ht] at this; simp [h] at this
  have has : a s ≠ 0 := by
    intro h; have := hdiag s; rw [hrow s hs] at this; simp [h] at this
  rw [hrow t ht]
  simpa using mul_ne_zero hct has

/-- hence `j_t ≥ |G| - 1` for each served row, and the group carries `≥ |G| (|G| - 1)` junk cells. -/
theorem single_arrival_junk (M : Matrix (Fin P) (Fin P) K) (hdiag : ∀ t, M t t ≠ 0) (a : Fin P → K) (c : Fin P → K)
    (G : Finset (Fin P)) (hrow : ∀ t ∈ G, M t = c t • a) :
    G.card * (G.card - 1) ≤ ∑ t ∈ G, jc M t := by
  have h : ∀ t ∈ G, G.card - 1 ≤ jc M t := by
    intro t ht
    rw [← Finset.card_erase_of_mem ht]
    refine Finset.card_le_card fun s hs => ?_
    simp only [mem_erase] at hs
    simp only [outN, mem_filter, mem_univ, true_and]
    exact ⟨hs.1, single_arrival_clique M hdiag a c G hrow t ht s hs.2 (Ne.symm hs.1)⟩
  calc G.card * (G.card - 1) = ∑ _t ∈ G, (G.card - 1) := by simp
    _ ≤ ∑ t ∈ G, jc M t := Finset.sum_le_sum h

end JunkLawA

#print axioms JunkLawA.maisBound
#print axioms JunkLawA.LawAModel.lawA
#print axioms JunkLawA.LawAModel.lawA_cs
#print axioms JunkLawA.LawAModel.lawA_lin
#print axioms JunkLawA.LawAModel.lawA_96
#print axioms JunkLawA.junkSet_card_ge_96
#print axioms JunkLawA.single_arrival_clique
#print axioms JunkLawA.single_arrival_junk
