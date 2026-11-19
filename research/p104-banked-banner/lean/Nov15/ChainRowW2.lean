/-
ChainRowW2 .  THEOREM W case (d): ZIGZAG chains whose re-ascents stay inside every earlier
gather output.  Kernel only.
`ZigChain`: charts a_j ⊇ b_j (descent), ascent b_j ≤ a_{j+1} (route), fresh f_j on {q ∈ a_j}, gather g_k on {q ⊥ b_k},
β ≠ 0, and
  * `reasc`   : k < j, g_k ≠ 0, f_j ≠ 0 ⇒ a_j ≤ b_k   (re-ascent stays inside every earlier gather-bearing output)
  * `fresh_in`: all fresh charts ⊆ a_0                (F3)
  * `gath_ge` : gather-bearing k ⇒ a_0 ⊓ b_n ≤ b_k    (F3)
PROVED: `zig_row` (odd pair ⇒ block = φ·c, rank-1), `potential` (dim a_0 − dim(a_0 ⊓ b_n) ≤ Σ drops, the potential
lemma), `ZigLayout.mass_ge_56` (≤ 8 zigzag chains realising the live pattern ⇒ descent mass ≥ 56).
-/
import Nov15.ChainRowW1

open Matrix Module

namespace ChainRow
open DecoderWall

variable {κ ι : Type*} [Fintype κ] [Fintype ι]

/-- intersection-with-a-subspace drops by at most the drop. -/
theorem inf_drop (X a b : Submodule (ZMod 2) (κ → ZMod 2)) (hba : b ≤ a) :
    finrank (ZMod 2) ↥(X ⊓ a) + finrank (ZMod 2) ↥b ≤ finrank (ZMod 2) ↥(X ⊓ b) + finrank (ZMod 2) ↥a := by
  have h := Submodule.finrank_sup_add_finrank_inf_eq (X ⊓ a) b
  have e : (X ⊓ a) ⊓ b = X ⊓ b := by
    rw [inf_assoc, inf_eq_right.2 hba]
  have hle : (X ⊓ a) ⊔ b ≤ a := sup_le inf_le_right hba
  have := Submodule.finrank_mono hle
  rw [e] at h
  omega

/-- A zigzag chain of `n+1` descents (indices 0..n). -/
structure ZigChain (K : Type*) [Field K] (q : ι → κ → ZMod 2) (n : ℕ) where
  a : ℕ → Submodule (ZMod 2) (κ → ZMod 2)
  b : ℕ → Submodule (ZMod 2) (κ → ZMod 2)
  b_le : ∀ j, b j ≤ a j
  route : ∀ j, b j ≤ a (j + 1)
  fresh : ℕ → ι → K
  fresh_supp : ∀ j p, fresh j p ≠ 0 → q p ∈ a j
  gath : ℕ → ι → K
  gath_supp : ∀ k s, gath k s ≠ 0 → ∀ y ∈ b k, dot (q s) y = 0
  beta : ℕ → K
  beta_ne : ∀ k, beta k ≠ 0
  reasc : ∀ k j, k < j → (∃ s, gath k s ≠ 0) → (∃ p, fresh j p ≠ 0) → a j ≤ b k
  fresh_in : ∀ j p, fresh j p ≠ 0 → q p ∈ a 0
  gath_ge : ∀ k, (∃ s, gath k s ≠ 0) → a 0 ⊓ b n ≤ b k

namespace ZigChain
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {n : ℕ} (C : ZigChain K q n)

def carried : ℕ → ι → K
  | 0 => C.fresh 0
  | k + 1 => fun p => C.beta (k + 1) * carried k p + C.fresh (k + 1) p

def block (p s : ι) : K := ∑ k ∈ Finset.range (n + 1), C.carried k p * C.gath k s

noncomputable def descentMass : ℕ :=
  ∑ j ∈ Finset.range (n + 1), (finrank (ZMod 2) (C.a j) - finrank (ZMod 2) (C.b j))

def P (k : ℕ) : K := ∏ i ∈ Finset.range (k + 1), C.beta i
theorem P_ne (k : ℕ) : C.P k ≠ 0 := Finset.prod_ne_zero_iff.2 fun i _ => C.beta_ne i

def phi (p : ι) : K := ∑ j ∈ Finset.range (n + 1), (C.P j)⁻¹ * C.fresh j p
def cv (s : ι) : K := ∑ k ∈ Finset.range (n + 1), C.P k * C.gath k s

