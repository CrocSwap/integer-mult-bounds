import Mathlib.Data.Complex.Basic
import Mathlib.Data.List.Perm.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Data.Real.Basic
import Mathlib.LinearAlgebra.Pi
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic.Abel
import Mathlib.Algebra.Order.Archimedean.Basic
import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.NormNum
import Mathlib.Analysis.Convex.SpecificFunctions.Pow

/-! Standalone exact native, recursion and moment lemmas. Apache-2.0.
See NOTICE.md for retained sources and scope. Eighty-seven named theorem APIs;
helper facts and extended retained algebra are counted as APIs, not discoveries. -/

/- Source part: Factors.lean; SHA256 5073b72b68037e401be2f48f104f122ddd5193bc8f349cb7d4a10c906ddc5cf5 -/
/-!
Exact Gaussian factor reordering, with the physical family retained in every
instruction. This is the algebraic assembly lemma; finite source bindings,
native normalization, chronology and physical cost are checked separately.
-/

namespace SelectiveBorrowing

noncomputable section

variable {G R K : Type*}

def weightedShift [AddCommMonoid G] [CommSemiring R]
    (a b : R) (v : G) (f : G → R) : G → R :=
  fun x => a * f x + b * f (x + v)

theorem weightedShift_commute [AddCommMonoid G] [CommSemiring R]
    (a b c d : R) (v w : G) (f : G → R) :
    weightedShift a b v (weightedShift c d w f) =
      weightedShift c d w (weightedShift a b v f) := by
  funext x
  simp only [weightedShift]
  rw [show (x + v) + w = (x + w) + v by ac_rfl]
  ring

/-- The full positive native Gaussian operator, including its scalar phase. -/
def gaussianStep [AddCommMonoid G] (v : G) (f : G → ℂ) : G → ℂ :=
  weightedShift ((1 + Complex.I) / 2) ((1 - Complex.I) / 2) v f

theorem gaussianStep_commute [AddCommMonoid G]
    (v w : G) (f : G → ℂ) :
    gaussianStep v (gaussianStep w f) = gaussianStep w (gaussianStep v f) :=
  weightedShift_commute _ _ _ _ _ _ _

def gaussianWord [AddCommMonoid G] (word : List G) (f : G → ℂ) : G → ℂ :=
  word.foldr gaussianStep f

theorem gaussianWord_append [AddCommMonoid G]
    (xs ys : List G) (f : G → ℂ) :
    gaussianWord (xs ++ ys) f = gaussianWord xs (gaussianWord ys f) := by
  simp [gaussianWord, List.foldr_append]

theorem gaussianWord_perm [AddCommMonoid G]
    {xs ys : List G} (h : xs.Perm ys) (f : G → ℂ) :
    gaussianWord xs f = gaussianWord ys f := by
  induction h with
  | nil => rfl
  | cons a h ih =>
      change gaussianStep a (gaussianWord _ f) = gaussianStep a (gaussianWord _ f)
      rw [ih]
  | swap a b l =>
      change gaussianStep _ (gaussianStep _ _) = gaussianStep _ (gaussianStep _ _)
      apply gaussianStep_commute
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

/-- Every factor acts on its named physical family and leaves all others fixed. -/
def familyStep [DecidableEq K] [AddCommMonoid G]
    (instruction : K × G) (f : K → G → ℂ) : K → G → ℂ :=
  fun k => if k = instruction.1 then gaussianStep instruction.2 (f k) else f k

theorem familyStep_commute [DecidableEq K] [AddCommMonoid G]
    (a b : K × G) (f : K → G → ℂ) :
    familyStep a (familyStep b f) = familyStep b (familyStep a f) := by
  funext k
  by_cases ha : k = a.1
  · by_cases hb : k = b.1
    · have hab : a.1 = b.1 := ha.symm.trans hb
      simpa [familyStep, ha, hab] using gaussianStep_commute a.2 b.2 (f k)
    · have hab : a.1 ≠ b.1 := fun h => hb (ha.trans h)
      simp [familyStep, ha, hab]
  · by_cases hb : k = b.1
    · have hba : b.1 ≠ a.1 := fun h => ha (hb.trans h)
      simp [familyStep, hb, hba]
    · simp [familyStep, ha, hb]

def familyWord [DecidableEq K] [AddCommMonoid G]
    (word : List (K × G)) (f : K → G → ℂ) : K → G → ℂ :=
  word.foldr familyStep f

/-- A permutation certificate must retain the family as well as the axis. -/
theorem familyWord_perm [DecidableEq K] [AddCommMonoid G]
    {xs ys : List (K × G)} (h : xs.Perm ys) (f : K → G → ℂ) :
    familyWord xs f = familyWord ys f := by
  induction h with
  | nil => rfl
  | cons a h ih =>
      change familyStep a (familyWord _ f) = familyStep a (familyWord _ f)
      rw [ih]
  | swap a b l =>
      change familyStep _ (familyStep _ _) = familyStep _ (familyStep _ _)
      apply familyStep_commute
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

def addressShift [AddCommMonoid G] (q : G) (f : G → ℂ) : G → ℂ :=
  fun x => f (x + q)

theorem gaussianStep_addressShift [AddCommMonoid G]
    (v q : G) (f : G → ℂ) :
    gaussianStep v (addressShift q f) = addressShift q (gaussianStep v f) := by
  funext x
  simp only [gaussianStep, weightedShift, addressShift]
  rw [show (x + v) + q = (x + q) + v by ac_rfl]

theorem gaussianWord_addressShift [AddCommMonoid G]
    (word : List G) (q : G) (f : G → ℂ) :
    gaussianWord word (addressShift q f) = addressShift q (gaussianWord word f) := by
  induction word with
  | nil => rfl
  | cons v vs ih =>
      change gaussianStep v (gaussianWord vs (addressShift q f)) =
        addressShift q (gaussianStep v (gaussianWord vs f))
      rw [ih, gaussianStep_addressShift]

end

end SelectiveBorrowing

