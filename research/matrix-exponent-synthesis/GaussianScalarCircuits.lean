import DyadicCertificates
import GaussianLattice

/-!
Exact Gaussian scalar arithmetic with heterogeneous pi-denominator tags.
The imported certificate modules are unchanged. Arithmetic equality is SameValue,
so arbitrary dirty scratch values and noncanonical denominators are permitted.
-/

namespace GaussianSynthesis
open GaussianParity

/-- Cancel a pi factor when the checked residue permits exact division.
The denominator tag is a decreasing termination measure; zero reaches tag zero. -/
def normalizeCore : Nat → GInt → Fraction
  | 0, z => ⟨z, 0⟩
  | e+1, z =>
      if residue z = 0 then normalizeCore e (dividePi z) else ⟨z, e+1⟩

def normalize (x : Fraction) : Fraction := normalizeCore x.exponent x.numerator

def Canonical (x : Fraction) : Prop := x.exponent = 0 ∨ residue x.numerator ≠ 0

theorem cancelPi_sameValue (z : GInt) (e : Nat) (h : residue z = 0) :
    SameValue ⟨dividePi z, e⟩ ⟨z, e+1⟩ := by
  have hx := (dividePi_exact_iff z).mpr ((residue_zero_iff z).mp h)
  simp only [SameValue, piIter]
  rw [← piIter_mulPi, hx]

theorem normalizeCore_sound (e : Nat) (z : GInt) :
    SameValue (normalizeCore e z) ⟨z, e⟩ := by
  induction e generalizing z with
  | zero => exact SameValue.refl _
  | succ e ih =>
    by_cases h : residue z = 0
    · simp only [normalizeCore, h, ↓reduceIte]
      exact SameValue.trans (ih _) (cancelPi_sameValue z e h)
    · simp only [normalizeCore, h, ↓reduceIte]
      exact SameValue.refl _

theorem normalize_sound (x : Fraction) : SameValue (normalize x) x := by
  exact normalizeCore_sound x.exponent x.numerator

theorem normalizeCore_canonical (e : Nat) (z : GInt) :
    Canonical (normalizeCore e z) := by
  induction e generalizing z with
  | zero => exact Or.inl rfl
  | succ e ih =>
    by_cases h : residue z = 0
    · simp only [normalizeCore, h, ↓reduceIte]
      exact ih _
    · simp only [normalizeCore, h, ↓reduceIte, Canonical]
      exact Or.inr h

theorem normalize_canonical (x : Fraction) : Canonical (normalize x) :=
  normalizeCore_canonical _ _

theorem normalize_fixed (x : Fraction) (h : Canonical x) : normalize x = x := by
  cases x with
  | mk z e =>
    cases e with
    | zero => rfl
    | succ e =>
      have hz : residue z ≠ 0 := by
        simp only [Canonical] at h
        omega
      simp [normalize, normalizeCore, hz]

theorem normalize_idempotent (x : Fraction) : normalize (normalize x) = normalize x :=
  normalize_fixed _ (normalize_canonical x)

theorem normalizeCore_exponent_bound (e : Nat) (z : GInt) :
    (normalizeCore e z).exponent ≤ e := by
  induction e generalizing z with
  | zero => simp [normalizeCore]
  | succ e ih =>
    by_cases h : residue z = 0
    · simp only [normalizeCore, h, ↓reduceIte]
      exact Nat.le_trans (ih _) (Nat.le_succ _)
    · simp [normalizeCore, h]

theorem normalize_zero (e : Nat) : normalize ⟨⟨0,0⟩,e⟩ = ⟨⟨0,0⟩,0⟩ := by
  unfold normalize
  induction e with
  | zero => rfl
  | succ e ih => simpa [normalizeCore, residue, dividePi] using ih

theorem positive_piIter_residue (e : Nat) (z : GInt) (h : 0 < e) :
    residue (piIter e z) = 0 := by
  cases e with
  | zero => omega
  | succ e => exact residue_mulPi _

