import S008.WalshShift
import S008.WalshRounding
import Mathlib.Analysis.Real.Sqrt

/-! The two integer group ports, their independent moduli, and one normalization. -/
namespace Moonshot.AlignedWalsh.Groups

open Finset Moonshot.CompactSpecialization Moonshot.AlignedWalsh.ShiftGeometry

/-- A raw integer Walsh row on the selected binary positions of one group. -/
def raw {s : ℕ} (x : Mask s → ℤ) (u : Mask s) : ℤ :=
  ∑ i, character u i*x i

/-- Dot signs on the original two disjoint subsets, with spectators held fixed. -/
def combined {a b : ℕ} (x : Mask a → Mask b → ℤ) (u : Mask a) (v : Mask b) : ℤ :=
  ∑ i, ∑ j, (-1:ℤ)^(maskDotCount u i+maskDotCount v j)*x i j

abbrev groupModulus (k w s U : ℕ) := modulus U (k+w+s+2)

/-- Raw integer Walsh rows require only their group's bit count in extra digits. -/
theorem raw_word_bound {s w : ℕ} (x : Mask s → ℤ) (hx : ∀ i, |x i|<(2:ℤ)^w)
    (u : Mask s) : |raw x u| < (2:ℤ)^(w+s) := by
  classical
  calc
    _ ≤ ∑ i, |character u i*x i| := abs_sum_le_sum_abs _ _
    _ = ∑ i, |x i| := by simp only [abs_mul,character_is_dot,abs_pow,abs_neg,abs_one,one_pow,one_mul]
    _ < ∑ _i : Mask s, (2:ℤ)^w := sum_lt_sum_of_nonempty univ_nonempty (fun i _ ↦ hx i)
    _ = _ := by simp [Mask,pow_add,mul_comm]

/-- Every positive aligned denominator product gives the required signed-lift interval. -/
theorem group_modulus_range (k w s : ℕ) {U : ℕ} (hu : 0<U) :
    2*(2:ℤ)^(w+s) ≤ (groupModulus k w s U : ℤ) := by
  have hp := Nat.pow_le_pow_right (n:=2) (by decide) (show w+s+1 ≤ k+w+s+2 by omega)
  have hm := Nat.le_mul_of_pos_right (2^(k+w+s+2)) hu
  have hn : 2*2^(w+s) ≤ groupModulus k w s U := by
    unfold groupModulus modulus
    rw [pow_succ] at hp
    omega
  exact_mod_cast hn

/-- All aligned moduli at the concrete outer widths fit the same 100k-bit port. -/
theorem group_modulus_fits {k w s U : ℕ} (hk : 1≤k) (hw : w+s≤86*k+1) (hu : U<2^k) :
    groupModulus k w s U < 2^(100*k) := by
  let e := k+w+s+2
  calc
    _ = 2^e*U+1 := rfl
    _ ≤ 2^e*(U+1) := by
      have hh : 0 < 2^e := by positivity
      rw [Nat.mul_add,Nat.mul_one]
      omega
    _ ≤ 2^e*2^k := Nat.mul_le_mul_left _ (by omega)
    _ = 2^(e+k) := (pow_add _ _ _).symm
    _ < 2^(100*k) := Nat.pow_lt_pow_right (by decide) (by dsimp [e]; omega)

/-- An actual canonical residue at an integer Walsh endpoint has its unique signed lift. -/
theorem recover_group {k w s U : ℕ} (hu : 0<U) (x : Mask s → ℤ)
    (hx : ∀ i, |x i|<(2:ℤ)^w) (u : Mask s) {r : ℕ} (hr : r<groupModulus k w s U)
    (ht : SourceTicket (groupModulus k w s U) ((raw x u:ℤ):ℚ) (r:ZMod (groupModulus k w s U))) :
    center (groupModulus k w s U) r = raw x u := by
  have hmag := raw_word_bound x hx u
  have hp := group_modulus_range k w s hu
  have hi := le_abs_self (raw x u)
  have lo := neg_le_abs (raw x u)
  exact signed_lift_of_ticket hr (by omega) (by omega) ht

/-- Carry out both integer groups before normalizing, including when both sizes are odd. -/
theorem group_tensor {a b : ℕ} (x : Mask a → Mask b → ℤ) (u : Mask a) (v : Mask b) :
    raw (fun j ↦ raw (fun i ↦ x i j) u) v = combined x u v := by
  classical
  unfold raw combined
  simp_rw [mul_sum]
  rw [sum_comm]
  apply sum_congr rfl
  intro i _
  apply sum_congr rfl
  intro j _
  rw [character_is_dot,character_is_dot,pow_add]
  ring

