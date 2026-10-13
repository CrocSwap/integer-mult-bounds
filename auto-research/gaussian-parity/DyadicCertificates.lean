import Std

/-!
# Gaussian parity certificates for normalized butterflies

This file uses Lean's integer arithmetic and kernel-checked `omega` proofs.
There are no project axioms, omitted proofs, or external mathematical libraries.
The pair `GInt` represents the Gaussian integer `re + im*i`.
-/

namespace GaussianParity

structure GInt where
  re : Int
  im : Int
  deriving DecidableEq, Repr

def add (u v : GInt) : GInt := ⟨u.re + v.re, u.im + v.im⟩
def mulI (z : GInt) : GInt := ⟨-z.im, z.re⟩
def mulPi (z : GInt) : GInt := ⟨z.re - z.im, z.re + z.im⟩
def dividePi (z : GInt) : GInt := ⟨(z.re + z.im) / 2, (z.im - z.re) / 2⟩
def residue (z : GInt) : Int := (z.re + z.im) % 2
def PiDvd (z : GInt) : Prop := z.re % 2 = z.im % 2
def SameResidue (u v : GInt) : Prop := residue u = residue v
def numeratorLeft (u v : GInt) : GInt := add (mulI u) v
def numeratorRight (u v : GInt) : GInt := add u (mulI v)
def butterfly (u v : GInt) : GInt × GInt :=
  (dividePi (numeratorLeft u v), dividePi (numeratorRight u v))

theorem GInt.ext {u v : GInt} (hre : u.re = v.re) (him : u.im = v.im) : u = v := by
  cases u; cases v; simp_all

/-- The residue is the quotient map Z[i] -> F2, written with integer residues. -/
theorem residue_zero_iff (z : GInt) : residue z = 0 ↔ PiDvd z := by
  simp only [residue, PiDvd]
  omega

/-- Division by 1+i is exact precisely on its Gaussian ideal. -/
theorem dividePi_exact_iff (z : GInt) : mulPi (dividePi z) = z ↔ PiDvd z := by
  constructor
  · intro h
    have hr := congrArg GInt.re h
    have hi := congrArg GInt.im h
    simp only [mulPi, dividePi] at hr hi
    simp only [PiDvd]
    omega
  · intro h
    apply GInt.ext
    · simp only [mulPi, dividePi, PiDvd] at *
      omega
    · simp only [mulPi, dividePi, PiDvd] at *
      omega

theorem dividePi_mulPi (z : GInt) : dividePi (mulPi z) = z := by
  apply GInt.ext <;> simp only [dividePi, mulPi] <;> omega

/-- Both butterfly numerators are divisible by 1+i exactly when inputs agree
in Z[i]/(1+i). This only checks one parity bit per Gaussian integer. -/
theorem butterfly_integral_iff (u v : GInt) :
    PiDvd (numeratorLeft u v) ∧ PiDvd (numeratorRight u v) ↔ SameResidue u v := by
  simp only [PiDvd, numeratorLeft, numeratorRight, add, mulI, SameResidue, residue]
  omega

theorem butterfly_exact (u v : GInt) (h : SameResidue u v) :
    mulPi (butterfly u v).1 = numeratorLeft u v ∧
    mulPi (butterfly u v).2 = numeratorRight u v := by
  have hp := (butterfly_integral_iff u v).mpr h
  exact ⟨(dividePi_exact_iff _).mpr hp.1, (dividePi_exact_iff _).mpr hp.2⟩

/-- The admissible pair lattice is stable under its own butterfly. -/
theorem butterfly_sameResidue (u v : GInt) (h : SameResidue u v) :
    SameResidue (butterfly u v).1 (butterfly u v).2 := by
  simp only [SameResidue, residue, butterfly, dividePi, numeratorLeft,
    numeratorRight, add, mulI] at *
  omega