/-- A canonical representation cannot acquire a strictly larger denominator
without introducing a detectable pi factor in its numerator. -/
theorem canonical_tags_equal {x y : Fraction}
    (hx : Canonical x) (hy : Canonical y) (h : SameValue x y) :
    x.exponent = y.exponent := by
  have no_less : ∀ a b : Fraction, Canonical b → SameValue a b →
      ¬ a.exponent < b.exponent := by
    intro a b hb hab hlt
    have hdiff : a.exponent + (b.exponent-a.exponent) = b.exponent := by omega
    have hp : 0 < b.exponent-a.exponent := by omega
    have heq : piIter (b.exponent-a.exponent) a.numerator = b.numerator := by
      apply piIter_injective a.exponent
      rw [← piIter_add, hdiff]
      exact hab
    have hz := positive_piIter_residue (b.exponent-a.exponent) a.numerator hp
    rw [heq] at hz
    simp only [Canonical] at hb
    omega
  have hxy := no_less x y hy h
  have hyx := no_less y x hx (SameValue.symm h)
  omega

/-- Canonicalization yields a unique exact representative, including zero. -/
theorem canonical_unique {x y : Fraction}
    (hx : Canonical x) (hy : Canonical y) (h : SameValue x y) : x = y := by
  have he := canonical_tags_equal hx hy h
  have hn : x.numerator = y.numerator := by
    apply piIter_injective x.exponent
    unfold SameValue at h
    rw [← he] at h
    exact h
  cases x; cases y; simp_all

theorem normalize_congr {x y : Fraction} (h : SameValue x y) :
    normalize x = normalize y := by
  apply canonical_unique (normalize_canonical x) (normalize_canonical y)
  exact SameValue.trans (normalize_sound x)
    (SameValue.trans h (SameValue.symm (normalize_sound y)))

end GaussianSynthesis

#print axioms GaussianSynthesis.normalize_sound
#print axioms GaussianSynthesis.normalize_idempotent
#print axioms GaussianSynthesis.canonical_unique
#print axioms GaussianSynthesis.normalize_congr

namespace GaussianSynthesis

/-!
## PR46 mixed-center producer image

These contracts describe the concrete h=28,d=19 scalar producer using integer
coordinates. They apply independently to real and imaginary numerators of any
common Gaussian dyadic grid. The incidence relation Σ_i G_i=3T is an explicit
hypothesis, so arbitrary dirty center contents are never silently assumed to
belong to the producer image.
-/

def mixedCenterN (sumB sumD : Int) : Int := sumB - 2*sumD

/-- The actual 19+9 center split has image identity N=-32T. -/
theorem mixed_center_image (T sumInsideG sumOutsideG sumD sumB : Int)
    (hG : sumInsideG + sumOutsideG = 3*T)
    (hD : sumD = 19*T-sumInsideG)
    (hB : sumB = 2*sumOutsideG) :
    mixedCenterN sumB sumD = -32*T := by
  simp only [mixedCenterN]
  omega

/-- Reading the total from fresh centers loses no bits, including for negative
integer coordinates. This does not assume arbitrary dirty centers are fresh. -/
theorem fresh_total_recovery (T sumInsideG sumOutsideG sumD sumB : Int)
    (hG : sumInsideG + sumOutsideG = 3*T)
    (hD : sumD = 19*T-sumInsideG)
    (hB : sumB = 2*sumOutsideG) :
    mixedCenterN sumB sumD / (-32) = T := by
  rw [mixed_center_image T sumInsideG sumOutsideG sumD sumB hG hD hB]
  omega

/-- A doubled incidence center can likewise be halved exactly on the image. -/
theorem fresh_doubled_center (G B : Int) (h : B = 2*G) : B/2 = G := by
  omega

/-- The literal scatter formula collected over denominator 64. -/
def scatterNumerator64 (sumSelectedB sumSelectedD N k : Int) : Int :=
  16*sumSelectedB - 32*sumSelectedD - (k-1)*N