/- Source part: Feedback.lean; SHA256 fcf41f9ed8aee6e081d70276474ae3512941da83f2f9ada19587dcdf8b0660c1 -/
/-! Sufficient all-cut feedback bounds for the selective-borrowing invoice.
These lemmas do not assert that a particular implementation meets the defect
contract; the independently recounted instruction envelope supplies that data.
-/

namespace IntegerMultBounds.SelectiveBorrowing

theorem absorb_feedback (error coefficient budget : ℝ)
    (herror : 0 ≤ error) (hsmall : coefficient ≤ 1 / 2)
    (hfeedback : error ≤ coefficient * (budget + error)) :
    error ≤ 2 * coefficient * budget := by
  have h := mul_nonneg (sub_nonneg.mpr hsmall) herror
  nlinarith

theorem relative_error_of_feedback (error amplification defect unit initial target : ℝ)
    (herror : 0 ≤ error) (hinitial : 0 ≤ initial)
    (hsmall : defect * unit ≤ 1 / 2)
    (hbudget : 2 * defect * unit * amplification ≤ target)
    (hfeedback : error ≤ defect * unit * (amplification * initial + error)) :
    error ≤ target * initial := by
  calc
    error ≤ 2 * (defect * unit) * (amplification * initial) :=
      absorb_feedback error (defect * unit) (amplification * initial) herror hsmall hfeedback
    _ = (2 * defect * unit * amplification) * initial := by simp only [mul_assoc]
    _ ≤ target * initial := mul_le_mul_of_nonneg_right hbudget hinitial

theorem owner_stock_reserve (oldHelpers newHelpers cleanup : ℕ)
    (hreserve : newHelpers ≤ oldHelpers) :
    newHelpers + cleanup ≤ oldHelpers + cleanup :=
  Nat.add_le_add_right hreserve cleanup

end IntegerMultBounds.SelectiveBorrowing

/- Source part: NativeAlgebra.lean; SHA256 3fb060e41ba0737c7a7e069d325f376c973f304472da4aba52d5bba476f4f63e -/
/-!
# Exact native operators and frame-correct data ABI

The Gaussian kernel includes its scalar phase. No finite-dimensionality, zero
scratch, cost oracle, or numerical approximation is assumed. Family tags in
reordering certificates are literal. The weighted-shift representation and the
family permutation argument extend SelectiveBorrowing's PR2260 Factors.lean;
all definitions needed here are included and only Mathlib is imported.
-/
namespace IntegerKappa.Native
noncomputable section

variable {G H K : Type*}

def weightedShift [AddCommMonoid G] (a b : ℂ) (v : G) (f : G → ℂ) : G → ℂ :=
  fun x => a * f x + b * f (x + v)

def shift [AddCommMonoid G] (v : G) (f : G → ℂ) : G → ℂ := fun x => f (x + v)

/-- The positive Gaussian-dyadic kernel, with its exact fourth-root phase. -/
def step [AddCommMonoid G] (v : G) (f : G → ℂ) : G → ℂ :=
  weightedShift ((1 + Complex.I) / 2) ((1 - Complex.I) / 2) v f

/-- The actual inverse kernel, not the positive kernel with a dropped phase. -/
def inverseStep [AddCommMonoid G] (v : G) (f : G → ℂ) : G → ℂ :=
  weightedShift ((1 - Complex.I) / 2) ((1 + Complex.I) / 2) v f

theorem weightedShift_add [AddCommMonoid G] (a b : ℂ) (v : G) (f g : G → ℂ) :
    weightedShift a b v (f + g) = weightedShift a b v f + weightedShift a b v g := by
  funext x
  simp only [weightedShift, Pi.add_apply]
  ring

theorem weightedShift_smul [AddCommMonoid G] (a b c : ℂ) (v : G) (f : G → ℂ) :
    weightedShift a b v (c • f) = c • weightedShift a b v f := by
  funext x
  simp only [weightedShift, Pi.smul_apply, smul_eq_mul]
  ring

/-- Exact two-factor composition on any involutive translation. -/
theorem weightedShift_composition [AddCommMonoid G] (a b c d : ℂ)
    (v : G) (hv : v + v = 0) (f : G → ℂ) :
    weightedShift a b v (weightedShift c d v f) =
      weightedShift (a*c + b*d) (a*d + b*c) v f := by
  funext x
  simp only [weightedShift]
  rw [add_assoc, hv, add_zero]
  ring

/-- C_v squared is the literal address flip. -/
theorem step_square [AddCommMonoid G] (v : G) (hv : v + v = 0) (f : G → ℂ) :
    step v (step v f) = shift v f := by
  unfold step
  rw [weightedShift_composition _ _ _ _ v hv]
  funext x
  simp only [weightedShift, shift]
  ring_nf
  simp [Complex.I_sq]
  ring

theorem shift_square [AddCommMonoid G] (v : G) (hv : v + v = 0) (f : G → ℂ) :
    shift v (shift v f) = f := by
  funext x
  simp [shift, add_assoc, hv]

/-- Four positive kernels restore every arbitrary input. -/
theorem step_fourth [AddCommMonoid G] (v : G) (hv : v + v = 0) (f : G → ℂ) :
    step v (step v (step v (step v f))) = f := by
  rw [step_square v hv, step_square v hv, shift_square v hv]

theorem inverseStep_left [AddCommMonoid G] (v : G) (hv : v + v = 0) (f : G → ℂ) :
    inverseStep v (step v f) = f := by
  unfold inverseStep step
  rw [weightedShift_composition _ _ _ _ v hv]
  funext x
  simp only [weightedShift]
  ring_nf
  simp [Complex.I_sq]
  ring

theorem inverseStep_right [AddCommMonoid G] (v : G) (hv : v + v = 0) (f : G → ℂ) :
    step v (inverseStep v f) = f := by
  unfold inverseStep step
  rw [weightedShift_composition _ _ _ _ v hv]
  funext x
  simp only [weightedShift]
  ring_nf
  simp [Complex.I_sq]
  ring

