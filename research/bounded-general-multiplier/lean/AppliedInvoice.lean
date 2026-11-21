import Invoice

namespace ShiftedCarrier
open CarrierGuards
set_option maxRecDepth 100000
set_option exponentiation.threshold 5000

theorem bit_terminal {L : ℝ}
    (cost : L ≤ ((2:ℝ)^bitH)^((1:ℝ)-0.003879928046148) *
                (height 8192 ((2:ℝ)^bitH))^71) :
    L*32 < ((2:ℝ)^bitH)^((1:ℝ)-0.003879928035648) := by
  have h := terminal (H:=bitH) (b:=8192) (p:=71) (overhead:=5) (q:=2520)
    (C:=0.003879928046148) (target:=0.003879928035648) (by decide)
    cost bit_final.2.1 (by norm_num [bitH])
  simpa only [show (2:ℝ)^5=32 by norm_num] using h

theorem complex_terminal {L : ℝ}
    (cost : L ≤ ((2:ℝ)^complexH)^((1:ℝ)-0.00388013) *
                (height 2048 ((2:ℝ)^complexH))^31) :
    L*2 < ((2:ℝ)^complexH)^((1:ℝ)-(0.00387992803556+5/100000000000000)) := by
  have h := terminal (H:=complexH) (b:=2048) (p:=31) (overhead:=1) (q:=666)
    (C:=0.00388013) (target:=0.00387992803556+5/100000000000000)
    (by decide) cost complex_final.2 (by norm_num [complexH])
  simpa only [pow_one] using h

#print axioms bit_terminal
#print axioms complex_terminal
end ShiftedCarrier
