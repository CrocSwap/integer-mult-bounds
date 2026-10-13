import DyadicCertificates

namespace GaussianParity

def scale (k : Int) (z : GInt) : GInt := ⟨k * z.re, k * z.im⟩
def repeatPi : Nat → GInt → GInt
  | 0, z => z
  | n+1, z => mulPi (repeatPi n z)
def repeatI : Nat → GInt → GInt
  | 0, z => z
  | n+1, z => mulI (repeatI n z)

theorem mulPi_square (z : GInt) : mulPi (mulPi z) = scale 2 (mulI z) := by
  apply GInt.ext <;> simp [mulPi, mulI, scale] <;> omega

theorem mulI_scale (k : Int) (z : GInt) : mulI (scale k z) = scale k (mulI z) := by
  apply GInt.ext <;> simp [mulI, scale] <;> grind

theorem scale_mul (k l : Int) (z : GInt) : scale k (scale l z) = scale (k*l) z := by
  apply GInt.ext <;> simp [scale, Int.mul_assoc]

theorem repeatPi_even (q : Nat) (z : GInt) :
    repeatPi (2*q) z = scale ((2 : Int)^q) (repeatI q z) := by
  induction q with
  | zero => simp [repeatPi, repeatI, scale]
  | succ q ih =>
    have hn : 2*(q+1) = 2*q+1+1 := by omega
    rw [hn]
    simp only [repeatPi]
    rw [mulPi_square, ih, mulI_scale, scale_mul]
    simp [repeatI, Int.pow_succ, Int.mul_comm]

end GaussianParity

namespace GaussianParity

def negI (z : GInt) : GInt := ⟨z.im, -z.re⟩
def repeatNegI : Nat → GInt → GInt
  | 0, z => z
  | n+1, z => negI (repeatNegI n z)

theorem mulI_negI (z : GInt) : mulI (negI z) = z := by
  apply GInt.ext <;> simp [mulI, negI]

theorem negI_mulI (z : GInt) : negI (mulI z) = z := by
  apply GInt.ext <;> simp [mulI, negI]

theorem repeatI_commute (q : Nat) (z : GInt) :
    repeatI q (mulI z) = mulI (repeatI q z) := by
  induction q with
  | zero => rfl
  | succ q ih => simp [repeatI, ih]

theorem repeatI_negI_commute (q : Nat) (z : GInt) :
    repeatI q (negI z) = negI (repeatI q z) := by
  induction q with
  | zero => rfl
  | succ q ih =>
    simp only [repeatI, ih]
    rw [mulI_negI, negI_mulI]

theorem repeatI_cancel (q : Nat) (z : GInt) :
    repeatI q (repeatNegI q z) = z := by
  induction q with
  | zero => rfl
  | succ q ih =>
    simp only [repeatNegI, repeatI]
    rw [repeatI_negI_commute, mulI_negI, ih]

theorem mulPi_scale (k : Int) (z : GInt) :
    mulPi (scale k z) = scale k (mulPi z) := by
  apply GInt.ext <;> simp [mulPi, scale] <;> grind

theorem repeatPi_odd (q : Nat) (z : GInt) :
    repeatPi (2*q+1) z = scale ((2 : Int)^q) (mulPi (repeatI q z)) := by
  simp only [repeatPi]
  rw [repeatPi_even, mulPi_scale]

def BinaryDivisible (q : Nat) (z : GInt) : Prop :=
  ∃ w : GInt, scale ((2 : Int)^q) w = z

def PiPowerDivisible (n : Nat) (z : GInt) : Prop :=
  ∃ w : GInt, repeatPi n w = z

/-- The even π-power ideal is exactly the binary-power ideal, with a unit phase. -/
theorem pi_even_ideal (q : Nat) (z : GInt) :
    PiPowerDivisible (2*q) z ↔ BinaryDivisible q z := by
  constructor
  · intro ⟨w, hw⟩
    exact ⟨repeatI q w, (repeatPi_even q w).symm.trans hw⟩
  · intro ⟨w, hw⟩
    refine ⟨repeatNegI q w, ?_⟩
    rw [repeatPi_even, repeatI_cancel]
    exact hw

/-- The odd π-power ideal is the binary-power ideal restricted by one Gaussian parity bit. -/
theorem pi_odd_ideal (q : Nat) (z : GInt) :
    PiPowerDivisible (2*q+1) z ↔
      ∃ w : GInt, scale ((2 : Int)^q) w = z ∧ PiDvd w := by
  constructor
  · intro ⟨v, hv⟩
    refine ⟨mulPi (repeatI q v), ?_, ?_⟩
    · exact (repeatPi_odd q v).symm.trans hv
    · exact (residue_zero_iff _).mp (residue_mulPi _)
  · intro ⟨w, hw, hp⟩
    refine ⟨repeatNegI q (dividePi w), ?_⟩
    rw [repeatPi_odd, repeatI_cancel, (dividePi_exact_iff w).mpr hp]
    exact hw