/-- On the admissible pair lattice, the normalized butterfly squared is swap. -/
theorem butterfly_square (u v : GInt) (h : SameResidue u v) :
    butterfly (butterfly u v).1 (butterfly u v).2 = (v, u) := by
  apply Prod.ext
  · apply GInt.ext
    · simp only [butterfly, dividePi, numeratorLeft, numeratorRight, add, mulI,
        SameResidue, residue] at *
      omega
    · simp only [butterfly, dividePi, numeratorLeft, numeratorRight, add, mulI,
        SameResidue, residue] at *
      omega
  · apply GInt.ext
    · simp only [butterfly, dividePi, numeratorLeft, numeratorRight, add, mulI,
        SameResidue, residue] at *
      omega
    · simp only [butterfly, dividePi, numeratorLeft, numeratorRight, add, mulI,
        SameResidue, residue] at *
      omega

/-- Gaussian phase rotation preserves the residue. -/
theorem residue_mulI (z : GInt) : residue (mulI z) = residue z := by
  simp only [residue, mulI]
  omega

/-- Addition propagates the residue by addition in F2. -/
theorem residue_add (u v : GInt) : residue (add u v) = (residue u + residue v) % 2 := by
  simp only [residue, add]
  omega

/-- Every Gaussian multiple of 1+i has zero residue. -/
theorem residue_mulPi (z : GInt) : residue (mulPi z) = 0 := by
  simp only [residue, mulPi]
  omega

/-- Componentwise parity equality is sufficient but stronger than required. -/
theorem component_parity_implies_sameResidue (u v : GInt)
    (hre : u.re % 2 = v.re % 2) (him : u.im % 2 = v.im % 2) : SameResidue u v := by
  simp only [SameResidue, residue]
  omega

/-- The valid input pair (1,i) refutes necessity of componentwise parity. -/
theorem cross_parity_example :
    SameResidue ⟨1, 0⟩ ⟨0, 1⟩ ∧
    (⟨1, 0⟩ : GInt).re % 2 ≠ (⟨0, 1⟩ : GInt).re % 2 ∧
    butterfly ⟨1, 0⟩ ⟨0, 1⟩ = (⟨1, 1⟩, ⟨0, 0⟩) := by
  simp [SameResidue, residue, butterfly, dividePi, numeratorLeft, numeratorRight, add, mulI]

/-- A first admissible layer need not make a differently paired second layer
admissible. Four original inputs all have the same Gaussian residue. -/
theorem changed_pairing_obstruction :
    SameResidue ⟨1, 0⟩ ⟨1, 0⟩ ∧ SameResidue ⟨1, 0⟩ ⟨0, 1⟩ ∧
    ¬ SameResidue (butterfly ⟨1, 0⟩ ⟨1, 0⟩).1
       (butterfly ⟨1, 0⟩ ⟨0, 1⟩).1 := by
  simp [SameResidue, residue, butterfly, dividePi, numeratorLeft, numeratorRight, add, mulI]

/-- Repeated multiplication by pi=1+i, used to compare exact denominator tags. -/
def piIter : Nat → GInt → GInt
  | 0, z => z
  | n + 1, z => mulPi (piIter n z)

theorem piIter_mulPi (n : Nat) (z : GInt) :
    piIter n (mulPi z) = mulPi (piIter n z) := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [piIter, ih]

theorem piIter_add (n m : Nat) (z : GInt) :
    piIter (n + m) z = piIter n (piIter m z) := by
  induction n with
  | zero => simp only [Nat.zero_add, piIter]
  | succ n ih => simp only [Nat.succ_add, piIter, ih]

theorem piIter_commute (n m : Nat) (z : GInt) :
    piIter n (piIter m z) = piIter m (piIter n z) := by
  rw [← piIter_add, ← piIter_add, Nat.add_comm]

theorem mulPi_injective {u v : GInt} (h : mulPi u = mulPi v) : u = v := by
  apply GInt.ext
  · have hr := congrArg GInt.re h
    have hi := congrArg GInt.im h
    simp only [mulPi] at hr hi
    omega
  · have hr := congrArg GInt.re h
    have hi := congrArg GInt.im h
    simp only [mulPi] at hr hi
    omega

