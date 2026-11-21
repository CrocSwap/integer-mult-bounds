import Mathlib.Data.List.Nodup
import Mathlib.Data.List.FinRange
import Mathlib.Data.Fintype.Pi
import Mathlib.Logic.Equiv.Defs
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/- Each stripe can have a different payload type. A visit reads its current
   slice, writes the entire returned slice, and keeps all other slices. -/
namespace NativeStock.Slices

universe u v w

def write {I : Type u} [DecidableEq I] {A : I → Type v}
    (op : ∀ i, A i → A i) (i : I) (data : ∀ j, A j) : ∀ j, A j :=
  fun j => if j = i then op j (data j) else data j

def visit {I : Type u} [DecidableEq I] {A : I → Type v}
    (op : ∀ i, A i → A i) : List I → (∀ j, A j) → (∀ j, A j)
  | [], data => data
  | i :: later, data => visit op later (write op i data)

theorem visited_slice {I : Type u} [DecidableEq I] {A : I → Type v}
    (op : ∀ i, A i → A i) (order : List I) (once : order.Nodup)
    (data : ∀ j, A j) (j : I) :
    visit op order data j = if j ∈ order then op j (data j) else data j := by
  induction order generalizing data with
  | nil => simp [visit]
  | cons i later ih =>
    have pair := List.nodup_cons.mp once
    rw [visit, ih pair.2]
    by_cases equal : j = i
    · subst j
      simp [pair.1, write]
    · by_cases member : j ∈ later <;> simp [member, equal, write]

theorem complete {I : Type u} [DecidableEq I] {A : I → Type v}
    (op : ∀ i, A i → A i) (order : List I) (once : order.Nodup)
    (covers : ∀ i, i ∈ order) (data : ∀ j, A j) :
    visit op order data = fun i => op i (data i) := by
  funext i
  simpa [covers i] using visited_slice op order once data i

/- The address service returns the same destination permutation for every
   opaque suffix. The input can depend jointly on address and stripe. -/
theorem permutation {I : Type u} [DecidableEq I] {X : Type v} {A : I → Type w}
    (π : X ≃ X) (order : List I) (once : order.Nodup) (covers : ∀ i, i ∈ order)
    (input : X → (i : I) → A i) (address : X) (i : I) :
    visit (fun j (slice : X → A j) x => slice (π.symm x)) order
        (fun j x => input x j) i address = input (π.symm address) i := by
  rw [complete _ order once covers]

def supply {J : Type u} [DecidableEq J] (x : J → Bool) (i : J) (b : Bool) : J → Bool :=
  fun j => if j = i then b else x j

def hadamard {J : Type u} [DecidableEq J] {V : Type v} [Add V] [Sub V]
    (i : J) (f : (J → Bool) → V) (x : J → Bool) : V :=
  let lo := f (supply x i false)
  let hi := f (supply x i true)
  if x i then lo - hi else lo + hi

def word {J : Type u} [DecidableEq J] {V : Type v} [Add V] [Sub V] :
    List J → ((J → Bool) → V) → ((J → Bool) → V)
  | [], f => f
  | i :: later, f => word later (hadamard i f)

theorem supply_join {S J : Type u} [DecidableEq S] [DecidableEq J]
    (s : S → Bool) (x : J → Bool) (i : J) (b : Bool) :
    supply (Sum.elim s x) (.inr i) b = Sum.elim s (supply x i b) := by
  funext j
  cases j <;> simp [supply]

theorem hadamard_join {S J : Type u} [DecidableEq S] [DecidableEq J]
    {V : Type v} [Add V] [Sub V] (s : S → Bool) (i : J)
    (f : (S ⊕ J → Bool) → V) :
    (fun x => hadamard (.inr i) f (Sum.elim s x)) =
      hadamard i (fun x => f (Sum.elim s x)) := by
  funext x
  simp [hadamard, supply_join]

theorem word_join {S J : Type u} [DecidableEq S] [DecidableEq J]
    {V : Type v} [Add V] [Sub V] (s : S → Bool) (indices : List J)
    (f : (S ⊕ J → Bool) → V) :
    (fun x => word (indices.map Sum.inr) f (Sum.elim s x)) =
      word indices (fun x => f (Sum.elim s x)) := by
  induction indices generalizing f with
  | nil => rfl
  | cons i later ih =>
    simp only [List.map_cons, word, ih, hadamard_join]

