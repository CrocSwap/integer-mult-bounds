import S008.NumericalCutoff

namespace S008.Recount.Sharp
open S008.NumericalCutoff

set_option exponentiation.threshold 1000

def factor : Bool → ℕ
  | false => 1
  | true => 2

def digit : Bool → ℕ
  | false => 0
  | true => 1

abbrev Edge := Bool × ℕ

/-- Each rounded upper mantissa dominates its normalization after squaring. -/
def upperOK (q a : ℕ) : List Edge → Bool
  | [] => decide (0 < a ∧ a ≤ 2*q)
  | (b,c) :: es => decide (0 < a ∧ 0 < c ∧ a*a ≤ factor b*c*q) && upperOK q c es

def weight : List Edge → ℕ
  | [] => 0
  | (b,_)::es => digit b * 2^es.length + weight es

/-- Generate a checkable upper bracket from the supplied binary digit word. -/
def emit (q a bits : ℕ) : ℕ → List Edge
  | 0 => []
  | n+1 =>
    let b := bits.testBit n
    let den := factor b * q
    let c := (a*a+den-1)/den
    (b,c)::emit q c bits n

private theorem logTwo_two : logTwo 2 = 1 := by
  unfold logTwo
  exact div_self (ne_of_gt (Real.log_pos (by norm_num)))

private theorem digit_factor (b : Bool) : logTwo (factor b : ℝ) = (digit b : ℝ) := by
  cases b with
  | false => simp [factor,digit,logTwo]
  | true => simpa only [factor,digit,Nat.cast_ofNat,Nat.cast_one] using logTwo_two

private theorem log_squaring_step (v w : ℝ) {b : Bool} (hv : 0<v) (hw : 0<w)
    (h : v*v ≤ (factor b : ℝ)*w) :
    2*logTwo v ≤ (digit b : ℝ)+logTwo w := by
  have hb : 0 < (factor b : ℝ) := by cases b <;> norm_num [factor]
  have z := logTwo_mono (mul_pos hv hv) h
  have hadd (j l : ℝ) (hj : 0<j) (hl : 0<l) :
      logTwo (j*l) = logTwo j + logTwo l := by
    unfold logTwo
    rw [Real.log_mul hj.ne' hl.ne']
    ring
  rw [hadd _ _ hv hv, hadd _ _ hb hw, digit_factor] at z
  linarith

