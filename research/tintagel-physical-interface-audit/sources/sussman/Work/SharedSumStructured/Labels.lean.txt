import Work.SharedSumStructured.GPath

/-!
# (key: shared-sum-structured) Single-factor labels as projectors, and their two lifts

A single-factor label is the orthogonal projector `P` (a matrix over `F_2`, `A.mat s` for some
orthonormal basis `A` and index set `s`) with a nominal dimension.  `Climb U V` says: in ONE
orthonormal basis, `U` and `V` are index sets `s ⊆ t` (so `V` is reached from `U` with
`|t \ s|` directional moves).

A frame map `FMap H α` sends projectors to frame matrices on `α` and respects climbs.  The two
frame maps of the two-stage network on `α = H × H` are
* stage 1 (second triple fixed):  `Phi1 t P  = frame of  P ⊗ <t>`,
* stage 2 (first  triple fixed):  `Phi2 t P  = frame of  <t> ⊗ P` times `Kmat t = frame of t^⊥ ⊗ F`.
The lemmas at the end are the "exterior" climbs between the stages.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace SS
open Binary Matrix Finset RAM
noncomputable section

section Single
variable {H : Type} [Fintype H] [DecidableEq H]

/-- single-factor label: projector and nominal dimension. -/
structure Lbl (H : Type) where
  P : Matrix H H F
  d : ℕ

def tt (z : Space H) : Matrix H H F := fun i j => z i * z j

def zeroL : Lbl H := ⟨0, 0⟩
def fullL : Lbl H := ⟨1, Fintype.card H⟩
def lineL (z : Space H) : Lbl H := ⟨tt z, 1⟩
def perpL (z : Space H) : Lbl H := ⟨1 + tt z, Fintype.card H - 1⟩
def coordL (Z : Finset H) : Lbl H := ⟨(OBase.canonical H).mat Z, Z.card⟩

/-- one climb inside one orthonormal basis. -/
def Climb (U V : Lbl H) : Prop :=
  ∃ (A : OBase H) (s t : Finset H), s ⊆ t ∧ U.P = A.mat s ∧ V.P = A.mat t ∧
    V.d = U.d + (t \ s).card

inductive Climbs : Lbl H → Lbl H → Prop
  | refl (U : Lbl H) : Climbs U U
  | step {U V W : Lbl H} : Climb U V → Climbs V W → Climbs U W

lemma Climb.climbs {U V : Lbl H} (h : Climb U V) : Climbs U V := .step h (.refl V)

lemma Climbs.trans {U V W : Lbl H} (h : Climbs U V) (g : Climbs V W) : Climbs U W := by
  induction h with
  | refl => exact g
  | step a _ ih => exact .step a (ih g)

lemma mat_empty (A : OBase H) : A.mat ∅ = 0 := by
  ext i j; simp [OBase.mat]

lemma mat_single (A : OBase H) (k : H) : A.mat {k} = tt (A.v k) := by
  ext i j; simp [OBase.mat, tt]

lemma mat_compl_single (A : OBase H) (k : H) : A.mat (univ \ {k}) = 1 + tt (A.v k) := by
  rw [OBase.mat_sub A univ {k} (subset_univ _), OBase.mat_univ, mat_single]
  ext i j
  simp only [Matrix.sub_apply, Matrix.add_apply]
  exact CharTwo.sub_eq_add _ _

lemma card_pos_of_base (A : OBase H) (k : H) : 1 ≤ Fintype.card H :=
  Fintype.card_pos_iff.mpr ⟨k⟩

lemma climb_zero_line (A : OBase H) (k : H) : Climb zeroL (lineL (A.v k)) :=
  ⟨A, ∅, {k}, empty_subset _, (mat_empty A).symm, (mat_single A k).symm, by simp [zeroL, lineL]⟩

lemma climb_line_full (A : OBase H) (k : H) : Climb (lineL (A.v k)) fullL := by
  refine ⟨A, {k}, univ, subset_univ _, (mat_single A k).symm, (OBase.mat_univ A).symm, ?_⟩
  have h1 := card_pos_of_base A k
  simp only [fullL, lineL]
  rw [card_sdiff_of_subset (subset_univ _), card_univ, card_singleton]
  omega

