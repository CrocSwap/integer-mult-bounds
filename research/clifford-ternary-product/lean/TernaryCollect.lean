import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Fin.Tuple.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! A mixed digit has two preimages. Each of the other digits has one.
The change of variables partitions all ordered pairs, including equal pairs. -/
namespace TernaryCollect

open Finset
open scoped BigOperators

abbrev Bits (m : ℕ) := Fin m → Bool
abbrev Trit := Option Bool
abbrev TritWord (m : ℕ) := Fin m → Trit
abbrev Free {m : ℕ} (t : TritWord m) := {i : Fin m // t i = none}

def trit (x y : Bool) : Trit := if x = y then some x else none
def classify {m : ℕ} (x y : Bits m) : TritWord m := fun i ↦ trit (x i) (y i)

def left {m : ℕ} (t : TritWord m) (u : Free t → Bool) : Bits m :=
  fun i ↦ if h : t i = none then u ⟨i,h⟩ else (t i).getD false

def right {m : ℕ} (t : TritWord m) (u : Free t → Bool) : Bits m :=
  fun i ↦ if h : t i = none then !(u ⟨i,h⟩) else (t i).getD false

theorem classify_expand {m : ℕ} (t : TritWord m) (u : Free t → Bool) :
    classify (left t u) (right t u) = t := by
  funext i
  cases hv : t i with
  | none => cases hb : u ⟨i,hv⟩ <;> simp [classify, trit, left, right, hv, hb]
  | some b => simp [classify, trit, left, right, hv]

def freeFrom {m : ℕ} (x y : Bits m) : Free (classify x y) → Bool := fun i ↦ x i.val

theorem expand_input {m : ℕ} (x y : Bits m) :
    left (classify x y) (freeFrom x y) = x ∧ right (classify x y) (freeFrom x y) = y := by
  constructor <;> funext i <;> cases hx : x i <;> cases hy : y i <;>
    simp [left, right, freeFrom, classify, trit, hx, hy]

def flatten {m : ℕ} (z : (t : TritWord m) × (Free t → Bool)) : Bits m × Bits m :=
  (left z.1 z.2, right z.1 z.2)

noncomputable def pairChart (m : ℕ) : ((t : TritWord m) × (Free t → Bool)) ≃ Bits m × Bits m :=
  Equiv.ofBijective flatten (by
    constructor
    · rintro ⟨t,u⟩ ⟨v,w⟩ h
      have e₁ : left t u = left v w := congrArg Prod.fst h
      have e₂ : right t u = right v w := congrArg Prod.snd h
      have tt : t = v := by rw [← classify_expand t u, e₁, e₂, classify_expand]
      subst v
      congr 1
      funext i
      simpa only [left, i.property, ↓reduceDIte] using congrFun e₁ i.val
    · rintro ⟨x,y⟩
      exact ⟨⟨classify x y,freeFrom x y⟩, Prod.ext (expand_input x y).1 (expand_input x y).2⟩)

def value (b : Bool) : ℕ := if b then 1 else 0
def digitValue : Trit → ℕ | none => 1 | some b => 2*value b

def spread {m : ℕ} (a : Bits m) : ℕ := ∑ i, value (a i)*3^i.val
def exponent {m : ℕ} (a : TritWord m) : ℕ := ∑ i, digitValue (a i)*3^i.val

theorem exponent_sum {m : ℕ} (x y : Bits m) :
    exponent (classify x y) = spread x + spread y := by
  unfold exponent spread
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  cases hx : x i <;> cases hy : y i <;> simp [classify,trit,digitValue,value,hx,hy,two_mul]

noncomputable def leaf {m : ℕ} {R : Type*} [AddCommMonoid R] (t : TritWord m)
    (f : Bits m → Bits m → R) := ∑ u : Free t → Bool, f (left t u) (right t u)

/-- Collection holds for arbitrary joint amplitudes and any specified weight. -/
theorem collect_joint {m : ℕ} {R : Type*} [CommSemiring R]
    (f : Bits m → Bits m → R) (w : ℕ → R) :
    (∑ x : Bits m, ∑ y : Bits m, w (spread x+spread y) * f x y) =
      ∑ t : TritWord m, w (exponent t) * leaf t f := by
  classical
  let g (p : Bits m × Bits m) := w (spread p.1+spread p.2) * f p.1 p.2
  change (∑ x : Bits m, ∑ y : Bits m, g (x,y)) = _
  rw [← Fintype.sum_prod_type, ← (pairChart m).sum_comp, Fintype.sum_sigma]
  apply Finset.sum_congr rfl
  intro t _
  rw [leaf, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro u _
  change w (spread (left t u)+spread (right t u)) * f (left t u) (right t u) = _
  rw [← exponent_sum, classify_expand]

noncomputable def operand {m : ℕ} (a : Bits m → Bool) : ℕ :=
  ∑ x, value (a x)*2^(spread x)

noncomputable def coeff {m : ℕ} (a b : Bits m → Bool) (t : TritWord m) : ℕ :=
  leaf t (fun x y ↦ value (a x)*value (b y))

theorem raw_product {m : ℕ} (a b : Bits m → Bool) :
    operand a * operand b = ∑ t : TritWord m, 2^(exponent t)*coeff a b t := by
  rw [operand, operand, Finset.sum_mul]
  simp_rw [Finset.mul_sum]
  unfold coeff
  rw [← collect_joint (fun x y ↦ value (a x)*value (b y)) (fun k ↦ 2^k)]
  apply Finset.sum_congr rfl
  intro x _
  apply Finset.sum_congr rfl
  intro y _
  rw [pow_add]
  ring

def sign (b : Bool) : ℤ := if b then -1 else 1
def gated (support phase : Bool) : ℤ := if support then sign phase else 0

theorem sign_xor (p q : Bool) : sign (p ^^ q) = sign p * sign q := by
  cases p <;> cases q <;> decide

theorem indicator (s p : Bool) :
    2*(value (s && p) : ℤ) = gated s false - gated s p := by
  cases s <;> cases p <;> decide

noncomputable def signedLeaf {m : ℕ} (t : TritWord m) (s q r p : Bits m → Bool) (a b : Bool) : ℤ :=
  leaf t (fun x y ↦ gated (s x && r y) ((a && q x) ^^ (b && p y)))

/-- The four signed leaves use a common pair partition and keep their signs. -/
theorem four_at {m : ℕ} (t : TritWord m) (s q r p : Bits m → Bool) :
    4 * (coeff (fun x ↦ s x && q x) (fun y ↦ r y && p y) t : ℤ) =
      signedLeaf t s q r p false false - signedLeaf t s q r p true false -
      signedLeaf t s q r p false true + signedLeaf t s q r p true true := by
  have each (i j k l : Bool) :
      4*(value (i && j) : ℤ)*(value (k && l) : ℤ) =
      gated (i && k) false - gated (i && k) j - gated (i && k) l + gated (i && k) (j ^^ l) := by
    cases i <;> cases j <;> cases k <;> cases l <;> decide
  simp only [coeff, leaf, signedLeaf, Nat.cast_sum, Nat.cast_mul, Bool.false_and, Bool.true_and,
    Bool.false_xor, Bool.xor_false, Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun u _ ↦ by rw [← mul_assoc]; exact each _ _ _ _

theorem four_product {m : ℕ} (s q r p : Bits m → Bool) :
    4 * ((operand (fun x ↦ s x && q x) * operand (fun y ↦ r y && p y) : ℕ) : ℤ) =
      ∑ t : TritWord m, (2:ℤ)^(exponent t) *
        (signedLeaf t s q r p false false - signedLeaf t s q r p true false -
          signedLeaf t s q r p false true + signedLeaf t s q r p true true) := by
  rw [raw_product, Nat.cast_sum, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro t _
  rw [Nat.cast_mul, Nat.cast_pow, Nat.cast_ofNat, ← four_at]
  ring

#print axioms raw_product
#print axioms collect_joint
#print axioms four_at
#print axioms four_product
end TernaryCollect
