import Std

/-!
A Nat encodes a row of coefficients over F₂. `evalRow n u r` interprets
the first n coefficients against an entirely arbitrary Boolean input u.
There is no restriction on correlations among the inputs. Applying this
theorem pointwise also permits arbitrary Boolean-valued payload functions.
-/
namespace LinearReplay

def evalRow : Nat → (Nat → Bool) → Nat → Bool
  | 0, _, _ => false
  | n + 1, u, row => evalRow n u row ^^ (row.testBit n && u n)

@[simp] theorem evalRow_zero (n : Nat) (u : Nat → Bool) : evalRow n u 0 = false := by
  induction n with
  | zero => rfl
  | succ n ih => simp [evalRow, ih]

theorem evalRow_xor (n : Nat) (u : Nat → Bool) (r s : Nat) :
    evalRow n u (r ^^^ s) = (evalRow n u r ^^ evalRow n u s) := by
  induction n with
  | zero => rfl
  | succ n ih =>
      simp only [evalRow, ih, Nat.testBit_xor]
      cases evalRow n u r <;> cases evalRow n u s <;>
        cases r.testBit n <;> cases s.testBit n <;> cases u n <;> rfl

theorem evalRow_basis (n : Nat) (u : Nat → Bool) (i : Nat) :
    evalRow n u (2 ^ i) = if i < n then u i else false := by
  induction n with
  | zero => simp [evalRow]
  | succ n ih =>
      rw [evalRow, ih, Nat.testBit_two_pow]
      by_cases h : i < n
      · have hne : i ≠ n := by omega
        simp [h, hne, Nat.lt_succ_of_lt h]
      · by_cases heq : i = n
        · subst i; simp
        · have hn : ¬ i < n + 1 := by omega
          simp [h, heq, hn]

theorem evalRow_shift_basis (n : Nat) (u : Nat → Bool) (i : Nat) :
    evalRow n u (1 <<< i) = if i < n then u i else false := by
  simpa [Nat.shiftLeft_eq] using evalRow_basis n u i

end LinearReplay