/-- Substituting the producer image cancels five of the apparent six
binary denominator bits: W/64 = (selectedG-T)/2. -/
theorem fresh_scatter_denominator_cancellation
    (T selectedInsideG selectedOutsideG selectedD selectedB N k : Int)
    (hD : selectedD = k*T-selectedInsideG)
    (hB : selectedB = 2*selectedOutsideG)
    (hN : N = -32*T) :
    scatterNumerator64 selectedB selectedD N k =
      32*(selectedInsideG+selectedOutsideG-T) := by
  simp only [scatterNumerator64]
  subst selectedD
  subst selectedB
  subst N
  grind

/-- Correct side injections make each scalar column integral; j is the
intersection size of its source and target triples. -/
def correctedBulkCoefficientNumerator (j : Int) : Int :=
  j-1 + (if j=0 then 1 else 0) - (if j=2 then 1 else 0)

theorem corrected_bulk_coefficient (j : Int) (hj : 0 ≤ j ∧ j ≤ 3) :
    correctedBulkCoefficientNumerator j = (if j=3 then 2 else 0) := by
  unfold correctedBulkCoefficientNumerator
  split <;> split <;> split <;> omega

/-- A dirty off-image center value exposes the denominator that would be
lost by applying the fresh-image total recovery without its hypotheses. -/
theorem dirty_center_obstruction :
    mixedCenterN 1 0 = 1 ∧ ¬ ∃ T : Int, mixedCenterN 1 0 = -32*T := by
  simp only [mixedCenterN]
  constructor
  · decide
  · omega

/-- Subtract the previous scratch contents before treating a center update
as a fresh producer value. Arbitrary initial scratch need not be zero. -/
theorem dirty_center_difference_is_fresh (old produced : Int) :
    (old+produced)-old = produced := by omega

end GaussianSynthesis

#print axioms GaussianSynthesis.mixed_center_image
#print axioms GaussianSynthesis.fresh_total_recovery
#print axioms GaussianSynthesis.fresh_scatter_denominator_cancellation
#print axioms GaussianSynthesis.corrected_bulk_coefficient
#print axioms GaussianSynthesis.dirty_center_obstruction

namespace GaussianSynthesis

/-- Aggregate center coordinates of the actual mixed-center producer.
The two scalar sums are sufficient for the shared correction N. -/
structure CenterTotals where
  total : Int
  sumD : Int
  sumB : Int
  deriving DecidableEq, Repr

def centerPlus (u v : CenterTotals) : CenterTotals :=
  ⟨u.total+v.total, u.sumD+v.sumD, u.sumB+v.sumB⟩

/-- A source triple contributes to k of the first 19 incidence centers and
3-k of the last nine incidence centers. Its scalar value is unrestricted. -/
def centerColumn (x k : Int) : CenterTotals :=
  ⟨x, (19-k)*x, 2*(3-k)*x⟩

def sumCenterColumns : List (Int × Int) → CenterTotals
  | [] => ⟨0,0,0⟩
  | (x,k)::xs => centerPlus (centerColumn x k) (sumCenterColumns xs)

def InCenterImage (c : CenterTotals) : Prop :=
  mixedCenterN c.sumB c.sumD = -32*c.total

/-- The producer image identity holds source-column by source-column,
without assuming any relation between distinct input values. -/
theorem centerColumn_image (x k : Int) : InCenterImage (centerColumn x k) := by
  simp only [InCenterImage, centerColumn, mixedCenterN]
  grind

theorem centerPlus_image (u v : CenterTotals)
    (hu : InCenterImage u) (hv : InCenterImage v) : InCenterImage (centerPlus u v) := by
  simp only [InCenterImage, centerPlus, mixedCenterN] at *
  omega