theorem carried_eq (k : ℕ) (p : ι) :
    C.carried k p = ∑ j ∈ Finset.range (k + 1), C.P k * (C.P j)⁻¹ * C.fresh j p := by
  induction k with
  | zero => simp [carried, C.P_ne 0]
  | succ k ih =>
    simp only [carried]
    rw [ih, Finset.sum_range_succ _ (k + 1), Finset.mul_sum]
    have hP : C.P (k + 1) = C.P k * C.beta (k + 1) := by
      simp only [P]; rw [Finset.prod_range_succ _ (k + 1)]
    rw [mul_inv_cancel₀ (C.P_ne (k + 1)), one_mul]
    congr 1
    refine Finset.sum_congr rfl fun j _ => ?_
    rw [hP]; ring

/-- later fresh against earlier gather vanishes on odd pairs (re-ascent inside the earlier gather output). -/
theorem cross_zero {p s : ι} (hps : dot (q p) (q s) = 1) {j k : ℕ} (hjk : k < j) :
    C.fresh j p * C.gath k s = 0 := by
  by_contra h
  have hf : C.fresh j p ≠ 0 := left_ne_zero_of_mul h
  have hg : C.gath k s ≠ 0 := right_ne_zero_of_mul h
  have hm : q p ∈ C.b k := C.reasc k j hjk ⟨s, hg⟩ ⟨p, hf⟩ (C.fresh_supp j p hf)
  have h0 := C.gath_supp k s hg (q p) hm
  have : dot (q s) (q p) = dot (q p) (q s) := dotProduct_comm _ _
  rw [this, hps] at h0
  exact one_ne_zero h0

/-- **ZIGZAG ROW LEMMA.** On every odd pair the zigzag chain's block is the rank-1 product φ p · c s. -/
theorem zig_row {p s : ι} (hps : dot (q p) (q s) = 1) : C.block p s = C.phi p * C.cv s := by
  unfold block phi cv
  rw [Finset.sum_mul_sum]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun k hk => ?_
  rw [carried_eq, Finset.sum_mul]
  have hsub : Finset.range (k + 1) ⊆ Finset.range (n + 1) := by
    intro j hj; simp only [Finset.mem_range] at *; omega
  rw [Finset.sum_subset hsub]
  · refine Finset.sum_congr rfl fun j _ => by ring
  · intro j _ hj
    simp only [Finset.mem_range, not_lt] at hj
    have := C.cross_zero hps (show k < j by omega)
    calc C.P k * (C.P j)⁻¹ * C.fresh j p * C.gath k s
        = C.P k * (C.P j)⁻¹ * (C.fresh j p * C.gath k s) := by ring
      _ = 0 := by rw [this, mul_zero]

theorem phi_supp (p : ι) (h : C.phi p ≠ 0) : q p ∈ C.a 0 := by
  obtain ⟨j, -, hj⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  exact C.fresh_in j p (right_ne_zero_of_mul hj)

theorem cv_supp (s : ι) (h : C.cv s ≠ 0) : ∀ y ∈ C.a 0 ⊓ C.b n, dot (q s) y = 0 := by
  obtain ⟨k, -, hk'⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  have hg : C.gath k s ≠ 0 := right_ne_zero_of_mul hk'
  intro y hy
  exact C.gath_supp k s hg y (C.gath_ge k ⟨s, hg⟩ hy)

/-- **POTENTIAL LEMMA** along the route: dim a_0 − dim(a_0 ⊓ b_j) ≤ Σ_{i≤j} drop_i. -/
theorem potential_aux (j : ℕ) :
    finrank (ZMod 2) ↥(C.a 0) - finrank (ZMod 2) ↥(C.a 0 ⊓ C.b j) ≤
      ∑ i ∈ Finset.range (j + 1), (finrank (ZMod 2) (C.a i) - finrank (ZMod 2) (C.b i)) := by
  induction j with
  | zero =>
    rw [Finset.sum_range_one, inf_eq_right.2 (C.b_le 0)]
  | succ j ih =>
    rw [Finset.sum_range_succ]
    have h1 := inf_drop (C.a 0) (C.a (j + 1)) (C.b (j + 1)) (C.b_le (j + 1))
    have h2 : finrank (ZMod 2) ↥(C.a 0 ⊓ C.b j) ≤ finrank (ZMod 2) ↥(C.a 0 ⊓ C.a (j + 1)) :=
      Submodule.finrank_mono (inf_le_inf_left _ (C.route j))
    have h3 := Submodule.finrank_mono (C.b_le (j + 1))
    have h4 : finrank (ZMod 2) ↥(C.a 0 ⊓ C.b (j + 1)) ≤ finrank (ZMod 2) ↥(C.a 0) :=
      Submodule.finrank_mono inf_le_left
    have h5 : finrank (ZMod 2) ↥(C.a 0 ⊓ C.b j) ≤ finrank (ZMod 2) ↥(C.a 0) :=
      Submodule.finrank_mono inf_le_left
    omega