/-- Coordinate parity is the one-bit constraint in the odd ideal. -/
theorem odd_ideal_parity (q : Nat) (z : GInt)
    (h : PiPowerDivisible (2*q+1) z) :
    ∃ w : GInt, scale ((2 : Int)^q) w = z ∧ w.re % 2 = w.im % 2 := by
  exact (pi_odd_ideal q z).mp h

/-- The next π level is not equivalent to one full binary bit: π itself
has odd coordinates, while every multiple of 2 has even coordinates. -/
theorem pi_not_binary_one :
    PiPowerDivisible 1 ⟨1,1⟩ ∧ ¬ BinaryDivisible 1 ⟨1,1⟩ := by
  constructor
  · exact ⟨⟨1,0⟩, rfl⟩
  · intro ⟨w, hw⟩
    have hr := congrArg GInt.re hw
    simp [scale] at hr
    omega

end GaussianParity

#print axioms GaussianParity.repeatPi_even
#print axioms GaussianParity.pi_even_ideal
#print axioms GaussianParity.pi_odd_ideal
#print axioms GaussianParity.pi_not_binary_one

namespace GaussianParity

/-- Integer numerator converting a π^{-2q} Gaussian rational to a binary grid. -/
theorem even_binary_conversion (q : Nat) (z : GInt) :
    repeatPi (2*q) (repeatNegI q z) = scale ((2 : Int)^q) z := by
  rw [repeatPi_even, repeatI_cancel]

/-- The inverse conversion at an odd level uses one additional π factor.
This certifies the exact fraction identity using cross multiplication only. -/
theorem odd_binary_conversion (q : Nat) (z : GInt) :
    repeatPi (2*q+1) (repeatNegI (q+1) (mulPi z)) =
      scale ((2 : Int)^(q+1)) z := by
  rw [repeatPi_odd]
  simp only [repeatNegI]
  rw [repeatI_negI_commute, repeatI_cancel]
  have hp : mulPi (negI (mulPi z)) = scale 2 z := by
    apply GInt.ext <;> simp only [mulPi, negI, scale] <;> omega
  rw [hp, scale_mul]
  simp [Int.pow_succ]

theorem residue_negI (z : GInt) : residue (negI z) = residue z := by
  simp only [residue, negI]
  omega

theorem repeatNegI_residue (q : Nat) (z : GInt) :
    residue (repeatNegI q z) = residue z := by
  induction q with
  | zero => rfl
  | succ q ih => simp [repeatNegI, residue_negI, ih]

/-- At odd levels the converted binary numerator occupies the proper
index-two lattice re ≡ im (mod 2), rather than all Gaussian integers. -/
theorem odd_binary_numerator_parity (q : Nat) (z : GInt) :
    PiDvd (repeatNegI (q+1) (mulPi z)) := by
  apply (residue_zero_iff _).mp
  rw [repeatNegI_residue, residue_mulPi]

/-- Full denominator upper bound for every π^{-D} Gaussian numerator.
The equation says z/π^D = w/2^ceil(D/2), with no rational arithmetic assumptions. -/
theorem binary_grid_conversion (D : Nat) (z : GInt) :
    ∃ w : GInt, repeatPi D w = scale ((2 : Int)^((D+1)/2)) z := by
  have hp : D % 2 = 0 ∨ D % 2 = 1 := by omega
  rcases hp with he | ho
  · have hd : D = 2*(D/2) := by omega
    have hceil : (D+1)/2 = D/2 := by omega
    refine ⟨repeatNegI (D/2) z, ?_⟩
    calc
      repeatPi D (repeatNegI (D/2) z) =
          repeatPi (2*(D/2)) (repeatNegI (D/2) z) :=
            congrArg (fun n => repeatPi n (repeatNegI (D/2) z)) hd
      _ = scale ((2 : Int)^(D/2)) z := even_binary_conversion (D/2) z
      _ = scale ((2 : Int)^((D+1)/2)) z := by rw [hceil]
  · have hd : D = 2*(D/2)+1 := by omega
    have hceil : (D+1)/2 = D/2+1 := by omega
    refine ⟨repeatNegI (D/2+1) (mulPi z), ?_⟩
    calc
      repeatPi D (repeatNegI (D/2+1) (mulPi z)) =
          repeatPi (2*(D/2)+1) (repeatNegI (D/2+1) (mulPi z)) :=
            congrArg (fun n => repeatPi n (repeatNegI (D/2+1) (mulPi z))) hd
      _ = scale ((2 : Int)^(D/2+1)) z := odd_binary_conversion (D/2) z
      _ = scale ((2 : Int)^((D+1)/2)) z := by rw [hceil]

/-- Every binary-even Gaussian number has zero Gaussian residue. -/
theorem binary_one_residue_zero (z : GInt) (h : BinaryDivisible 1 z) :
    residue z = 0 := by
  rcases h with ⟨w, rfl⟩
  simp only [residue, scale]
  omega

