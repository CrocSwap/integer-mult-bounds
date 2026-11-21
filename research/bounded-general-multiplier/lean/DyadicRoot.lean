import Std

/-! Integer certificates for bounds on a positive rational power. The checker
stores a power of two outside each mantissa. Its soundness statement uses the
complete mathematical integers, including when they have trillions of bits. -/
namespace DyadicRoot

structure Sci where
  mant : Nat
  scale : Nat
  deriving Repr

def val (x : Sci) := x.mant * 2^x.scale

def roundUp (m u : Nat) := m/u + if m%u = 0 then 0 else 1

theorem roundUp_spec (m u : Nat) (hu : 0<u) : m ≤ roundUp m u * u := by
  have eqn := Nat.div_add_mod' m u
  have rem := Nat.mod_lt m hu
  by_cases he : m%u = 0
  · simp only [roundUp, he, ite_true, Nat.add_zero]
    omega
  · simp only [roundUp, he, ite_false, Nat.add_mul, Nat.one_mul]
    omega

def multiply (bits : Nat) (up : Bool) (x y : Sci) : Sci :=
  let m := x.mant*y.mant
  let trim := m.log2 - bits
  let u := 2^trim
  ⟨if up then roundUp m u else m/u, trim + (x.scale+y.scale)⟩

