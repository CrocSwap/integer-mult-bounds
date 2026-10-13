import Std

/-!
Exact completed-child precision accounting for the PR46 complex profile.
This module proves finite certificate accounting. GaussianTensorExecution
separately proves the recursive finite tensor's execution and precision grid.
The physical frame/tape compiler is outside these proofs. No changed exponent.
-/
namespace CommunityPrecision

def ceilHalf (n : Nat) : Nat := (n+1)/2

theorem ceilHalf_subadditive (a b : Nat) :
    ceilHalf (a+b) ≤ ceilHalf a + ceilHalf b := by
  unfold ceilHalf
  omega

theorem ceilHalf_mul_bound (r f : Nat) :
    ceilHalf (r*f) ≤ ceilHalf r * f := by
  induction f with
  | zero => simp [ceilHalf]
  | succ f ih =>
    rw [Nat.mul_succ, Nat.mul_succ]
    exact Nat.le_trans (ceilHalf_subadditive _ _) (Nat.add_le_add_right ih _)

def profile : List (Nat × Nat) :=
  [(1,540572760), (2,336785904), (3,161899920), (4,117097344),
   (5,93051504), (6,64779624), (7,52822224), (8,70243992),
   (9,32150664), (10,50699376), (11,22728888), (12,47580624),
   (13,26208000), (14,44907408), (15,24714144), (16,49192416),
   (17,20815704), (18,52501176), (19,22624056), (20,46348848),
   (21,37759176), (22,58961448), (23,40773096), (24,38781288),
   (25,2208024), (26,3741192), (27,43112160),
   (729,21464352), (756,516232080)]

def rankMass (xs : List (Nat × Nat)) : Nat :=
  (xs.map fun x => x.1*x.2).sum

def precisionCharge (xs : List (Nat × Nat)) (f : Nat) : Nat :=
  (xs.map fun x => ceilHalf (x.1*f)*x.2).sum

def oddMultiplicity (xs : List (Nat × Nat)) : Nat :=
  (xs.map fun x => (x.1%2)*x.2).sum

theorem arbitrary_profile_bound (xs : List (Nat × Nat)) (f : Nat) :
    precisionCharge xs f ≤ precisionCharge xs 1 * f := by
  induction xs with
  | nil => simp [precisionCharge]
  | cons x xs ih =>
    simp only [precisionCharge, List.map_cons, List.sum_cons] at *
    rw [Nat.add_mul]
    have h := Nat.mul_le_mul_right x.2 (ceilHalf_mul_bound x.1 f)
    simpa only [Nat.mul_one, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm]
      using Nat.add_le_add h ih

theorem profile_rank_mass : rankMass profile = 421548223824 := by decide
theorem profile_odd_multiplicity : oddMultiplicity profile = 1142904672 := by decide
theorem profile_precision_charge : precisionCharge profile 1 = 211345564248 := by decide
theorem profile_call_count : (profile.map Prod.snd).sum = 2640757392 := by decide

theorem certified_all_width_bound (f : Nat) :
    precisionCharge profile f ≤ 211345564248 * f := by
  simpa only [profile_precision_charge] using arbitrary_profile_bound profile f

theorem profile_saving : rankMass profile - precisionCharge profile 1 = 210202659576 := by
  rw [profile_rank_mass, profile_precision_charge]

end CommunityPrecision

#print axioms CommunityPrecision.ceilHalf_subadditive
#print axioms CommunityPrecision.ceilHalf_mul_bound
#print axioms CommunityPrecision.arbitrary_profile_bound
#print axioms CommunityPrecision.certified_all_width_bound
