import FrameData
import FramedReplay
import Mathlib.Data.Matrix.Mul
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
Concrete gauges from every literal source frame. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

The field has arbitrary characteristic other than two. Integer certificates
are cast directly, then divided by four; no homomorphism from Q is assumed.
The formula and involution argument are the matrix specialization of main's
`AddressGauges.partialSwap` / `matrixPartialSwapGauge`. We use the identical
four-field `FramedReplay.Gauge` interface required by the actual COPY/ERASE
interpreter. This does not import or claim to recheck unrelated FramedXor
fanout proofs from a different Lean build.
-/
namespace FrameGeometry
open scoped Matrix BigOperators

/-- The Std data are plain functions; these wrappers select matrix rather
than pointwise multiplication when interpreting their certificates. -/
abbrev scaledMatrix (f : Fin 944) : Matrix (Fin 8) (Fin 8) Int := Matrix.of (scaled f)
abbrev stackMatrix (f : Fin 944) : Matrix (Fin 8) (Fin 8) Int := Matrix.of (stack f)
abbrev inverseMatrix (f : Fin 944) : Matrix (Fin 8) (Fin 8) Int := Matrix.of (inverse256 f)

theorem scaled_full_entries : ∀ i j : Fin 8, scaled 1 i j = if i = j then 4 else 0 := by decide
theorem scaled_zero_entries : ∀ i j : Fin 8, scaled 0 i j = 0 := by decide

theorem scaled_idempotent (f : Fin 944) :
    scaledMatrix f * scaledMatrix f = (4 : Int) • scaledMatrix f := by
  ext i j
  simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, dot8, scaledMatrix, stackMatrix, inverseMatrix] using
    scaled_idempotent_entries f i j

theorem scaled_symmetric (f : Fin 944) : (scaledMatrix f).transpose = scaledMatrix f := by
  ext i j
  exact (scaled_symmetric_entries f i j).symm

theorem stack_inverse (f : Fin 944) :
    stackMatrix f * inverseMatrix f = (256 : Int) • (1 : Matrix (Fin 8) (Fin 8) Int) := by
  ext i j
  have h := stack_inverse_entries f i j
  by_cases hij : i = j <;>
    simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, Matrix.one_apply, dot8, hij, scaledMatrix, stackMatrix, inverseMatrix] using h

theorem inverse_stack (f : Fin 944) :
    inverseMatrix f * stackMatrix f = (256 : Int) • (1 : Matrix (Fin 8) (Fin 8) Int) := by
  ext i j
  have h := inverse_stack_entries f i j
  by_cases hij : i = j <;>
    simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, Matrix.one_apply, dot8, hij, scaledMatrix, stackMatrix, inverseMatrix] using h

def castMatrix (K : Type*) [Field K] (a : Matrix (Fin 8) (Fin 8) Int) : Matrix (Fin 8) (Fin 8) K :=
  a.map (Int.castRingHom K)

theorem cast_mul_factor (K : Type*) [Field K] (a b c : Matrix (Fin 8) (Fin 8) Int) (k : Int)
    (h : a * b = k • c) :
    castMatrix K a * castMatrix K b = (k : K) • castMatrix K c := by
  have hc := congrArg (fun m : Matrix (Fin 8) (Fin 8) Int => m.map (Int.castRingHom K)) h
  dsimp only at hc
  rw [Matrix.map_mul] at hc
  change castMatrix K a * castMatrix K b = _ at hc
  rw [hc]
  ext i j
  simp [castMatrix, Matrix.map, Matrix.smul_apply]

def projector (K : Type*) [Field K] (f : Fin 944) : Matrix (Fin 8) (Fin 8) K :=
  (4 : K)⁻¹ • castMatrix K (scaledMatrix f)

theorem four_ne_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) : (4 : K) ≠ 0 := by
  have h : (4 : K) = 2 * 2 := by norm_num
  rw [h]
  exact mul_ne_zero h2 h2

