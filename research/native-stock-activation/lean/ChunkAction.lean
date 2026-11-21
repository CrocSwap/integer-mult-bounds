import Mathlib.Data.Matrix.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.Pi
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination

namespace ChunkAction
open Finset Matrix
open scoped BigOperators

variable {ι J : Type} [Fintype ι] [DecidableEq ι] {u : ℕ}

/-- Reduce one matrix coefficient at the true width of a chunk. -/
def reduce {t : ℕ} (h : t ≤ u) : ZMod (3^u) →+* ZMod (3^t) :=
  ZMod.castHom (pow_dvd_pow 3 h) _

/-- A common coefficient acts on all chunks of the same address. -/
def scalar (width : J → ℕ) (lim : ∀ j, width j ≤ u) :
    ZMod (3^u) →+* ((j : J) → ZMod (3^(width j))) :=
  RingHom.pi fun j => reduce (lim j)

variable (width : J → ℕ) (lim : ∀ j, width j ≤ u)
abbrev Word (width : J → ℕ) (ι : Type) := (j : J) → ι → ZMod (3^(width j))

def act (g : Matrix ι ι (ZMod (3^u))) (x : Word width ι) : Word width ι :=
  fun j => (reduce (lim j)).mapMatrix g *ᵥ x j

theorem act_mul (g s : Matrix ι ι (ZMod (3^u))) (x : Word width ι) :
    act width lim (g*s) x = act width lim g (act width lim s x) := by
  funext j
  simp only [act, map_mul, mulVec_mulVec]

theorem act_one (x : Word width ι) : act width lim (1 : Matrix ι ι (ZMod (3^u))) x = x := by
  funext j
  simp [act]

/-- The returned placement of a matched job agrees on every chunk and input. -/
theorem shared_match (p q g s : Matrix ι ι (ZMod (3^u)))
    (match_eq : p*s=s*q) (x : Word width ι) :
    act width lim g (act width lim p (act width lim s x)) =
    act width lim (g*s) (act width lim q x) := by
  rw [← act_mul width lim p s, match_eq, act_mul width lim s q, act_mul width lim g s]

theorem restore (g : (Matrix ι ι (ZMod (3^u)))ˣ) (x : Word width ι) :
    act width lim (↑g⁻¹) (act width lim (↑g) x) = x := by
  rw [← act_mul, g.inv_mul, act_one]

/-- The complete atom still has all of its original addresses. -/
theorem address_count [Fintype J] [DecidableEq J] :
    Fintype.card ((j : J) → ZMod (3^(width j))) = 3^(∑ j,width j) := by
  simp only [Fintype.card_pi, ZMod.card]
  exact prod_pow_eq_pow_sum univ width 3

/-- Two ordinary swaps turn a lower addition into an upper one. The last
sign scan gives the weighted exchange on every component, for every unit. -/
theorem weighted_pair {R : Type} [CommRing R] (a : Rˣ) (x y : R) :
    let t := (↑a⁻¹ : R)
    let y₁ := y+t*x
    let x₂ := x-(a : R)*y₁
    let y₃ := y₁+t*x₂
    (-x₂,y₃) = ((a : R)*y,t*x) := by
  dsimp only
  have h : (↑a : R) * (↑a⁻¹ : R) = 1 := a.mul_inv
  have h' : (↑a⁻¹ : R) * (↑a : R) = 1 := a.inv_mul
  apply Prod.ext
  · linear_combination x*h
  · linear_combination -(y+(↑a⁻¹ : R)*x)*h'

#print axioms shared_match
#print axioms restore
#print axioms address_count
#print axioms weighted_pair
end ChunkAction