/-- Read the first group's centered signed words under its own modulus, and the
second group's arbitrary independently aligned modulus. The returned integer has
the joint dot-product sign on the original address. -/
theorem two_group_return {k w a b U V : ℕ} (hU : 0<U) (hV : 0<V)
    (x : Mask a → Mask b → ℤ) (hx : ∀ i j, |x i j|<(2:ℤ)^w)
    (r₁ : Mask a → Mask b → ℕ) (r₂ : Mask a → Mask b → ℕ)
    (h₁ : ∀ i j, r₁ i j < groupModulus k w a U)
    (h₂ : ∀ i j, r₂ i j < groupModulus k (w+a) b V)
    (t₁ : ∀ u j, SourceTicket (groupModulus k w a U) ((raw (fun i ↦ x i j) u:ℤ):ℚ)
      (r₁ u j:ZMod (groupModulus k w a U)))
    (t₂ : ∀ u v, SourceTicket (groupModulus k (w+a) b V)
      ((raw (fun j ↦ center (groupModulus k w a U) (r₁ u j)) v:ℤ):ℚ)
      (r₂ u v:ZMod (groupModulus k (w+a) b V))) (u : Mask a) (v : Mask b) :
    center (groupModulus k (w+a) b V) (r₂ u v) = combined x u v := by
  have hfirst (j) : center (groupModulus k w a U) (r₁ u j) = raw (fun i ↦ x i j) u :=
    recover_group hU (fun i ↦ x i j) (fun i ↦ hx i j) u (h₁ u j) (t₁ u j)
  have hn (j) : |center (groupModulus k w a U) (r₁ u j)| < (2:ℤ)^(w+a) := by
    rw [hfirst j]
    exact raw_word_bound _ (fun i ↦ hx i j) u
  have hsec := recover_group hV (fun j ↦ center (groupModulus k w a U) (r₁ u j)) hn v
    (h₂ u v) (t₂ u v)
  simp_rw [hfirst] at hsec
  exact hsec.trans (group_tensor x u v)

/-- The even-total branch rounds a single binary shift, including zero selected bits. -/
def shiftedEven (p t : ℕ) : ℕ := (2*t+2^p)/(2*2^p)

