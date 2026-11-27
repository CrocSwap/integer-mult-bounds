import S008.WalshAligned

/-! Exact integer midpoint bounds for the actual odd-width Walsh return operation. -/
namespace Moonshot.AlignedWalsh

/-- Magnitude nearest to t/√q, selecting the upper integer in a tie. -/
def midpointSpec (q t r : ℕ) : Prop :=
  (r = 0 ∨ q*(2*r-1)^2 ≤ 4*t^2) ∧ 4*t^2 < q*(2*r+1)^2

def roundedWord (q t S A : ℕ) : ℕ :=
  let j := (2*t*A+S)/(2*S)
  if q*(2*j+1)^2 ≤ 4*t^2 then j+1 else j

theorem rounded_word_spec {q t S A : ℕ} (hq : 0 < q) (hS : 0 < S) (ht : t ≤ S)
    (hlo : q*A^2 ≤ S^2) (hhi : S^2 < q*(A+1)^2) :
    midpointSpec q t (roundedWord q t S A) := by
  let j := (2*t*A+S)/(2*S)
  have hfloor : j*(2*S) ≤ 2*t*A+S := Nat.div_mul_le_self _ _
  have hceil : 2*t*A+S < (2*S)*(j+1) := Nat.lt_mul_div_succ _ (by omega)
  have hceil' : 2*t*A < (2*j+1)*S := by
    rw [show (2*S)*(j+1)=(2*j+1)*S+S by ring] at hceil
    omega
  have hthird : 2*t*(A+1) < (2*j+3)*S := calc
    _ = 2*t*A + 2*t := by ring
    _ < (2*j+1)*S + 2*S := add_lt_add_of_lt_of_le hceil' (Nat.mul_le_mul_left 2 ht)
    _ = _ := by ring
  have hup : 4*t^2 < q*(2*j+3)^2 := by
    apply Nat.lt_of_mul_lt_mul_right (a := S^2)
    calc
      _ ≤ (4*t^2)*(q*(A+1)^2) := Nat.mul_le_mul_left _ hhi.le
      _ = q*(2*t*(A+1))^2 := by ring
      _ < q*((2*j+3)*S)^2 := Nat.mul_lt_mul_of_pos_left (Nat.pow_lt_pow_left hthird (by decide)) hq
      _ = _ := by ring
  have hdown (hj : 0 < j) : q*(2*j-1)^2 ≤ 4*t^2 := by
    have hj' : 1 ≤ 2*j := by omega
    have h1 : (2*j-1)*S + S = j*(2*S) := calc
      _ = (2*j-1+1)*S := by ring
      _ = _ := by rw [Nat.sub_add_cancel hj']; ring
    have h2 : (2*j-1)*S ≤ 2*t*A := by omega
    apply Nat.le_of_mul_le_mul_right (c := S^2) _ (by positivity)
    calc
      _ = q*((2*j-1)*S)^2 := by ring
      _ ≤ q*(2*t*A)^2 := Nat.mul_le_mul_left _ (Nat.pow_le_pow_left h2 2)
      _ = (4*t^2)*(q*A^2) := by ring
      _ ≤ _ := Nat.mul_le_mul_left _ hlo
  change midpointSpec q t (if q*(2*j+1)^2 ≤ 4*t^2 then j+1 else j)
  split_ifs with hit
  · unfold midpointSpec
    rw [show 2*(j+1)-1=2*j+1 by omega, show 2*(j+1)+1=2*j+3 by omega]
    exact ⟨Or.inr hit,hup⟩
  · refine ⟨?_, lt_of_not_ge hit⟩
    by_cases hz : j=0
    · exact Or.inl hz
    · exact Or.inr (hdown (Nat.pos_of_ne_zero hz))

/-- The caller's J=w+s+3 and integer square root provide the exact midpoint bracket. -/
theorem dyadic_rounding_spec {w s t : ℕ} (ht : t < 2^(w+s)) :
    let J := w+s+3
    let S := 2^J
    let q := 2^s
    let A := Nat.sqrt (2^(2*J-s))
    midpointSpec q t (roundedWord q t S A) := by
  let J := w+s+3
  let n := 2^(2*J-s)
  change midpointSpec (2^s) t (roundedWord (2^s) t (2^J) n.sqrt)
  have hJ : s ≤ 2*J := by dsimp [J]; omega
  have hn : 2^s*n = (2^J)^2 := calc
    _ = 2^(2*J-s)*2^s := by dsimp [n]; ac_rfl
    _ = 2^(2*J) := Nat.pow_sub_mul_pow 2 hJ
    _ = _ := by rw [← pow_mul]; congr 1; omega
  apply rounded_word_spec (by positivity) (by positivity)
  · exact ht.le.trans (Nat.pow_le_pow_right (by decide) (by dsimp [J]; omega))
  · rw [← hn]
    exact Nat.mul_le_mul_left _ (by simpa [pow_two] using Nat.sqrt_le n)
  · rw [← hn]
    exact Nat.mul_lt_mul_of_pos_left (Nat.lt_succ_sqrt' n) (by positivity)


/-- The squared midpoint specification selects exactly one magnitude, including rational ties. -/
theorem midpoint_unique {q t r s : ℕ} (hr : midpointSpec q t r) (hs : midpointSpec q t s) :
    r = s := by
  have contra {a b : ℕ} (ha : midpointSpec q t a) (hb : midpointSpec q t b) (hab : a < b) :
      False := by
    have hb0 : b ≠ 0 := by omega
    have hl := hb.1.resolve_left hb0
    have hle : q*(2*a+1)^2 ≤ q*(2*b-1)^2 :=
      Nat.mul_le_mul_left _ (Nat.pow_le_pow_left (by omega) 2)
    exact (Nat.not_lt_of_ge (hle.trans hl)) ha.2
  exact le_antisymm (le_of_not_gt (contra hs hr)) (le_of_not_gt (contra hr hs))

end Moonshot.AlignedWalsh
