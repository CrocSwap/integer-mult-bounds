import BinaryDelivery
import Mathlib.Algebra.BigOperators.Fin

namespace PhysicalInput
open Finset TernaryCollect QuadraticProduct BinaryDelivery
open scoped BigOperators

theorem radix_step {m} (t : TritWord (m+1)) :
    exponent t = digitValue (t 0) + 3*exponent (Fin.tail t) := by
  rw [exponent, Fin.sum_univ_succ, exponent, Finset.mul_sum]
  simp only [Fin.val_zero,pow_zero,mul_one,Fin.val_succ,pow_succ,Fin.tail]
  congr 1
  exact Finset.sum_congr rfl fun i _ ↦ by ring

theorem digit_lt (t : Trit) : digitValue t < 3 := by
  cases t with
  | none => decide
  | some b => cases b <;> decide

theorem digit_injective : Function.Injective digitValue := by
  intro a b h
  cases a with
  | none => cases b with
            | none => rfl
            | some b => cases b <;> contradiction
  | some a =>
    cases b with
    | none => cases a <;> contradiction
    | some b => cases a <;> cases b <;> first | rfl | contradiction

theorem exponent_lt (m : ℕ) (t : TritWord m) : exponent t < 3^m := by
  induction m with
  | zero => simp [exponent]
  | succ m ih =>
    rw [radix_step, pow_succ]
    have := ih (Fin.tail t)
    have := digit_lt (t 0)
    omega

theorem exponent_injective (m : ℕ) : Function.Injective (exponent (m := m)) := by
  induction m with
  | zero => exact fun x y _ ↦ Subsingleton.elim x y
  | succ m ih =>
    intro x y he
    rw [radix_step,radix_step y] at he
    have hd := congrArg (· % 3) he
    simp only [Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt (digit_lt _)] at hd
    have ht : exponent (Fin.tail x) = exponent (Fin.tail y) := by omega
    rw [← Fin.cons_self_tail x, ← Fin.cons_self_tail y, digit_injective hd, ih ht]

noncomputable def address (m : ℕ) : TritWord m ≃ Fin (3^m) :=
  let f (t : TritWord m) : Fin (3^m) := ⟨exponent t, exponent_lt m t⟩
  Equiv.ofBijective f ((Fintype.bijective_iff_injective_and_card f).mpr
    ⟨fun _ _ h ↦ exponent_injective m (congrArg Fin.val h), by simp [TritWord,Trit]⟩)

def small (b : Bool) : Trit := if b then none else some false
def ternary {m} (x : Bits m) : TritWord m := fun i ↦ small (x i)

theorem spread_address {m} (x : Bits m) : exponent (ternary x) = spread x := by
  apply Finset.sum_congr rfl
  intro i _
  cases hx : x i <;> simp [ternary,small,hx,digitValue,value]

theorem ternary_injective (m : ℕ) : Function.Injective (ternary (m := m)) := by
  intro x y h
  funext i
  have hv := congrFun h i
  cases hx : x i <;> cases hy : y i <;> simp_all [ternary,small]

theorem value_record (n : ℕ) (f : Fin n → Bool) :
    binary (List.ofFn f) = ∑ i, value (f i)*2^i.val := by
  induction n with
  | zero => simp [binary]
  | succ n ih =>
    rw [List.ofFn_succ, binary, ih, Fin.sum_univ_succ, Finset.mul_sum]
    simp only [Fin.val_zero,pow_zero,mul_one,Fin.val_succ,pow_succ]
    congr 1
    exact Finset.sum_congr rfl fun i _ ↦ by ring

/-- The admission scan covers the complete physical bit word. It requires
zeros outside the Cantor addresses and exact mask agreement at every live site. -/
def Valid {m} (M : BooleanGauss.Model (Fin m)) (f : Fin (3^m) → Bool) : Prop :=
  (∀ x, f (address m (ternary x)) = mask M x) ∧
  (∀ t, (¬ ∃ x, ternary x = t) → f (address m t) = false)

theorem literal_value {m} (M : BooleanGauss.Model (Fin m)) (f : Fin (3^m) → Bool)
    (h : Valid M f) : binary (List.ofFn f) = operand (mask M) := by
  classical
  rw [value_record, ← (address m).sum_comp]
  let L := Finset.univ.image (ternary (m := m))
  let q (t : TritWord m) := value (f (address m t)) * 2^(address m t).val
  change (∑ t, q t) = _
  have hsub : (∑ t ∈ L, q t) = ∑ t, q t := by
    apply Finset.sum_subset (Finset.subset_univ L)
    intro t _ ht
    have hn : ¬ ∃ x, ternary x = t := by simpa [L] using ht
    simp [q,h.2 t hn,value]
  rw [← hsub, Finset.sum_image (fun x _ y _ e ↦ ternary_injective m e)]
  apply Finset.sum_congr rfl
  intro x _
  change value (f (address m (ternary x))) * 2^exponent (ternary x) = _
  rw [h.1,spread_address]

/-- A finite equality scan verifies an offered affine-quadratic fit.
Only the raw bit streams determine the values in the conclusion. -/
noncomputable def checked {m} (a b : Fin (3^m) → Bool) (A B : BooleanGauss.Model (Fin m)) : Option ℕ := by
  classical
  exact if Valid A a ∧ Valid B b then some (fromGauss A B) else none

theorem checked_product {m} (a b : Fin (3^m) → Bool) (A B : BooleanGauss.Model (Fin m)) {z : ℕ}
    (h : checked a b A B = some z) : z = binary (List.ofFn a) * binary (List.ofFn b) := by
  classical
  rw [checked] at h
  split at h
  next hc =>
    obtain ⟨ha,hb⟩ := hc
    replace h := Option.some.inj h
    rw [← h, literal_value _ _ ha, literal_value _ _ hb]
    exact from_operand_bits _ _ _ _ (fun _ ↦ rfl) (fun _ ↦ rfl)
  next => contradiction

#print axioms address
#print axioms literal_value
#print axioms checked_product
end PhysicalInput