/-- Thus an arbitrary list of fresh source values produces centers with
N=-32T. No fresh-image premise is assumed in this theorem. -/
theorem arbitrary_fresh_columns_image (xs : List (Int × Int)) :
    InCenterImage (sumCenterColumns xs) := by
  induction xs with
  | nil => simp [InCenterImage, sumCenterColumns, mixedCenterN]
  | cons x xs ih => exact centerPlus_image _ _ (centerColumn_image x.1 x.2) ih

theorem arbitrary_fresh_columns_total (xs : List (Int × Int)) :
    mixedCenterN (sumCenterColumns xs).sumB (sumCenterColumns xs).sumD / (-32)
      = (sumCenterColumns xs).total := by
  have h := arbitrary_fresh_columns_image xs
  simp only [InCenterImage] at h
  rw [h]
  omega

/-- Dirty scratch may be arbitrary. Its update difference, rather than its
raw contents, has the fresh producer invariant. -/
theorem dirty_update_difference_image (oldD oldB : Int) (xs : List (Int × Int)) :
    mixedCenterN
      ((oldB+(sumCenterColumns xs).sumB)-oldB)
      ((oldD+(sumCenterColumns xs).sumD)-oldD)
      = -32*(sumCenterColumns xs).total := by
  have h := arbitrary_fresh_columns_image xs
  simp only [InCenterImage, mixedCenterN] at *
  omega

/-- Merely adding a valid fresh image to dirty centers leaves the old defect
present; this identity guards against applying image-aware division too early. -/
theorem raw_dirty_update_defect (oldD oldB : Int) (xs : List (Int × Int)) :
    mixedCenterN (oldB+(sumCenterColumns xs).sumB)
      (oldD+(sumCenterColumns xs).sumD)
      = mixedCenterN oldB oldD - 32*(sumCenterColumns xs).total := by
  have h := arbitrary_fresh_columns_image xs
  simp only [InCenterImage, mixedCenterN] at *
  omega

end GaussianSynthesis

#print axioms GaussianSynthesis.arbitrary_fresh_columns_image
#print axioms GaussianSynthesis.arbitrary_fresh_columns_total
#print axioms GaussianSynthesis.dirty_update_difference_image
#print axioms GaussianSynthesis.raw_dirty_update_defect

namespace GaussianSynthesis

def correctedScatterColumn64 (x j : Int) : Int :=
  32*(j-1)*x + 32*(if j=0 then x else 0) - 32*(if j=2 then x else 0)

/-- With the actual disjoint and intersection-two side terms, each column
of the collected scatter is 64 times its diagonal source value. -/
theorem corrected_scatter_column_exact (x j : Int) (hj : 0 ≤ j ∧ j ≤ 3) :
    correctedScatterColumn64 x j = 64*(if j=3 then x else 0) := by
  unfold correctedScatterColumn64
  have hc := corrected_bulk_coefficient j hj
  unfold correctedBulkCoefficientNumerator at hc
  split <;> split <;> split <;> grind

def sumCorrectedScatter64 : List (Int × Int) → Int
  | [] => 0
  | (x,j)::xs => correctedScatterColumn64 x j + sumCorrectedScatter64 xs

def sumDiagonalSources : List (Int × Int) → Int
  | [] => 0
  | (x,j)::xs => (if j=3 then x else 0) + sumDiagonalSources xs

/-- Arbitrary fresh scalar input values superpose exactly; the only hypothesis
is that each triple intersection size lies between zero and three. -/
theorem corrected_scatter_sum_exact (xs : List (Int × Int))
    (hj : ∀ entry ∈ xs, 0 ≤ entry.2 ∧ entry.2 ≤ 3) :
    sumCorrectedScatter64 xs = 64*sumDiagonalSources xs := by
  induction xs with
  | nil => simp [sumCorrectedScatter64, sumDiagonalSources]
  | cons entry xs ih =>
    have hfirst := hj entry (by simp)
    have hrest : ∀ e ∈ xs, 0 ≤ e.2 ∧ e.2 ≤ 3 := by
      intro e he
      exact hj e (by simp [he])
    simp only [sumCorrectedScatter64, sumDiagonalSources]
    rw [corrected_scatter_column_exact _ _ hfirst, ih hrest]
    grind

