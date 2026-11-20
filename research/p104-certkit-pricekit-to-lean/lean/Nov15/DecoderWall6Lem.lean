import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.FieldSimp
import Nov15.DecoderWall6Gen

/-! DecoderWall6Lem (lane RIGID): small field lemmas used by the generated ratio-transport files. -/
namespace DW6
variable {K : Type*} [Field K]

theorem nz_of {a e : K} [CharZero K] (h : a * e = 1 / 4) : a ≠ 0 := by
  rintro rfl; norm_num at h

/-- `0 = a e + b f`, `c e = 1/4`, `d f = 1/4` ⇒ `a d + b c = 0`. -/
theorem edge_core [CharZero K] {a b c d e f : K} (h0 : 0 = a * e + b * f) (he : c * e = 1 / 4) (hf : d * f = 1 / 4) :
    a * d + b * c = 0 := by
  linear_combination (-4 * c * d) * h0 - 4 * a * d * he - 4 * b * c * hf

/-- ratio transport across an edge: `a d + b c = 0`, signs with `sa sd = -(sb sc)` ⇒ `(a sa)/(b sb) = (c sc)/(d sd)`. -/
theorem edge_ratio {a b c d sa sb sc sd : K} (E : a * d + b * c = 0) (hs : sb * sc = -(sa * sd))
    (hb : b * sb ≠ 0) (hd : d * sd ≠ 0) : (a * sa) / (b * sb) = (c * sc) / (d * sd) := by
  rw [div_eq_div_iff hb hd]
  linear_combination (sa * sd) * E - (b * c) * hs

/-- the cocycle step: `pk/pa = tk/ta`, `t0/ta = r0/ra`, `t0/tk = k0/kb` ⇒ `pa (kb/k0) = pk (ra/r0)`. -/
theorem star_lemma {pa pk ta tk t0 ra r0 kb k0 : K} (hpa : pa ≠ 0) (htk : tk ≠ 0) (hta : ta ≠ 0)
    (ht0 : t0 ≠ 0) (hra : ra ≠ 0) (hr0 : r0 ≠ 0) (hkb : kb ≠ 0) (hk0 : k0 ≠ 0)
    (h1 : pk / pa = tk / ta) (h2 : t0 / ta = r0 / ra) (h3 : t0 / tk = k0 / kb) :
    pa * (kb / k0) = pk * (ra / r0) := by
  rw [div_eq_div_iff hpa hta] at h1
  rw [div_eq_div_iff hta hra] at h2
  rw [div_eq_div_iff htk hkb] at h3
  have key : (pa * kb * r0 - pk * ra * k0) * t0 = 0 := by
    linear_combination (pa * r0) * h3 - (r0 * k0) * h1 - (k0 * pk) * h2
  have h4 : pa * kb * r0 - pk * ra * k0 = 0 := by
    rcases mul_eq_zero.mp key with h | h
    · exact h
    · exact absurd h ht0
  rw [← mul_div_assoc, ← mul_div_assoc, div_eq_div_iff hk0 hr0]
  linear_combination h4

/-- the cocycle step when `k = 0` (`μ₀ = 1`). -/
theorem star0 {pa p0 ra r0 : K} (hpa : pa ≠ 0) (hra : ra ≠ 0) (hr0 : r0 ≠ 0) (h : p0 / pa = r0 / ra) :
    pa * 1 = p0 * (ra / r0) := by
  rw [div_eq_div_iff hpa hra] at h
  rw [mul_one, ← mul_div_assoc, eq_div_iff hr0]
  linear_combination (-1 : K) * h

/-- `x s mk = vk ma`, `s² = 1` ⇒ `x = s (vk/mk) ma`. -/
theorem xform {x s vk mk ma : K} (hs : s * s = 1) (hm : mk ≠ 0) (h : x * s * mk = vk * ma) :
    x = s * (vk / mk) * ma := by
  rw [show s * (vk / mk) * ma = (s * vk * ma) / mk by ring, eq_div_iff hm]
  linear_combination s * h - (x * mk) * hs

/-- `x y = 1/4`, `x = s a b`, `s² = 1` ⇒ `y = s / (4 a b)`. -/
theorem yform [CharZero K] {x y s a b : K} (hs : s * s = 1) (ha : a ≠ 0) (hb : b ≠ 0) (hx : x = s * a * b)
    (hxy : x * y = 1 / 4) : y = s / (4 * a * b) := by
  subst hx
  have hne : (4 : K) * a * b ≠ 0 := mul_ne_zero (mul_ne_zero (by norm_num) ha) hb
  rw [eq_div_iff hne]
  linear_combination (4 * s) * hxy - (4 * a * b * y) * hs

end DW6