/-- The impulse numerator is primitive at every even denominator level. -/
theorem even_impulse_primitive (q : Nat) :
    ¬ BinaryDivisible 1 (repeatNegI q ⟨1,0⟩) := by
  intro h
  have hz := binary_one_residue_zero _ h
  rw [repeatNegI_residue] at hz
  simp [residue] at hz

def BothOdd (z : GInt) : Prop := z.re % 2 = 1 ∧ z.im % 2 = 1

theorem bothOdd_negI (z : GInt) (h : BothOdd z) : BothOdd (negI z) := by
  simp only [BothOdd, negI] at *
  omega

theorem bothOdd_repeatNegI (q : Nat) (z : GInt) (h : BothOdd z) :
    BothOdd (repeatNegI q z) := by
  induction q with
  | zero => exact h
  | succ q ih => exact bothOdd_negI _ ih

/-- The impulse numerator is primitive at every odd denominator level too. -/
theorem odd_impulse_primitive (q : Nat) :
    ¬ BinaryDivisible 1 (repeatNegI (q+1) (mulPi ⟨1,0⟩)) := by
  intro ⟨w, hw⟩
  have hp : BothOdd (mulPi ⟨1,0⟩) := by simp [BothOdd, mulPi]
  have hb := bothOdd_repeatNegI (q+1) _ hp
  have hr := congrArg GInt.re hw
  simp only [scale, BothOdd] at hr hb
  omega

end GaussianParity

#print axioms GaussianParity.binary_grid_conversion
#print axioms GaussianParity.odd_binary_numerator_parity
#print axioms GaussianParity.even_impulse_primitive
#print axioms GaussianParity.odd_impulse_primitive

namespace GaussianParity

theorem scale_injective (k : Int) (hk : k ≠ 0) {u v : GInt}
    (h : scale k u = scale k v) : u = v := by
  apply GInt.ext
  · have hr := congrArg GInt.re h
    simp only [scale] at hr
    exact Int.eq_of_mul_eq_mul_left hk hr
  · have hi := congrArg GInt.im h
    simp only [scale] at hi
    exact Int.eq_of_mul_eq_mul_left hk hi

/-- No representation on the one-bit coarser binary grid exists for the
impulse coefficient at a positive even π-denominator level. -/
theorem even_grid_sharp (q : Nat) :
    ¬ ∃ w : GInt, repeatPi (2*(q+1)) w = scale ((2 : Int)^q) ⟨1,0⟩ := by
  intro ⟨w, hw⟩
  rw [repeatPi_even] at hw
  have hpow : (2 : Int)^(q+1) = (2 : Int)^q * 2 := by simp [Int.pow_succ]
  rw [hpow, ← scale_mul] at hw
  have hcancel := scale_injective ((2 : Int)^q) (Int.pow_ne_zero (by decide)) hw
  have hr := congrArg GInt.re hcancel
  simp only [scale] at hr
  omega

/-- No representation on the one-bit coarser binary grid exists for the
impulse coefficient at an odd π-denominator level. -/
theorem odd_grid_sharp (q : Nat) :
    ¬ ∃ w : GInt, repeatPi (2*q+1) w = scale ((2 : Int)^q) ⟨1,0⟩ := by
  intro ⟨w, hw⟩
  rw [repeatPi_odd] at hw
  have hcancel := scale_injective ((2 : Int)^q) (Int.pow_ne_zero (by decide)) hw
  have hzero := residue_mulPi (repeatI q w)
  rw [hcancel] at hzero
  simp [residue] at hzero

end GaussianParity

#print axioms GaussianParity.even_grid_sharp
#print axioms GaussianParity.odd_grid_sharp

namespace GaussianParity

def gaussianMul (u v : GInt) : GInt :=
  ⟨u.re*v.re - u.im*v.im, u.re*v.im + u.im*v.re⟩

/-- Multiplying two π factors contributes one full binary bit, together
with a unit phase. This is the normalization cancellation at odd depth. -/
theorem gaussianMul_pi_pi (u v : GInt) :
    gaussianMul (mulPi u) (mulPi v) = scale 2 (mulI (gaussianMul u v)) := by
  apply GInt.ext <;> simp only [gaussianMul, mulPi, scale, mulI] <;> grind

/-- Two odd-depth numerator sublattice constraints must be preserved:
together they certify divisibility by 2 in a normalized product. -/
theorem two_pi_factors_binary (u v : GInt) (hu : PiDvd u) (hv : PiDvd v) :
    BinaryDivisible 1 (gaussianMul u v) := by
  refine ⟨mulI (gaussianMul (dividePi u) (dividePi v)), ?_⟩
  change scale 2 (mulI (gaussianMul (dividePi u) (dividePi v))) = gaussianMul u v
  rw [← gaussianMul_pi_pi, (dividePi_exact_iff u).mpr hu,
      (dividePi_exact_iff v).mpr hv]

end GaussianParity

#print axioms GaussianParity.gaussianMul_pi_pi
#print axioms GaussianParity.two_pi_factors_binary