theorem corrected_scatter_sum_integral (xs : List (Int × Int))
    (hj : ∀ entry ∈ xs, 0 ≤ entry.2 ∧ entry.2 ≤ 3) :
    sumCorrectedScatter64 xs / 64 = sumDiagonalSources xs := by
  rw [corrected_scatter_sum_exact xs hj]
  omega

/-- One fractional bit in the fresh bulk scatter is necessary in general:
a source triple disjoint from the target contributes -1/2 before side repair. -/
theorem fresh_bulk_half_sharp : ¬ ∃ z : Int, 2*z = (0-1)*(1 : Int) := by
  omega

end GaussianSynthesis

#print axioms GaussianSynthesis.corrected_scatter_column_exact
#print axioms GaussianSynthesis.corrected_scatter_sum_exact
#print axioms GaussianSynthesis.corrected_scatter_sum_integral
#print axioms GaussianSynthesis.fresh_bulk_half_sharp

namespace GaussianSynthesis
open GaussianParity

/-- The unconditionally exact C step retains a pi denominator unit. It is
valid for arbitrary Gaussian numerators, including dirty scratch. -/
def rawC (u v : GInt) (e : Nat) : PackedPair :=
  ⟨numeratorLeft u v, numeratorRight u v, e+1⟩

def packedLeft (p : PackedPair) : Fraction := ⟨p.left,p.exponent⟩
def packedRight (p : PackedPair) : Fraction := ⟨p.right,p.exponent⟩

theorem rawC_left_square (u v : GInt) :
    numeratorLeft (numeratorLeft u v) (numeratorRight u v) = mulPi (mulPi v) := by
  apply GInt.ext <;> simp only [numeratorLeft, numeratorRight, add, mulI, mulPi] <;> omega

theorem rawC_right_square (u v : GInt) :
    numeratorRight (numeratorLeft u v) (numeratorRight u v) = mulPi (mulPi u) := by
  apply GInt.ext <;> simp only [numeratorLeft, numeratorRight, add, mulI, mulPi] <;> omega

theorem two_pi_numerator_sameValue (z : GInt) (e : Nat) :
    SameValue ⟨mulPi (mulPi z),e+2⟩ ⟨z,e⟩ := by
  simp only [SameValue]
  rw [piIter_mulPi, piIter_mulPi]
  rfl

/-- C squared is swap without any parity guard when denominator tags are
retained. Exact semantic restoration need not restore the original tag. -/
theorem rawC_square_exact (u v : GInt) (e : Nat) :
    let p := rawC u v e
    let q := rawC p.left p.right p.exponent
    SameValue (packedLeft q) ⟨v,e⟩ ∧ SameValue (packedRight q) ⟨u,e⟩ := by
  simp only [rawC, packedLeft, packedRight]
  rw [rawC_left_square, rawC_right_square]
  exact ⟨two_pi_numerator_sameValue v e,two_pi_numerator_sameValue u e⟩

/-- X C is C inverse. It restores all Gaussian fractions, not only integral
pairs passing the local cancellation guard. -/
def rawCInverse (p : PackedPair) : PackedPair :=
  let q := rawC p.left p.right p.exponent
  ⟨q.right,q.left,q.exponent⟩

theorem rawC_inverse_exact (u v : GInt) (e : Nat) :
    SameValue (packedLeft (rawCInverse (rawC u v e))) ⟨u,e⟩ ∧
    SameValue (packedRight (rawCInverse (rawC u v e))) ⟨v,e⟩ := by
  have h := rawC_square_exact u v e
  exact ⟨h.2,h.1⟩