lemma climb_zero_perp (A : OBase H) (k : H) : Climb zeroL (perpL (A.v k)) := by
  refine ⟨A, ∅, univ \ {k}, empty_subset _, (mat_empty A).symm, (mat_compl_single A k).symm, ?_⟩
  simp only [zeroL, perpL, sdiff_empty]
  rw [card_sdiff_of_subset (subset_univ _), card_univ, card_singleton]
  omega

lemma climb_perp_full (A : OBase H) (k : H) : Climb (perpL (A.v k)) fullL := by
  refine ⟨A, univ \ {k}, univ, subset_univ _, (mat_compl_single A k).symm,
    (OBase.mat_univ A).symm, ?_⟩
  have h1 := card_pos_of_base A k
  have e : (univ : Finset H) \ (univ \ {k}) = {k} := by ext x; simp
  simp only [fullL, perpL, e, card_singleton]
  omega

lemma climb_line_perp (A : OBase H) (k l : H) (hkl : k ≠ l) :
    Climb (lineL (A.v k)) (perpL (A.v l)) := by
  have hs : ({k} : Finset H) ⊆ univ \ {l} := by
    intro x hx; simp only [mem_singleton] at hx; subst hx; simp [hkl]
  refine ⟨A, {k}, univ \ {l}, hs, (mat_single A k).symm, (mat_compl_single A l).symm, ?_⟩
  have h2 : 2 ≤ Fintype.card H := by
    have : ({k, l} : Finset H).card ≤ Fintype.card H := card_le_univ _
    rwa [card_pair hkl] at this
  simp only [lineL, perpL]
  rw [card_sdiff_of_subset hs, card_sdiff_of_subset (subset_univ _), card_univ, card_singleton,
    card_singleton]
  omega

