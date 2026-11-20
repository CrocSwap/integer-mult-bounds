import Std

namespace PhaseBudget

/-- Numerators of a Gaussian value at one common binary denominator. -/
structure Gauss where
  re : Int
  im : Int
  deriving DecidableEq

/-- Twice the output of the actual C kernel at its first source address.
The caller supplies the partner address to obtain the other output. -/
def twiceC (x y : Gauss) : Gauss :=
  ⟨x.re - x.im + y.re + y.im, x.re + x.im + y.im - y.re⟩

def Fits (m : Int) (x : Gauss) : Prop :=
  -m ≤ x.re ∧ x.re ≤ m ∧ -m ≤ x.im ∧ x.im ≤ m

theorem one_axis_bound {x y : Gauss} {m : Int} (hx : Fits m x)
    (hy : Fits m y) : Fits (4*m) (twiceC x y) := by
  rcases hx with ⟨a,b,c,d⟩
  rcases hy with ⟨e,f,g,h⟩
  simp only [Fits, twiceC]
  omega

/-- Each partner map is the reversal of the indicated selected coordinate.
The bound also permits any sequence of partner maps. -/
def kernels {A : Type} (x : A → Gauss) : List (A → A) → A → Gauss
  | [], a => x a
  | f :: fs, a => kernels (fun i => twiceC (x i) (x (f i))) fs a

theorem kernel_numerators {A : Type} (fs : List (A → A))
    (x : A → Gauss) (m : Int) (hx : ∀ a, Fits m (x a)) :
    ∀ a, Fits ((4:Int)^fs.length * m) (kernels x fs a) := by
  induction fs generalizing x m with
  | nil => simpa [kernels] using hx
  | cons f fs ih =>
    have step := ih (fun i => twiceC (x i) (x (f i))) (4*m)
      (fun i => one_axis_bound (hx i) (hx (f i)))
    simpa [kernels, Int.pow_succ, Int.mul_assoc] using step

/-- Compatibility of the local all-prefix proof with a common physical
format when a previous completed phase has a finer input grid. -/
theorem same_guard (p h m a d : Nat) (had : m+a ≤ d) :
    (p+m)+a ≤ p+d ∧ (h+m)+a+2 ≤ h+d+2 ∧
      (p+m)+(h+m)+2*a+3 ≤ p+h+2*d+3 := by omega

theorem denominator_composition (p : Nat) (bits : List Nat) :
    bits.foldl (· + ·) p = p + bits.sum := by
  induction bits generalizing p with
  | nil => simp
  | cons b bs ih => simp [ih, Nat.add_assoc]

private theorem square_residue (a : Nat) :
    a*a%4 = a%2 := by
  have ha : a%4=0 ∨ a%4=1 ∨ a%4=2 ∨ a%4=3 := by omega
  have mod2 : a%4%2 = a%2 := by omega
  rw [Nat.mul_mod, ← mod2]
  rcases ha with h|h|h|h <;> rw [h] <;> decide

/-- Apply to the absolute values of the two reduced numerators of a nonzero
Gaussian-dyadic Clifford entry. A row with 2^r equal-modulus entries has
squared modulus 2^(-r). No ambient factor is charged for completed siblings. -/
theorem clifford_denominator (a b k r : Nat)
    (reduced : a%2=1 ∨ b%2=1)
    (flat : (a*a+b*b)*2^r = 2^(2*k)) :
    k ≤ (r+1)/2 := by
  by_cases h : k ≤ (r+1)/2
  · exact h
  have hexp : 2*k = (2+(2*k-r-2))+r := by omega
  rw [hexp, Nat.pow_add] at flat
  have hs := Nat.eq_of_mul_eq_mul_right (Nat.pow_pos (by decide : 0<2)) flat
  rw [Nat.pow_add] at hs
  have hzero : (a*a+b*b)%4 = 0 := by
    rw [hs]
    simp
  rw [Nat.add_mod, square_residue, square_residue] at hzero
  omega

#print axioms kernel_numerators
#print axioms same_guard
#print axioms denominator_composition
#print axioms clifford_denominator

end PhaseBudget