/-- Heterogeneous tags are aligned exactly before the raw C step. -/
def rawAlignedC (x y : Fraction) : PackedPair :=
  let e := commonExponent x y
  rawC (raiseTo x e).numerator (raiseTo y e).numerator e

theorem heterogeneous_inverse_restores (x y : Fraction) :
    SameValue (packedLeft (rawCInverse (rawAlignedC x y))) x ∧
    SameValue (packedRight (rawCInverse (rawAlignedC x y))) y := by
  have hc := rawC_inverse_exact
    (raiseTo x (commonExponent x y)).numerator
    (raiseTo y (commonExponent x y)).numerator (commonExponent x y)
  have ha := alignedButterfly_input_exact x y
  exact ⟨SameValue.trans hc.1 ha.1,SameValue.trans hc.2 ha.2⟩

/-- Canonicalization turns semantic restoration into literal representation
restoration for arbitrary heterogeneous-tag inputs. -/
theorem canonical_inverse_restores (x y : Fraction) :
    normalize (packedLeft (rawCInverse (rawAlignedC x y))) = normalize x ∧
    normalize (packedRight (rawCInverse (rawAlignedC x y))) = normalize y := by
  have h := heterogeneous_inverse_restores x y
  exact ⟨normalize_congr h.1,normalize_congr h.2⟩

/-- Multiplication by i is exact in every pi-denominator format. -/
def phaseI (x : Fraction) : Fraction := ⟨mulI x.numerator,x.exponent⟩
def phaseNegI (x : Fraction) : Fraction := ⟨mulNegI x.numerator,x.exponent⟩

theorem phase_inverse_restores (x : Fraction) : phaseNegI (phaseI x) = x := by
  cases x
  simp only [phaseNegI, phaseI]
  congr
  apply GInt.ext <;> simp [mulNegI,mulI]

/-- Halving changes the pi tag by two and rotates the numerator by i,
since pi squared is 2i. It applies to all values without integer truncation. -/
def exactHalf (x : Fraction) : Fraction := ⟨mulI x.numerator,x.exponent+2⟩
def exactDouble (x : Fraction) : Fraction := ⟨scaleTwo x.numerator,x.exponent⟩

theorem half_double_restores (x : Fraction) : SameValue (exactHalf (exactDouble x)) x := by
  have hp : mulI (scaleTwo x.numerator) = mulPi (mulPi x.numerator) := by
    apply GInt.ext <;> simp only [mulI,scaleTwo,mulPi] <;> omega
  simp only [exactHalf,exactDouble]
  rw [hp]
  exact two_pi_numerator_sameValue _ _

end GaussianSynthesis

#print axioms GaussianSynthesis.rawC_square_exact
#print axioms GaussianSynthesis.heterogeneous_inverse_restores
#print axioms GaussianSynthesis.canonical_inverse_restores
#print axioms GaussianSynthesis.half_double_restores

namespace GaussianSynthesis
open GaussianParity

def gaussianDifference (u v : GInt) : GInt := add u (neg v)

theorem gaussian_update_difference (old fresh : GInt) :
    gaussianDifference (add old fresh) old = fresh := by
  apply GInt.ext <;> simp only [gaussianDifference,add,neg] <;> omega

theorem mulI_difference (u v : GInt) :
    mulI (gaussianDifference u v) = gaussianDifference (mulI u) (mulI v) := by
  apply GInt.ext <;> simp only [mulI,gaussianDifference,add,neg] <;> omega

theorem phase_difference (q : Nat) (u v : GInt) :
    repeatI q (gaussianDifference u v) =
      gaussianDifference (repeatI q u) (repeatI q v) := by
  induction q with
  | zero => rfl
  | succ q ih => simp only [repeatI,ih,mulI_difference]

/-- Old and updated dirty values must be transported through the SAME scalar
phase before subtraction. Matching phases preserve the fresh update exactly. -/
theorem matching_phase_dirty_difference (q : Nat) (old fresh : GInt) :
    gaussianDifference (repeatI q (add old fresh)) (repeatI q old) = repeatI q fresh := by
  rw [← phase_difference,gaussian_update_difference]

