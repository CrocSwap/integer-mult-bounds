import Mathlib.Data.Complex.Basic
import Mathlib.Data.List.Perm.Basic
import Mathlib.Tactic.Ring

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