/-- Inverse is C cubed with no missing global unit. -/
theorem inverseStep_eq_cube [AddCommMonoid G] (v : G) (hv : v + v = 0)
    (f : G → ℂ) : inverseStep v f = step v (step v (step v f)) := by
  have h := inverseStep_left v hv (step v (step v (step v f)))
  rw [step_fourth v hv] at h
  exact h

theorem step_add [AddCommMonoid G] (v : G) (f g : G → ℂ) :
    step v (f + g) = step v f + step v g := weightedShift_add _ _ _ _ _

theorem step_smul [AddCommMonoid G] (v : G) (c : ℂ) (f : G → ℂ) :
    step v (c • f) = c • step v f := weightedShift_smul _ _ _ _ _

/-- The exact kernel packaged for direct use by the source/target ABI lemmas. -/
def stepLinear [AddCommMonoid G] (v : G) : (G → ℂ) →ₗ[ℂ] (G → ℂ) where
  toFun := step v
  map_add' := step_add v
  map_smul' := step_smul v

/-- A Gaussian kernel is an actual linear equivalence on arbitrary arrays when
its address translation is involutive. The inverse includes the scalar phase. -/
def stepEquiv [AddCommMonoid G] (v : G) (hv : v+v=0) :
    (G → ℂ) ≃ₗ[ℂ] (G → ℂ) where
  toFun := step v
  invFun := inverseStep v
  left_inv := inverseStep_left v hv
  right_inv := inverseStep_right v hv
  map_add' := step_add v
  map_smul' := step_smul v

/-- Exact naturality under any address homomorphism, including a binary chart. -/
theorem step_natural [AddCommMonoid G] [AddCommMonoid H] (A : G →+ H)
    (v : G) (f : H → ℂ) : step v (f ∘ A) = step (A v) f ∘ A := by
  funext x
  simp [step, weightedShift, map_add]

theorem inverseStep_natural [AddCommMonoid G] [AddCommMonoid H] (A : G →+ H)
    (v : G) (f : H → ℂ) : inverseStep v (f ∘ A) = inverseStep (A v) f ∘ A := by
  funext x
  simp [inverseStep, weightedShift, map_add]

/-- The unit-phase inverse wrapper for a sign character anticommuting with X_v.
The hypotheses are exact pointwise equalities, not an assumed inverse oracle. -/
theorem inverseStep_sign_wrapper [AddCommMonoid G] (v : G) (χ f : G → ℂ)
    (hunit : ∀ x, χ x * χ x = 1) (hflip : ∀ x, χ (x + v) = -χ x) :
    inverseStep v f = fun x => -Complex.I * (χ x * step v (fun y => χ y * f y) x) := by
  funext x
  simp only [inverseStep, step, weightedShift, hflip]
  calc
    _ = ((1-Complex.I)/2)*f x + ((1+Complex.I)/2)*f (x+v) := rfl
    _ = -Complex.I * (((1+Complex.I)/2)*(χ x*χ x)*f x -
        ((1-Complex.I)/2)*(χ x*χ x)*f (x+v)) := by
          rw [hunit]
          ring_nf
          simp [Complex.I_sq]
          ring
    _ = _ := by ring

/-- A monomial phase invariant along this axis commutes with the positive kernel. -/
theorem step_monomial_natural [AddCommMonoid G] [AddCommMonoid H]
    (A : G →+ H) (v : G) (χ : G → ℂ) (f : H → ℂ)
    (hχ : ∀ x, χ (x+v) = χ x) :
    step v (fun x => χ x * f (A x)) = fun x => χ x * step (A v) f (A x) := by
  funext x
  simp only [step, weightedShift, hχ, map_add]
  ring

/-- Anticommuting monomial phases switch the kernel direction AND introduce i.
Dropping that scalar would give a false operator equality. -/
theorem step_monomial_anticommuting [AddCommMonoid G] [AddCommMonoid H]
    (A : G →+ H) (v : G) (χ : G → ℂ) (f : H → ℂ)
    (hχ : ∀ x, χ (x+v) = -χ x) :
    step v (fun x => χ x * f (A x)) =
      fun x => Complex.I * (χ x * inverseStep (A v) f (A x)) := by
  funext x
  simp only [step, inverseStep, weightedShift, hχ, map_add]
  ring_nf
  simp [Complex.I_sq]
  ring

theorem step_commute [AddCommMonoid G] (v w : G) (f : G → ℂ) :
    step v (step w f) = step w (step v f) := by
  funext x
  simp only [step, weightedShift]
  rw [show (x+v)+w = (x+w)+v by ac_rfl]
  ring

def word [AddCommMonoid G] (xs : List G) (f : G → ℂ) : G → ℂ := xs.foldr step f

/-- An exact list-permutation certificate suffices for a Gaussian factor reorder. -/
theorem word_perm [AddCommMonoid G] {xs ys : List G} (h : xs.Perm ys) (f : G → ℂ) :
    word xs f = word ys f := by
  induction h with
  | nil => rfl
  | cons a h ih => change step a (word _ f) = step a (word _ f); rw [ih]
  | swap a b l => exact step_commute _ _ _
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

/-- Conjugation by an invertible binary chart, including its actual axis image. -/
theorem step_chart_conjugation [AddCommMonoid G] [AddCommMonoid H]
    (A : G ≃+ H) (v : G) (f : H → ℂ) :
    step v (f ∘ A) ∘ A.symm = step (A v) f := by
  funext x
  simp [step, weightedShift, Function.comp_def, map_add]

/-- Physical-family labels are retained in every instruction. -/
def familyStep [DecidableEq K] [AddCommMonoid G] (a : K × G)
    (f : K → G → ℂ) : K → G → ℂ :=
  fun k => if k = a.1 then step a.2 (f k) else f k

