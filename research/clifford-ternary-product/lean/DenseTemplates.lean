import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Data.Int.Basic
import Mathlib.Tactic.Ring

namespace DenseTemplates

open Finset
open scoped BigOperators

/-- The running window just before limb i is processed. The supplied digit
sequence has value zero outside the physical input. -/
def window (a : ℤ → ℕ) (count : ℕ) (i : ℤ) : ℕ :=
  ∑ j ∈ range count, a (i - j - 1)

theorem window_slide (a : ℤ → ℕ) (count : ℕ) (i : ℤ) :
    window a count (i+1) + a (i-count) = window a count i + a i := by
  cases count with
  | zero => simp [window]
  | succ c =>
    unfold window
    rw [sum_range_succ' (fun j : ℕ ↦ a (i+1-j-1)),
        sum_range_succ (fun j : ℕ ↦ a (i-j-1))]
    have h : (∑ j ∈ range c, a (i+1-(↑(j+1:ℕ):ℤ)-1)) =
        ∑ j ∈ range c, a (i-j-1) := by
      apply sum_congr rfl
      intro j _
      congr 1
      omega
    rw [h]
    have hu : i - (↑(c+1:ℕ):ℤ) = i-c-1 := by omega
    simp only [Nat.cast_zero, sub_zero, add_sub_cancel_right, hu]
    omega

def geometric (D count : ℕ) : ℕ := ∑ j ∈ range count, D^j
def inputValue (a : ℤ → ℕ) (D L : ℕ) : ℕ := ∑ i ∈ range L, a i * D^i

/-- These are the mathematical values of the current running word, outgoing
carry, and the output limbs already written. -/
structure State where
  running : ℕ
  carry : ℕ
  written : ℕ

def step (D i incoming outgoing : ℕ) (s : State) : State :=
  let w := s.running + incoming - outgoing
  let v := s.carry + w
  ⟨w, v / D, s.written + (v % D) * D^i⟩

def run (a : ℤ → ℕ) (D count : ℕ) : ℕ → State
  | 0 => ⟨0, 0, 0⟩
  | i+1 => step D i (a i) (a ((i:ℤ)-count)) (run a D count i)

theorem run_window (a : ℤ → ℕ) (D count i : ℕ)
    (hleft : ∀ z < 0, a z = 0) :
    (run a D count i).running = window a count i := by
  induction i with
  | zero =>
    simp only [run, Nat.cast_zero, window]
    symm
    exact sum_eq_zero fun j _ ↦ hleft _ (by omega)
  | succ i ih =>
    simp only [run, step, ih]
    have h := window_slide a count (i:ℤ)
    push_cast
    omega

theorem window_bound (a : ℤ → ℕ) (M count : ℕ) (i : ℤ)
    (ha : ∀ z, a z ≤ M) : window a count i ≤ count*M := by
  induction count with
  | zero => simp [window]
  | succ c ih =>
    simpa [window, sum_range_succ, Nat.succ_mul] using Nat.add_le_add ih (ha (i-c-1))

/-- The outgoing carry is less than the number of repeated copies. -/
theorem register_bounds (a : ℤ → ℕ) (D count i : ℕ) (hD : 0 < D) (hc : 0 < count)
    (ha : ∀ z, a z < D) (hleft : ∀ z < 0, a z = 0) :
    (run a D count i).running ≤ count*(D-1) ∧ (run a D count i).carry < count := by
  have bound (k : ℤ) : window a count k ≤ count*(D-1) :=
    window_bound a (D-1) count k fun z ↦ by have := ha z; omega
  constructor
  · rw [run_window a D count i hleft]
    exact bound i
  · induction i with
    | zero => simpa [run] using hc
    | succ i ih =>
      simp only [run, step]
      apply (Nat.div_lt_iff_lt_mul hD).mpr
      rw [run_window a D count i hleft]
      have slide := window_slide a count (i:ℤ)
      have hb := bound ((i:ℤ)+1)
      have h : count*(D-1)+count = count*D := by
        calc
          _ = count*((D-1)+1) := by rw [Nat.mul_add, Nat.mul_one]
          _ = _ := by congr 1; omega
      omega

