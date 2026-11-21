import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

namespace TriangularStages

set_option maxRecDepth 16384
set_option maxHeartbeats 1000000
set_option exponentiation.threshold 4096

def costed (h d before after : ℕ) : Prop :=
  32 * (8192 + h)^71 < 2^(d + 923) ∧
  before < after ∧
  (after : ℚ) / 10^18 <
    (249 * (3879928046148 / 10^15 - (d : ℚ) / h) + (before : ℚ)/10^18)/250 ∧
  (after : ℚ)/10^18 < 97/25000

theorem six_carrier_prices :
    costed 60000000000 1625 0 3864381358963407 ∧
    costed 400000000000 1819 3864381358963407 3879861330089260 ∧
    costed 2500000000000 2007 3879861330089260 3879926979694964 ∧
    costed 16000000000000 2197 3879926979694964 3879927905118936 ∧
    costed 100000000000000 2384 3879927905118936 3879928021839242 ∧
    costed 236800000000000 2473 3879928021839242 3879928035646000 := by
  norm_num [costed]

theorem covered_price {h d a actual : ℝ} (hh : 0 < h)
    (word : actual ≤ ((2:ℝ)^h)^(1-a) * (1+h/8192)^71)
    (certificate : 32 * (1+h/8192)^71 < (2:ℝ)^d) :
    32 * actual < ((2:ℝ)^h)^(1-(a-d/h)) := by
  have hn : (0:ℝ) < 2^h := Real.rpow_pos_of_pos (by norm_num) _
  have hd : ((2:ℝ)^h)^(d/h) = 2^d := by
    rw [← Real.rpow_mul (by norm_num : (0:ℝ) ≤ 2)]
    congr 1
    field_simp
  calc
    32 * actual ≤ ((2:ℝ)^h)^(1-a) * (32 * (1+h/8192)^71) := by linarith
    _ < ((2:ℝ)^h)^(1-a) * 2^d := mul_lt_mul_of_pos_left certificate (Real.rpow_pos_of_pos hn _)
    _ = ((2:ℝ)^h)^(1-(a-d/h)) := by
      rw [← hd, ← Real.rpow_add hn]
      congr 1
      ring

theorem use_integer_certificate {h d : ℕ} {a actual : ℝ} (hh : 0 < h)
    (word : actual ≤ ((2:ℝ)^(h:ℝ))^(1-a) * (1+(h:ℝ)/8192)^71)
    (debit : 32*(8192+h)^71 < 2^(d+923)) :
    32*actual < ((2:ℝ)^(h:ℝ))^(1-(a-(d:ℝ)/h)) := by
  apply covered_price (by exact_mod_cast hh) word
  rw [Real.rpow_natCast, show 1+(h:ℝ)/8192 = (8192+h)/8192 by ring,
      div_pow, ← mul_div_assoc, div_lt_iff₀ (by norm_num : (0:ℝ)<8192^71),
      show (8192:ℝ)^71 = 2^923 by norm_num, ← pow_add]
  exact_mod_cast debit

theorem balanced_scans {m g w c e : ℝ} (hc : 0 ≤ c) (hgw : g ≤ w)
    (hm : m*g ≤ w+g) (field : w*c ≤ e) :
    m*c*g ≤ 2*e := by
  have a := mul_le_mul_of_nonneg_right hm hc
  have b := mul_le_mul_of_nonneg_right hgw hc
  nlinarith

/-- In a direct packet the actual linear reheading cost has a fixed multiplier. -/
theorem direct_charge {c n a : ℝ} (hc : 0 < c) (bounded : c ≤ n^8)
    (saving : 0 ≤ a) : c ≤ (n^8)^a * c^(1-a) := by
  have h := Real.rpow_le_rpow hc.le bounded saving
  have ht := mul_le_mul_of_nonneg_right h (Real.rpow_nonneg hc.le (1-a))
  rw [← Real.rpow_add hc, show a+(1-a)=1 by ring, Real.rpow_one] at ht
  exact ht