theorem familyStep_commute [DecidableEq K] [AddCommMonoid G]
    (a b : K × G) (f : K → G → ℂ) :
    familyStep a (familyStep b f) = familyStep b (familyStep a f) := by
  funext k
  by_cases ha : k = a.1
  · by_cases hb : k = b.1
    · have hab : a.1 = b.1 := ha.symm.trans hb
      simpa [familyStep, ha, hab] using step_commute a.2 b.2 (f k)
    · have hab : a.1 ≠ b.1 := fun h => hb (ha.trans h)
      simp [familyStep, ha, hab]
  · by_cases hb : k = b.1
    · have hba : b.1 ≠ a.1 := fun h => ha (hb.trans h)
      simp [familyStep, hb, hba]
    · simp [familyStep, ha, hb]

def familyWord [DecidableEq K] [AddCommMonoid G] (xs : List (K × G))
    (f : K → G → ℂ) : K → G → ℂ := xs.foldr familyStep f

/-- Axis counts alone cannot instantiate this theorem: the permutation includes
both the literal family tag and the axis. -/
theorem familyWord_perm [DecidableEq K] [AddCommMonoid G]
    {xs ys : List (K × G)} (h : xs.Perm ys) (f : K → G → ℂ) :
    familyWord xs f = familyWord ys f := by
  induction h with
  | nil => rfl
  | cons a h ih => change familyStep a (familyWord _ f) = familyStep a (familyWord _ f); rw [ih]
  | swap a b l => exact familyStep_commute _ _ _
  | trans h₁ h₂ ih₁ ih₂ => exact ih₁.trans ih₂

section ABI
variable {R V : Type*} [CommRing R] [AddCommGroup V] [Module R V]

/-- Source and target frames are separately encoded. -/
def framedKernel (source target : V ≃ₗ[R] V) (U : V →ₗ[R] V) : V →ₗ[R] V :=
  target.toLinearMap.comp (U.comp source.symm.toLinearMap)

/-- Native kernel on a source-encoded arbitrary value returns the target encoding. -/
theorem framedKernel_encoded (source target : V ≃ₗ[R] V) (U : V →ₗ[R] V) (x : V) :
    framedKernel source target U (source x) = target (U x) := by
  simp [framedKernel]

/-- Correct source/target ABI for a scaled ADD. Distinct frames are allowed. -/
theorem framed_add_decode (source target : V ≃ₗ[R] V) (U : V →ₗ[R] V)
    (c : R) (x y : V) :
    target.symm (target y + c • framedKernel source target U (source x)) =
      y + c • U x := by
  simp [framedKernel, map_add]

/-- A shared frame cancels around an ADD; a bare ADD in distinct frames does not
follow from this theorem. -/
theorem shared_frame_add (frame : V ≃ₗ[R] V) (c : R) (x y : V) :
    frame.symm (frame y + c • frame x) = y + c • x := by
  simp [map_add]

/-- Sequential kernels cancel exactly at their shared intermediate ABI. -/
theorem framedKernel_comp (a b c : V ≃ₗ[R] V) (U W : V →ₗ[R] V) :
    (framedKernel b c W).comp (framedKernel a b U) =
      framedKernel a c (W.comp U) := by
  ext x
  simp [framedKernel]

/-- An arbitrary dirty relay contributes its difference, with no fresh-zero premise. -/
theorem dirty_relay_restoration (U : V →ₗ[R] V) (c : R) (x y dirty : V) :
    y + c • (dirty + U x) - c • dirty = y + c • U x := by
  rw [smul_add]
  abel

/-- Decode the dirty relay in its actual target frame. -/
theorem framed_dirty_relay_restoration (source target : V ≃ₗ[R] V)
    (U : V →ₗ[R] V) (c : R) (x y dirty : V) :
    target.symm (target y + c • (target dirty + framedKernel source target U (source x)) -
      c • target dirty) = y + c • U x := by
  simp only [framedKernel_encoded]
  rw [← map_add target dirty (U x), ← map_smul, ← map_add, ← map_smul, ← map_sub]
  rw [LinearEquiv.symm_apply_apply]
  exact dirty_relay_restoration U c x y dirty

end ABI
end
end IntegerKappa.Native

/- Source part: Recursion.lean; SHA256 098ecce913798bf932a613a578b453f67b96309f479b9099c09caafb23d2d59d -/
/-!
# Active-depth exact-grid bounds and affine exponent bootstrap

Universal sufficient algebraic interfaces. No recursive child implementation,
rounding model, multiplication runtime, or numerical frontier is assumed here.
-/

namespace IntegerMultBounds.Recursion

/-- A proper rank gives a nonincreasing child width, including short tails. -/
theorem child_le (m r e : ℕ) (hr : r ≤ m) : r * (e / m) ≤ e := by
  calc
    r * (e / m) ≤ m * (e / m) := Nat.mul_le_mul_right _ hr
    _ ≤ e := Nat.mul_div_le e m

/-- Once a node is nonleaf, the proper-rank child is strictly smaller. -/
theorem child_lt (m r e : ℕ) (hm : 0 < m) (hr : r < m) (he : m ≤ e) :
    r * (e / m) < e := by
  have hq : 0 < e / m := Nat.div_pos he hm
  exact lt_of_lt_of_le (Nat.mul_lt_mul_of_pos_right hr hq) (Nat.mul_div_le e m)

/-- A short tail contains no complete field. -/
theorem child_eq_zero_of_lt (m r e : ℕ) (he : e < m) : r * (e / m) = 0 := by
  simp [Nat.div_eq_of_lt he]

/-- The fixed nonchild charge may be absorbed because a nonleaf has q>=1. -/
theorem quotient_budget (m r e C s E : ℕ) (hm : 0 < m) (he : m ≤ e)
    (hbudget : C * r + s + E ≤ C * m) :
    C * (r * (e / m)) + s * (e / m) + E ≤ C * e := by
  have hq : 0 < e / m := Nat.div_pos he hm
  calc
    C * (r * (e / m)) + s * (e / m) + E ≤
        C * (r * (e / m)) + s * (e / m) + E * (e / m) := by
      exact Nat.add_le_add_left (Nat.le_mul_of_pos_right E hq) _
    _ = (C * r + s + E) * (e / m) := by ring
    _ ≤ (C * m) * (e / m) := Nat.mul_le_mul_right _ hbudget
    _ = C * (m * (e / m)) := by ring
    _ ≤ C * e := Nat.mul_le_mul_left _ (Nat.mul_div_le e m)