theorem two_fifty_six_ne_zero (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) :
    (256 : K) ≠ 0 := by
  have h : (256 : K) = 2 ^ 8 := by norm_num
  rw [h]
  exact pow_ne_zero _ h2

theorem projector_idempotent (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    projector K f * projector K f = projector K f := by
  unfold projector
  rw [Matrix.smul_mul, Matrix.mul_smul, cast_mul_factor K _ _ _ 4 (scaled_idempotent f)]
  have h4 := four_ne_zero K h2
  have hs : ((4 : K)⁻¹ * (4 : K)⁻¹) * 4 = (4 : K)⁻¹ := by
    field_simp [h4]
  simp only [smul_smul, Int.cast_ofNat, ← mul_assoc, hs]

theorem projector_symmetric (K : Type*) [Field K] (f : Fin 944) :
    (projector K f).transpose = projector K f := by
  ext i j
  simp only [projector, Matrix.transpose_apply, Matrix.smul_apply, castMatrix, Matrix.map_apply, scaledMatrix, Matrix.of_apply]
  rw [scaled_symmetric_entries f j i]

theorem projector_full (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) :
    projector K 1 = 1 := by
  ext i j
  by_cases hij : i = j <;>
    simp [projector, castMatrix, Matrix.smul_apply, Matrix.one_apply,
      scaled_full_entries, hij, four_ne_zero K h2]

theorem projector_zero (K : Type*) [Field K] : projector K 0 = 0 := by
  ext i j
  simp [projector, castMatrix, Matrix.smul_apply, scaled_zero_entries]

def basisSelector (K : Type*) [Zero K] [One K] (f : Fin 944) :
    Matrix (Fin 8) (Fin 8) K :=
  Matrix.diagonal fun j => if j.val < (frame f).dimension then 1 else 0

theorem scaled_stack (f : Fin 944) :
    scaledMatrix f * (stackMatrix f).transpose = (4 : Int) • ((stackMatrix f).transpose * basisSelector Int f) := by
  ext i j
  simp only [Matrix.smul_apply, smul_eq_mul, Matrix.mul_diagonal, basisSelector]
  have h := scaled_stack_entries f i j
  by_cases hj : j.val < (frame f).dimension <;>
    simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.transpose_apply, dot8, hj, scaledMatrix, stackMatrix, inverseMatrix] using h

theorem cast_transpose (K : Type*) [Field K] (a : Matrix (Fin 8) (Fin 8) Int) :
    castMatrix K a.transpose = (castMatrix K a).transpose := by rfl

theorem cast_product (K : Type*) [Field K] (a b : Matrix (Fin 8) (Fin 8) Int) :
    castMatrix K (a * b) = castMatrix K a * castMatrix K b := by
  exact Matrix.map_mul

theorem cast_selector (K : Type*) [Field K] (f : Fin 944) :
    castMatrix K (basisSelector Int f) = basisSelector K f := by
  ext i j
  by_cases hij : i = j <;> by_cases hj : j.val < (frame f).dimension <;>
    simp [castMatrix, Matrix.map, basisSelector, Matrix.diagonal_apply, hij, hj]

/-- The projector fixes every literal B row and annihilates every literal
A row. Together with the checked inverse of [B;A], this identifies the
projector on a complete basis over every permitted field. -/
theorem projector_stack (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    projector K f * (castMatrix K (stackMatrix f)).transpose =
      (castMatrix K (stackMatrix f)).transpose * basisSelector K f := by
  have h := cast_mul_factor K _ _ _ 4 (scaled_stack f)
  rw [cast_transpose, cast_product, cast_transpose, cast_selector] at h
  unfold projector
  rw [Matrix.smul_mul, h, smul_smul]
  simp [four_ne_zero K h2]

-- Keep the literal lookup tables abstract while converting their checked
-- entrywise identities into matrix multiplication identities.
attribute [local irreducible] lookup transitionLookup in
theorem transition_scaled_left (n : Fin 3357) :
    scaledMatrix (transition n).1 * scaledMatrix (transition n).2 = (4 : Int) • scaledMatrix (transition n).1 := by
  ext i j
  simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, dot8, scaledMatrix, stackMatrix, inverseMatrix] using
    (transition_absorbs n).1 i j

