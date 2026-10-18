import Mathlib.Data.Complex.Basic
import Mathlib.Data.List.Perm.Basic
import Mathlib.LinearAlgebra.Pi
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Abel

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