theorem run_value (a : ℤ → ℕ) (D count i : ℕ)
    (hleft : ∀ z < 0, a z = 0) :
    (run a D count i).written + (run a D count i).carry * D^i =
      ∑ j ∈ range i, window a count ((j:ℤ)+1) * D^j := by
  induction i with
  | zero => simp [run]
  | succ i ih =>
    let s := run a D count i
    let w := window a count ((i:ℤ)+1)
    have hw : s.running + a i - a ((i:ℤ)-count) = w := by
      dsimp [s,w]
      rw [run_window a D count i hleft]
      have h := window_slide a count (i:ℤ)
      omega
    rw [sum_range_succ]
    change (step D i _ _ s).written + (step D i _ _ s).carry*D^(i+1) = _
    simp only [step, hw, pow_succ]
    calc
      _ = s.written + ((s.carry+w)%D + D*((s.carry+w)/D))*D^i := by ring
      _ = s.written + (s.carry+w)*D^i := by rw [Nat.mod_add_div]
      _ = (s.written+s.carry*D^i) + w*D^i := by ring
      _ = _ := by rw [show s.written+s.carry*D^i = _ from ih]

/-- One fixed delayed copy contributes its full value shifted by j limbs. -/
theorem shift_sum (a : ℤ → ℕ) (D L j M : ℕ) (hM : j+L ≤ M)
    (hleft : ∀ z < 0, a z = 0) (hright : ∀ z, (L:ℤ) ≤ z → a z = 0) :
    (∑ i ∈ range M, a ((i:ℤ)-j) * D^i) = inputValue a D L * D^j := by
  obtain ⟨r, rfl⟩ := Nat.exists_eq_add_of_le hM
  rw [Nat.add_assoc, sum_range_add]
  have hs : (∑ i ∈ range j, a ((i:ℤ)-j) * D^i) = 0 := by
    apply sum_eq_zero
    intro i hi
    rw [hleft _ (by have := mem_range.mp hi; omega), zero_mul]
  rw [hs, zero_add, sum_range_add]
  have ht : (∑ i ∈ range r, a ((↑(j+(L+i):ℕ):ℤ)-j) * D^(j+(L+i))) = 0 := by
    apply sum_eq_zero
    intro i _
    rw [hright _ (by omega), zero_mul]
  rw [ht, add_zero]
  unfold inputValue
  rw [sum_mul]
  apply sum_congr rfl
  intro i _
  have h : (↑(j+i:ℕ):ℤ)-j = i := by omega
  rw [h, pow_add]
  ring

theorem window_sum (a : ℤ → ℕ) (D L count : ℕ)
    (hleft : ∀ z < 0, a z = 0) (hright : ∀ z, (L:ℤ) ≤ z → a z = 0) :
    (∑ i ∈ range (L+count-1), window a count ((i:ℤ)+1) * D^i) =
      inputValue a D L * geometric D count := by
  unfold window geometric
  simp_rw [sum_mul]
  rw [sum_comm, mul_sum]
  apply sum_congr rfl
  intro j hj
  have h : ∀ i : ℕ, (i:ℤ)+1-j-1 = i-j := by intro i; omega
  simp_rw [h]
  exact shift_sum a D L j _ (by have := mem_range.mp hj; omega) hleft hright

/-- Append the final outgoing carry after the last written limb. -/
theorem complete_window (a : ℤ → ℕ) (D L count : ℕ)
    (hleft : ∀ z < 0, a z = 0) (hright : ∀ z, (L:ℤ) ≤ z → a z = 0) :
    let i := L+count-1
    (run a D count i).written + (run a D count i).carry * D^i =
      inputValue a D L * geometric D count :=
  (run_value a D count _ hleft).trans (window_sum a D L count hleft hright)

theorem digit_preview (x D L : ℕ) :
    (∑ i ∈ range L, (x / D^i % D) * D^i) + (x / D^L) * D^L = x := by
  induction L with
  | zero => simp
  | succ L ih =>
    rw [sum_range_succ, pow_succ, ← Nat.div_div_eq_div_mul]
    calc
      _ = (∑ i ∈ range L, (x / D^i % D) * D^i) +
        ((x / D^L % D) + D * (x / D^L / D)) * D^L := by ring
      _ = x := by rw [Nat.mod_add_div]; exact ih

/-- Read one zero-padded binary limb. The literal implementation copies the
bits of this interval to a short word before it updates the window. -/
def bitLimb (x u L : ℕ) (z : ℤ) : ℕ :=
  if 0 ≤ z ∧ z < L then (x >>> (u*z.toNat)) &&& (2^u-1) else 0

theorem limb_value (x u L : ℕ) (hx : x < (2^u)^L) :
    inputValue (bitLimb x u L) (2^u) L = x := by
  unfold inputValue
  calc
    _ = ∑ i ∈ range L, (x / (2^u)^i % (2^u)) * (2^u)^i := by
      apply sum_congr rfl
      intro i hi
      have h : 0 ≤ (i:ℤ) ∧ (i:ℤ) < L := by have := mem_range.mp hi; omega
      simp [bitLimb, h, Nat.shiftRight_eq_div_pow, Nat.and_two_pow_sub_one_eq_mod, pow_mul]
    _ = x := by
      have h := digit_preview x (2^u) L
      simpa [Nat.div_eq_of_lt hx] using h