/-- The active-depth theorem allows arbitrary tails and any larger stopping rule. -/
theorem linear_bound_of_stopped_recursion (A r : ℕ → ℕ) (m stop C s E : ℕ)
    (hm : 0 < m) (hstop : m ≤ stop) (hr : ∀ e, r e < m)
    (hleaf : ∀ e, e < stop → A e ≤ C * e)
    (hstep : ∀ e, stop ≤ e → A e ≤ A (r e * (e / m)) + s * (e / m) + E)
    (hbudget : ∀ e, C * r e + s + E ≤ C * m) :
    ∀ e, A e ≤ C * e := by
  intro e
  induction e using Nat.strong_induction_on with
  | h e ih =>
    by_cases leaf : e < stop
    · exact hleaf e leaf
    have hnonleaf : stop ≤ e := Nat.le_of_not_gt leaf
    have he : m ≤ e := hstop.trans hnonleaf
    have hchild := ih (r e * (e / m)) (child_lt m (r e) e hm (hr e) he)
    calc
      A e ≤ A (r e * (e / m)) + s * (e / m) + E := hstep e hnonleaf
      _ ≤ C * (r e * (e / m)) + s * (e / m) + E := by omega
      _ ≤ C * e := quotient_budget m (r e) e C s E hm he (hbudget e)

/-- Every proper rank fits the standard linear common-exponent budget. -/
theorem standard_rank_budget (m r s E : ℕ) (hr : r < m) :
    2 * (s + E) * r + s + E ≤ 2 * (s + E) * m := by
  have h : r + 1 ≤ m := hr
  nlinarith

/-- Leaf 8e plus the exact active-child recurrence implies a linear 2Be bound. -/
theorem exact_grid_linear_bound (A r : ℕ → ℕ) (m stop s E : ℕ)
    (hm : 0 < m) (hstop : m ≤ stop) (hr : ∀ e, r e < m) (hB : 8 ≤ s + E)
    (hleaf : ∀ e, e < stop → A e ≤ 8 * e)
    (hstep : ∀ e, stop ≤ e → A e ≤ A (r e * (e / m)) + s * (e / m) + E) :
    ∀ e, A e ≤ 2 * (s + E) * e := by
  apply linear_bound_of_stopped_recursion A r m stop (2 * (s + E)) s E hm hstop hr
  · intro e he
    exact (hleaf e he).trans (Nat.mul_le_mul_right e (by omega))
  · exact hstep
  · intro e
    exact standard_rank_budget m (r e) s E (hr e)

/-- Finite partitions add linear excess only on their actual selected axes. -/
theorem partition_linear_bound {ι : Type*} (I : Finset ι) (A size : ι → ℕ)
    (C d : ℕ) (hA : ∀ i ∈ I, A i ≤ C * size i)
    (hsize : ∑ i ∈ I, size i ≤ d) : ∑ i ∈ I, A i ≤ C * d := by
  calc
    ∑ i ∈ I, A i ≤ ∑ i ∈ I, C * size i := Finset.sum_le_sum hA
    _ = C * ∑ i ∈ I, size i := by rw [Finset.mul_sum]
    _ ≤ C * d := Nat.mul_le_mul_left C hsize

/-- Outer phases and preprocessing are charged after the finite partition. -/
theorem layer_excess_bound {ι : Type*} (I : Finset ι) (A size : ι → ℕ)
    (B d outer : ℕ) (hA : ∀ i ∈ I, A i ≤ 2 * B * size i)
    (hsize : ∑ i ∈ I, size i ≤ d) :
    (∑ i ∈ I, A i) + outer * d ≤ (2 * B + outer) * d := by
  have h := partition_linear_bound I A size (2 * B) d hA hsize
  nlinarith

/-- The traditional C0 reserve dominates the linear exact-grid coefficient. -/
theorem standard_C0_guard (m B : ℕ) (hm : 1 ≤ m) (hB : 8 ≤ B) :
    2 * B + 18 < 32 * m * B ^ 2 := by
  have hb : B ≤ B ^ 2 := by nlinarith
  have hmB := Nat.mul_le_mul_right (B ^ 2) hm
  nlinarith

/-- A strict coefficient reserve remains strict for every positive dimension. -/
theorem common_grid_sufficient (excess C C0 d : ℕ) (hexcess : excess ≤ C * d)
    (hC : C < C0) (hd : 0 < d) : excess < C0 * d := by
  exact lt_of_le_of_lt hexcess (Nat.mul_lt_mul_of_pos_right hC hd)

/-- Repeated active-child descent, kept separate from sibling work. -/
def descent (child : ℕ → ℕ) (e : ℕ) : ℕ → ℕ
  | 0 => e
  | n + 1 => child (descent child e n)

/-- Any strictly decreasing positive active width reaches zero in at most e steps. -/
theorem descent_le_sub (child : ℕ → ℕ) (hzero : child 0 = 0)
    (hdecrease : ∀ x, 0 < x → child x < x) (e n : ℕ) :
    descent child e n ≤ e - n := by
  induction n with
  | zero => simp [descent]
  | succ n ih =>
    simp only [descent]
    by_cases hz : descent child e n = 0
    · simp [hz, hzero]
    · have h := hdecrease (descent child e n) (by omega)
      omega

/-- A coarse but unconditional finite-depth certificate. -/
theorem descent_terminates (child : ℕ → ℕ) (hzero : child 0 = 0)
    (hdecrease : ∀ x, 0 < x → child x < x) (e : ℕ) :
    descent child e e = 0 := by
  have h := descent_le_sub child hzero hdecrease e e
  omega