lemma climb_coord (Z Z' : Finset H) (h : Z ⊆ Z') : Climb (coordL Z) (coordL Z') :=
  ⟨OBase.canonical H, Z, Z', h, rfl, rfl, by
    simp only [coordL]; rw [card_sdiff_of_subset h]; have := card_le_card h; omega⟩

lemma climb_zero_coord (Z : Finset H) : Climb zeroL (coordL Z) :=
  ⟨OBase.canonical H, ∅, Z, empty_subset _, (mat_empty _).symm, rfl, by simp [zeroL, coordL]⟩

lemma climb_coord_full (Z : Finset H) : Climb (coordL Z) fullL :=
  ⟨OBase.canonical H, Z, univ, subset_univ _, rfl, (OBase.mat_univ _).symm, by
    simp only [coordL, fullL]
    rw [card_sdiff_of_subset (subset_univ _), card_univ]
    have := card_le_univ Z; omega⟩

/-- A transvection along `w` (norm 0) does not move the projector of an index set whose span
contains `w`. -/
lemma acted_mat (A : OBase H) (w : Space H) (hw : dot w w = 0) (s : Finset H)
    (hs : ∀ k, k ∉ s → dot w (A.v k) = 0) : (OBase.acted A w hw).mat s = A.mat s := by
  have e1 : ∀ i, ∑ k ∈ s, dot w (A.v k) * A.v k i = w i := by
    intro i
    have h1 : ∑ k ∈ s, dot w (A.v k) * A.v k i = ∑ k, dot w (A.v k) * A.v k i := by
      apply Finset.sum_subset (subset_univ s)
      intro k _ hk; rw [hs k hk, zero_mul]
    rw [h1]
    have h2 := congr_fun (A.proj_univ w) i
    simp only [OBase.proj, Finset.sum_apply, Pi.smul_apply, smul_eq_mul] at h2
    rw [← h2]
    apply sum_congr rfl
    intro k _; rw [dot_symm]
  have e2 : ∑ k ∈ s, dot w (A.v k) * dot w (A.v k) = 0 := by
    have h1 : ∑ k ∈ s, dot w (A.v k) * dot w (A.v k) = ∑ k, dot w (A.v k) * dot w (A.v k) := by
      apply Finset.sum_subset (subset_univ s)
      intro k _ hk; rw [hs k hk, zero_mul]
    rw [h1]
    have h3 : dot w w = ∑ k, dot w (A.v k) * dot w (A.v k) := by
      have h4 : dot w w = dot w (A.proj univ w) := by rw [A.proj_univ]
      rw [h4, OBase.proj, dot_sum]
      apply sum_congr rfl
      intro k _
      rw [dot_smul_right, dot_symm (A.v k) w]
    rw [← h3, hw]
  ext i j
  simp only [OBase.mat, OBase.acted, OBase.tv, Pi.add_apply, Pi.smul_apply, smul_eq_mul]
  have h5 : ∀ k, (A.v k i + dot w (A.v k) * w i) * (A.v k j + dot w (A.v k) * w j)
      = A.v k i * A.v k j + w j * (dot w (A.v k) * A.v k i) + w i * (dot w (A.v k) * A.v k j)
        + w i * w j * (dot w (A.v k) * dot w (A.v k)) := by
    intro k; ring
  simp_rw [h5, sum_add_distrib, ← mul_sum, e1, e2]
  rw [mul_zero, add_zero, mul_comm (w j), add_assoc, cancel, add_zero]

/-- some orthonormal basis contains the unit vector `z`, given one coordinate outside it. -/
lemma exists_base_one (z : Space H) (hz : dot z z = 1) (p : H) (hp : z p = 0) :
    ∃ (A : OBase H) (k : H), A.v k = z :=
  ⟨OBase.adapt (OBase.canonical H) p z hz (by simpa [OBase.canonical] using hp), p,
    OBase.adapt_pivot _ _ _ _ _⟩

/-- some orthonormal basis contains the orthonormal pair `z, w`. -/
lemma exists_base_two (z w : Space H) (hz : dot z z = 1) (hw : dot w w = 1) (hwz : dot w z = 0)
    (p q : H) (hpq : p ≠ q) (hp : z p = 0) (hq : z q = 0) (hq' : w q = 0) :
    ∃ (A : OBase H) (k l : H), k ≠ l ∧ A.v k = z ∧ A.v l = w := by
  have hcan : dot z ((OBase.canonical H).v p) = 0 := by simpa [OBase.canonical] using hp
  have hcanq : dot z ((OBase.canonical H).v q) = 0 := by simpa [OBase.canonical] using hq
  obtain ⟨B, hBp, hBq⟩ : ∃ B : OBase H, B.v p = z ∧ B.v q = eu q :=
    ⟨OBase.adapt (OBase.canonical H) p z hz hcan, OBase.adapt_pivot _ _ _ _ _,
      OBase.adapt_other (OBase.canonical H) p q z hpq hz hcan hcanq⟩
  have hsq : dot w (B.v q) = 0 := by rw [hBq]; simpa using hq'
  have hsp : dot w (B.v p) = 0 := by rw [hBp]; exact hwz
  exact ⟨OBase.adapt B q w hw hsq, p, q, hpq,
    (OBase.adapt_other B q p w hpq.symm hw hsq hsp).trans hBp, OBase.adapt_pivot _ _ _ _ _⟩

/-- line of `z` up to a coordinate space containing the support of `z` and one more point. -/
lemma climb_line_coord (z : Space H) (hz : dot z z = 1) (p : H) (hp : z p = 0) (Z : Finset H)
    (hpZ : p ∈ Z) (hZ : ∀ k, k ∉ Z → z k = 0) : Climb (lineL z) (coordL Z) := by
  have hcan : dot z ((OBase.canonical H).v p) = 0 := by simpa [OBase.canonical] using hp
  let A := OBase.adapt (OBase.canonical H) p z hz hcan
  have hAp : A.v p = z := OBase.adapt_pivot _ _ _ _ _
  have hmat : A.mat Z = (OBase.canonical H).mat Z := by
    apply acted_mat
    intro k hk
    have hkp : p ≠ k := fun h => hk (h ▸ hpZ)
    simp [OBase.canonical, hZ k hk, eu, hkp]
  have hs : ({p} : Finset H) ⊆ Z := by simpa using hpZ
  refine ⟨A, {p}, Z, hs, by rw [mat_single, hAp]; rfl, hmat.symm, ?_⟩
  simp only [lineL, coordL]
  rw [card_sdiff_of_subset hs, card_singleton]
  have := card_pos.mpr ⟨p, hpZ⟩
  omega

/-- a coordinate space up to `w^⊥`, when `w` vanishes on it and one more point `q` is free. -/
lemma climb_coord_perp (w : Space H) (hw : dot w w = 1) (q : H) (hq : w q = 0) (Z : Finset H)
    (hqZ : q ∉ Z) (hZ : ∀ k, k ∈ Z → w k = 0) : Climb (coordL Z) (perpL w) := by
  have hcan : dot w ((OBase.canonical H).v q) = 0 := by simpa [OBase.canonical] using hq
  let A := OBase.adapt (OBase.canonical H) q w hw hcan
  have hAq : A.v q = w := OBase.adapt_pivot _ _ _ _ _
  have hmat : A.mat Z = (OBase.canonical H).mat Z := by
    ext i j
    simp only [OBase.mat]
    apply sum_congr rfl
    intro k hk
    have hqk : q ≠ k := fun h => hqZ (h ▸ hk)
    have : A.v k = (OBase.canonical H).v k :=
      OBase.adapt_other _ q k w hqk hw hcan (by simpa [OBase.canonical] using hZ k hk)
    rw [this]
  have hs : Z ⊆ univ \ {q} := by
    intro x hx; simp only [mem_sdiff, mem_univ, mem_singleton, true_and]
    exact fun h => hqZ (h ▸ hx)
  refine ⟨A, Z, univ \ {q}, hs, hmat.symm, by rw [mat_compl_single, hAq]; rfl, ?_⟩
  simp only [coordL, perpL]
  rw [card_sdiff_of_subset hs, card_sdiff_of_subset (subset_univ _), card_univ, card_singleton]
  have h1 := card_le_card hs
  rw [card_sdiff_of_subset (subset_univ _), card_univ, card_singleton] at h1
  omega

end Single

/-- frame of a projector matrix. -/
def frameM {α : Type*} [Fintype α] [DecidableEq α] (M : Matrix α α F) : CMat α := wrap fun x => lum (M *ᵥ x)

lemma frame_eq {α : Type*} [Fintype α] [DecidableEq α] (A : OBase α) (s : Finset α) :
    frame A s = frameM (A.mat s) := by
  unfold frame frameM
  congr 1
  funext x
  congr 1
  funext i
  rw [OBase.proj_apply]
  rfl

/-- A frame map: projectors of `H` to frame matrices on `α`, compatible with climbs. -/
structure FMap (H α : Type) [Fintype H] [DecidableEq H] [Fintype α] [DecidableEq α] where
  Φ : Matrix H H F → CMat α
  off : ℕ
  climb : ∀ (A : OBase H) (s t : Finset H), s ⊆ t →
    Reach (Φ (A.mat s)) (Φ (A.mat t)) (t \ s).card

section FMapLemmas
variable {H α : Type} [Fintype H] [DecidableEq H] [Fintype α] [DecidableEq α]

def FMap.lab (Fm : FMap H α) (U : Lbl H) : Fr α := ⟨Fm.Φ U.P, U.d + Fm.off⟩

lemma FMap.reach (Fm : FMap H α) {U V : Lbl H} (h : Climbs U V) :
    ∃ n, Reach (Fm.lab U).M (Fm.lab V).M n ∧ (Fm.lab V).d = (Fm.lab U).d + n := by
  induction h with
  | refl U => exact ⟨0, Reach.refl _, rfl⟩
  | step a _ ih =>
    obtain ⟨A, s, t, hst, hU, hV, hd⟩ := a
    obtain ⟨n, hr, hn⟩ := ih
    refine ⟨(t \ s).card + n, ?_, ?_⟩
    · have := Fm.climb A s t hst
      simp only [FMap.lab] at hr ⊢
      rw [hU]
      rw [hV] at hr
      exact this.trans hr
    · simp only [FMap.lab] at hn ⊢
      omega

end FMapLemmas

section Two
variable {H : Type} [Fintype H] [DecidableEq H]

def tens (a b : Space H) : Space (H × H) := fun p => a p.1 * b p.2

lemma dot_tens (a b c d : Space H) : dot (tens a b) (tens c d) = dot a c * dot b d := by
  simp only [dot, tens, Fintype.sum_prod_type, Finset.sum_mul_sum]
  apply sum_congr rfl; intro i _
  apply sum_congr rfl; intro j _
  ring

/-- product of two orthonormal bases. -/
def pbase (A B : OBase H) : OBase (H × H) where
  v := fun p => tens (A.v p.1) (B.v p.2)
  rows := fun p q => by
    rw [dot_tens, A.rows, B.rows]
    rcases p with ⟨a,b⟩
    rcases q with ⟨c,d⟩
    by_cases h1 : a = c <;> by_cases h2 : b = d <;> simp [h1, h2]

def kron (M N : Matrix H H F) : Matrix (H × H) (H × H) F := fun p q => M p.1 q.1 * N p.2 q.2

lemma mat_prod (A B : OBase H) (s u : Finset H) :
    (pbase A B).mat (s ×ˢ u) = kron (A.mat s) (B.mat u) := by
  ext ⟨i,j⟩ ⟨i',j'⟩
  simp only [OBase.mat, pbase, tens, kron, Finset.sum_product, Finset.sum_mul_sum]
  apply sum_congr rfl; intro a _
  apply sum_congr rfl; intro b _
  ring

/-- stage 1: label `P` on the first factor, the line of `t` on the second. -/
def Phi1 (t : Space H) (P : Matrix H H F) : CMat (H × H) := frameM (kron P (tt t))
/-- frame of `t^⊥ ⊗ F`. -/
def Kmat (t : Space H) : CMat (H × H) := frameM (kron (1 + tt t) 1)
/-- stage 2: `t^⊥ ⊗ F` plus the line of `t` on the first factor with label `P` on the second. -/
def Phi2 (t : Space H) (P : Matrix H H F) : CMat (H × H) := frameM (kron (tt t) P) * Kmat t

lemma Phi1_eq (A B : OBase H) (k : H) (s : Finset H) :
    Phi1 (B.v k) (A.mat s) = frame (pbase A B) (s ×ˢ {k}) := by
  rw [frame_eq, mat_prod, mat_single]; rfl

lemma Kmat_eq (B C : OBase H) (k : H) :
    Kmat (B.v k) = frame (pbase B C) ((univ \ {k}) ×ˢ univ) := by
  rw [frame_eq, mat_prod, mat_compl_single, OBase.mat_univ]; rfl

lemma Phi2_eq (A B : OBase H) (k : H) (s : Finset H) :
    Phi2 (B.v k) (A.mat s) = frame (pbase B A) ({k} ×ˢ s) * Kmat (B.v k) := by
  rw [frame_eq, mat_prod, mat_single]; rfl

lemma Phi2_eq' (A B : OBase H) (k : H) (s : Finset H) :
    Phi2 (B.v k) (A.mat s) = frame (pbase B A) (({k} ×ˢ s) ∪ ((univ \ {k}) ×ˢ univ)) := by
  rw [Phi2_eq, Kmat_eq B A k, frame_union]
  rw [disjoint_left]
  rintro ⟨i,j⟩ h1 h2
  simp only [mem_product, mem_singleton, mem_sdiff, mem_univ, true_and, and_true] at h1 h2
  exact h2 h1.1

/-- stage 1 frame map (second factor fixed to the basis vector `B.v k`). -/
def fmap1 (B : OBase H) (k : H) : FMap H (H × H) where
  Φ := Phi1 (B.v k)
  off := 0
  climb := fun A s t hst => by
    rw [Phi1_eq, Phi1_eq]
    have hsub : s ×ˢ ({k} : Finset H) ⊆ t ×ˢ {k} := product_subset_product hst (Subset.refl _)
    refine (Reach.of_subset _ hsub).cast ?_
    rw [card_sdiff_of_subset hsub, card_product, card_product, card_singleton, mul_one, mul_one,
      card_sdiff_of_subset hst]

/-- stage 2 frame map (first factor fixed to the basis vector `B.v k`). -/
def fmap2 (B : OBase H) (k : H) : FMap H (H × H) where
  Φ := Phi2 (B.v k)
  off := (Fintype.card H - 1) * Fintype.card H
  climb := fun A s t hst => by
    rw [Phi2_eq, Phi2_eq]
    have hsub : ({k} : Finset H) ×ˢ s ⊆ {k} ×ˢ t := product_subset_product (Subset.refl _) hst
    refine ((Reach.of_subset _ hsub).mul_right _).cast ?_
    rw [card_sdiff_of_subset hsub, card_product, card_product, card_singleton, one_mul, one_mul,
      card_sdiff_of_subset hst]

lemma frameM_zero {α : Type*} [Fintype α] [DecidableEq α] : frameM (0 : Matrix α α F) = 1 := by
  unfold frameM
  have h : (fun x : Space α => lum ((0 : Matrix α α F) *ᵥ x)) = fun _ => 1 := by
    funext x; rw [Matrix.zero_mulVec]; exact lum_zero
  rw [h, wrap_one]

lemma kron_zero_left (N : Matrix H H F) : kron 0 N = 0 := by
  ext p q; simp [kron]
lemma kron_zero_right (N : Matrix H H F) : kron N 0 = 0 := by
  ext p q; simp [kron]

lemma Phi1_zero (t : Space H) : Phi1 t 0 = 1 := by
  rw [Phi1, kron_zero_left, frameM_zero]

lemma Phi2_zero (t : Space H) : Phi2 t 0 = Kmat t := by
  rw [Phi2, kron_zero_right, frameM_zero, Matrix.one_mul]

/-! ### the exterior climbs and the terminal identities, in the product basis -/

variable (A B : OBase H) (ka kb : H)

lemma Phi1_line : Phi1 (B.v kb) (tt (A.v ka)) = frame (pbase A B) {(ka,kb)} := by
  rw [← mat_single, Phi1_eq, singleton_product_singleton]

lemma Phi1_full : Phi1 (B.v kb) 1 = frame (pbase A B) (univ ×ˢ {kb}) := by
  rw [← OBase.mat_univ A, Phi1_eq]

lemma Phi1_perp : Phi1 (B.v kb) (1 + tt (A.v ka)) = frame (pbase A B) ((univ \ {ka}) ×ˢ {kb}) := by
  rw [← mat_compl_single, Phi1_eq]

lemma Phi2_zero' : Phi2 (A.v ka) 0 = frame (pbase A B) ((univ \ {ka}) ×ˢ univ) := by
  rw [Phi2_zero, Kmat_eq A B ka]

lemma Phi2_full : Phi2 (A.v ka) 1 = kernel (H × H) := by
  rw [← OBase.mat_univ (OBase.canonical H), Phi2_eq' (OBase.canonical H) A ka univ]
  have e : (({ka} : Finset H) ×ˢ (univ : Finset H)) ∪ ((univ \ {ka}) ×ˢ univ) = univ := by
    ext ⟨i,j⟩
    simp only [mem_union, mem_product, mem_singleton, mem_sdiff, mem_univ, true_and, and_true]
    tauto
  rw [e, frame_univ]

lemma Phi2_perp : Phi2 (A.v ka) (1 + tt (B.v kb)) = frame (pbase A B) (univ \ {(ka,kb)}) := by
  rw [← mat_compl_single, Phi2_eq' B A ka]
  congr 1
  ext ⟨i,j⟩
  simp only [mem_union, mem_product, mem_singleton, mem_sdiff, mem_univ, true_and, and_true,
    Prod.mk.injEq]
  tauto

/-- `X(a,b)` between the stages: `F ⊗ t_b` up to `t_a^⊥ ⊗ F + <t_a ⊗ t_b>`. -/
lemma reach_X : ∃ n, Reach (Phi1 (B.v kb) 1) (Phi2 (A.v ka) (tt (B.v kb))) n ∧
    n + Fintype.card H = (Fintype.card H - 1) * Fintype.card H + 1 := by
  rw [Phi1_full A B kb, ← mat_single, Phi2_eq' B A ka]
  have hsub : (univ : Finset H) ×ˢ ({kb} : Finset H)
      ⊆ (({ka} : Finset H) ×ˢ {kb}) ∪ ((univ \ {ka}) ×ˢ univ) := by
    rintro ⟨i,j⟩ h
    simp only [mem_union, mem_product, mem_singleton, mem_sdiff, mem_univ, true_and,
      and_true] at h ⊢
    by_cases hi : i = ka
    · exact Or.inl ⟨hi, h⟩
    · exact Or.inr hi
  refine ⟨_, Reach.of_subset _ hsub, ?_⟩
  have hdis : Disjoint (({ka} : Finset H) ×ˢ ({kb} : Finset H)) ((univ \ {ka}) ×ˢ univ) := by
    rw [disjoint_left]
    rintro ⟨i,j⟩ h1 h2
    simp only [mem_product, mem_singleton, mem_sdiff, mem_univ, true_and, and_true] at h1 h2
    exact h2 h1.1
  have h1 := Finset.card_sdiff_add_card_eq_card hsub
  rw [card_union_of_disjoint hdis, card_product, card_product, card_product, card_singleton,
    card_singleton, card_sdiff_of_subset (subset_univ _), card_univ, card_singleton] at h1
  omega

/-- `Y(a,b)` between the stages: `t_a^⊥ ⊗ t_b` up to `t_a^⊥ ⊗ F`. -/
lemma reach_Y : ∃ n, Reach (Phi1 (B.v kb) (1 + tt (A.v ka))) (Phi2 (A.v ka) 0) n ∧
    n + (Fintype.card H - 1) = (Fintype.card H - 1) * Fintype.card H := by
  rw [Phi1_perp A B ka kb, Phi2_zero' A B ka]
  have hsub : ((univ : Finset H) \ {ka}) ×ˢ ({kb} : Finset H) ⊆ (univ \ {ka}) ×ˢ univ :=
    product_subset_product (Subset.refl _) (subset_univ _)
  refine ⟨_, Reach.of_subset _ hsub, ?_⟩
  have h1 := Finset.card_sdiff_add_card_eq_card hsub
  rw [card_product, card_product, card_singleton,
    card_sdiff_of_subset (subset_univ _), card_univ, card_singleton] at h1
  omega

/-- a stage-1 helper slot after its invocation: `F ⊗ t_b` up to everything. -/
lemma reach_S1 : ∃ n, Reach (Phi1 (B.v kb) 1) (kernel (H × H)) n ∧
    n + Fintype.card H = Fintype.card H * Fintype.card H := by
  rw [Phi1_full (OBase.canonical H) B kb, ← frame_univ (pbase (OBase.canonical H) B)]
  have hsub : (univ : Finset H) ×ˢ ({kb} : Finset H) ⊆ univ := subset_univ _
  refine ⟨_, Reach.of_subset _ hsub, ?_⟩
  have h1 := Finset.card_sdiff_add_card_eq_card hsub
  rw [card_product, card_singleton, card_univ, card_univ, Fintype.card_prod] at h1
  omega

/-- a stage-2 helper slot before its invocation: nothing up to `t_a^⊥ ⊗ F`. -/
lemma reach_S2 : ∃ n, Reach (1 : CMat (H × H)) (Phi2 (A.v ka) 0) n ∧
    n = (Fintype.card H - 1) * Fintype.card H := by
  rw [Phi2_zero' A (OBase.canonical H) ka, ← frame_zero (pbase A (OBase.canonical H))]
  refine ⟨_, Reach.of_subset _ (empty_subset _), ?_⟩
  rw [sdiff_empty, card_product, card_sdiff_of_subset (subset_univ _), card_univ, card_singleton]

/-- an idle role: nothing up to everything. -/
lemma reach_idle : ∃ n, Reach (1 : CMat (H × H)) (kernel (H × H)) n ∧
    n = Fintype.card H * Fintype.card H := by
  rw [← frame_zero (OBase.canonical (H × H)), ← frame_univ (OBase.canonical (H × H))]
  refine ⟨_, Reach.of_subset _ (empty_subset _), ?_⟩
  rw [sdiff_empty, card_univ, Fintype.card_prod]

/-- the endpoint copy: one step separates `u^⊥` from everything. -/
lemma reach_end : Reach (Phi2 (A.v ka) (1 + tt (B.v kb))) (kernel (H × H)) 1 := by
  rw [Phi2_perp A B ka kb, ← frame_univ (pbase A B)]
  refine (Reach.of_subset _ (subset_univ _)).cast ?_
  have e : (univ : Finset (H × H)) \ (univ \ {(ka,kb)}) = {(ka,kb)} := by ext x; simp
  rw [e, card_singleton]

/-- terminal identity for `X(a,b)`: its source frame times the kernel is the final frame of
`Y(a,b)` up to a free shift. -/
lemma terminal_X : kernel (H × H) * Phi1 (B.v kb) (tt (A.v ka))
    = shift (tens (A.v ka) (B.v kb)) * Phi2 (A.v ka) (1 + tt (B.v kb)) := by
  rw [Phi1_line A B ka kb, Phi2_perp A B ka kb]
  exact terminal_calc (pbase A B) (ka,kb)

end Two
end
end SS
end PowerSaving
end OAI