theorem low_mul (bits : Nat) (x y : Sci) :
    val (multiply bits false x y) ≤ val x * val y := by
  let m := x.mant*y.mant
  let trim := m.log2-bits
  have hlo := Nat.div_mul_le_self m (2^trim)
  have hm := Nat.mul_le_mul_right (2^(x.scale+y.scale)) hlo
  unfold val multiply
  simp only [Bool.false_eq_true, ite_false, Nat.pow_add] at *
  simpa only [m, trim, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hm

theorem high_mul (bits : Nat) (x y : Sci) :
    val x * val y ≤ val (multiply bits true x y) := by
  let m := x.mant*y.mant
  let trim := m.log2-bits
  have hhi := roundUp_spec m (2^trim) (Nat.pow_pos (by decide))
  have hm := Nat.mul_le_mul_right (2^(x.scale+y.scale)) hhi
  unfold val multiply
  simp only [ite_true, Nat.pow_add] at *
  simpa only [m, trim, Nat.mul_assoc, Nat.mul_comm, Nat.mul_left_comm] using hm

def digits : Nat → Nat → List Bool
  | 0, _ => []
  | fuel+1, e => if e=0 then [] else (e%2 == 1) :: digits fuel (e/2)

def exponent : List Bool → Nat
  | [] => 0
  | b::bs => (if b then 1 else 0) + (exponent bs + exponent bs)

def powered (bits : Nat) (up : Bool) (x : Sci) : List Bool → Sci
  | [] => ⟨1,0⟩
  | b::bs =>
    let r := powered bits up x bs
    let z := multiply bits up r r
    if b then multiply bits up x z else z

theorem low_pow (bits : Nat) (x : Sci) (bs : List Bool) :
    val (powered bits false x bs) ≤ val x ^ exponent bs := by
  induction bs with
  | nil => simp [powered, exponent, val]
  | cons b bs ih =>
    let r := powered bits false x bs
    have h := Nat.le_trans (low_mul bits r r) (Nat.mul_le_mul ih ih)
    cases b with
    | false => simpa [powered, exponent, Nat.pow_add, r] using h
    | true =>
      have hh := Nat.le_trans (low_mul bits x (multiply bits false r r)) (Nat.mul_le_mul_left (val x) h)
      simpa [powered, exponent, Nat.pow_add, r] using hh

theorem high_pow (bits : Nat) (x : Sci) (bs : List Bool) :
    val x ^ exponent bs ≤ val (powered bits true x bs) := by
  induction bs with
  | nil => simp [powered, exponent, val]
  | cons b bs ih =>
    let r := powered bits true x bs
    have h := Nat.le_trans (Nat.mul_le_mul ih ih) (high_mul bits r r)
    cases b with
    | false => simpa [powered, exponent, Nat.pow_add, r] using h
    | true =>
      have hh := Nat.le_trans (Nat.mul_le_mul_left (val x) h) (high_mul bits x (multiply bits true r r))
      simpa [powered, exponent, Nat.pow_add, r] using hh

def shift (s : Nat) (x : Sci) : Sci := ⟨x.mant, x.scale+s⟩

theorem val_shift (s : Nat) (x : Sci) : val (shift s x) = val x * 2^s :=
  by simp [val, shift, Nat.pow_add, Nat.mul_assoc]

def leTest (x y : Sci) : Bool :=
  if x.scale ≤ y.scale then decide (x.mant ≤ y.mant * 2^(y.scale-x.scale))
  else decide (x.mant * 2^(x.scale-y.scale) ≤ y.mant)

theorem leTest_sound (x y : Sci) (ht : leTest x y = true) : val x ≤ val y := by
  by_cases h : x.scale ≤ y.scale
  · have hr : x.mant ≤ y.mant * 2^(y.scale-x.scale) := by simpa [leTest,h] using ht
    have hs : y.scale-x.scale+x.scale=y.scale := by omega
    have hm := Nat.mul_le_mul_right (2^x.scale) hr
    simpa only [val, Nat.mul_assoc, ←Nat.pow_add, hs] using hm
  · have hr : x.mant * 2^(x.scale-y.scale) ≤ y.mant := by simpa [leTest,h] using ht
    have hs : x.scale-y.scale+y.scale=x.scale := by omega
    have hm := Nat.mul_le_mul_right (2^y.scale) hr
    simpa only [val, Nat.mul_assoc, ←Nat.pow_add, hs] using hm

structure Claim where
  rank : Nat
  num : Nat
  den : Nat
  lo : Nat
  hi : Nat

def valid (bits frac : Nat) (c : Claim) : Bool :=
  let m := digits 64 c.num
  let d := digits 64 c.den
  let k : Sci := ⟨c.rank,0⟩
  exponent m == c.num && exponent d == c.den && c.den > 0 &&
  leTest (powered bits true ⟨c.lo,0⟩ d) (shift (frac*c.den) (powered bits false k m)) &&
  leTest (shift (frac*c.den) (powered bits true k m)) (powered bits false ⟨c.hi,0⟩ d)

theorem valid_sound (bits frac : Nat) (c : Claim) (ok : valid bits frac c = true) :
    0 < c.den ∧ c.lo^c.den ≤ c.rank^c.num * 2^(frac*c.den) ∧
      c.rank^c.num * 2^(frac*c.den) ≤ c.hi^c.den := by
  let m := digits 64 c.num
  let d := digits 64 c.den
  let k : Sci := ⟨c.rank,0⟩
  simp only [valid, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at ok
  obtain ⟨⟨⟨⟨hm,hd⟩,hpos⟩,hl⟩,hu⟩ := ok
  have lo := Nat.le_trans (high_pow bits ⟨c.lo,0⟩ d) (leTest_sound _ _ hl)
  have hi := Nat.le_trans (leTest_sound _ _ hu) (low_pow bits ⟨c.hi,0⟩ d)
  rw [val_shift] at lo hi
  have lowMiddle := Nat.mul_le_mul_right (2^(frac*c.den)) (low_pow bits k m)
  have highMiddle := Nat.mul_le_mul_right (2^(frac*c.den)) (high_pow bits k m)
  refine ⟨hpos, ?_, ?_⟩
  · simpa [m,d,k,val,hm,hd] using Nat.le_trans lo lowMiddle
  · simpa [m,d,k,val,hm,hd] using Nat.le_trans highMiddle hi

end DyadicRoot

#print axioms DyadicRoot.valid_sound