attribute [local irreducible] lookup transitionLookup in
theorem transition_scaled_right (n : Fin 3357) :
    scaledMatrix (transition n).2 * scaledMatrix (transition n).1 = (4 : Int) • scaledMatrix (transition n).1 := by
  ext i j
  simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, dot8, scaledMatrix, stackMatrix, inverseMatrix] using
    (transition_absorbs n).2 i j

theorem normalized_absorption (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (a b c : Fin 944) (h : scaledMatrix a * scaledMatrix b = (4 : Int) • scaledMatrix c) :
    projector K a * projector K b = projector K c := by
  unfold projector
  rw [Matrix.smul_mul, Matrix.mul_smul, cast_mul_factor K _ _ _ 4 h]
  have h4 := four_ne_zero K h2
  have hs : ((4 : K)⁻¹ * (4 : K)⁻¹) * 4 = (4 : K)⁻¹ := by field_simp [h4]
  simp only [smul_smul, Int.cast_ofNat, ← mul_assoc, hs]

theorem transition_projectors (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (n : Fin 3357) :
    projector K (transition n).1 * projector K (transition n).2 = projector K (transition n).1 ∧
    projector K (transition n).2 * projector K (transition n).1 = projector K (transition n).1 :=
  ⟨normalized_absorption K h2 _ _ _ (transition_scaled_left n),
    normalized_absorption K h2 _ _ _ (transition_scaled_right n)⟩

/-- The source's row stack remains invertible after reduction to every odd
field. Hence its B and A rows are a complete basis, not merely eigenvectors. -/
theorem stack_right_inverse (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    castMatrix K (stackMatrix f) * ((256 : K)⁻¹ • castMatrix K (inverseMatrix f)) = 1 := by
  rw [Matrix.mul_smul, cast_mul_factor K _ _ _ 256 (stack_inverse f), smul_smul]
  simp [two_fifty_six_ne_zero K h2, castMatrix]

theorem stack_left_inverse (K : Type*) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    ((256 : K)⁻¹ • castMatrix K (inverseMatrix f)) * castMatrix K (stackMatrix f) = 1 := by
  rw [Matrix.smul_mul, cast_mul_factor K _ _ _ 256 (inverse_stack f), smul_smul]
  simp [two_fifty_six_ne_zero K h2, castMatrix]

def partialSwap {K : Type*} [Field K] (p : Matrix (Fin 8) (Fin 8) K)
    (v : (Fin 8 → K) × (Fin 8 → K)) : (Fin 8 → K) × (Fin 8 → K) :=
  (v.1 + p *ᵥ (v.2 - v.1), v.2 - p *ᵥ (v.2 - v.1))

theorem partialSwap_involution {K : Type*} [Field K] (p : Matrix (Fin 8) (Fin 8) K)
    (idem : p * p = p) (v : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap p (partialSwap p v) = v := by
  apply Prod.ext <;>
    simp only [partialSwap, Matrix.mulVec_sub, Matrix.mulVec_add, Matrix.mulVec_mulVec, idem] <;>
    ext i <;> simp only [Pi.add_apply, Pi.sub_apply] <;> ring

theorem partialSwap_nested {K : Type*} [Field K]
    (small large : Matrix (Fin 8) (Fin 8) K) (absorb : large * small = small)
    (p : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap large (partialSwap small p) = partialSwap (large - small) p := by
  apply Prod.ext <;>
    simp only [partialSwap, Matrix.mulVec_sub, Matrix.mulVec_add, Matrix.sub_mulVec,
      Matrix.mulVec_mulVec, absorb] <;>
    ext i <;> simp only [Pi.add_apply, Pi.sub_apply] <;> ring

theorem partialSwap_nested_reverse {K : Type*} [Field K]
    (small large : Matrix (Fin 8) (Fin 8) K) (absorb : small * large = small)
    (p : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap small (partialSwap large p) = partialSwap (large - small) p := by
  apply Prod.ext <;>
    simp only [partialSwap, Matrix.mulVec_sub, Matrix.mulVec_add, Matrix.sub_mulVec,
      Matrix.mulVec_mulVec, absorb] <;>
    ext i <;> simp only [Pi.add_apply, Pi.sub_apply] <;> ring

theorem full_after_frame (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (p : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap (projector K 1) (partialSwap (projector K f) p) =
      partialSwap (projector K 1 - projector K f) p := by
  apply partialSwap_nested
  rw [projector_full K h2, one_mul]

theorem frame_after_full (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (p : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap (projector K f) (partialSwap (projector K 1) p) =
      partialSwap (projector K 1 - projector K f) p := by
  apply partialSwap_nested_reverse
  rw [projector_full K h2, mul_one]

def gauge (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    FramedReplay.Gauge ((Fin 8 → K) × (Fin 8 → K)) where
  forward := partialSwap (projector K f)
  inverse := partialSwap (projector K f)
  inverse_forward := partialSwap_involution _ (projector_idempotent K h2 f)
  forward_inverse := partialSwap_involution _ (projector_idempotent K h2 f)

def firstEight {K : Type*} (v : Fin 64 → K) : Fin 8 → K :=
  fun i => v ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩

def replaceFirst {K : Type*} (v : Fin 64 → K) (w : Fin 8 → K) : Fin 64 → K :=
  fun i => if hi : i.val < 8 then w ⟨i.val, hi⟩ else v i

theorem firstEight_replaceFirst {K : Type*} (v : Fin 64 → K) (w : Fin 8 → K) :
    firstEight (replaceFirst v w) = w := by
  funext i
  simp [firstEight, replaceFirst, i.isLt]

theorem replaceFirst_twice {K : Type*} (v : Fin 64 → K) (w z : Fin 8 → K) :
    replaceFirst (replaceFirst v w) z = replaceFirst v z := by
  funext i
  by_cases hi : i.val < 8 <;> simp [replaceFirst, hi]

theorem replaceFirst_firstEight {K : Type*} (v : Fin 64 → K) :
    replaceFirst v (firstEight v) = v := by
  funext i
  by_cases hi : i.val < 8 <;> simp [replaceFirst, firstEight, hi]

def liftPair {K : Type*}
    (f : ((Fin 8 → K) × (Fin 8 → K)) → ((Fin 8 → K) × (Fin 8 → K)))
    (p : (Fin 64 → K) × (Fin 64 → K)) : (Fin 64 → K) × (Fin 64 → K) :=
  let q := f (firstEight p.1, firstEight p.2)
  (replaceFirst p.1 q.1, replaceFirst p.2 q.2)

theorem liftPair_comp {K : Type*}
    (f g : ((Fin 8 → K) × (Fin 8 → K)) → ((Fin 8 → K) × (Fin 8 → K)))
    (p : (Fin 64 → K) × (Fin 64 → K)) :
    liftPair f (liftPair g p) = liftPair (f ∘ g) p := by
  simp [liftPair, firstEight_replaceFirst, replaceFirst_twice]

theorem liftPair_id {K : Type*} (p : (Fin 64 → K) × (Fin 64 → K)) :
    liftPair id p = p := by
  simp [liftPair, replaceFirst_firstEight]

def liftGauge {K : Type} (g : FramedReplay.Gauge ((Fin 8 → K) × (Fin 8 → K))) :
    FramedReplay.Gauge ((Fin 64 → K) × (Fin 64 → K)) where
  forward := liftPair g.forward
  inverse := liftPair g.inverse
  inverse_forward p := by
    rw [liftPair_comp]
    have h : g.inverse ∘ g.forward = id := by funext x; exact g.inverse_forward x
    rw [h, liftPair_id]
  forward_inverse p := by
    rw [liftPair_comp]
    have h : g.forward ∘ g.inverse = id := by funext x; exact g.forward_inverse x
    rw [h, liftPair_id]

def gauge64 (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    FramedReplay.Gauge ((Fin 64 → K) × (Fin 64 → K)) :=
  liftGauge (gauge K h2 f)

def coordinateProjector (K : Type*) [Field K] (mask : Fin 8 → Bool) :
    Matrix (Fin 8) (Fin 8) K := Matrix.diagonal fun i => if mask i then 1 else 0

theorem partialSwap_coordinate {K : Type*} [Field K] (mask : Fin 8 → Bool)
    (p : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap (coordinateProjector K mask) p =
      (fun i => if mask i then p.2 i else p.1 i,
       fun i => if mask i then p.1 i else p.2 i) := by
  apply Prod.ext <;> funext i <;>
    simp only [partialSwap, coordinateProjector, Matrix.mulVec_diagonal, Pi.add_apply, Pi.sub_apply]
  all_goals cases mask i <;> simp

/-- A finite integer-table equality is sufficient to identify the source
entrance-to-exit residual with the literal coordinate mask in every odd
field. The hypothesis is intended to be discharged for the selected source
tag table, not assumed from ranks or sampled modular computations. -/
theorem coordinate_residual (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (mask : Fin 8 → Bool)
    (hc : ∀ i j : Fin 8, scaledMatrix 1 i j - scaledMatrix f i j =
      if i = j ∧ mask i = true then 4 else 0) :
    projector K 1 - projector K f = coordinateProjector K mask := by
  ext i j
  have h := congrArg (fun z : Int => (z : K)) (hc i j)
  have h4 := four_ne_zero K h2
  simp only [Int.cast_sub, scaledMatrix, Matrix.of_apply] at h
  simp only [Matrix.sub_apply, projector, Matrix.smul_apply, castMatrix, Matrix.map_apply,
    coordinateProjector, Matrix.diagonal_apply, scaledMatrix, Matrix.of_apply, smul_eq_mul]
  change (4 : K)⁻¹ * (scaled 1 i j : K) - (4 : K)⁻¹ * (scaled f i j : K) = _
  rw [← mul_sub, h]
  by_cases hij : i = j <;> cases mask i <;> simp [hij, h4]

theorem residual_partialSwap (K : Type*) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (mask : Fin 8 → Bool)
    (hc : ∀ i j : Fin 8, scaledMatrix 1 i j - scaledMatrix f i j =
      if i = j ∧ mask i = true then 4 else 0)
    (p : (Fin 8 → K) × (Fin 8 → K)) :
    partialSwap (projector K 1 - projector K f) p =
      (fun i => if mask i then p.2 i else p.1 i,
       fun i => if mask i then p.1 i else p.2 i) := by
  rw [coordinate_residual K h2 f mask hc]
  exact partialSwap_coordinate mask p

def coordinateSwap64 {K : Type*} (mask : Fin 64 → Bool)
    (p : (Fin 64 → K) × (Fin 64 → K)) : (Fin 64 → K) × (Fin 64 → K) :=
  (fun i => if mask i then p.2 i else p.1 i,
   fun i => if mask i then p.1 i else p.2 i)

/-- Complete source entrance/exit frame transport, on all 64 address
coordinates. The finite certificate refers to the literal projector table;
the outside-support condition prevents an unnoticed change of chart. -/
theorem full_after_frame64_coordinate (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (mask : Fin 64 → Bool)
    (hc : ∀ i j : Fin 8, scaledMatrix 1 i j - scaledMatrix f i j =
      if i = j ∧ mask ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩ = true then 4 else 0)
    (outside : ∀ i : Fin 64, 8 ≤ i.val → mask i = false)
    (p : (Fin 64 → K) × (Fin 64 → K)) :
    (gauge64 K h2 1).forward ((gauge64 K h2 f).forward p) = coordinateSwap64 mask p := by
  change liftPair (partialSwap (projector K 1))
    (liftPair (partialSwap (projector K f)) p) = _
  rw [liftPair_comp]
  have hlocal := full_after_frame K h2 f (firstEight p.1, firstEight p.2)
  rw [residual_partialSwap K h2 f
    (fun i => mask ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩) hc] at hlocal
  change (replaceFirst p.1 ((partialSwap (projector K 1)
      (partialSwap (projector K f) (firstEight p.1, firstEight p.2))).1),
    replaceFirst p.2 ((partialSwap (projector K 1)
      (partialSwap (projector K f) (firstEight p.1, firstEight p.2))).2)) = _
  rw [hlocal]
  apply Prod.ext <;> funext i
  all_goals
    by_cases hi : i.val < 8
    · simp [replaceFirst, firstEight, coordinateSwap64, hi]
    · simp [replaceFirst, coordinateSwap64, hi, outside i (Nat.le_of_not_gt hi)]

theorem frame_after_full64_coordinate (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (mask : Fin 64 → Bool)
    (hc : ∀ i j : Fin 8, scaledMatrix 1 i j - scaledMatrix f i j =
      if i = j ∧ mask ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩ = true then 4 else 0)
    (outside : ∀ i : Fin 64, 8 ≤ i.val → mask i = false)
    (p : (Fin 64 → K) × (Fin 64 → K)) :
    (gauge64 K h2 f).forward ((gauge64 K h2 1).inverse p) = coordinateSwap64 mask p := by
  change liftPair (partialSwap (projector K f))
    (liftPair (partialSwap (projector K 1)) p) = _
  rw [liftPair_comp]
  have hlocal := frame_after_full K h2 f (firstEight p.1, firstEight p.2)
  rw [residual_partialSwap K h2 f
    (fun i => mask ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩) hc] at hlocal
  change (replaceFirst p.1 ((partialSwap (projector K f)
      (partialSwap (projector K 1) (firstEight p.1, firstEight p.2))).1),
    replaceFirst p.2 ((partialSwap (projector K f)
      (partialSwap (projector K 1) (firstEight p.1, firstEight p.2))).2)) = _
  rw [hlocal]
  apply Prod.ext <;> funext i
  all_goals
    by_cases hi : i.val < 8
    · simp [replaceFirst, firstEight, coordinateSwap64, hi]
    · simp [replaceFirst, coordinateSwap64, hi, outside i (Nat.le_of_not_gt hi)]

theorem coordinateSwap64_involution {K : Type*} (mask : Fin 64 → Bool)
    (p : (Fin 64 → K) × (Fin 64 → K)) :
    coordinateSwap64 mask (coordinateSwap64 mask p) = p := by
  apply Prod.ext <;> funext i <;> cases hm : mask i <;> simp [coordinateSwap64, hm]

/-- Literal common stage-2 subspace E₂: coordinates 8 through 21. -/
def stage2Mask : Fin 64 → Bool := fun i => decide (8 ≤ i.val ∧ i.val < 22)

/-- The actual stage-2 gauge D_(Pframe ⊕ I14 ⊕ 0). The common E₂ factor is
present on both endpoints and both inverse laws; it is not silently omitted. -/
def gaugeStage2 (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (f : Fin 944) :
    FramedReplay.Gauge ((Fin 64 → K) × (Fin 64 → K)) where
  forward p := (gauge64 K h2 f).forward (coordinateSwap64 stage2Mask p)
  inverse p := coordinateSwap64 stage2Mask ((gauge64 K h2 f).inverse p)
  inverse_forward p := by
    rw [(gauge64 K h2 f).inverse_forward, coordinateSwap64_involution]
  forward_inverse p := by
    rw [coordinateSwap64_involution, (gauge64 K h2 f).forward_inverse]

theorem stage2_relative_transport (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (initial final : Fin 944) (p : (Fin 64 → K) × (Fin 64 → K)) :
    (gaugeStage2 K h2 initial).forward ((gaugeStage2 K h2 final).inverse p) =
      (gauge64 K h2 initial).forward ((gauge64 K h2 final).inverse p) := by
  simp only [gaugeStage2, coordinateSwap64_involution]

/-- The raw-payload orientation of the complete stage-2 helper endpoint.
This includes all 64 coordinates and cancels the actual common E₂ factor. -/
theorem stage2_helper_endpoint (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (f : Fin 944) (mask : Fin 64 → Bool)
    (hc : ∀ i j : Fin 8, scaledMatrix 1 i j - scaledMatrix f i j =
      if i = j ∧ mask ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩ = true then 4 else 0)
    (outside : ∀ i : Fin 64, 8 ≤ i.val → mask i = false)
    (p : (Fin 64 → K) × (Fin 64 → K)) :
    (gaugeStage2 K h2 f).forward ((gaugeStage2 K h2 1).inverse p) = coordinateSwap64 mask p := by
  rw [stage2_relative_transport]
  exact frame_after_full64_coordinate K h2 f mask hc outside p

end FrameGeometry

#print axioms FrameGeometry.scaled_full_entries
#print axioms FrameGeometry.scaled_zero_entries
#print axioms FrameGeometry.scaled_idempotent
#print axioms FrameGeometry.scaled_symmetric
#print axioms FrameGeometry.stack_inverse
#print axioms FrameGeometry.inverse_stack
#print axioms FrameGeometry.cast_mul_factor
#print axioms FrameGeometry.four_ne_zero
#print axioms FrameGeometry.two_fifty_six_ne_zero
#print axioms FrameGeometry.projector_idempotent
#print axioms FrameGeometry.projector_symmetric
#print axioms FrameGeometry.projector_full
#print axioms FrameGeometry.projector_zero
#print axioms FrameGeometry.scaled_stack
#print axioms FrameGeometry.cast_transpose
#print axioms FrameGeometry.cast_product
#print axioms FrameGeometry.cast_selector
#print axioms FrameGeometry.projector_stack
#print axioms FrameGeometry.transition_scaled_left
#print axioms FrameGeometry.transition_scaled_right
#print axioms FrameGeometry.normalized_absorption
#print axioms FrameGeometry.transition_projectors
#print axioms FrameGeometry.stack_right_inverse
#print axioms FrameGeometry.stack_left_inverse
#print axioms FrameGeometry.partialSwap_involution
#print axioms FrameGeometry.partialSwap_nested
#print axioms FrameGeometry.partialSwap_nested_reverse
#print axioms FrameGeometry.full_after_frame
#print axioms FrameGeometry.frame_after_full
#print axioms FrameGeometry.firstEight_replaceFirst
#print axioms FrameGeometry.replaceFirst_twice
#print axioms FrameGeometry.replaceFirst_firstEight
#print axioms FrameGeometry.liftPair_comp
#print axioms FrameGeometry.liftPair_id
#print axioms FrameGeometry.partialSwap_coordinate
#print axioms FrameGeometry.coordinate_residual
#print axioms FrameGeometry.residual_partialSwap
#print axioms FrameGeometry.full_after_frame64_coordinate
#print axioms FrameGeometry.frame_after_full64_coordinate
#print axioms FrameGeometry.coordinateSwap64_involution
#print axioms FrameGeometry.stage2_relative_transport
#print axioms FrameGeometry.stage2_helper_endpoint
