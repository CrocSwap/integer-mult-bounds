import Std

/-!
Exact late-quotient bridge for denominator-cleared integer circuits.
The circuit identity is an explicit component contract. These theorems
prove finite-precision recovery, not a tensor rank or physical network cost.
-/
namespace MatrixParityBridge

def decode (numerator scale modulus : Int) : Int :=
  (numerator % (scale * modulus)) / scale

theorem scaled_residue (x m d : Int) (hd : 0 < d) :
    (d*x) % (d*m) = d*(x % m) := by
  exact Int.mul_emod_mul_of_pos x m hd

theorem scaled_residue_divisible (x m d : Int) (hd : 0 < d) :
    d ∣ (d*x) % (d*m) := by
  rw [scaled_residue x m d hd]
  exact ⟨x % m, rfl⟩

theorem exact_late_decode (x m d : Int) (hd : 0 < d) :
    decode (d*x) d m = x % m := by
  unfold decode
  rw [scaled_residue x m d hd]
  exact Int.mul_ediv_cancel_left _ (by omega)

theorem circuit_contract_late_decode (n x m d : Int) (hd : 0 < d)
    (circuit_correct : n = d*x) : decode n d m = x % m := by
  rw [circuit_correct]
  exact exact_late_decode x m d hd

theorem congruent_late_decode (n x m d : Int) (hd : 0 < d)
    (simulation_correct : n % (d*m) = (d*x) % (d*m)) :
    decode n d m = x % m := by
  unfold decode
  rw [simulation_correct, scaled_residue x m d hd]
  exact Int.mul_ediv_cancel_left _ (by omega)

theorem dirty_difference_late_decode (old x m d : Int) (hd : 0 < d) :
    decode ((old+d*x) % (d*m) - old % (d*m)) d m = x % m := by
  unfold decode
  rw [← Int.sub_emod]
  have h : old + d*x - old = d*x := by omega
  rw [h, scaled_residue x m d hd]
  exact Int.mul_ediv_cancel_left _ (by omega)

theorem power_two_positive (s : Nat) : 0 < (2:Int)^s := by
  exact Int.pow_pos (by decide)

theorem dyadic_late_decode (x : Int) (p s : Nat) :
    (((2:Int)^s*x) % ((2:Int)^(s+p))) / (2:Int)^s = x % (2:Int)^p := by
  rw [Int.pow_add]
  exact exact_late_decode x ((2:Int)^p) ((2:Int)^s) (power_two_positive s)

theorem eighth_late_decode (x : Int) (p : Nat) :
    ((8*x) % ((2:Int)^(3+p))) / 8 = x % (2:Int)^p := by
  have h := dyadic_late_decode x p 3
  simpa using h

theorem numerator_eight_mod_two_zero (x : Int) : (8*x) % 2 = 0 := by
  have h : 8*x = (4*x)*2 := by omega
  rw [h, Int.mul_emod_left]

theorem lost_bit_counterexample :
    ((8*0:Int) % 8 = (8*1:Int) % 8) ∧ ((0:Int) % 2 ≠ (1:Int) % 2) := by
  decide

theorem correct_lift_counterexample :
    ((8*0:Int) % 16)/8 = 0 ∧ ((8*1:Int) % 16)/8 = 1 := by
  decide

end MatrixParityBridge
