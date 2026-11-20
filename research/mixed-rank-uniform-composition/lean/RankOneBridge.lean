import Mathlib.Algebra.Module.LinearMap.End
import Mathlib.Tactic.Abel
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

namespace RankOneBridge

variable {R X Y : Type*} [CommRing R] [AddCommGroup X] [Module R X]
  [AddCommGroup Y] [Module R Y]

/-- Cross-bank additions. The head is read only. -/
def shear (K : X →ₗ[R] Y) (v : X × Y) : X × Y := (v.1, v.2 + K v.1)

/-- The rank-one residual after the head and tail elimination. -/
def residual (e : X) (b : Y) (a : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (d : R) (v : X × Y) : X × Y :=
  let t := a v.1 + d * Z v.2
  (v.1 + t • e, v.2 + t • b)

/-- Replace one head and one tail coordinate. Keep their complements. -/
def exchange (e : X) (z : Y) (E : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (d i : R) (v : X × Y) : X × Y :=
  (v.1 + (d * Z v.2 - E v.1) • e, v.2 + (i * E v.1 - Z v.2) • z)

/-- The cross-bank coefficients in the good branch of the leaf program. -/
def lower (e : X) (b z : Y) (E a : X →ₗ[R] R) (i : R) : X →ₗ[R] Y :=
  E.smulRight (-(b + i • z)) + (a - a e • E).smulRight (i • z)

theorem lower_at (e : X) (b z : Y) (E a : X →ₗ[R] R) (i : R)
    (he : E e = 1) : lower e b z E a i e = -(b + i • z) := by
  simp [lower, he]

theorem lower_row (e : X) (b z : Y) (E a : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (d i : R) (hi : d * i = 1) (hz : Z z = 1) (hc : a e + d * Z b = -2) (x : X) :
    d * Z (lower e b z E a i x) = a x + E x := by
  simp only [lower, LinearMap.add_apply, LinearMap.smulRight_apply, LinearMap.sub_apply,
    LinearMap.smul_apply, map_add, map_smul, map_neg, hz, smul_eq_mul, mul_one]
  calc
    _ = (d*i) * a x - E x * (d * Z b + d*i + (d*i) * a e) := by ring
    _ = _ := by rw [hi]; linear_combination -(E x) * hc

theorem shear_undo (K : X →ₗ[R] Y) (v : X × Y) :
    shear (-K) (shear K v) = v := by
  obtain ⟨x,y⟩ := v
  simp [shear]

theorem conjugated (e : X) (b z : Y) (E a : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (d i : R) (hi : d * i = 1) (he : E e = 1) (hz : Z z = 1)
    (hc : a e + d * Z b = -2) (v : X × Y) :
    let K := lower e b z E a i
    shear K (residual e b a Z d (shear (-K) v)) = exchange e z E Z d i v := by
  let K := lower e b z E a i
  change shear K (residual e b a Z d (shear (-K) v)) = exchange e z E Z d i v
  obtain ⟨x,y⟩ := v
  have hk : K e = -(b + i • z) := lower_at _ _ _ _ _ _ he
  have hr : d * Z (K x) = a x + E x := lower_row _ _ _ _ _ _ _ _ hi hz hc x
  have ht : a x + d * Z (y - K x) = d * Z y - E x := by
    rw [map_sub, mul_sub, hr]
    ring
  apply Prod.ext
  · simp only [shear, residual, exchange, LinearMap.neg_apply, ← sub_eq_add_neg, ht]
  · simp only [shear, residual, exchange, LinearMap.neg_apply, map_add,
      map_smul, ← sub_eq_add_neg, ht, hk]
    have hm : (d * Z y - E x) * i = Z y - i * E x := by
      calc _ = (d*i) * Z y - i * E x := by ring
           _ = _ := by rw [hi, one_mul]
    simp only [smul_neg, smul_add, smul_smul, hm, sub_smul]
    abel

/-- The program executes the lower shears, one weighted exchange, then their inverse. -/
theorem good_leaf (e : X) (b z : Y) (E a : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (d i : R) (hi : d * i = 1) (he : E e = 1) (hz : Z z = 1)
    (hc : a e + d * Z b = -2) (v : X × Y) :
    let K := lower e b z E a i
    shear (-K) (exchange e z E Z d i (shear K v)) = residual e b a Z d v := by
  let K := lower e b z E a i
  change shear (-K) (exchange e z E Z d i (shear K v)) = _
  rw [← conjugated e b z E a Z d i hi he hz hc (shear K v)]
  change shear (-K) (shear K (residual e b a Z d (shear (-K) (shear K v)))) = _
  rw [shear_undo, shear_undo]

def rowAdd (f : X →ₗ[R] R) (v : X) : X →ₗ[R] X := LinearMap.id + f.smulRight v

theorem rowAdd_apply (f : X →ₗ[R] R) (v x : X) : rowAdd f v x = x + f x • v := rfl

theorem rowAdd_undo (f : X →ₗ[R] R) (v x : X) (hz : f v = 0) :
    rowAdd f (-v) (rowAdd f v x) = x := by
  simp [rowAdd_apply, hz]

/-- A single rank-one displacement before the first local elimination. -/
def displaced (s : X) (t : Y) (α : X →ₗ[R] R) (β : Y →ₗ[R] R)
    (v : X × Y) : X × Y :=
  let t₀ := α v.1 + β v.2
  (v.1 + t₀ • s, v.2 + t₀ • t)

/-- The first head-to-head and tail-to-tail elimination, all cross-bank
    additions, one exchange and the inverse additions on both banks. -/
def program (e s : X) (z t : Y) (E α : X →ₗ[R] R) (Z β : Y →ₗ[R] R)
    (l li r ri : R) (v : X × Y) : X × Y :=
    let vH := e - li • s
    let fT := ri • β - Z
    let H := rowAdd E vH
    let H' := rowAdd E (-vH)
    let T := rowAdd fT z
    let T' := rowAdd fT (-z)
    let b := li • T t
    let a := l • (α.comp H')
    let K := lower e b z E a (li*ri)
    let out := shear (-K) (exchange e z E Z (l*r) (li*ri) (shear K (H v.1,T v.2)))
    (H' out.1, T' out.2)

theorem normalized_word (e s : X) (z t : Y) (E α : X →ₗ[R] R) (Z β : Y →ₗ[R] R)
    (l li r ri : R) (hl : l * li = 1) (hr : r * ri = 1)
    (he : E e = 1) (hz : Z z = 1) (hs : E s = l) (hb : β z = r)
    (hc : α s + β t = -2) (v : X × Y) :
    program e s z t E α Z β l li r ri v = displaced s t α β v := by
  let vH := e - li • s
  let fT := ri • β - Z
  let H := rowAdd E vH
  let H' := rowAdd E (-vH)
  let T := rowAdd fT z
  let T' := rowAdd fT (-z)
  let b := li • T t
  let a := l • (α.comp H')
  let K := lower e b z E a (li*ri)
  let v' := (H v.1,T v.2)
  let out := shear (-K) (exchange e z E Z (l*r) (li*ri) (shear K v'))
  change (H' out.1,T' out.2) = _
  have hl' : li * l = 1 := by rw [mul_comm, hl]
  have hr' : ri * r = 1 := by rw [mul_comm, hr]
  have hH : E vH = 0 := by simp [vH, he, hs, hl']
  have hT : fT z = 0 := by simp [fT, hz, hb, hr']
  have hHi (x : X) : H' (H x) = x := rowAdd_undo _ _ _ hH
  have hTi (y : Y) : T' (T y) = y := rowAdd_undo _ _ _ hT
  have hHe : H' e = li • s := by simp [H', rowAdd_apply, he, vH]
  have hHs : H s = l • e := by
    simp [H,rowAdd_apply,hs,vH,smul_sub,smul_smul,hl]
  have hZ (y : Y) : Z (T y) = ri * β y := by
    simp [T,rowAdd_apply, hz,fT]
  have hA (x : X) : a (H x) = l * α x := by simp [a,hHi]
  have hAe : a e = α s := by simp [a,hHe,← mul_assoc,hl]
  have hZb : (l*r) * Z b = β t := by
    change (l*r) * Z (li • T t) = β t
    simp only [map_smul, smul_eq_mul, hZ]
    calc _ = (l*li) * (r*ri) * β t := by ring
         _ = _ := by rw [hl,hr,one_mul,one_mul]
  have hd : (l*r) * (li*ri) = 1 := by
    calc _ = (l*li) * (r*ri) := by ring
         _ = _ := by rw [hl,hr,one_mul]
  have h₁ : out = residual e b a Z (l*r) v' := by
    exact good_leaf e b z E a Z _ _ hd he hz (by rw [hAe,hZb,hc]) v'
  let t₀ := α v.1 + β v.2
  have hφ : a (H v.1) + (l*r) * Z (T v.2) = l * t₀ := by
    rw [hA,hZ]
    change l * α v.1 + (l*r) * (ri * β v.2) = l * (α v.1 + β v.2)
    calc _ = l * α v.1 + l * (r*ri) * β v.2 := by ring
         _ = _ := by rw [hr,mul_one,mul_add]
  have hout : out = (H (v.1 + t₀ • s),T (v.2 + t₀ • t)) := by
    rw [h₁]
    simp only [residual,v',b,hφ,map_add,map_smul,hHs,smul_smul]
    have hh : l * t₀ * li = t₀ := by
      calc _ = (l*li) * t₀ := by ring
           _ = _ := by rw [hl,one_mul]
    rw [hh,mul_comm l t₀]
  rw [hout,hHi,hTi]
  rfl

def partialExchange (P : X →ₗ[R] X) (v : X × X) : X × X :=
  let δ := P (v.2 - v.1)
  (v.1 + δ, v.2 - δ)

def weighted (P : X →ₗ[R] X) (A : X ≃ₗ[R] X) (C : X ≃ₗ[R] Y)
    (v : X × Y) : X × Y :=
  let w := partialExchange P (A.symm v.1,C.symm v.2)
  (A w.1,C w.2)

/-- The entire good branch acts on an arbitrary split rank-one projector,
    invertible head weights and physical tail placement. -/
theorem whole_good (u e : X) (z : Y) (V E : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (A : X ≃ₗ[R] X) (C : X ≃ₗ[R] Y)
    (l li r ri : R) (hl : l * li = 1) (hr : r * ri = 1)
    (hu : V u = 1) (he : E e = 1) (hz : Z z = 1)
    (hs : E (A u) = l) (hb : V (C.symm z) = r) (v : X × Y) :
    program e (A u) z (-(C u)) E (-(V.comp A.symm.toLinearMap)) Z
      (V.comp C.symm.toLinearMap) l li r ri v = weighted (V.smulRight u) A C v := by
  rw [normalized_word _ _ _ _ _ _ _ _ _ _ _ _ hl hr he hz hs hb (by simp [hu]; ring)]
  apply Prod.ext <;>
    simp only [weighted,partialExchange,displaced,LinearMap.smulRight_apply,
      LinearMap.neg_apply,LinearMap.comp_apply,LinearEquiv.coe_coe,map_add,map_smul,
      LinearEquiv.apply_symm_apply,smul_neg,sub_eq_add_neg,map_neg,add_smul,neg_smul] <;>
    abel

/-- One inverse of the actual weighted pivot gives both elementary reductions. -/
theorem covered_good (u e : X) (z : Y) (V E : X →ₗ[R] R) (Z : Y →ₗ[R] R)
    (A : X ≃ₗ[R] X) (C : X ≃ₗ[R] Y) (di : R)
    (hu : V u = 1) (he : E e = 1) (hz : Z z = 1)
    (hd : E (A u) * V (C.symm z) * di = 1) (v : X × Y) :
    let l := E (A u)
    let r := V (C.symm z)
    program e (A u) z (-(C u)) E (-(V.comp A.symm.toLinearMap)) Z
      (V.comp C.symm.toLinearMap) l (r*di) r (l*di) v = weighted (V.smulRight u) A C v := by
  apply whole_good
  · rwa [← mul_assoc]
  · calc _ = E (A u) * V (C.symm z) * di := by ring
         _ = 1 := hd
  · exact hu
  · exact he
  · exact hz
  · rfl
  · rfl

end RankOneBridge

#print axioms RankOneBridge.good_leaf
#print axioms RankOneBridge.normalized_word
#print axioms RankOneBridge.whole_good
#print axioms RankOneBridge.covered_good
