/-
UniRowsPMath (lane ROWS2, Nov 19).  Digit algebra behind the packed row checker (UniRowsPDefs):
* `nat_digits`  : V < 2^(W n) ⇒ V = Σ_{o<n} dig o V · 2^(W o).
* `int_inj`     : Σ_{o<n} x_o · 2^(W o) = 0 with |x_o| < 2^W ⇒ every x_o = 0.
* `dig_lt_of_bnd` : `bnd` (one AND + compare) ⇒ every digit < 2K.
* `pz`, `pz_lin`, `pz_abs` : the signed digit vector of a valid packing, its linear identity and bound.
* `comb_sound`, `add_sound`, `pz_Z0`, `pz_eq` : exactness of the packed ADD / SCALE / birth steps.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.UniRowsSound
import Nov15.UniRowsPDefs

set_option linter.unusedSectionVars false

namespace UniRowsP
open Finset

def dig (W o V : ℕ) : ℕ := V / 2 ^ (W * o) % 2 ^ W

theorem dig_succ (W o V : ℕ) : dig W (o + 1) V = dig W o (V / 2 ^ W) := by
  unfold dig; rw [Nat.div_div_eq_div_mul, ← pow_add]; congr 3; ring

theorem nat_digits (W : ℕ) : ∀ (n V : ℕ), V < 2 ^ (W * n) →
    (V : ℤ) = ∑ o ∈ range n, (dig W o V : ℤ) * 2 ^ (W * o) := by
  intro n
  induction n with
  | zero => intro V h; simp at h; simp [h]
  | succ n ih =>
    intro V h
    have h1 : V / 2 ^ W < 2 ^ (W * n) := by
      rw [Nat.div_lt_iff_lt_mul (by positivity), ← pow_add]; rw [show W * n + W = W * (n + 1) by ring]; exact h
    rw [sum_range_succ']
    have e1 : ∑ o ∈ range n, (dig W (o + 1) V : ℤ) * 2 ^ (W * (o + 1)) =
        2 ^ W * ∑ o ∈ range n, (dig W o (V / 2 ^ W) : ℤ) * 2 ^ (W * o) := by
      rw [mul_sum]; refine sum_congr rfl (fun o _ => ?_); rw [dig_succ]; ring
    rw [e1, ← ih _ h1]
    have : (dig W 0 V : ℤ) = ((V % 2 ^ W : ℕ) : ℤ) := by simp [dig]
    rw [this]; simp only [mul_zero, pow_zero, mul_one]
    have := Nat.div_add_mod V (2 ^ W)
    zify at this; push_cast; linarith

theorem int_inj (W : ℕ) : ∀ (n : ℕ) (x : ℕ → ℤ), (∀ o < n, |x o| < 2 ^ W) →
    ∑ o ∈ range n, x o * 2 ^ (W * o) = 0 → ∀ o < n, x o = 0 := by
  intro n
  induction n with
  | zero => intro x _ _ o ho; omega
  | succ n ih =>
    intro x hx hs
    rw [sum_range_succ'] at hs
    have e1 : ∑ o ∈ range n, x (o + 1) * 2 ^ (W * (o + 1)) = 2 ^ W * ∑ o ∈ range n, x (o + 1) * 2 ^ (W * o) := by
      rw [mul_sum]; refine sum_congr rfl (fun o _ => ?_); ring
    rw [e1] at hs
    simp only [mul_zero, pow_zero, mul_one] at hs
    have hd : (2 : ℤ) ^ W ∣ x 0 := ⟨-(∑ o ∈ range n, x (o + 1) * 2 ^ (W * o)), by linarith⟩
    have h0 : x 0 = 0 := Int.eq_zero_of_abs_lt_dvd hd (hx 0 (by omega))
    rw [h0, add_zero] at hs
    have hp : (2 : ℤ) ^ W ≠ 0 := by positivity
    have hT := (mul_eq_zero.1 hs).resolve_left hp
    have := ih (fun o => x (o + 1)) (fun o ho => hx (o + 1) (by omega)) hT
    intro o ho
    cases o with
    | zero => exact h0
    | succ o => exact this o (by omega)

theorem rp_sum (W c : ℕ) : ∀ n, (rp W c n : ℤ) = ∑ o ∈ range n, (c : ℤ) * 2 ^ (W * o) := by
  intro n
  induction n with
  | zero => simp [rp]
  | succ n ih =>
    rw [sum_range_succ']
    have e1 : ∑ o ∈ range n, (c : ℤ) * 2 ^ (W * (o + 1)) = 2 ^ W * ∑ o ∈ range n, (c : ℤ) * 2 ^ (W * o) := by
      rw [mul_sum]; refine sum_congr rfl (fun o _ => ?_); ring
    rw [e1, ← ih]; simp [rp]

theorem testBit_rp (W c : ℕ) (hc : c < 2 ^ W) : ∀ n j,
    Nat.testBit (rp W c n) j = (decide (j < W * n) && Nat.testBit c (j % W)) := by
  intro n
  induction n with
  | zero => intro j; simp [rp]
  | succ n ih =>
    intro j
    simp only [rp]
    rw [Nat.testBit_two_pow_mul_add _ hc]
    by_cases h : j < W
    · rw [if_pos h, Nat.mod_eq_of_lt h]
      have : j < W * (n + 1) := by rw [Nat.mul_add, Nat.mul_one]; omega
      simp [this]
    · rw [if_neg h, ih]
      have e1 : j % W = (j - W + W) % W := by congr 1; omega
      rw [e1, Nat.add_mod_right]
      have : (j - W < W * n) ↔ (j < W * (n + 1)) := by rw [Nat.mul_add, Nat.mul_one]; omega
      simp only [this]

theorem testBit_gap (W m i : ℕ) (hm : m ≤ W) (h1 : m ≤ i) (h2 : i < W) : Nat.testBit (2 ^ W - 2 ^ m) i = true := by
  have e : 2 ^ W - 2 ^ m = (2 ^ (W - m) - 1) <<< m := by
    rw [Nat.shiftLeft_eq, Nat.sub_mul, one_mul, ← pow_add, Nat.sub_add_cancel hm]
  rw [e, Nat.testBit_shiftLeft, Nat.testBit_two_pow_sub_one]
  simp only [ge_iff_le, h1, decide_true, Bool.true_and, decide_eq_true_eq]; omega

/-- `bnd` ⇒ digits < 2^(kb+1) and V < 2^(W·NO). -/
theorem dig_lt_of_bnd {k : Pk} (hk : k.okb = true) {V : ℕ} (h : bnd k V = true) :
    V < 2 ^ (k.W * k.NO) ∧ ∀ o < k.NO, dig k.W o V < 2 ^ (k.kb + 1) := by
  simp only [Pk.okb, Bool.and_eq_true, Nat.beq_eq, Nat.ble_eq] at hk
  obtain ⟨⟨⟨⟨⟨_, _⟩, hkW⟩, _⟩, hM⟩, hBN⟩ := hk
  simp only [bnd, Bool.and_eq_true, Nat.beq_eq, Nat.blt_eq] at h
  obtain ⟨hA, hL⟩ := h
  refine ⟨hBN ▸ hL, fun o ho => ?_⟩
  apply Nat.lt_pow_two_of_testBit
  intro i hi
  unfold dig
  rw [Nat.testBit_mod_two_pow, Nat.testBit_div_two_pow]
  by_cases hiW : i < k.W
  · simp only [hiW, decide_true, Bool.true_and]
    have hc : 2 ^ k.W - 2 ^ (k.kb + 1) < 2 ^ k.W := by
      have : 0 < 2 ^ (k.kb + 1) := by positivity
      have : 2 ^ (k.kb + 1) ≤ 2 ^ k.W := Nat.pow_le_pow_right (by norm_num) (by omega)
      omega
    have hb := congrArg (fun x => Nat.testBit x (i + k.W * o)) hA
    simp only [Nat.testBit_and, Nat.zero_testBit, hM, testBit_rp _ _ hc] at hb
    have hlt : i + k.W * o < k.W * k.NO := by
      have : k.W * (o + 1) ≤ k.W * k.NO := Nat.mul_le_mul_left _ ho
      rw [Nat.mul_add, Nat.mul_one] at this; omega
    have hmod : (i + k.W * o) % k.W = i := by rw [Nat.add_mul_mod_self_left, Nat.mod_eq_of_lt hiW]
    rw [hmod, testBit_gap _ _ _ (by omega) hi hiW] at hb
    simpa [hlt] using hb
  · simp [hiW]

/-- the signed digit vector of a packing. -/
def pz (k : Pk) (V o : ℕ) : ℤ := if o < k.NO then (dig k.W o V : ℤ) - k.K else 0

theorem okb_parts {k : Pk} (hk : k.okb = true) :
    k.B = 2 ^ k.W ∧ k.K = 2 ^ k.kb ∧ k.kb + 2 ≤ k.W ∧ k.Z0 = rp k.W k.K k.NO := by
  simp only [Pk.okb, Bool.and_eq_true, Nat.beq_eq, Nat.ble_eq] at hk
  exact ⟨hk.1.1.1.1.1, hk.1.1.1.1.2, hk.1.1.1.2, hk.1.1.2⟩

theorem pz_abs {k : Pk} (hk : k.okb = true) {V : ℕ} (h : bnd k V = true) (o : ℕ) : |pz k V o| ≤ k.K := by
  obtain ⟨_, hK, _, _⟩ := okb_parts hk
  unfold pz
  split_ifs with ho
  · have := (dig_lt_of_bnd hk h).2 o ho
    rw [pow_succ, ← hK] at this
    rw [abs_le]; constructor <;> push_cast <;> omega
  · simp

theorem pz_lin {k : Pk} (hk : k.okb = true) {V : ℕ} (h : bnd k V = true) :
    (V : ℤ) - k.Z0 = ∑ o ∈ range k.NO, pz k V o * 2 ^ (k.W * o) := by
  obtain ⟨_, _, _, hZ⟩ := okb_parts hk
  rw [nat_digits k.W k.NO V (dig_lt_of_bnd hk h).1, hZ, rp_sum, ← sum_sub_distrib]
  refine sum_congr rfl (fun o ho => ?_)
  rw [mem_range] at ho; simp only [pz, if_pos ho]; ring

theorem kB {k : Pk} (hk : k.okb = true) : 4 * (k.K : ℤ) ≤ 2 ^ k.W := by
  obtain ⟨_, hK, hkW, _⟩ := okb_parts hk
  have h1 : 2 ^ (k.kb + 2) ≤ 2 ^ k.W := Nat.pow_le_pow_right (by norm_num) hkW
  have h4 : 4 * k.K ≤ 2 ^ k.W := by rw [pow_add, ← hK] at h1; norm_num at h1; omega
  exact_mod_cast h4

theorem pz_bd {k : Pk} (hk : k.okb = true) {V : ℕ} (h : bnd k V = true) (o : ℕ) :
    -(k.K : ℤ) ≤ pz k V o ∧ pz k V o ≤ k.K := abs_le.1 (pz_abs hk h o)

theorem pz_Z0 {k : Pk} (hk : k.okb = true) (hZ : bnd k k.Z0 = true) (o : ℕ) : pz k k.Z0 o = 0 := by
  by_cases ho : o < k.NO
  · have hl := pz_lin hk hZ
    rw [sub_self] at hl
    have hK := kB hk
    exact int_inj k.W k.NO (pz k k.Z0) (fun o _ => by
      have := pz_bd hk hZ o; have h0 : (0 : ℤ) ≤ k.K := by positivity
      have h2 : (0 : ℤ) < 2 ^ k.W := by positivity
      rw [abs_lt]; constructor <;> linarith [this.1, this.2]) hl.symm o ho
  · simp [pz, ho]

/-- packed ADD / SCALE step. -/
theorem comb_sound {k : Pk} (hk : k.okb = true) {Va Vr V p q : ℕ} {neg : Bool} (ha : bnd k Va = true)
    (hr : bnd k Vr = true) (hq : q ≠ 0) (hc : k.K * (2 * q + p) < k.B) (h : comb k Va Vr neg p q = some V) :
    bnd k V = true ∧ ∀ o, (pz k V o : ℚ) = pz k Va o + ((if neg then -(p : ℤ) else p : ℤ) : ℚ) / (q : ℚ) * pz k Vr o := by
  obtain ⟨hB, _, _, _⟩ := okb_parts hk
  unfold comb at h
  obtain ⟨h1, h2⟩ := UniInhabit.cond_some h
  simp only [Bool.and_eq_true, Nat.ble_eq, Nat.beq_eq] at h1
  obtain ⟨⟨hle, hdv⟩, hbV⟩ := h1
  generalize hN : cond neg (Va * q + p * k.Z0) (Va * q + p * Vr) = N at hle hdv hbV h2
  generalize hS : cond neg (p * Vr) (p * k.Z0) = S at hle hdv hbV h2
  have hVe : (N - S) / q = V := Option.some.inj h2
  have hq1 : q * ((N - S) / q) = N - S := Nat.mul_div_cancel' (Nat.dvd_of_mod_eq_zero hdv)
  rw [hVe] at hq1 hbV
  refine ⟨hbV, ?_⟩
  have hqZ := congrArg (Nat.cast : ℕ → ℤ) hq1
  rw [Nat.cast_mul, Nat.cast_sub hle] at hqZ
  have hNS : (N : ℤ) - S = q * Va + (if neg then -(p : ℤ) else p) * ((Vr : ℤ) - k.Z0) := by
    rw [← hN, ← hS]; cases neg <;> simp only [cond_true, cond_false, Bool.false_eq_true, ↓reduceIte] <;>
      push_cast <;> ring
  have hid : (q : ℤ) * ((V : ℤ) - k.Z0) - q * ((Va : ℤ) - k.Z0) - (if neg then -(p : ℤ) else p) * ((Vr : ℤ) - k.Z0) = 0 := by
    linear_combination hqZ + hNS
  rw [pz_lin hk hbV, pz_lin hk ha, pz_lin hk hr, mul_sum, mul_sum, mul_sum, ← sum_sub_distrib,
    ← sum_sub_distrib] at hid
  have hps : (if neg then -(p : ℤ) else p) = p ∨ (if neg then -(p : ℤ) else p) = -p := by
    cases neg <;> simp
  have hB' : (k.K : ℤ) * (2 * q + p) < 2 ^ k.W := by have h' := hc; rw [hB] at h'; exact_mod_cast h'
  have hz := int_inj k.W k.NO (fun o => (q : ℤ) * pz k V o - q * pz k Va o - (if neg then -(p : ℤ) else p) * pz k Vr o)
    (fun o _ => by
      try dsimp only
      obtain ⟨a1, a1'⟩ := pz_bd hk hbV o; obtain ⟨a2, a2'⟩ := pz_bd hk ha o; obtain ⟨a3, a3'⟩ := pz_bd hk hr o
      have q0 : (0 : ℤ) ≤ q := by positivity
      have p0 : (0 : ℤ) ≤ p := by positivity
      have m1 := mul_le_mul_of_nonneg_left a1' q0; have m1' := mul_le_mul_of_nonneg_left a1 q0
      have m2 := mul_le_mul_of_nonneg_left a2' q0; have m2' := mul_le_mul_of_nonneg_left a2 q0
      have m3 := mul_le_mul_of_nonneg_left a3' p0; have m3' := mul_le_mul_of_nonneg_left a3 p0
      rw [abs_lt]
      rcases hps with e | e <;> rw [e] <;> constructor <;> linarith)
    (Eq.trans (sum_congr rfl (fun o _ => by (try dsimp only); ring)) hid)
  intro o
  by_cases ho : o < k.NO
  · have := hz o ho
    try dsimp only at this
    have hq' : (q : ℚ) ≠ 0 := by exact_mod_cast hq
    have e : ((q : ℤ) : ℚ) * pz k V o - q * pz k Va o - (((if neg then -(p : ℤ) else p : ℤ)) : ℚ) * pz k Vr o = 0 := by
      exact_mod_cast this
    field_simp
    push_cast at e ⊢; linarith
  · simp [pz, ho]

/-- packed birth step: a' = g + a. -/
theorem add_sound {k : Pk} (hk : k.okb = true) {Vg Va : ℕ} (hg : bnd k Vg = true) (ha : bnd k Va = true)
    (hle : k.Z0 ≤ Vg + Va) (hV : bnd k (Vg + Va - k.Z0) = true) :
    ∀ o, pz k (Vg + Va - k.Z0) o = pz k Vg o + pz k Va o := by
  have hid : ((Vg + Va - k.Z0 : ℕ) : ℤ) - k.Z0 - ((Vg : ℤ) - k.Z0) - ((Va : ℤ) - k.Z0) = 0 := by
    push_cast [hle]; ring
  rw [pz_lin hk hV, pz_lin hk hg, pz_lin hk ha, ← sum_sub_distrib, ← sum_sub_distrib] at hid
  have hK := kB hk
  have hz := int_inj k.W k.NO (fun o => pz k (Vg + Va - k.Z0) o - pz k Vg o - pz k Va o) (fun o _ => by
    try dsimp only
    have a1 := pz_bd hk hV o; have a2 := pz_bd hk hg o; have a3 := pz_bd hk ha o
    have h0 : (0 : ℤ) ≤ k.K := by positivity
    have h2 : (0 : ℤ) < 2 ^ k.W := by positivity
    rw [abs_lt]; constructor <;> linarith [a1.1, a1.2, a2.1, a2.2, a3.1, a3.2])
    (Eq.trans (sum_congr rfl (fun o _ => by (try dsimp only); ring)) hid)
  intro o
  by_cases ho : o < k.NO
  · have := hz o ho; (try dsimp only at this); linarith
  · simp [pz, ho]

/-- read a packing off an explicit small digit vector. -/
theorem pz_eq {k : Pk} (hk : k.okb = true) {V : ℕ} (h : bnd k V = true) (x : ℕ → ℤ) (hx : ∀ o < k.NO, |x o| ≤ k.K)
    (hs : (V : ℤ) - k.Z0 = ∑ o ∈ range k.NO, x o * 2 ^ (k.W * o)) : ∀ o < k.NO, pz k V o = x o := by
  rw [pz_lin hk h] at hs
  have hK := kB hk
  have hz := int_inj k.W k.NO (fun o => pz k V o - x o) (fun o ho => by
    try dsimp only
    have a1 := pz_bd hk h o; have a2 := abs_le.1 (hx o ho)
    have h0 : (0 : ℤ) ≤ k.K := by positivity
    have h2 : (0 : ℤ) < 2 ^ k.W := by positivity
    rw [abs_lt]; constructor <;> linarith [a1.1, a1.2, a2.1, a2.2])
    (by rw [sum_congr rfl (fun o _ => sub_mul (pz k V o) (x o) _), sum_sub_distrib, hs, sub_self])
  intro o ho; have := hz o ho; (try dsimp only at this); linarith

end UniRowsP