/-- A phase mismatch creates a false fresh update even when no source update
occurred. Its numerator fails the actual PR46 division-by-32 image guard. -/
theorem mismatched_phase_image_obstruction :
    ¬ ∃ t : GInt,
      gaussianDifference (mulI ⟨1,0⟩) ⟨1,0⟩ = scale (-32) t := by
  intro ⟨t,ht⟩
  have hr := congrArg GInt.re ht
  simp only [gaussianDifference,mulI,add,neg,scale] at hr
  omega

end GaussianSynthesis

#print axioms GaussianSynthesis.matching_phase_dirty_difference
#print axioms GaussianSynthesis.mismatched_phase_image_obstruction

namespace GaussianSynthesis

/-!
## Complete image certificates

Divisibility of N by 32 is only a necessary local guard. Complete membership
uses the full producer P and a proved left inverse Q, including every side port.
This interface must not be instantiated with center-only data unless its left
inverse hypothesis is actually established.
-/

/-- A left-inverse decoder induces a necessary AND sufficient producer-image
round-trip test. Local divisibility checks alone are not this test. -/
theorem producer_image_iff_roundtrip {A B : Type}
    (P : A → B) (Q : B → A) (hQP : ∀ x, Q (P x) = x) (d : B) :
    (∃ x, P x = d) ↔ P (Q d) = d := by
  constructor
  · intro ⟨x,hx⟩
    rw [← hx,hQP x]
  · intro h
    exact ⟨Q d,h⟩

theorem producer_projection_idempotent {A B : Type}
    (P : A → B) (Q : B → A) (hQP : ∀ x, Q (P x) = x) (d : B) :
    P (Q (P (Q d))) = P (Q d) := by rw [hQP (Q d)]

/-- Once the complete difference is in the image, the recovered source is
unique and is decoded exactly by Q. -/
theorem image_difference_recovers {A B : Type}
    (P : A → B) (Q : B → A) (hQP : ∀ x, Q (P x) = x)
    (d : B) (x : A) (hd : d = P x) :
    Q d = x ∧ P (Q d) = d := by
  constructor
  · rw [hd,hQP]
  · rw [hd,hQP]

def recoverIfImage {A B : Type} [DecidableEq B]
    (P : A → B) (Q : B → A) (d : B) : Option A :=
  if P (Q d) = d then some (Q d) else none

/-- The executable total guard succeeds exactly on the complete producer
image and returns its unique preimage. -/
theorem recoverIfImage_exact {A B : Type} [DecidableEq B]
    (P : A → B) (Q : B → A) (hQP : ∀ x, Q (P x) = x) (d : B) (x : A) :
    recoverIfImage P Q d = some x ↔ P x = d := by
  unfold recoverIfImage
  by_cases h : P (Q d) = d
  · simp only [h,↓reduceIte,Option.some.injEq]
    constructor
    · intro hx
      rw [← hx]
      exact h
    · intro hx
      rw [← hx,hQP]
  · simp only [h,↓reduceIte]
    constructor
    · intro impossible
      cases impossible
    · intro hx
      have hc := (producer_image_iff_roundtrip P Q hQP d).mp ⟨x,hx⟩
      exact False.elim (h hc)

/-- Rejection is certified absence of a producer-image preimage, provided
Q P = identity was proved for the full producer/decoder pair. -/
theorem recoverIfImage_rejects {A B : Type} [DecidableEq B]
    (P : A → B) (Q : B → A) (hQP : ∀ x, Q (P x) = x) (d : B) :
    recoverIfImage P Q d = none ↔ ¬ ∃ x, P x = d := by
  unfold recoverIfImage
  rw [producer_image_iff_roundtrip P Q hQP d]
  by_cases h : P (Q d) = d <;> simp [h]

end GaussianSynthesis