/-- The floor-rank child shrinks geometrically without requiring divisible widths. -/
theorem descent_scaled_bound (m r e n : ℕ) :
    m ^ n * descent (fun x => r * (x / m)) e n ≤ r ^ n * e := by
  induction n with
  | zero => simp [descent]
  | succ n ih =>
    simp only [descent, pow_succ]
    have h := Nat.mul_div_le (descent (fun x => r * (x / m)) e n) m
    have h1 := Nat.mul_le_mul_left (m ^ n * r) h
    have h2 := Nat.mul_le_mul_left r ih
    nlinarith

/-- An explicit geometric inequality is sufficient to stop the recursion. -/
theorem descent_eq_zero_of_scaled_lt (m r e n : ℕ)
    (hstop : r ^ n * e < m ^ n) :
    descent (fun x => r * (x / m)) e n = 0 := by
  have h := descent_scaled_bound m r e n
  by_contra hn
  have hp : 1 ≤ descent (fun x => r * (x / m)) e n := by omega
  have hmul := Nat.mul_le_mul_left (m ^ n) hp
  nlinarith

/-- The affine improvement used by stopped exponent bootstraps. -/
def bootstrap (s a : ℝ) : ℕ → ℝ
  | 0 => a
  | n + 1 => (1 - s) * s + s * bootstrap s a n

/-- Closed form for the remaining gap, valid for every real s and initial a. -/
theorem bootstrap_gap (s a : ℝ) (n : ℕ) :
    s - bootstrap s a n = s ^ n * (s - a) := by
  induction n with
  | zero => simp [bootstrap]
  | succ n ih =>
    simp only [bootstrap, pow_succ]
    calc
      s - ((1 - s) * s + s * bootstrap s a n) = s * (s - bootstrap s a n) := by ring
      _ = s * (s ^ n * (s - a)) := by rw [ih]
      _ = s ^ n * s * (s - a) := by ring

/-- The bootstrap never crosses its fixed point. -/
theorem bootstrap_le (s a : ℝ) (hs : 0 ≤ s) (ha : a ≤ s) (n : ℕ) :
    bootstrap s a n ≤ s := by
  have h := mul_nonneg (pow_nonneg hs n) (sub_nonneg.mpr ha)
  rw [← bootstrap_gap] at h
  linarith

/-- Strictly positive contraction leaves strictly positive headroom. -/
theorem bootstrap_lt (s a : ℝ) (hs : 0 < s) (ha : a < s) (n : ℕ) :
    bootstrap s a n < s := by
  have h := mul_pos (pow_pos hs n) (sub_pos.mpr ha)
  rw [← bootstrap_gap] at h
  linarith

/-- Each positive-gap bootstrap stage makes strict progress when 0<s<1. -/
theorem bootstrap_strict_progress (s a : ℝ) (hs : 0 < s) (hs1 : s < 1)
    (ha : a < s) (n : ℕ) : bootstrap s a n < bootstrap s a (n + 1) := by
  have hgap := bootstrap_lt s a hs ha n
  have hpos := mul_pos (sub_pos.mpr hs1) (sub_pos.mpr hgap)
  simp only [bootstrap]
  nlinarith

/-- A checked power bound is a sufficient finite-stage target certificate. -/
theorem bootstrap_target_of_power_bound (s a target : ℝ) (n : ℕ)
    (hbound : s ^ n * (s - a) ≤ s - target) : target ≤ bootstrap s a n := by
  rw [← bootstrap_gap] at hbound
  linarith

/-- Every target below the fixed point is reached in finitely many stages. -/
theorem bootstrap_eventually_above (s a target : ℝ)
    (_hs : 0 ≤ s) (hs1 : s < 1) (ha : a < s) (htarget : target < s) :
    ∃ n : ℕ, target < bootstrap s a n := by
  obtain ⟨n, hn⟩ := exists_pow_lt_of_lt_one
    (div_pos (sub_pos.mpr htarget) (sub_pos.mpr ha)) hs1
  refine ⟨n, ?_⟩
  have hmul := (mul_lt_mul_of_pos_right hn (sub_pos.mpr ha))
  have hden : s - a ≠ 0 := ne_of_gt (sub_pos.mpr ha)
  rw [div_mul_cancel₀ _ hden] at hmul
  rw [← bootstrap_gap] at hmul
  linarith


/-- Nonnegative input exponents remain nonnegative under a valid bootstrap. -/
theorem bootstrap_nonnegative (s a : ℝ) (hs : 0 ≤ s) (hs1 : s ≤ 1)
    (ha : 0 ≤ a) (n : ℕ) : 0 ≤ bootstrap s a n := by
  induction n with
  | zero => exact ha
  | succ n ih =>
    exact add_nonneg (mul_nonneg (sub_nonneg.mpr hs1) hs) (mul_nonneg hs ih)

/-- Arbitrarily many extra bootstrap stages preserve all established savings. -/
theorem bootstrap_monotone (s a : ℝ) (hs : 0 ≤ s) (hs1 : s ≤ 1) (ha : a ≤ s) :
    Monotone (bootstrap s a) := by
  apply monotone_nat_of_le_succ
  intro n
  have hgap := bootstrap_le s a hs ha n
  have h := mul_nonneg (sub_nonneg.mpr hs1) (sub_nonneg.mpr hgap)
  simp only [bootstrap]
  nlinarith

/-- A finite target witness remains valid at every later stage. -/
theorem bootstrap_eventually_always_above (s a target : ℝ)
    (hs : 0 ≤ s) (hs1 : s < 1) (ha : a < s) (htarget : target < s) :
    ∃ N : ℕ, ∀ n, N ≤ n → target < bootstrap s a n := by
  obtain ⟨N, hN⟩ := bootstrap_eventually_above s a target hs hs1 ha htarget
  refine ⟨N, fun n hn => ?_⟩
  exact hN.trans_le (bootstrap_monotone s a hs hs1.le ha.le hn)

end IntegerMultBounds.Recursion

/- Source part: MomentTransfer.lean; SHA256 68e89786008dd3f222632920a00eafd6fc64661e08548c5325a3daa4ba964522 -/
/-! Sufficient certificate transfer for finite paid-rank profiles.
The analytic cost is an arbitrary real weight until the concentration section,
where it is proved for real powers with exponent in [0,1]. -/

