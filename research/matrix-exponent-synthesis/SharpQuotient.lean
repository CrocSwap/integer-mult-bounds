import Std

/-!
Sharp information boundary for numerator-only decoding of denominator-cleared
circuits. No lower bound on arbitrary multiplication algorithms is asserted.
The parameter n means n+1 requested target bits; the smaller residue retains
s+n bits rather than the sufficient s+n+1 bits for scale 2^s.
-/
namespace MatrixParityBridge

theorem target_power_residue (n : Nat) :
    ((2:Int)^n) % ((2:Int)^(n+1)) = (2:Int)^n := by
  have hp : 0 < (2:Int)^n := Int.pow_pos (by decide)
  apply Int.emod_eq_of_lt (by omega)
  rw [Int.pow_succ]
  omega

/-- Zero and 2^n have equal scaled numerator residues one bit below the
needed precision, but different requested n+1-bit output residues. -/
theorem lower_precision_collision (n s : Nat) :
    (((2:Int)^s*0) % ((2:Int)^(s+n)) =
       ((2:Int)^s*(2:Int)^n) % ((2:Int)^(s+n))) ∧
    ((0:Int) % ((2:Int)^(n+1)) ≠ ((2:Int)^n) % ((2:Int)^(n+1))) := by
  constructor
  · rw [← Int.pow_add]
    simp
  · rw [target_power_residue]
    have hp : 0 < (2:Int)^n := Int.pow_pos (by decide)
    simp only [Int.zero_emod]
    omega

/-- No function receiving only that insufficient numerator residue can
recover all the requested low output bits. This is an information collision,
independent of the decoder's implementation or running time. -/
theorem no_decoder_at_lower_precision (n s : Nat) :
    ¬ ∃ f : Int → Int, ∀ x : Int,
      f (((2:Int)^s*x) % ((2:Int)^(s+n))) = x % ((2:Int)^(n+1)) := by
  intro ⟨f,hf⟩
  have hz := hf 0
  have hp := hf ((2:Int)^n)
  have hc := lower_precision_collision n s
  rw [hc.1] at hz
  rw [hp] at hz
  exact hc.2 hz.symm

/-- For the actual N=8AB interface, retaining only p+2 numerator bits is
insufficient for any p>=1 requested product bits. The p+3 lift is sharp for
numerator-only recovery, rather than for multiplication in general. -/
theorem eighth_insufficient_modulus (p : Nat) (hp : 0 < p) :
    ¬ ∃ f : Int → Int, ∀ x : Int,
      f ((8*x) % ((2:Int)^(p+2))) = x % ((2:Int)^p) := by
  have hn : p-1+1=p := by omega
  have he : 3+(p-1)=p+2 := by omega
  have h := no_decoder_at_lower_precision (p-1) 3
  simpa only [show (2:Int)^3=8 from rfl,hn,he] using h

end MatrixParityBridge

#print axioms MatrixParityBridge.lower_precision_collision
#print axioms MatrixParityBridge.no_decoder_at_lower_precision
#print axioms MatrixParityBridge.eighth_insufficient_modulus