theorem actual_step (u i incoming outgoing : ℕ) (s : State) :
    let w := s.running + incoming - outgoing
    let v := s.carry + w
    step (2^u) i incoming outgoing s =
       ⟨w, v >>> u, s.written + (v &&& (2^u-1))*(2^u)^i⟩ := by
  simp [step, Nat.shiftRight_eq_div_pow]

/-- The loop returns the emitted limbs and then the outgoing carry. -/
def windowResult (x u count L : ℕ) : ℕ :=
  let i := L+count-1
  let s := run (bitLimb x u L) (2^u) count i
  s.written + s.carry*(2^u)^i

theorem full_binary_window (x u count L : ℕ) (hx : x < (2^u)^L) :
    windowResult x u count L = x * geometric (2^u) count := by
  unfold windowResult
  rw [complete_window, limb_value x u L hx]
  · intro z hz
    simp [bitLimb, not_le.mpr hz]
  · intro z hz
    simp [bitLimb, not_lt.mpr hz]

/-- Choose the number of limbs of a trimmed word of value x. The zero word
has one bit. Arbitrary extra zero limbs are covered by full_binary_window. -/
def repeatWord (x u count : ℕ) : ℕ := windowResult x u count (x.log2/u+1)

theorem repeat_word_value (x u count : ℕ) (hu : 0 < u) :
    repeatWord x u count = x * geometric (2^u) count := by
  apply full_binary_window
  rw [← pow_mul]
  rcases Nat.eq_zero_or_pos x with rfl | hx
  · exact Nat.two_pow_pos _
  apply (Nat.log2_lt (by omega)).mp
  have hr := Nat.mod_lt x.log2 hu
  have hd := Nat.mod_add_div x.log2 u
  rw [Nat.mul_add, Nat.mul_one]
  omega

theorem geometric_succ (D c : ℕ) :
    geometric D (c+1) = 1 + D*geometric D c := by
  unfold geometric
  rw [sum_range_succ', mul_sum]
  simp only [pow_zero]
  rw [add_comm]
  congr 1
  apply sum_congr rfl
  intro i _
  rw [pow_succ, Nat.mul_comm]

theorem protected_period (D P count : ℕ) (hP : P < D) (signedDefect : ℤ) :
    ((P:ℤ)*(geometric D (count+1):ℤ) + (D:ℤ)*signedDefect) % (D:ℤ) = P := by
  rw [geometric_succ]
  push_cast
  have h : (P:ℤ)*(1+D*(geometric D count:ℤ))+D*signedDefect =
      P+(P*(geometric D count:ℤ)+signedDefect)*D := by ring
  rw [h, Int.add_mul_emod_self_right]
  exact Int.emod_eq_of_lt (by omega) (by exact_mod_cast hP)

theorem protected_binary_template (u P c : ℕ) (hP : P < 2^u)
    (sign defect : ℤ) :
    ((P:ℤ)*(geometric (2^u) (c+1):ℤ) + (2:ℤ)^u*(sign*defect)) %
      ((2:ℤ)^u) = P := by
  simpa using protected_period (2^u) P c hP (sign*defect)

/-- Evaluate the two copies of the template product, the two cross terms,
and the delivered residual product. Each repeatWord runs the sliding loop. -/
def assemble (u c P Q F H e f : ℕ) (s t : ℤ) : ℤ :=
  let rep := fun x ↦ repeatWord x u c
  (rep (rep (P*Q)):ℤ) + s*t*((2:ℤ)^e*(2:ℤ)^f)*(F*H:ℕ) +
      s*(2:ℤ)^e*(rep (F*Q):ℤ) + t*(2:ℤ)^f*(rep (H*P):ℤ)

theorem assembled_signed_product (u c P Q F H e f : ℕ) (hu : 0 < u) (s t : ℤ) :
    let G : ℤ := geometric (2^u) c
    assemble u c P Q F H e f s t =
      ((P:ℤ)*G+s*2^e*F)*((Q:ℤ)*G+t*2^f*H) := by
  dsimp [assemble]
  simp only [repeat_word_value _ _ _ hu, Nat.cast_mul]
  ring

#print axioms complete_window
#print axioms full_binary_window
#print axioms protected_binary_template
#print axioms assembled_signed_product
#print axioms register_bounds

end DenseTemplates