#print axioms GaussianSynthesis.producer_image_iff_roundtrip
#print axioms GaussianSynthesis.producer_projection_idempotent
#print axioms GaussianSynthesis.recoverIfImage_exact
#print axioms GaussianSynthesis.recoverIfImage_rejects

namespace GaussianSynthesis

/-- Abstract dirty-scratch restoration uses only the complete image test and
the backend's subtraction restoration law. This separates image membership
from the representation-specific arithmetic implementation. -/
theorem certified_dirty_recovery_and_restore {A B : Type} [Sub B]
    (P : A → B) (Q : B → A) (hQP : ∀ x, Q (P x) = x)
    (old updated : B) (x : A)
    (himage : updated-old = P x)
    (hrestore : updated-(updated-old) = old) :
    Q (updated-old) = x ∧
    P (Q (updated-old)) = updated-old ∧
    updated-P (Q (updated-old)) = old := by
  have h := image_difference_recovers P Q hQP (updated-old) x himage
  exact ⟨h.1,h.2,by rw [h.2]; exact hrestore⟩

end GaussianSynthesis

#print axioms GaussianSynthesis.certified_dirty_recovery_and_restore

namespace GaussianSynthesis
open GaussianParity

theorem phase_scale (q : Nat) (k : Int) (z : GInt) :
    repeatI q (scale k z) = scale k (repeatI q z) := by
  induction q with
  | zero => rfl
  | succ q ih => simp only [repeatI,ih,mulI_scale]

/-- ONE common unit phase preserves the fresh center image relation. This
is stronger than merely matching each role's old/new phase separately. -/
theorem common_phase_center_image (q : Nat) (N T : GInt)
    (h : N = scale (-32) T) :
    repeatI q N = scale (-32) (repeatI q T) := by
  rw [h,phase_scale]

/-- In the actual fresh impulse (0,1,19), changing only B19 from 2 to 2i
adds (-2+2i) to the fresh N=-32. Old/new phases may agree within each role
while these unequal inter-role phases destroy the producer image. -/
theorem per_role_phase_image_obstruction :
    add ⟨-32,0⟩ (gaussianDifference ⟨0,2⟩ ⟨2,0⟩) = ⟨-34,2⟩ ∧
    ¬ ∃ t : GInt, add ⟨-32,0⟩ (gaussianDifference ⟨0,2⟩ ⟨2,0⟩)
      = scale (-32) t := by
  constructor
  · apply GInt.ext <;> simp [add,gaussianDifference,neg]
  · intro ⟨t,ht⟩
    have hr := congrArg GInt.re ht
    simp only [add,gaussianDifference,neg,scale] at hr
    omega

end GaussianSynthesis

#print axioms GaussianSynthesis.common_phase_center_image
#print axioms GaussianSynthesis.per_role_phase_image_obstruction

namespace GaussianSynthesis
open GaussianParity

/-- A canonical pi tag is the least possible nonnegative tag among all exact
Gaussian numerator representations of the same value. -/
theorem canonical_tag_minimal {x y : Fraction}
    (hx : Canonical x) (hxy : SameValue x y) : x.exponent ≤ y.exponent := by
  have he : x.exponent = (normalize y).exponent :=
    canonical_tags_equal hx (normalize_canonical y)
      (SameValue.trans hxy (SameValue.symm (normalize_sound y)))
  rw [he]
  exact normalizeCore_exponent_bound y.exponent y.numerator

/-- The computed normalizer attains that minimal tag, rather than merely
returning some equivalent representation with a reduced denominator. -/
theorem normalized_tag_minimal {x y : Fraction} (hxy : SameValue x y) :
    (normalize x).exponent ≤ y.exponent := by
  exact canonical_tag_minimal (normalize_canonical x)
    (SameValue.trans (normalize_sound x) hxy)

end GaussianSynthesis

#print axioms GaussianSynthesis.canonical_tag_minimal
#print axioms GaussianSynthesis.normalized_tag_minimal
