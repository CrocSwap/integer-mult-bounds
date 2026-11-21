import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.Pi
import Mathlib.Tactic.DeriveFintype
/-!
ALL-OR-NOTHING LAW (VALCOUPLE VC.md item 2), abstract version.  Kernel-only.
Ports P (finite).  Fp : Set (P → ZMod 2) is F^perp (the frame-orthogonal code); Lam = L ∩ M_k is
the port set of a 7-dim blocking space.  A = Abar_k (odd support of row k's w), B = Bbar_l.
Named hypotheses:
  H_frame  [COMPUTED, vc3/vc4, all 1152 7-dim blockings]: the only vectors of F^perp supported in
           Lam are 0 and 1_Lam.
  H_FS4    [FS item 4]: the indicator of A ∩ B lies in F^perp.
  H_supp   : A ⊆ Lam (the odd support of a row lies in L ∩ M_k).
Conclusion: A ∩ B = ∅, or (A = Lam and Lam ⊆ B).
The step "so M_k ⊆ N_l" (spans) is not formalised here.
-/
namespace AllOrNothing

variable {P : Type*} [DecidableEq P]

/-- indicator vector of a finset over F2 -/
def ind (S : Finset P) : P → ZMod 2 := fun p => if p ∈ S then 1 else 0

lemma ind_inj {S T : Finset P} (h : ind S = ind T) : S = T := by
  ext p
  have := congrFun h p
  by_cases hs : p ∈ S <;> by_cases ht : p ∈ T <;> simp_all [ind]

theorem all_or_nothing (Fp : Set (P → ZMod 2)) (Lam A B : Finset P)
    (H_frame : ∀ x ∈ Fp, (∀ p, x p ≠ 0 → p ∈ Lam) → x = 0 ∨ x = ind Lam)
    (H_FS4 : ind (A ∩ B) ∈ Fp)
    (H_supp : A ⊆ Lam) :
    A ∩ B = ∅ ∨ (A = Lam ∧ Lam ⊆ B) := by
  have hsup : ∀ p, ind (A ∩ B) p ≠ 0 → p ∈ Lam := by
    intro p hp
    by_contra hn
    apply hp
    have : p ∉ A ∩ B := fun h => hn (H_supp (Finset.mem_inter.1 h).1)
    simp [ind, this]
  rcases H_frame _ H_FS4 hsup with h0 | h1
  · left
    ext p
    have := congrFun h0 p
    by_cases hp : p ∈ A ∩ B <;> simp_all [ind]
  · right
    have e : A ∩ B = Lam := ind_inj h1
    have hAL : Lam ⊆ A := by rw [← e]; exact Finset.inter_subset_left
    have hBL : Lam ⊆ B := by rw [← e]; exact Finset.inter_subset_right
    exact ⟨Finset.Subset.antisymm H_supp hAL, hBL⟩

/-- the row-quantified form: if every row l satisfies H_FS4 against A then the law holds for each l -/
theorem all_or_nothing_rows {κ : Type*} (Fp : Set (P → ZMod 2)) (Lam A : Finset P) (Bs : κ → Finset P)
    (H_frame : ∀ x ∈ Fp, (∀ p, x p ≠ 0 → p ∈ Lam) → x = 0 ∨ x = ind Lam)
    (H_FS4 : ∀ l, ind (A ∩ Bs l) ∈ Fp) (H_supp : A ⊆ Lam) :
    ∀ l, A ∩ Bs l = ∅ ∨ (A = Lam ∧ Lam ⊆ Bs l) :=
  fun l => all_or_nothing Fp Lam A (Bs l) H_frame (H_FS4 l) H_supp

/-! Non-vacuity: P = Fin 4, F^perp = {x | x0 = x1 ∧ x2 = x3}, Lam = {0,1}.  H_frame holds by decide,
   and the conclusion is non-trivial (A = Lam, Lam ⊆ B) for A = {0,1}, B = {0,1,2}; and
   A ∩ B = ∅ for A = {0,1}, B = {2,3}. -/
def Fp0 : Set (Fin 4 → ZMod 2) := {x | x 0 = x 1 ∧ x 2 = x 3}

def Lam0 : Finset (Fin 4) := {0, 1}

lemma frame0 : ∀ x ∈ Fp0, (∀ p, x p ≠ 0 → p ∈ Lam0) → x = 0 ∨ x = ind Lam0 := by
  intro x hx hs
  have h2 : x 2 = 0 := by by_contra h; exact absurd (hs 2 h) (by decide)
  have h3 : x 3 = 0 := by by_contra h; exact absurd (hs 3 h) (by decide)
  obtain ⟨h01, _⟩ := hx
  have key : ∀ a : ZMod 2, a = 0 ∨ a = 1 := by decide
  rcases key (x 0) with h | h
  · left; funext p; fin_cases p <;> simp_all
  · right; funext p; fin_cases p <;> simp_all [ind, Lam0]

example : ({0, 1} : Finset (Fin 4)) ∩ {0, 1, 2} = ∅ ∨
    (({0, 1} : Finset (Fin 4)) = Lam0 ∧ Lam0 ⊆ {0, 1, 2}) :=
  all_or_nothing Fp0 Lam0 {0, 1} {0, 1, 2} frame0
    (by simp only [Fp0, Set.mem_setOf_eq]; decide) (by decide)

/-- the "nothing" branch is also realised, and the conclusion is not always the first disjunct -/
example : ({0, 1} : Finset (Fin 4)) ∩ {2, 3} = ∅ :=
  (all_or_nothing Fp0 Lam0 {0, 1} {2, 3} frame0 (by simp only [Fp0, Set.mem_setOf_eq]; decide)
    (by decide)).resolve_right (by decide)

/-- a middle ("partial") overlap is excluded: A = {0,1}, B = {1} has ind(A∩B) ∉ Fp0 -/
example : ind (({0, 1} : Finset (Fin 4)) ∩ {1}) ∉ Fp0 := by
  simp only [Fp0, Set.mem_setOf_eq]; decide

#print axioms all_or_nothing
#print axioms all_or_nothing_rows

end AllOrNothing