/- This theorem uses the signed two-input butterfly at every selected
   position. All amendments of earlier stripes are part of `visit`. -/
theorem inplace_hadamard {S J : Type u} [DecidableEq S] [DecidableEq J]
    [DecidableEq (S → Bool)] {V : Type v} [Add V] [Sub V]
    (order : List (S → Bool)) (once : order.Nodup) (covers : ∀ i, i ∈ order)
    (indices : List J) (f : (S ⊕ J → Bool) → V) (s : S → Bool) (x : J → Bool) :
    visit (fun _ => word indices) order (fun t y => f (Sum.elim t y)) s x =
      word (indices.map Sum.inr) f (Sum.elim s x) := by
  rw [complete _ order once covers]
  exact (congrFun (word_join s indices f) x).symm

theorem ordinal_permutation (k : ℕ) {X : Type v} {A : Fin k → Type w}
    (π : X ≃ X) (input : X → (i : Fin k) → A i) (address : X) (i : Fin k) :
    visit (fun j (slice : X → A j) x => slice (π.symm x)) (List.finRange k)
      (fun j x => input x j) i address = input (π.symm address) i :=
  permutation π _ (List.nodup_finRange _) (fun _ => List.mem_finRange _) input address i

theorem full_spectator_cube {S J : Type u} [Fintype S] [DecidableEq S] [DecidableEq J]
    [DecidableEq (S → Bool)] {V : Type v} [Add V] [Sub V]
    (indices : List J) (f : (S ⊕ J → Bool) → V) (s : S → Bool) (x : J → Bool) :
    visit (fun _ => word indices) (Finset.univ : Finset (S → Bool)).toList
       (fun t y => f (Sum.elim t y)) s x =
      word (indices.map Sum.inr) f (Sum.elim s x) :=
  inplace_hadamard _ (Finset.nodup_toList _) (by simp) indices f s x

/- The private grid has p+d fractional bits. An expanded public-grid
   component has d zero low bits. Both quotients truncate toward zero. -/
theorem parked_public_product (p d : ℕ) (a b c e : ℤ) :
    let g := (2 : ℤ) ^ d
    let den := (2 : ℤ) ^ (p + 2*d)
    (((g*a)*(g*c) - (g*b)*(g*e)).tdiv den,
     ((g*a)*(g*e) + (g*b)*(g*c)).tdiv den) =
    ((a*c-b*e).tdiv (2^p), (a*e+b*c).tdiv (2^p)) := by
  dsimp only
  have split : (2 : ℤ)^(p+2*d) = (2^d * 2^d) * 2^p := by
    rw [show 2*d = d+d by omega, pow_add, pow_add]
    ring
  have positive : (0:ℤ) < 2^d * 2^d := by positivity
  rw [split, show (2^d*a)*(2^d*c) - (2^d*b)*(2^d*e) =
       (2^d * 2^d) * (a*c-b*e) by ring,
      show (2^d*a)*(2^d*e) + (2^d*b)*(2^d*c) =
       (2^d * 2^d) * (a*e+b*c) by ring,
      Int.mul_tdiv_mul_of_pos _ _ positive, Int.mul_tdiv_mul_of_pos _ _ positive]

def radixValue (base : ℕ) : List ℕ → ℕ
  | [] => 0
  | a :: rest => a + base * radixValue base rest

def emittedValue (base : ℕ) : List ℕ → ℕ → ℕ
  | [], carry => carry
  | a :: rest, carry =>
      (carry + a) % base + base * emittedValue base rest ((carry + a) / base)

/- The streamed result consumes each recovered coefficient once. It carries
   to the next digit before reading the next coefficient. -/
theorem streamed_carry (base : ℕ) (coefficients : List ℕ) (carry : ℕ) :
    emittedValue base coefficients carry = carry + radixValue base coefficients := by
  induction coefficients generalizing carry with
  | nil => simp [emittedValue, radixValue]
  | cons a rest ih =>
    simp only [emittedValue, radixValue, ih, Nat.mul_add, ← Nat.add_assoc, Nat.mod_add_div]

#print axioms permutation
#print axioms inplace_hadamard
#print axioms ordinal_permutation
#print axioms full_spectator_cube
#print axioms parked_public_product
#print axioms streamed_carry

end NativeStock.Slices