theorem potential :
    finrank (ZMod 2) ↥(C.a 0) - finrank (ZMod 2) ↥(C.a 0 ⊓ C.b n) ≤ C.descentMass :=
  C.potential_aux n

/-- the single-row relay chain carrying (φ, c) between `a_0` and `a_0 ⊓ b_n`. -/
noncomputable def toRow : RelayChain K q 1 where
  ch := fun j => if j = 0 then C.a 0 else C.a 0 ⊓ C.b n
  desc := fun j => by
    by_cases h : j = 0
    · subst h; simp
    · simp [h]
  fresh := fun j => if j = 0 then C.phi else 0
  fresh_supp := fun j p hp => by
    by_cases h : j = 0
    · subst h; simpa using C.phi_supp p (by simpa using hp)
    · simp [h] at hp
  gath := fun k => if k = 0 then C.cv else 0
  gath_supp := fun k s hs y hy => by
    by_cases h : k = 0
    · subst h
      exact C.cv_supp s (by simpa using hs) y (by simpa using hy)
    · simp [h] at hs
  beta := fun _ => 1
  beta_ne := fun _ => one_ne_zero

theorem toRow_block (p s : ι) : C.toRow.block p s = C.phi p * C.cv s := by
  simp [RelayChain.block, RelayChain.carried, toRow]

theorem toRow_mass : C.toRow.descentMass ≤ C.descentMass := by
  refine le_trans (le_of_eq ?_) C.potential
  simp [RelayChain.descentMass, toRow]
  try rfl

end ZigChain

/-- A layout of zigzag chains indexed by `T`. -/
structure ZigLayout (K : Type*) [Field K] (q : ι → κ → ZMod 2) (T : Type*) where
  len : T → ℕ
  chain : ∀ c, ZigChain K q (len c)

namespace ZigLayout
variable {K : Type*} [Field K] {q : ι → κ → ZMod 2} {T : Type*} [Fintype T] (Z : ZigLayout K q T)

def block (p s : ι) : K := ∑ c, (Z.chain c).block p s
noncomputable def descentMass : ℕ := ∑ c, (Z.chain c).descentMass

structure Realises : Prop where
  diag : ∀ t, Z.block t t = 1
  odd : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → Z.block t s = 0

/-- the induced one-row-per-chain pure layout. -/
noncomputable def toLayout : ChainLayout K q T where
  len := fun _ => 1
  chain := fun c => (Z.chain c).toRow

theorem toLayout_block {p s : ι} (h : dot (q p) (q s) = 1) : Z.toLayout.block p s = Z.block p s := by
  unfold ChainLayout.block block
  refine Finset.sum_congr rfl fun c _ => ?_
  exact ((Z.chain c).toRow_block p s).trans ((Z.chain c).zig_row h).symm

theorem toLayout_mass : Z.toLayout.descentMass ≤ Z.descentMass :=
  Finset.sum_le_sum fun c _ => (Z.chain c).toRow_mass

end ZigLayout

variable {T : Type} [Fintype T]

/-- **THEOREM W (d): zigzags with re-ascent inside earlier gather outputs.**  At most 8 such chains realising the
live pattern have descent mass ≥ 56. -/
theorem zig_mass_ge_56 (Z : ZigLayout ℚ DF.lq T) (hR : Z.Realises) (h8 : Fintype.card T ≤ 8) :
    56 ≤ Z.descentMass := by
  have hR' : Z.toLayout.Realises :=
    { diag := fun t => by rw [Z.toLayout_block (lq_odd t)]; exact hR.diag t
      odd := fun t s h1 h2 => by rw [Z.toLayout_block h2]; exact hR.odd t s h1 h2 }
  exact (chain_mass_ge_56 Z.toLayout hR' h8).trans Z.toLayout_mass

/-- any number of zigzag chains with stacked induced ranks ≤ 8. -/
theorem zig_mass_ge_56_rank8 (Z : ZigLayout ℚ DF.lq T) (hR : Z.Realises)
    (hW : (DW7.Wm Z.toLayout.W).rank ≤ 8) (hU : (DW7.Wm Z.toLayout.U).rank ≤ 8) :
    56 ≤ Z.descentMass := by
  have hR' : Z.toLayout.Realises :=
    { diag := fun t => by rw [Z.toLayout_block (lq_odd t)]; exact hR.diag t
      odd := fun t s h1 h2 => by rw [Z.toLayout_block h2]; exact hR.odd t s h1 h2 }
  exact (chain_mass_ge_56_rank8 Z.toLayout hR' hW hU).trans Z.toLayout_mass

end ChainRow

#print axioms ChainRow.ZigChain.zig_row
#print axioms ChainRow.ZigChain.potential
#print axioms ChainRow.zig_mass_ge_56
#print axioms ChainRow.zig_mass_ge_56_rank8