theorem piIter_injective (n : Nat) {u v : GInt} (h : piIter n u = piIter n v) : u = v := by
  induction n with
  | zero => exact h
  | succ n ih => exact ih (mulPi_injective h)

/-- The exact formal fraction numerator / pi^exponent. -/
structure Fraction where
  numerator : GInt
  exponent : Nat
  deriving DecidableEq, Repr

def SameValue (x y : Fraction) : Prop :=
  piIter y.exponent x.numerator = piIter x.exponent y.numerator

theorem SameValue.refl (x : Fraction) : SameValue x x := rfl
theorem SameValue.symm {x y : Fraction} (h : SameValue x y) : SameValue y x := Eq.symm h

theorem SameValue.trans {x y z : Fraction} (hxy : SameValue x y) (hyz : SameValue y z) :
    SameValue x z := by
  unfold SameValue at *
  apply piIter_injective y.exponent
  calc
    piIter y.exponent (piIter z.exponent x.numerator)
        = piIter z.exponent (piIter y.exponent x.numerator) := piIter_commute _ _ _
    _ = piIter z.exponent (piIter x.exponent y.numerator) := congrArg (piIter z.exponent) hxy
    _ = piIter x.exponent (piIter z.exponent y.numerator) := piIter_commute _ _ _
    _ = piIter x.exponent (piIter y.exponent z.numerator) := congrArg (piIter x.exponent) hyz
    _ = piIter y.exponent (piIter x.exponent z.numerator) := piIter_commute _ _ _

structure PackedPair where
  left : GInt
  right : GInt
  exponent : Nat
  deriving DecidableEq, Repr

/-- A total, exact step. Success removes pi; failure records one denominator
unit instead of applying inexact integer division. -/
def certifiedButterfly (u v : GInt) (e : Nat) : PackedPair :=
  if residue u = residue v then
    ⟨(butterfly u v).1, (butterfly u v).2, e⟩
  else
    ⟨numeratorLeft u v, numeratorRight u v, e + 1⟩

theorem certifiedButterfly_contract (u v : GInt) (e : Nat) :
    let p := certifiedButterfly u v e
    (p.exponent = e ∧ mulPi p.left = numeratorLeft u v ∧
      mulPi p.right = numeratorRight u v) ∨
    (p.exponent = e + 1 ∧ p.left = numeratorLeft u v ∧ p.right = numeratorRight u v) := by
  by_cases h : residue u = residue v
  · left
    have hc := butterfly_exact u v h
    simp [certifiedButterfly, h, hc.1, hc.2]
  · right
    simp [certifiedButterfly, h]

theorem certifiedButterfly_refines (u v : GInt) (e : Nat) :
    let p := certifiedButterfly u v e
    SameValue ⟨p.left, p.exponent⟩ ⟨numeratorLeft u v, e + 1⟩ ∧
    SameValue ⟨p.right, p.exponent⟩ ⟨numeratorRight u v, e + 1⟩ := by
  by_cases h : residue u = residue v
  · have hc := butterfly_exact u v h
    simp only [certifiedButterfly, h, ↓reduceIte, SameValue, piIter]
    constructor
    · rw [← piIter_mulPi, hc.1]
    · rw [← piIter_mulPi, hc.2]
  · simp [certifiedButterfly, h, SameValue]

theorem certifiedButterfly_exponent_bound (u v : GInt) (e : Nat) :
    e ≤ (certifiedButterfly u v e).exponent ∧
    (certifiedButterfly u v e).exponent ≤ e + 1 := by
  unfold certifiedButterfly
  split <;> simp <;> omega

def neg (z : GInt) : GInt := ⟨-z.re, -z.im⟩
def mulNegI (z : GInt) : GInt := ⟨z.im, -z.re⟩
def inverseButterfly (u v : GInt) : GInt × GInt :=
  (mulNegI (butterfly u (neg v)).1, mulI (butterfly u (neg v)).2)