namespace IntegerMultBounds.MomentTransfer

open scoped BigOperators

variable {ι : Type*}

noncomputable def weighted (s : Finset ι) (c w : ι → ℝ) : ℝ :=
  ∑ i ∈ s, c i * w i

theorem weighted_zero (s : Finset ι) (w : ι → ℝ) : weighted s (fun _ => 0) w = 0 := by
  simp [weighted]

theorem weighted_add (s : Finset ι) (a b w : ι → ℝ) :
    weighted s (fun i => a i + b i) w = weighted s a w + weighted s b w := by
  simp [weighted, add_mul, Finset.sum_add_distrib]

theorem weighted_sub (s : Finset ι) (a b w : ι → ℝ) :
    weighted s (fun i => a i - b i) w = weighted s a w - weighted s b w := by
  simp [weighted, sub_mul, Finset.sum_sub_distrib]

theorem weighted_scale (s : Finset ι) (a w : ι → ℝ) (k : ℝ) :
    weighted s (fun i => k * a i) w = k * weighted s a w := by
  simp [weighted, mul_assoc, Finset.mul_sum]

theorem weighted_nonneg (s : Finset ι) (c w : ι → ℝ)
    (hc : ∀ i ∈ s, 0 ≤ c i) (hw : ∀ i ∈ s, 0 ≤ w i) :
    0 ≤ weighted s c w := by
  exact Finset.sum_nonneg fun i hi => mul_nonneg (hc i hi) (hw i hi)

theorem weighted_mono_counts (s : Finset ι) (a b w : ι → ℝ)
    (hab : ∀ i ∈ s, a i ≤ b i) (hw : ∀ i ∈ s, 0 ≤ w i) :
    weighted s a w ≤ weighted s b w := by
  exact Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_right (hab i hi) (hw i hi)

theorem weighted_mono_weights (s : Finset ι) (c u v : ι → ℝ)
    (hc : ∀ i ∈ s, 0 ≤ c i) (huv : ∀ i ∈ s, u i ≤ v i) :
    weighted s c u ≤ weighted s c v := by
  exact Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (huv i hi) (hc i hi)

/-- Remove a paid subprofile and insert another; the identity is exact. -/
theorem replacement_identity (s : Finset ι) (old removed added w : ι → ℝ) :
    weighted s (fun i => old i - removed i + added i) w =
      weighted s old w - weighted s removed w + weighted s added w := by
  rw [weighted_add, weighted_sub]

theorem replacement_nonneg (s : Finset ι) (old removed added : ι → ℝ)
    (hremove : ∀ i ∈ s, removed i ≤ old i) (hadd : ∀ i ∈ s, 0 ≤ added i) :
    ∀ i ∈ s, 0 ≤ old i - removed i + added i := by
  intro i hi
  exact add_nonneg (sub_nonneg.mpr (hremove i hi)) (hadd i hi)

theorem admission_of_replacement (s : Finset ι) (old removed added w : ι → ℝ)
    (budget : ℝ) (hold : weighted s old w < budget)
    (hmove : weighted s added w ≤ weighted s removed w) :
    weighted s (fun i => old i - removed i + added i) w < budget := by
  rw [replacement_identity]
  linarith

/-- A move's saving may pay a genuinely positive new reserve. -/
theorem admission_with_reserve (s : Finset ι) (old removed added w : ι → ℝ)
    (budget reserve margin saving : ℝ)
    (hold : weighted s old w ≤ budget - margin)
    (hmove : weighted s added w ≤ weighted s removed w - saving)
    (hreserve : reserve < margin + saving) :
    weighted s (fun i => old i - removed i + added i) w + reserve < budget := by
  rw [replacement_identity]
  linarith

/-- Equal removed/added stock or mass is inherited by the new profile. -/
theorem conserved_weight_of_replacement (s : Finset ι) (old removed added w : ι → ℝ)
    (hmove : weighted s added w = weighted s removed w) :
    weighted s (fun i => old i - removed i + added i) w = weighted s old w := by
  rw [replacement_identity, hmove]
  ring

theorem deficit_preserved (s : Finset ι) (old removed added rank : ι → ℝ)
    (capacity : ℝ) (hmass : weighted s added rank = weighted s removed rank) :
    capacity - weighted s (fun i => old i - removed i + added i) rank =
      capacity - weighted s old rank := by
  rw [conserved_weight_of_replacement s old removed added rank hmass]

/-- Soundness of finite rational upper bounds for arbitrary real costs. -/
theorem rational_upper_certificate (s : Finset ι) (c upper : ι → ℚ) (w : ι → ℝ)
    (budget : ℚ) (hc : ∀ i ∈ s, 0 ≤ c i)
    (hupper : ∀ i ∈ s, w i ≤ (upper i : ℝ))
    (hcertificate : (∑ i ∈ s, c i * upper i) < budget) :
    weighted s (fun i => (c i : ℝ)) w < (budget : ℝ) := by
  have h := weighted_mono_weights s (fun i => (c i : ℝ)) w (fun i => (upper i : ℝ))
    (fun i hi => by exact_mod_cast hc i hi) hupper
  have hcast : weighted s (fun i => (c i : ℝ)) (fun i => (upper i : ℝ)) < (budget : ℝ) := by
    change (∑ i ∈ s, (c i : ℝ) * (upper i : ℝ)) < (budget : ℝ)
    exact_mod_cast hcertificate
  exact h.trans_lt hcast

/-- Dividing by a positive budget connects paid sums to moment < 1. -/
theorem normalized_admission (cost budget : ℝ) (hbudget : 0 < budget) :
    cost / budget < 1 ↔ cost < budget := by
  rw [div_lt_one hbudget]