/-- These logarithmic inequalities apply to all widths in each entry interval. -/
def direct_interval (h previous entry limit parentLimit : ℕ) : Prop :=
  250*(h+64) ≤ 249*entry ∧
  (previous = 0 ∨ h+previous+64 ≤ entry) ∧
  limit-previous ≤ 8*h ∧ previous < h ∧
  entry+1 < limit ∧ parentLimit+250 < 250*limit

theorem all_direct_intervals :
  direct_interval 60000000000 0 60240963920 460240963984 2960240964048 ∧
  direct_interval 400000000000 60240963920 460240963984 2960240964048 18960240964112 ∧
  direct_interval 2500000000000 460240963984 2960240964048 18960240964112 118960240964176 ∧
  direct_interval 16000000000000 2960240964048 18960240964112 118960240964176 355760240964240 ∧
  direct_interval 100000000000000 18960240964112 118960240964176 355760240964240 355763540965265 ∧
  direct_interval 236800000000000 118960240964176 355760240964240 355763540965265 355763540965265 := by
  norm_num [direct_interval]

theorem connected_arithmetic :
    355763540965265 < (2:ℕ)^49 ∧
    355760240964240 ≤ 355763540965265-100-16*50-3300000000-2 ∧
    355760240964240 ≤ 355763540965265-13 ∧
    1050*355760000000000 + 448*(3*3300000000+355763540965265+1) =
      532934501552439168 ∧
    532934501552439168 < (2:ℕ)^59 := by
  norm_num

noncomputable section
def eta : ℝ := 97/25000

private theorem depth_growth {z : ℝ} (hz : 0 ≤ z) :
    1+z/4 ≤ (2:ℝ)^((1-eta)*z) := by
  have h := Real.one_sub_inv_le_log_of_pos (by norm_num : (0:ℝ)<2)
  have hl : (1:ℝ)/2 ≤ Real.log 2 := by linarith
  have he := Real.add_one_le_exp (Real.log 2*((1-eta)*z))
  rw [Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2)]
  unfold eta at *
  nlinarith [mul_le_mul_of_nonneg_right hl hz]

/-- Charge one stage's complete row reserve, also when the caller is suspended. -/
theorem stage_reserve {h cut t n k : ℝ}
    (hh : 1 ≤ h) (hc : cut ≤ 3*h) (entered : cut ≤ t) (hn : 1 ≤ n)
    (nonnegative : 0 ≤ t)
    (first : (2:ℝ)^64 * n^2 ≤ (2:ℝ)^((1-eta)*cut))
    (bill : k ≤ 1+6*(3+t/h)*n^2*(2:ℝ)^(eta*t)) :
    k < (2:ℝ)^t/64 := by
  have hd' := depth_growth (sub_nonneg.mpr entered)
  set D := (2:ℝ)^((1-eta)*(t-cut))
  have hd : 1 ≤ D := (by linarith : (1:ℝ) ≤ 1+(t-cut)/4).trans hd'
  have hcut : cut/h ≤ 3 := (div_le_iff₀ (by linarith : 0 < h)).mpr hc
  have hrem : (t-cut)/h ≤ t-cut :=
    div_le_self (sub_nonneg.mpr entered) hh
  have hsum : 3+t/h ≤ 6*D := by
    rw [show t/h = cut/h+(t-cut)/h by ring]
    dsimp [D] at *
    linarith
  have hp : 1 ≤ (2:ℝ)^(eta*t) :=
    Real.one_le_rpow (by norm_num) (mul_nonneg (by norm_num [eta]) nonnegative)
  have prod : 1 ≤ n^2 * D * (2:ℝ)^(eta*t) :=
    one_le_mul_of_one_le_of_one_le
      (one_le_mul_of_one_le_of_one_le (one_le_pow₀ hn) hd) hp
  have iden : (2:ℝ)^((1-eta)*cut) * (D * 2^(eta*t)) = 2^t := by
    dsimp [D]
    rw [← Real.rpow_add (by norm_num : (0:ℝ)<2),
        ← Real.rpow_add (by norm_num : (0:ℝ)<2)]
    congr 1
    ring
  have room := mul_le_mul_of_nonneg_right first
    (mul_nonneg (le_trans (by norm_num) hd) (le_trans (by norm_num) hp))
  rw [iden] at room
  have tariff := mul_le_mul_of_nonneg_right hsum
    (mul_nonneg (sq_nonneg n) (le_trans (by norm_num) hp))
  norm_num at room
  nlinarith