theorem even_shift_spec (p t : ℕ) : midpointSpec (2^(2*p)) t (shiftedEven p t) := by
  let e := 2^p
  let r := shiftedEven p t
  have he : 0<e := by dsimp [e]; positivity
  have hlo : r*(2*e) ≤ 2*t+e := Nat.div_mul_le_self _ _
  have hhi : 2*t+e < (2*e)*(r+1) := Nat.lt_mul_div_succ _ (by omega)
  have hhi' : 2*t < (2*r+1)*e := by
    rw [show (2*e)*(r+1)=(2*r+1)*e+e by ring] at hhi
    omega
  have hsquare : 2^(2*p) = e^2 := by
    dsimp [e]
    rw [←pow_mul]
    congr 1
    omega
  change (r=0 ∨ 2^(2*p)*(2*r-1)^2 ≤ 4*t^2) ∧ 4*t^2 < 2^(2*p)*(2*r+1)^2
  rw [hsquare]
  constructor
  · by_cases hr : r=0
    · exact Or.inl hr
    · right
      have hp' : 1≤2*r := by omega
      have hpre : (2*r-1)*e+e = r*(2*e) := calc
        _ = (2*r-1+1)*e := by ring
        _ = _ := by rw [Nat.sub_add_cancel hp']; ring
      have hl : (2*r-1)*e ≤ 2*t := by omega
      calc
        _ = ((2*r-1)*e)^2 := by ring
        _ ≤ (2*t)^2 := Nat.pow_le_pow_left hl _
        _ = _ := by ring
  · calc
      _ = (2*t)^2 := by ring
      _ < ((2*r+1)*e)^2 := Nat.pow_lt_pow_left hhi' (by decide)
      _ = _ := by ring

/-- The squared-integer midpoint specification gives half one unit in real magnitude. -/
theorem real_midpoint_error {q t r : ℕ} (hq : 0<q) (h : midpointSpec q t r) :
    |(r:ℝ)-(t:ℝ)/Real.sqrt q| ≤ 1/2 := by
  let e := Real.sqrt (q:ℝ)
  have hq' : (0:ℝ)<q := by exact_mod_cast hq
  have he : 0<e := Real.sqrt_pos_of_pos hq'
  have heq : e^2=(q:ℝ) := Real.sq_sqrt hq'.le
  have hhi' : 4*(t:ℝ)^2<(q:ℝ)*(2*(r:ℝ)+1)^2 := by exact_mod_cast h.2
  have hsq : (2*(t:ℝ))^2<((2*(r:ℝ)+1)*e)^2 := calc
    _ = 4*(t:ℝ)^2 := by ring
    _ < (q:ℝ)*(2*(r:ℝ)+1)^2 := hhi'
    _ = _ := by rw [mul_pow,heq]; ring
  have hu := (pow_lt_pow_iff_left₀ (by positivity) (mul_nonneg (by positivity) he.le)
      (by decide : 2≠0)).mp hsq
  have hupper : (t:ℝ)/e ≤ (r:ℝ)+1/2 := (div_le_iff₀ he).mpr (by linarith)
  have hlower : (r:ℝ)-1/2 ≤ (t:ℝ)/e := by
    apply (le_div_iff₀ he).mpr
    by_cases hr : r=0
    · subst r
      have ht : (0:ℝ)≤t := by positivity
      norm_num
      linarith
    · have hn : 1≤2*r := by omega
      have hl := h.1.resolve_left hr
      have hreal : (q:ℝ)*(↑(2*r-1:ℕ):ℝ)^2≤4*(t:ℝ)^2 := by exact_mod_cast hl
      rw [Nat.cast_sub hn] at hreal
      push_cast at hreal
      have hz : (0:ℝ)≤2*(r:ℝ)-1 := sub_nonneg.mpr (by exact_mod_cast hn)
      have hsq' : ((2*(r:ℝ)-1)*e)^2≤(2*(t:ℝ))^2 := calc
        _ = (q:ℝ)*(2*(r:ℝ)-1)^2 := by rw [mul_pow,heq]; ring
        _ ≤ 4*(t:ℝ)^2 := hreal
        _ = _ := by ring
      have hlin := (pow_le_pow_iff_left₀ (mul_nonneg hz he.le) (by positivity)
        (by decide : 2≠0)).mp hsq'
      linarith
  change |(r:ℝ)-(t:ℝ)/e| ≤ 1/2
  exact abs_le.mpr ⟨by linarith,by linarith⟩

/-- The executable branch uses the even shift or the odd integer square root, with
one final normalization after both groups. -/
def normalizedMagnitude (w s t : ℕ) : ℕ :=
  if s%2=0 then shiftedEven (s/2) t else
    let J := w+s+3
    roundedWord (2^s) t (2^J) (Nat.sqrt (2^(2*J-s)))

theorem normalized_magnitude_spec {w s t : ℕ} (ht : t<2^(w+s)) :
    midpointSpec (2^s) t (normalizedMagnitude w s t) := by
  unfold normalizedMagnitude
  split_ifs with hs
  · have he : 2*(s/2)=s := by omega
    simpa only [he] using even_shift_spec (s/2) t
  · exact dyadic_rounding_spec ht

/-- Reattach the input sign after choosing the one nearest magnitude. -/
def normalizedSigned (w s : ℕ) (z : ℤ) : ℤ :=
  let r := normalizedMagnitude w s z.natAbs
  if z<0 then -(r:ℤ) else r

theorem normalized_signed_error {w s : ℕ} {z : ℤ} (hz : |z| < (2:ℤ)^(w+s)) :
    |(normalizedSigned w s z:ℝ)-(z:ℝ)/Real.sqrt (2^s:ℕ)| ≤ 1/2 := by
  have ht : z.natAbs < 2^(w+s) := by
    have hh : (z.natAbs : ℤ) < (2:ℤ)^(w+s) := by rwa [Int.natCast_natAbs]
    exact_mod_cast hh
  have mag : (z.natAbs : ℝ) = |(z:ℝ)| := by
    calc
      _ = ((z.natAbs:ℤ):ℝ) := (Int.cast_natCast _).symm
      _ = ((|z|:ℤ):ℝ) := congrArg (fun y : ℤ ↦ (y:ℝ)) (Int.natCast_natAbs z)
      _ = _ := Int.cast_abs
  have h := real_midpoint_error (show 0<2^s by positivity) (normalized_magnitude_spec ht)
  rw [mag] at h
  by_cases hn : z<0
  · have hn' : (z:ℝ)<0 := by exact_mod_cast hn
    rw [abs_of_neg hn'] at h
    simp only [normalizedSigned,ite_eq_left hn,Int.cast_neg,Int.cast_natCast]
    rw [show -(normalizedMagnitude w s z.natAbs : ℝ)-(z:ℝ)/Real.sqrt (2^s:ℕ) =
      -((normalizedMagnitude w s z.natAbs : ℝ)-(-(z:ℝ))/Real.sqrt (2^s:ℕ)) by ring,abs_neg]
    exact h
  · have hp : (0:ℝ)≤z := by exact_mod_cast (le_of_not_gt hn)
    rw [abs_of_nonneg hp] at h
    simpa only [normalizedSigned,ite_eq_right hn,Int.cast_natCast] using h

/-- Real error at p fractional bits after the signed modular integer boundary. -/
theorem grid_error {p w s : ℕ} {z : ℤ} (hz : |z| < (2:ℤ)^(w+s)) :
    |(normalizedSigned w s z:ℝ)/(2:ℝ)^p-(z:ℝ)/(Real.sqrt (2^s:ℕ)*(2:ℝ)^p)| ≤
      1/(2*(2:ℝ)^p) := by
  have hp : (0:ℝ)<2^p := by positivity
  rw [←div_div,←sub_div,abs_div,abs_of_pos hp,←div_div]
  exact div_le_div_of_nonneg_right (normalized_signed_error hz) hp.le

/-- An exact join from the combined genuine dot signs to the physical signed normalizer. -/
theorem grouped_grid_error {p w a b : ℕ} (x : Mask a → Mask b → ℤ)
    (hx : ∀ i j, |x i j|<(2:ℤ)^w) (u : Mask a) (v : Mask b) :
    |(normalizedSigned w (a+b) (combined x u v):ℝ)/(2:ℝ)^p-
      (combined x u v:ℝ)/(Real.sqrt (2^(a+b):ℕ)*(2:ℝ)^p)| ≤ 1/(2*(2:ℝ)^p) := by
  apply grid_error
  rw [←group_tensor]
  have h₁ j := raw_word_bound (fun i ↦ x i j) (fun i ↦ hx i j) u
  simpa only [Nat.add_assoc] using raw_word_bound (fun j ↦ raw (fun i ↦ x i j) u) h₁ v

/-- The one boundary on both real components of each of the 2^k physical records
has total squared Euclidean error strictly below the square of 2^(-50k) at p=72k. -/
theorem complex_layer_squared_error {k w s : ℕ} (z : Fin (2*2^k) → ℤ)
    (hz : ∀ i, |z i|<(2:ℤ)^(w+s)) :
    (∑ i, ((normalizedSigned w s (z i):ℝ)/(2:ℝ)^(72*k)-
      (z i:ℝ)/(Real.sqrt (2^s:ℕ)*(2:ℝ)^(72*k)))^2) < (1/(2:ℝ)^(50*k))^2 := by
  classical
  let scale := (2:ℝ)^(72*k)
  let E (i : Fin (2*2^k)) := (normalizedSigned w s (z i):ℝ)/scale-
    (z i:ℝ)/(Real.sqrt (2^s:ℕ)*scale)
  have hE (i) : |E i|≤1/(2*scale) := grid_error (hz i)
  have hsq (i) : (E i)^2 ≤ (1/(2*scale))^2 := calc
    _ = |E i|^2 := (sq_abs _).symm
    _ ≤ _ := pow_le_pow_left₀ (abs_nonneg _) (hE i) 2
  have hboth : ((2:ℝ)*2^k)*((2:ℝ)^(50*k))^2 = (2:ℝ)^(101*k+1) := by
    rw [←pow_mul,show 50*k*2=100*k by omega,show 101*k+1=(k+100*k)+1 by omega,
      pow_succ,pow_add]
    ring
  have hscale : (2*scale)^2=(2:ℝ)^(144*k+2) := by
    dsimp [scale]
    rw [mul_pow,←pow_mul,show 72*k*2=144*k by omega,pow_add]
    ring
  have hcross : ((2:ℝ)*2^k)*((2:ℝ)^(50*k))^2 < (2*scale)^2 := by
    rw [hboth,hscale]
    exact pow_lt_pow_right₀ (by norm_num) (by omega)
  calc
    _ = ∑ i, (E i)^2 := rfl
    _ ≤ ∑ _i : Fin (2*2^k), (1/(2*scale))^2 := sum_le_sum (fun i _ ↦ hsq i)
    _ = ((2:ℝ)*2^k)*(1/(2*scale))^2 := by simp [nsmul_eq_mul]
    _ < _ := by
      simp only [div_pow,one_pow,mul_one_div]
      exact (div_lt_div_iff₀ (by dsimp [scale]; positivity) (by positivity)).mpr (by simpa using hcross)

end Moonshot.AlignedWalsh.Groups