/-- A concave cost decreases when two bins are mixed towards the endpoints. -/
theorem concave_pair_mix (f : ℝ → ℝ) (hf : ConcaveOn ℝ (Set.Ici 0) f)
    (x y a b : ℝ) (hx : 0 ≤ x) (hy : 0 ≤ y)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a + b = 1) :
    f x + f y ≤ f (a*x + b*y) + f (b*x + a*y) := by
  have h₁ := hf.2 hx hy ha hb hab
  have h₂ := hf.2 hx hy hb ha (by linarith : b + a = 1)
  simp only [smul_eq_mul] at h₁ h₂
  have heq : (a*f x+b*f y)+(b*f x+a*f y)=f x+f y := by
    calc
      _ = (a+b)*(f x+f y) := by ring
      _ = _ := by rw [hab]; ring
  linarith

/-- Reverse Robin Hood exchange: move rank from the smaller bin to the larger. -/
theorem concave_concentration (f : ℝ → ℝ) (hf : ConcaveOn ℝ (Set.Ici 0) f)
    (x y d : ℝ) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y) :
    f (x-d) + f (y+d) ≤ f x + f y := by
  by_cases hzero : d = 0
  · simp [hzero]
  have hdpos : 0 < d := lt_of_le_of_ne hd (Ne.symm hzero)
  have hden : 0 < y-x+2*d := by linarith
  let a := (y-x+d)/(y-x+2*d)
  let b := d/(y-x+2*d)
  have ha : 0 ≤ a := div_nonneg (by linarith) hden.le
  have hb : 0 ≤ b := div_nonneg hd hden.le
  have hab : a+b=1 := by
    dsimp [a,b]
    rw [← add_div]
    rw [show (y-x+d)+d=y-x+2*d by ring]
    exact div_self (ne_of_gt hden)
  have hx : 0 ≤ x-d := by linarith
  have hy : 0 ≤ y+d := by linarith
  have h := concave_pair_mix f hf (x-d) (y+d) a b hx hy ha hb hab
  have e₁ : a*(x-d)+b*(y+d)=x := by
    dsimp [a,b]
    calc
      _ = ((y-x+d)*(x-d)+d*(y+d))/(y-x+2*d) := by ring
      _ = x := (div_eq_iff (ne_of_gt hden)).2 (by ring)
  have e₂ : b*(x-d)+a*(y+d)=y := by
    dsimp [a,b]
    calc
      _ = (d*(x-d)+(y-x+d)*(y+d))/(y-x+2*d) := by ring
      _ = y := (div_eq_iff (ne_of_gt hden)).2 (by ring)
  simpa only [e₁,e₂] using h

theorem rpow_concentration (p x y d : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1)
    (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y) :
    (x-d)^p + (y+d)^p ≤ x^p + y^p :=
  concave_concentration (fun t : ℝ => t^p) (Real.concaveOn_rpow hp hp1) x y d hd hdx hxy

/-- The physical rank mass of this two-bin move is unchanged. -/
theorem concentration_rank_mass (x y d : ℝ) : (x-d)+(y+d)=x+y := by ring

/-- The same move preserves unused rank capacity, for any fixed stock. -/
theorem concentration_rank_deficit (capacity x y d : ℝ) :
    capacity-((x-d)+(y+d))=capacity-(x+y) := by ring

/-- Pair concentration is already a sufficient admission-preserving compiler rule. -/
theorem admission_of_concentration (p x y d rest budget : ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y)
    (hold : rest+x^p+y^p < budget) :
    rest+(x-d)^p+(y+d)^p < budget := by
  have h := rpow_concentration p x y d hp hp1 hd hdx hxy
  linarith

/-- Uniform scaling preserves a profitable exchange, including cover normalizers. -/
theorem scaled_rpow_concentration (p x y d factor : ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y)
    (hfactor : 0 ≤ factor) :
    factor*((x-d)^p+(y+d)^p) ≤ factor*(x^p+y^p) :=
  mul_le_mul_of_nonneg_left (rpow_concentration p x y d hp hp1 hd hdx hxy) hfactor

/-- The cost comparison in the project's normalized rank coordinates. -/
theorem normalized_rpow_concentration (p x y d dimension : ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : 0 ≤ d) (hdx : d ≤ x) (hxy : x ≤ y)
    (hm : 0 < dimension) :
    ((x-d)/dimension)^p+((y+d)/dimension)^p ≤
      (x/dimension)^p+(y/dimension)^p := by
  have h := rpow_concentration p (x/dimension) (y/dimension) (d/dimension)
    hp hp1 (div_nonneg hd hm.le) (div_le_div_of_nonneg_right hdx hm.le)
    (div_le_div_of_nonneg_right hxy hm.le)
  simpa only [sub_div,add_div] using h

/-- Any finite batch is sound from the individually checkable move contracts. -/
theorem batch_rpow_concentration (s : Finset ι) (p : ℝ) (a b d : ι → ℝ)
    (hp : 0 ≤ p) (hp1 : p ≤ 1) (hd : ∀ i ∈ s, 0 ≤ d i)
    (hda : ∀ i ∈ s, d i ≤ a i) (hab : ∀ i ∈ s, a i ≤ b i) :
    (∑ i ∈ s, ((a i-d i)^p+(b i+d i)^p)) ≤
      ∑ i ∈ s, ((a i)^p+(b i)^p) := by
  exact Finset.sum_le_sum fun i hi =>
    rpow_concentration p (a i) (b i) (d i) hp hp1 (hd i hi) (hda i hi) (hab i hi)

theorem admission_of_batch_concentration (s : Finset ι) (p : ℝ) (a b d : ι → ℝ)
    (rest budget : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1)
    (hd : ∀ i ∈ s, 0 ≤ d i) (hda : ∀ i ∈ s, d i ≤ a i)
    (hab : ∀ i ∈ s, a i ≤ b i)
    (hold : rest+(∑ i ∈ s, ((a i)^p+(b i)^p)) < budget) :
    rest+(∑ i ∈ s, ((a i-d i)^p+(b i+d i)^p)) < budget := by
  have h := batch_rpow_concentration s p a b d hp hp1 hd hda hab
  linarith

end IntegerMultBounds.MomentTransfer
