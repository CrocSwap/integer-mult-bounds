/-
XBalA (lane LEAN-XBAL, Nov 18).  HOSTDIR accounting, kernel-only, minimal event-list model of fold().
Charts C with heights h; paid moves M (src,dst charts; Δh = h dst - h src); publics P (born at ini, finish at fin;
public climb c_p = h fin - h ini); owned registers O (INIT chart, CLEAR chart).
`Flow` = chart conservation with owned: moves in + born + owned INIT = moves out + finishing + owned CLEAR (every chart).
A = ascent mass, D = descent mass, Σc = public climb, X = Σ|Δh| - Σc = A + D - Σc, W = Σ_owned (h_CLEAR - h_INIT).
  XBal.telescope : A - D - Σc = W                       (hyp: Flow)
  XBal.X_eq      : X = 2D + W                           (hyp: Flow)
  XBal.X_ge      : 0 ≤ W → 2D ≤ X                       (hyp: Flow)
  XBal.W_zero_X  : W = 0 (e.g. P-BAL, no owned) → X = 2D
-/
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Fintype.Card
import Mathlib.Algebra.Order.Group.Abs

namespace XBal
open Finset

variable {C M P O : Type} [Fintype C] [DecidableEq C] [Fintype M] [Fintype P] [Fintype O]

structure Model (C M P O : Type) where
  h : C → ℤ
  src : M → C
  dst : M → C
  ini : P → C
  fin : P → C
  oinit : O → C
  oclear : O → C

namespace Model
variable (G : Model C M P O)

def delta (m : M) : ℤ := G.h (G.dst m) - G.h (G.src m)
def A : ℤ := ∑ m, max (G.delta m) 0
def D : ℤ := ∑ m, max (-G.delta m) 0
def absMass : ℤ := ∑ m, |G.delta m|
def climb : ℤ := ∑ p, (G.h (G.fin p) - G.h (G.ini p))
def W : ℤ := ∑ o, (G.h (G.oclear o) - G.h (G.oinit o))
/-- paid mass net of public climb -/
def X : ℤ := G.absMass - G.climb

def cnt {α : Type} [Fintype α] (f : α → C) (c : C) : ℤ := ((univ.filter fun a => f a = c).card : ℤ)

def Flow : Prop := ∀ c, cnt G.dst c + cnt G.ini c + cnt G.oinit c = cnt G.src c + cnt G.fin c + cnt G.oclear c

theorem sum_fib {α : Type} [Fintype α] (f : α → C) (h : C → ℤ) :
    ∑ a, h (f a) = ∑ c, cnt f c * h c := by
  rw [← Finset.sum_fiberwise Finset.univ f (fun a => h (f a))]
  refine Finset.sum_congr rfl fun c _ => ?_
  have : ∑ a ∈ univ.filter (fun a => f a = c), h (f a) = ∑ a ∈ univ.filter (fun a => f a = c), h c :=
    Finset.sum_congr rfl fun a ha => by rw [(Finset.mem_filter.1 ha).2]
  rw [this, Finset.sum_const, nsmul_eq_mul]; simp [cnt]

theorem A_sub_D : G.A - G.D = ∑ m, G.delta m := by
  unfold A D; rw [← Finset.sum_sub_distrib]
  exact Finset.sum_congr rfl fun m _ => by rcases le_total (G.delta m) 0 with h | h <;> simp [max_eq_left, max_eq_right, h]

theorem A_add_D : G.A + G.D = G.absMass := by
  unfold A D absMass; rw [← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun m _ => by rcases le_total (G.delta m) 0 with h | h <;> simp [abs_of_nonpos, abs_of_nonneg, h]

theorem D_nonneg : 0 ≤ G.D := Finset.sum_nonneg fun m _ => le_max_right _ _

/-- telescoping identity -/
theorem telescope (hF : G.Flow) : G.A - G.D - G.climb = G.W := by
  have e1 : G.A - G.D = ∑ c, (cnt G.dst c - cnt G.src c) * G.h c := by
    rw [A_sub_D]; unfold delta
    simp only [Finset.sum_sub_distrib]; rw [sum_fib G.dst G.h, sum_fib G.src G.h, ← Finset.sum_sub_distrib]
    exact Finset.sum_congr rfl fun c _ => by ring
  have e2 : G.climb = ∑ c, (cnt G.fin c - cnt G.ini c) * G.h c := by
    unfold climb; simp only [Finset.sum_sub_distrib]; rw [sum_fib G.fin G.h, sum_fib G.ini G.h, ← Finset.sum_sub_distrib]
    exact Finset.sum_congr rfl fun c _ => by ring
  have e3 : G.W = ∑ c, (cnt G.oclear c - cnt G.oinit c) * G.h c := by
    unfold W; simp only [Finset.sum_sub_distrib]; rw [sum_fib G.oclear G.h, sum_fib G.oinit G.h, ← Finset.sum_sub_distrib]
    exact Finset.sum_congr rfl fun c _ => by ring
  rw [e1, e2, e3, ← Finset.sum_sub_distrib]
  refine Finset.sum_congr rfl fun c _ => ?_
  have := hF c
  have : cnt G.dst c - cnt G.src c - (cnt G.fin c - cnt G.ini c) = cnt G.oclear c - cnt G.oinit c := by linarith
  rw [← this]; ring

theorem X_eq (hF : G.Flow) : G.X = 2 * G.D + G.W := by
  have := telescope G hF; have := A_add_D G; unfold X; linarith

theorem X_ge (hF : G.Flow) (hW : 0 ≤ G.W) : 2 * G.D ≤ G.X := by
  have := X_eq G hF; linarith

theorem W_zero_X (hF : G.Flow) (hW : G.W = 0) : G.X = 2 * G.D := by
  have := X_eq G hF; linarith

/-- with no owned registers (pure P-BAL) -/
theorem X_eq_noOwned [IsEmpty O] (hF : G.Flow) : G.X = 2 * G.D := W_zero_X G hF (by simp [W])

end Model
end XBal