/-- The inverse wrapper -i Z C Z equals X C on admissible pairs. -/
theorem inverseButterfly_eq_swap (u v : GInt) (h : SameResidue u v) :
    inverseButterfly u v = ((butterfly u v).2, (butterfly u v).1) := by
  apply Prod.ext <;> apply GInt.ext <;>
    simp only [inverseButterfly, neg, mulNegI, butterfly, dividePi, numeratorLeft,
      numeratorRight, add, mulI, SameResidue, residue] at * <;> omega

theorem inverseButterfly_after (u v : GInt) (h : SameResidue u v) :
    inverseButterfly (butterfly u v).1 (butterfly u v).2 = (u, v) := by
  rw [inverseButterfly_eq_swap _ _ (butterfly_sameResidue u v h)]
  have hs := butterfly_square u v h
  have hl := congrArg (fun p : GInt × GInt => p.1) hs
  have hr := congrArg (fun p : GInt × GInt => p.2) hs
  exact Prod.ext hr hl

def butterflyPair (p : GInt × GInt) : GInt × GInt := butterfly p.1 p.2

theorem butterfly_fourth (u v : GInt) (h : SameResidue u v) :
    butterflyPair (butterflyPair (butterflyPair (butterflyPair (u, v)))) = (u, v) := by
  have hs := butterfly_square u v h
  have hvu : SameResidue v u := Eq.symm h
  change butterflyPair (butterflyPair (butterfly (butterfly u v).1 (butterfly u v).2)) = _
  rw [hs]
  exact butterfly_square v u hvu

/-- Twice C has Gaussian integer coordinates, all four with one common parity. -/
def doubleButterfly (u v : GInt) : GInt × GInt :=
  (⟨u.re - u.im + v.re + v.im, u.re + u.im - v.re + v.im⟩,
   ⟨u.re + u.im + v.re - v.im, -u.re + u.im + v.re + v.im⟩)

theorem doubleButterfly_joint_parity (u v : GInt) :
    (doubleButterfly u v).1.re % 2 = (u.re + u.im + v.re + v.im) % 2 ∧
    (doubleButterfly u v).1.im % 2 = (u.re + u.im + v.re + v.im) % 2 ∧
    (doubleButterfly u v).2.re % 2 = (u.re + u.im + v.re + v.im) % 2 ∧
    (doubleButterfly u v).2.im % 2 = (u.re + u.im + v.re + v.im) % 2 := by
  simp only [doubleButterfly]
  omega

/-- One retained bit records the common half-integer defect of four coordinates. -/
def sharedDefect (u v : GInt) : Int := (u.re + u.im + v.re + v.im) % 2

theorem sharedDefect_is_bit (u v : GInt) :
    sharedDefect u v = 0 ∨ sharedDefect u v = 1 := by
  simp only [sharedDefect]
  omega

theorem sharedDefect_zero_iff (u v : GInt) :
    sharedDefect u v = 0 ↔ SameResidue u v := by
  simp only [sharedDefect, SameResidue, residue]
  omega

/-- Euclidean integer quotients plus the shared bit reconstruct all four
numerators of twice C. This is an exact identity, including negative inputs. -/
theorem shared_defect_reconstruction (u v : GInt) :
    let n := doubleButterfly u v
    let epsilon := sharedDefect u v
    n.1.re = 2 * (n.1.re / 2) + epsilon ∧
    n.1.im = 2 * (n.1.im / 2) + epsilon ∧
    n.2.re = 2 * (n.2.re / 2) + epsilon ∧
    n.2.im = 2 * (n.2.im / 2) + epsilon := by
  simp only [doubleButterfly, sharedDefect]
  omega

def scaleTwo (z : GInt) : GInt := ⟨2 * z.re, 2 * z.im⟩

theorem doubleButterfly_exact (u v : GInt) (h : SameResidue u v) :
    doubleButterfly u v = (scaleTwo (butterfly u v).1, scaleTwo (butterfly u v).2) := by
  apply Prod.ext <;> apply GInt.ext <;>
    simp only [doubleButterfly, scaleTwo, butterfly, dividePi, numeratorLeft,
      numeratorRight, add, mulI, SameResidue, residue] at * <;> omega