theorem upper_chain {q a : ℕ} (hq : 0<q) (es : List Edge) (h : upperOK q a es) :
    (2:ℝ)^es.length * logTwo ((a:ℝ)/q) ≤ (weight es : ℝ)+1 := by
  induction es generalizing a with
  | nil =>
    have hh : 0<a ∧ a ≤ 2*q := of_decide_eq_true h
    have hq' : (0:ℝ)<q := by exact_mod_cast hq
    have hv : (0:ℝ)<a := by exact_mod_cast hh.1
    have ha : (a:ℝ)/q ≤ 2 := by
      rw [div_le_iff₀ hq']
      exact_mod_cast hh.2
    have z := logTwo_mono (div_pos hv hq') ha
    simpa [weight, logTwo_two] using z
  | cons e es ih =>
    rcases e with ⟨b,c⟩
    simp only [upperOK, Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨ha,hc,hh⟩, he⟩ := h
    have hq' : (0:ℝ)<q := by exact_mod_cast hq
    have ha' : (0:ℝ)<a := by exact_mod_cast ha
    have hc' : (0:ℝ)<c := by exact_mod_cast hc
    have hraw : (a:ℝ)*a ≤ (factor b:ℝ)*c*q := by exact_mod_cast hh
    have hv : ((a:ℝ)/q)*((a:ℝ)/q) ≤ (factor b:ℝ)*((c:ℝ)/q) := by
      field_simp [hq'.ne']
      nlinarith only [hraw]
    have hstep := log_squaring_step _ _ (div_pos ha' hq') (div_pos hc' hq') hv
    have hw := mul_le_mul_of_nonneg_left hstep (show 0≤(2:ℝ)^es.length by positivity)
    have hr := ih he
    simp only [List.length_cons, pow_succ, weight, Nat.cast_add, Nat.cast_mul,
      Nat.cast_pow, Nat.cast_ofNat]
    nlinarith only [hw,hr]


private theorem log_mul {v w : ℝ} (hv : 0<v) (hw : 0<w) :
    logTwo (v*w) = logTwo v + logTwo w := by
  unfold logTwo
  rw [Real.log_mul hv.ne' hw.ne']
  ring

/-- A closed integer certificate bounds the real binary logarithm. -/
theorem certify (q a n j bits : ℕ)
    (ha : 0<a) (hq : 0<q) (rep : n*q=2^j*a)
    (check : upperOK q a (emit q a bits 112))
    (len : (emit q a bits 112).length=112) (wgt : weight (emit q a bits 112)=bits) :
    logTwo (n:ℝ) ≤ (j:ℝ) + ((bits:ℝ)+1)/2^112 := by
  have hq' : (0:ℝ)<q := by exact_mod_cast hq
  have ha' : (0:ℝ)<a := by exact_mod_cast ha
  have rr : (n:ℝ)=(2:ℝ)^j*(a/q) := by
    field_simp [hq'.ne']
    exact_mod_cast rep
  have hz := upper_chain hq (emit q a bits 112) check
  rw [len,wgt] at hz
  have hz' : logTwo ((a:ℝ)/q) ≤ ((bits:ℝ)+1)/2^112 := by
    rw [le_div_iff₀ (by positivity)]
    linarith
  have hh : logTwo ((2:ℝ)^j) = (j:ℝ) := by
    simpa only [Real.rpow_natCast] using logTwo_two_rpow (j:ℝ)
  rw [rr,log_mul (by positivity) (div_pos ha' hq'),hh]
  linarith

private theorem real_nonneg {v : ℝ} (h : 1≤v) : 0≤logTwo v := by
  unfold logTwo
  exact div_nonneg (Real.log_nonneg h) (Real.log_nonneg (by norm_num))

def Q : ℕ := 2^448

def first (n j : ℕ) : ℕ := n*2^(448-j)

def lowerOK (q a : ℕ) : List Edge → Bool
  | [] => decide (q ≤ a)
  | (b,c) :: es => decide (0 < a ∧ 0 < c ∧ factor b*c*q ≤ a*a) && lowerOK q c es

def lowerEmit (q a bits : ℕ) : ℕ → List Edge
  | 0 => []
  | n+1 =>
    let b := bits.testBit n
    let c := a*a/(factor b*q)
    (b,c)::lowerEmit q c bits n

theorem lower_chain {q a : ℕ} (hq : 0<q) (es : List Edge) (h : lowerOK q a es) :
    (weight es : ℝ) ≤ (2:ℝ)^es.length * logTwo ((a:ℝ)/q) := by
  induction es generalizing a with
  | nil =>
    have hh : q ≤ a := of_decide_eq_true h
    have hq' : (0:ℝ)<q := by exact_mod_cast hq
    have ha : 1≤(a:ℝ)/q := by
      rw [le_div_iff₀ hq',one_mul]
      exact_mod_cast hh
    simpa [weight] using real_nonneg ha
  | cons e es ih =>
    rcases e with ⟨b,c⟩
    simp only [lowerOK, Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨ha,hc,hh⟩, he⟩ := h
    have hq' : (0:ℝ)<q := by exact_mod_cast hq
    have ha' : (0:ℝ)<a := by exact_mod_cast ha
    have hc' : (0:ℝ)<c := by exact_mod_cast hc
    have hraw : (factor b:ℝ)*c*q ≤ (a:ℝ)*a := by exact_mod_cast hh
    have hv : (factor b:ℝ)*((c:ℝ)/q) ≤ ((a:ℝ)/q)*((a:ℝ)/q) := by
      field_simp [hq'.ne']
      nlinarith only [hraw]
    have hb : (0:ℝ) < factor b := by cases b <;> norm_num [factor]
    have rz := logTwo_mono (mul_pos hb (div_pos hc' hq')) hv
    rw [log_mul hb (div_pos hc' hq'),log_mul (div_pos ha' hq') (div_pos ha' hq'),digit_factor] at rz
    have hw := mul_le_mul_of_nonneg_left rz (show 0≤(2:ℝ)^es.length by positivity)
    have hr := ih he
    simp only [List.length_cons, pow_succ, weight, Nat.cast_add, Nat.cast_mul,
      Nat.cast_pow, Nat.cast_ofNat]
    nlinarith only [hw,hr]

theorem certify_lower (q a n j bits : ℕ)
    (ha : 0<a) (hq : 0<q) (rep : n*q=2^j*a)
    (check : lowerOK q a (lowerEmit q a bits 112))
    (len : (lowerEmit q a bits 112).length=112) (wgt : weight (lowerEmit q a bits 112)=bits) :
    (j:ℝ) + (bits:ℝ)/2^112 ≤ logTwo (n:ℝ) := by
  have hq' : (0:ℝ)<q := by exact_mod_cast hq
  have ha' : (0:ℝ)<a := by exact_mod_cast ha
  have rr : (n:ℝ)=(2:ℝ)^j*(a/q) := by
    field_simp [hq'.ne']
    exact_mod_cast rep
  have hz := lower_chain hq (lowerEmit q a bits 112) check
  rw [len,wgt] at hz
  have hz' : (bits:ℝ)/2^112 ≤ logTwo ((a:ℝ)/q) := by
    rw [div_le_iff₀ (by positivity)]
    nlinarith only [hz]
  have hh : logTwo ((2:ℝ)^j) = (j:ℝ) := by
    simpa only [Real.rpow_natCast] using logTwo_two_rpow (j:ℝ)
  rw [rr,log_mul (by positivity) (div_pos ha' hq'),hh]
  linarith


end S008.Recount.Sharp
