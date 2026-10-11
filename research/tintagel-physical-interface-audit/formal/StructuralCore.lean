import Std

/- Independent, dependency-free structural proof. No source repository imports.
   This file proves the change-of-frame induction, correlated substitution,
   right-owner bijections, and a finite rank-eight character obstruction.
   It does not formalize the full Clifford construction or a PR390 program. -/
namespace TintagelValidation

def steps {A : Type u} (F : Nat → A → A) : Nat → A → A
  | 0, x => x
  | n+1, x => F n (steps F n x)

/-- A cut equation must hold on the entire joint state. No independence
    or inverse for any individual helper encoding is used. -/
theorem cut_induction {A : Type u}
    (E S G : Nat → A → A)
    (cut : ∀ n x, G n (E n x) = E (n+1) (S n x)) :
    ∀ n x, steps G n (E 0 x) = E n (steps S n x) := by
  intro n
  induction n with
  | zero => intro x; rfl
  | succ n ih =>
    intro x
    simp only [steps, ih, cut]

theorem correlated_cut {A : Type u} {Ω : Type v}
    (E S G : Nat → A → A)
    (cut : ∀ n x, G n (E n x) = E (n+1) (S n x))
    (joint : Ω → A) (n : Nat) (ω : Ω) :
    steps G n (E 0 (joint ω)) = E n (steps S n (joint ω)) :=
  cut_induction E S G cut n (joint ω)

/-- Surjectivity of the INITIAL full frame suffices to cancel it. -/
theorem cancel_initial_frame {A : Type u} (P K E J : A → A)
    (rightInverse : ∀ x, E (J x) = x)
    (normalized : ∀ x, P (E x) = K (E x)) : P = K := by
  funext x
  have h := normalized (J x)
  simpa only [rightInverse] using h

structure GroupLaw (A : Type u) where
  mul : A → A → A
  one : A
  inv : A → A
  assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c)
  mul_one : ∀ a, mul a one = a
  inv_mul : ∀ a, mul (inv a) a = one
  mul_inv : ∀ a, mul a (inv a) = one

/-- g = d*A^-1 is solved uniquely by d = g*A. -/
theorem owner_solution {A : Type u} (H : GroupLaw A) (d g a : A) :
    H.mul d (H.inv a) = g ↔ d = H.mul g a := by
  constructor
  · intro h
    have e := congrArg (fun z => H.mul z a) h
    simpa only [H.assoc, H.inv_mul, H.mul_one] using e
  · intro h
    rw [h, H.assoc, H.mul_inv, H.mul_one]

theorem owner_injective {A : Type u} (H : GroupLaw A) (d e a : A)
    (h : H.mul d (H.inv a) = H.mul e (H.inv a)) : d = e := by
  have k := congrArg (fun z => H.mul z a) h
  simpa only [H.assoc, H.inv_mul, H.mul_one] using k

theorem owner_surjective {A : Type u} (H : GroupLaw A) (g a : A) :
    ∃ d, H.mul d (H.inv a) = g := by
  exact ⟨H.mul g a, (owner_solution H _ g a).mpr rfl⟩

def bit (v i : Nat) : Nat := (v / 2^i) % 2
def weight9 (v : Nat) : Nat := ((List.range 9).map (bit v)).sum
def dot9 (v z : Nat) : Nat :=
  (((List.range 9).map (fun i => bit v i * bit z i)).sum) % 2
def directionalPhase (vs : List Nat) (z : Nat) : Nat :=
  ((vs.map (fun v => dot9 v z)).sum) % 4
def axes9 : List Nat := (List.range 9).map (fun i => 2^i)

/-- Concrete direction lists. Below, Lean proves their orthogonality to q
    and phase arithmetic only. Orthonormality/spanning and operator semantics
    are established separately in the prose and exact Python checker. -/
def q508dirs : List Nat := [2, 505, 501, 493, 477, 445, 381, 253]
def q499dirs : List Nat := [501, 502, 8, 487, 471, 439, 375, 247]

theorem normals_weight7 : weight9 508 = 7 ∧ weight9 499 = 7 := by decide
theorem residual508_orthogonal :
    ∀ v ∈ q508dirs, dot9 v 508 = 0 := by decide
theorem residual499_orthogonal :
    ∀ v ∈ q499dirs, dot9 v 499 = 0 := by decide
theorem obstruction508 :
    directionalPhase q508dirs 508 = 0 ∧
    directionalPhase axes9 508 = 3 := by decide
theorem obstruction499 :
    directionalPhase q499dirs 499 = 0 ∧
    directionalPhase axes9 499 = 3 := by decide

def gaussI (p : Nat) : Int × Int :=
  match p % 4 with
  | 0 => (1,0)
  | 1 => (0,1)
  | 2 => (-1,0)
  | _ => (0,-1)

theorem rank8_not_common_full508 :
    gaussI (directionalPhase q508dirs 508) ≠
    gaussI (directionalPhase axes9 508) := by decide
theorem rank8_not_common_full499 :
    gaussI (directionalPhase q499dirs 499) ≠
    gaussI (directionalPhase axes9 499) := by decide

theorem b3_idle_ranks_smaller (h : Nat) (hh : 2 ≤ h) :
    4*h+2 < 7*h ∧ 2*h+4 < 7*h ∧ 6 < 7*h ∧
    2*h-2 < 7*h ∧ 4*h-4 < 7*h ∧ h-1 < 7*h := by omega

theorem b3_idle_ranks_positive (h : Nat) (hh : 2 ≤ h) :
    1 ≤ 4*h+2 ∧ 1 ≤ 2*h+4 ∧ 1 ≤ (6 : Nat) ∧
    1 ≤ 2*h-2 ∧ 1 ≤ 4*h-4 ∧ 1 ≤ h-1 := by omega

end TintagelValidation

#print axioms TintagelValidation.cut_induction
#print axioms TintagelValidation.correlated_cut
#print axioms TintagelValidation.cancel_initial_frame
#print axioms TintagelValidation.owner_solution
#print axioms TintagelValidation.owner_injective
#print axioms TintagelValidation.owner_surjective
#print axioms TintagelValidation.rank8_not_common_full508
#print axioms TintagelValidation.rank8_not_common_full499
#print axioms TintagelValidation.b3_idle_ranks_smaller

#print axioms TintagelValidation.normals_weight7
#print axioms TintagelValidation.residual508_orthogonal
#print axioms TintagelValidation.residual499_orthogonal
#print axioms TintagelValidation.obstruction508
#print axioms TintagelValidation.obstruction499
#print axioms TintagelValidation.b3_idle_ranks_positive