/-- The ordinary half-Hadamard has a different, stronger integrality guard. -/
def halfHadamard (u v : GInt) : GInt × GInt :=
  (⟨(u.re + v.re) / 2, (u.im + v.im) / 2⟩,
   ⟨(u.re - v.re) / 2, (u.im - v.im) / 2⟩)

theorem halfHadamard_exact_iff (u v : GInt) :
    (scaleTwo (halfHadamard u v).1 = add u v ∧
     scaleTwo (halfHadamard u v).2 = add u (neg v)) ↔
    (u.re % 2 = v.re % 2 ∧ u.im % 2 = v.im % 2) := by
  constructor
  · intro h
    have hr := congrArg GInt.re h.1
    have hi := congrArg GInt.im h.1
    simp only [scaleTwo, halfHadamard, add] at hr hi
    omega
  · intro h
    constructor <;> apply GInt.ext <;>
      simp only [scaleTwo, halfHadamard, add, neg] <;> omega

theorem cross_parity_fails_halfHadamard :
    ¬ (scaleTwo (halfHadamard ⟨1, 0⟩ ⟨0, 1⟩).1 = add ⟨1, 0⟩ ⟨0, 1⟩) := by
  decide

/-- Aligning denominator tags is exact; its arithmetic work must still be charged. -/
def raiseTo (x : Fraction) (e : Nat) : Fraction :=
  ⟨piIter (e - x.exponent) x.numerator, e⟩

theorem raiseTo_sameValue (x : Fraction) (e : Nat) (h : x.exponent ≤ e) :
    SameValue (raiseTo x e) x := by
  unfold SameValue raiseTo
  simp only
  rw [← piIter_add]
  have he : x.exponent + (e - x.exponent) = e := by omega
  rw [he]

def commonExponent (x y : Fraction) : Nat := max x.exponent y.exponent

/-- Arbitrary input tags are first aligned, then passed through the total checker. -/
def alignedButterfly (x y : Fraction) : PackedPair :=
  let e := commonExponent x y
  certifiedButterfly (raiseTo x e).numerator (raiseTo y e).numerator e

theorem alignedButterfly_input_exact (x y : Fraction) :
    SameValue (raiseTo x (commonExponent x y)) x ∧
    SameValue (raiseTo y (commonExponent x y)) y := by
  constructor
  · apply raiseTo_sameValue
    exact Nat.le_max_left _ _
  · apply raiseTo_sameValue
    exact Nat.le_max_right _ _

theorem alignedButterfly_refines (x y : Fraction) :
    let e := commonExponent x y
    let u := (raiseTo x e).numerator
    let v := (raiseTo y e).numerator
    let p := alignedButterfly x y
    SameValue ⟨p.left, p.exponent⟩ ⟨numeratorLeft u v, e + 1⟩ ∧
    SameValue ⟨p.right, p.exponent⟩ ⟨numeratorRight u v, e + 1⟩ := by
  exact certifiedButterfly_refines _ _ _

end GaussianParity

#print axioms GaussianParity.butterfly_integral_iff
#print axioms GaussianParity.butterfly_exact
#print axioms GaussianParity.butterfly_sameResidue
#print axioms GaussianParity.butterfly_square
#print axioms GaussianParity.changed_pairing_obstruction
#print axioms GaussianParity.SameValue.trans
#print axioms GaussianParity.certifiedButterfly_refines
#print axioms GaussianParity.inverseButterfly_after
#print axioms GaussianParity.butterfly_fourth
#print axioms GaussianParity.doubleButterfly_joint_parity
#print axioms GaussianParity.halfHadamard_exact_iff
#print axioms GaussianParity.raiseTo_sameValue
#print axioms GaussianParity.alignedButterfly_refines
#print axioms GaussianParity.sharedDefect_zero_iff
#print axioms GaussianParity.shared_defect_reconstruction
