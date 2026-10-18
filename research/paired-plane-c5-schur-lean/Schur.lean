/- Apache-2.0. Prepared for ywz65 with substantial OpenAI Codex assistance.
   Formal Schur interface from thakrarsagar/PR2484's C5 proof.
   This file does not define matrix rank or formalize the rank-to-pivot bridge. -/
import Std

namespace PairedC5
open Lean.Grind

structure Mat2 (K : Type) where
  a : K
  b : K
  c : K
  d : K
  deriving DecidableEq

variable {K : Type} [CommRing K]

def mul (x y : Mat2 K) : Mat2 K :=
  ⟨x.a*y.a+x.b*y.c, x.a*y.b+x.b*y.d,
   x.c*y.a+x.d*y.c, x.c*y.b+x.d*y.d⟩
def one : Mat2 K := ⟨1,0,0,1⟩
def zero : Mat2 K := ⟨0,0,0,0⟩
def add (x y : Mat2 K) : Mat2 K := ⟨x.a+y.a,x.b+y.b,x.c+y.c,x.d+y.d⟩

theorem mul_assoc (x y z : Mat2 K) : mul (mul x y) z = mul x (mul y z) := by
  cases x; cases y; cases z
  simp only [mul, Mat2.mk.injEq]
  grind

@[simp] theorem mul_one (x : Mat2 K) : mul x one = x := by
  cases x
  simp only [mul, one, Mat2.mk.injEq]
  grind

@[simp] theorem one_mul (x : Mat2 K) : mul one x = x := by
  cases x
  simp only [mul, one, Mat2.mk.injEq]
  grind

@[simp] theorem mul_zero (x : Mat2 K) : mul x zero = zero := by
  cases x
  simp only [mul, zero, Mat2.mk.injEq]
  grind

@[simp] theorem zero_mul (x : Mat2 K) : mul zero x = zero := by
  cases x
  simp only [mul, zero, Mat2.mk.injEq]
  grind

@[simp] theorem add_zero (x : Mat2 K) : add x zero = x := by
  cases x
  simp only [add, zero, Mat2.mk.injEq]
  grind

@[simp] theorem zero_add (x : Mat2 K) : add zero x = x := by
  cases x
  simp only [add, zero, Mat2.mk.injEq]
  grind

/-- The square-block step cannot be replaced by rectangular one-sided inversion. -/
theorem reverse_inverse (x y : Mat2 K) (h : mul x y = one) : mul y x = one := by
  cases x; cases y
  simp only [mul, one, Mat2.mk.injEq] at h ⊢
  grind

theorem cancel_right_zero (x y z : Mat2 K)
    (hinv : mul x y = one) (hzero : mul z y = zero) : z = zero := by
  have rev := reverse_inverse x y hinv
  calc
    z = mul z (mul y x) := by rw [rev, mul_one]
    _ = mul (mul z y) x := (mul_assoc z y x).symm
    _ = zero := by rw [hzero, zero_mul]

abbrev BlockMatrix (K : Type) := Fin 5 → Fin 5 → Mat2 K

/-- Non-neighbouring planes of the orthogonality C5 have forced zero blocks. -/
def Far (i j : Fin 5) : Prop := (i.val+2)%5 = j.val ∨ (j.val+2)%5 = i.val

def Fits (m : BlockMatrix K) : Prop :=
  (∀ i, m i i = one) ∧ (∀ i j, Far i j → m i j = zero)

/-- Schur factorization through the four scalar pivot ports in planes 0 and 2. -/
def FourPivot (m : BlockMatrix K) : Prop :=
  ∀ i j, m i j = add (mul (m i 0) (m 0 j)) (mul (m i 2) (m 2 j))

/-- Exact formalized proposition: no fitting C5 matrix has the normalized
    four-pivot factorization. Ordinary matrix rank is not a hypothesis here. -/
theorem no_four_pivot (hne : (0 : K) ≠ 1) (m : BlockMatrix K)
    (hfit : Fits m) (hf : FourPivot m) : False := by
  rcases hfit with ⟨hd, hz⟩
  have h30 : m 3 0 = zero := hz 3 0 (by unfold Far; decide)
  have h03 : m 0 3 = zero := hz 0 3 (by unfold Far; decide)
  have h42 : m 4 2 = zero := hz 4 2 (by unfold Far; decide)
  have h24 : m 2 4 = zero := hz 2 4 (by unfold Far; decide)
  have h13 : m 1 3 = zero := hz 1 3 (by unfold Far; decide)
  have h14 : m 1 4 = zero := hz 1 4 (by unfold Far; decide)
  have d : mul (m 3 2) (m 2 3) = one := by
    simpa [h30, hd 3] using (hf 3 3).symm
  have e : mul (m 4 0) (m 0 4) = one := by
    simpa [h42, hd 4] using (hf 4 4).symm
  have bd : mul (m 1 2) (m 2 3) = zero := by
    simpa [h13, h03] using (hf 1 3).symm
  have be : mul (m 1 0) (m 0 4) = zero := by
    simpa [h14, h24] using (hf 1 4).symm
  have bc : m 1 2 = zero := cancel_right_zero _ _ _ d bd
  have ba : m 1 0 = zero := cancel_right_zero _ _ _ e be
  have contradiction : (one : Mat2 K) = zero := by
    simpa [hd 1, ba, bc] using hf 1 1
  have scalar : (1 : K) = 0 := congrArg Mat2.a contradiction
  exact hne scalar.symm

/-- Concrete integer witness after freeing the B-D pair. Planes A,E share
    two coordinates; B,C,D share the other two. -/
def group (i : Fin 5) : Bool := i.val == 0 || i.val == 4

def relaxed : BlockMatrix Int := fun i j => if group i == group j then one else zero

theorem relaxed_diagonal : ∀ i, relaxed i i = one := by decide

theorem relaxed_remaining_zeros : ∀ i j, Far i j →
    ¬ ((i = 1 ∧ j = 3) ∨ (i = 3 ∧ j = 1)) → relaxed i j = zero := by unfold Far; decide

theorem relaxed_four_pivot : FourPivot relaxed := by unfold FourPivot; decide

theorem relaxed_missing_edge : relaxed 1 3 = one ∧ relaxed 1 3 ≠ zero := by decide

end PairedC5

#print axioms PairedC5.reverse_inverse
#print axioms PairedC5.no_four_pivot
#print axioms PairedC5.relaxed_diagonal
#print axioms PairedC5.relaxed_remaining_zeros
#print axioms PairedC5.relaxed_four_pivot
#print axioms PairedC5.relaxed_missing_edge