end

#print axioms six_carrier_prices
#print axioms covered_price
#print axioms use_integer_certificate
#print axioms balanced_scans
#print axioms direct_charge
#print axioms all_direct_intervals
#print axioms connected_arithmetic
#print axioms stage_reserve
end TriangularStages

namespace TriangularReserve

def rows (owners charts height : ℕ) : ℕ := owners^(2+height) * charts^(height-8)

def issued (rank owners charts atoms : ℕ) : ℕ :=
  if atoms ≤ rank^8 then owners else owners*charts

/-- One fresh bank leaves all rows needed by the next coarse height. -/
theorem bank_divides (rank owners charts atoms h : ℕ) (hr : 0 < rank)
    (hc : atoms ≤ rank^(h+1)) :
    issued rank owners charts atoms * rows owners charts h ∣ rows owners charts (h+1) := by
  have he : 2+(h+1) = (2+h)+1 := by omega
  by_cases h8 : h < 8
  · have near : atoms ≤ rank^8 := hc.trans (Nat.pow_le_pow_right hr (by omega))
    have branch : issued rank owners charts atoms = owners := by simp [issued, near]
    rw [branch]
    apply dvd_of_eq
    simp only [rows, he, show h-8 = 0 by omega, show h+1-8 = 0 by omega, pow_zero, mul_one]
    rw [pow_succ, Nat.mul_comm]
  · have heq : h+1-8 = (h-8)+1 := by omega
    by_cases near : atoms ≤ rank^8
    · have branch : issued rank owners charts atoms = owners := by simp [issued, near]
      refine ⟨charts, ?_⟩
      rw [branch]
      simp only [rows, he, heq, pow_succ]
      ring
    · have branch : issued rank owners charts atoms = owners*charts := by simp [issued, near]
      rw [branch]
      apply dvd_of_eq
      simp only [rows, he, heq, pow_succ]
      ring

/-- This is the successful divmod in the weighted receiver for all surplus multiplicities. -/
theorem funded_child (rank owners charts atoms h available : ℕ)
    (hr : 0 < rank) (ho : 0 < owners) (hz : 0 < charts)
    (ha : 0 < available) (hc : atoms ≤ rank^(h+1)) (fund : rows owners charts (h+1) ∣ available) :
    atoms / rank ≤ rank^h ∧ available % issued rank owners charts atoms = 0 ∧
      0 < available / issued rank owners charts atoms ∧
      rows owners charts h ∣ available / issued rank owners charts atoms := by
  let I := issued rank owners charts atoms
  have hi : 0 < I := by
    dsimp [I, issued]; split <;> positivity
  obtain ⟨q, hq⟩ := dvd_trans (bank_divides rank owners charts atoms h hr hc) fund
  change available = I * rows owners charts h * q at hq
  have measured : available = (rows owners charts h * q) * I := by rw [hq]; ring
  have hqpos : 0 < rows owners charts h * q := by
    by_contra! hn
    have zero : rows owners charts h * q = 0 := by omega
    rw [zero, Nat.zero_mul] at measured
    omega
  refine ⟨?_, ?_, ?_, q, ?_⟩
  · calc atoms/rank ≤ rank^(h+1)/rank := Nat.div_le_div_right hc
         _ = rank^h := by rw [pow_succ]; exact Nat.mul_div_cancel _ hr
  · change available % I = 0
    rw [measured, Nat.mul_mod_left]
  · change 0 < available / I
    simpa [measured, Nat.mul_div_cancel _ hi] using hqpos
  · change available / I = _
    rw [measured, Nat.mul_div_cancel _ hi]

set_option exponentiation.threshold 4096 in
/-- The retained envelope cannot fund the required ordinary price at this rank. -/
theorem price_floor_certificate :
    2^(923+2471) < 32*(8192+234000000000000 : ℕ)^71 ∧
      (249 : ℚ)*2471/(250*234000000000000) >
        (3879928046148-3879928035646 : ℚ)/10^15 := by
  norm_num

#print axioms price_floor_certificate
#print axioms bank_divides
#print axioms funded_child
end TriangularReserve
