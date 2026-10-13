import Std
import Init.Data.Rat.Lemmas

/-!
Finite rational moment-envelope and assembly-check interface.
Weighted upper bounds use one explicit positive common denominator. Their
analytic validity, source/profile binding, completeness of assembly rows and
inherited multiplication theorem remain explicit external contracts.
No successful frontier instance is asserted merely by compiling this helper.
-/
namespace FrontierRationalCertificate

structure Data where
  width : Nat
  volume : Nat
  weightDenominator : Nat
  weightedRows : List (Nat × Nat)
  assemblySlacks : List Rat
  expectedAssemblyRows : Nat
  kappa : Rat
  latestKappa : Rat

def momentNumerator (c : Data) : Nat :=
  (c.weightedRows.map fun row => row.1*row.2).sum

def momentUpper (c : Data) : Rat :=
  Rat.divInt (momentNumerator c : Int) (c.weightDenominator*c.width*c.volume : Nat)

def check (c : Data) : Bool :=
  decide (0<c.width ∧ 0<c.volume ∧ 0<c.weightDenominator) &&
  decide (momentUpper c < 1) &&
  c.assemblySlacks.all (fun slack => decide (0<slack)) &&
  decide (c.assemblySlacks.length=c.expectedAssemblyRows ∧ 0<c.expectedAssemblyRows) &&
  decide (0<c.kappa ∧ c.latestKappa<c.kappa)

/-- Every finite inequality is checked in the kernel; the declared row count
prevents a truncated assembly list from passing its own completeness contract. -/
theorem check_sound (c : Data) (h : check c = true) :
    (0<c.width ∧ 0<c.volume ∧ 0<c.weightDenominator) ∧
    momentUpper c < 1 ∧
    (∀ slack ∈ c.assemblySlacks, 0<slack) ∧
    (c.assemblySlacks.length=c.expectedAssemblyRows ∧ 0<c.expectedAssemblyRows) ∧
    (0<c.kappa ∧ c.latestKappa<c.kappa) := by
  simp only [check,Bool.and_eq_true,List.all_eq_true,decide_eq_true_eq] at h
  exact ⟨h.1.1.1.1,h.1.1.1.2,h.1.1.2,h.1.2,h.2⟩

/-- Ordinary enclosure contract: when a rational modeled moment is bounded
by the checked rational envelope, its strict target follows. -/
theorem rational_enclosed_moment (c : Data) (h : check c = true)
    (moment : Rat) (henclosure : moment ≤ momentUpper c) : moment < 1 := by
  have hu := (check_sound c h).2.1
  apply Rat.lt_of_le_of_ne (Rat.le_trans henclosure (Rat.le_of_lt hu))
  intro heq
  rw [heq] at henclosure
  exact (Rat.not_le.mpr hu) henclosure

/-- The exact analytic interface can be specialized to an ordered real model.
Its enclosure and rational embedding laws are ordinary explicit hypotheses,
not new project axioms or a formalization of inherited analytic lemmas. -/
theorem analytic_enclosure_contract {M : Type} (le lt : M → M → Prop)
    (embed : Rat → M)
    (hstrict : ∀ a b : Rat, a<b → lt (embed a) (embed b))
    (htrans : ∀ a b d : M, le a b → lt b d → lt a d)
    (c : Data) (h : check c = true) (moment : M)
    (henclosure : le moment (embed (momentUpper c))) :
    lt moment (embed 1) := by
  exact htrans _ _ _ henclosure (hstrict _ _ ((check_sound c h).2.1))

/-- A successful checked instance would give an observable rational frontier
comparison; this helper does not manufacture such an instance. -/
theorem checked_frontier_strict (c : Data) (h : check c = true) :
    c.latestKappa < c.kappa :=
  (check_sound c h).2.2.2.2.2

end FrontierRationalCertificate

#print axioms FrontierRationalCertificate.check_sound
#print axioms FrontierRationalCertificate.rational_enclosed_moment
#print axioms FrontierRationalCertificate.analytic_enclosure_contract
#print axioms FrontierRationalCertificate.checked_frontier_strict
