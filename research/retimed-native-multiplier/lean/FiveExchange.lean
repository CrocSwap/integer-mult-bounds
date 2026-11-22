import Mathlib.Tactic

namespace FiveExchange

variable {R : Type*} [CommRing R]

/-- A lower shear sends a dual backwards and preserves its pairing with every vector. -/
theorem shearPair (wSrc wDst xSrc xDst c : R) :
    (wSrc - c*wDst)*xSrc + wDst*(xDst+c*xSrc) = wSrc*xSrc+wDst*xDst := by ring

/-- The last coordinate after the two lower sweeps and the final corner shear.
    The scalar y is the middle dual applied to all the middle coordinates. -/
def endValue (ai bi zLast mid x y t : R) :=
  t+bi*(y-ai*x*mid)+ai*(bi-zLast)*x

theorem endAdd (ai bi zLast mid x y t X Y T c : R) :
    endValue ai bi zLast mid (x-c*X) (y-c*Y) (t-c*T) =
      endValue ai bi zLast mid x y t - c*endValue ai bi zLast mid X Y T := by
  unfold endValue
  ring

/-- The spent factors are only the indicated corner units. This applies over every
    commutative ring, including ternary residue rings with zero divisors. -/
theorem endOfVector {a ai bi : R} (ha : a*ai=1) (zLast mid : R) :
    endValue ai bi zLast mid a mid zLast = bi := by
  unfold endValue
  rw [show ai*a=1 by simpa [mul_comm] using ha, one_mul, sub_self, mul_zero,
      add_zero, show ai*(bi-zLast)*a=(a*ai)*(bi-zLast) by ring, ha]
  ring

theorem factoredDual {a ai b bi zLast mid w0 : R} (ha : a*ai=1) (hb : b*bi=1)
    (charge : w0*a+mid+b*zLast=2) (x y t : R) :
    w0*x+y+b*t = ai*x + b*endValue ai bi zLast mid x y t := by
  have inv : ai*a = 1 := by simpa [mul_comm] using ha
  have w : w0*x = ai*x*(2-mid-b*zLast) := by
    rw [← charge, show w0*a+mid+b*zLast-mid-b*zLast=w0*a by ring,
        show ai*x*(w0*a)=(ai*a)*(w0*x) by ring, inv, one_mul]
  rw [w]
  unfold endValue
  linear_combination (-(ai*x*mid)+y+ai*x) * (-hb)

/-- Running the lower sweeps on the reflected input gives the weighted outside swap
    of the swept original input, and preserves each swept middle coordinate.
    y is the original middle dual evaluated on the middle vector, Y is any original
    middle coordinate, and Z is the corresponding coordinate of the primal factor. -/
theorem loweredReflection {a ai b bi zLast mid w0 : R} (ha : a*ai=1) (hb : b*bi=1)
    (charge : w0*a+mid+b*zLast=2) (x y t Y Z : R) :
    let d := w0*x+y+b*t
    let out := endValue ai bi zLast mid x y t
    x-d*a = (-a*b)*out ∧
    (Y-d*Z)-ai*(x-d*a)*Z = Y-ai*x*Z ∧
    endValue ai bi zLast mid (x-d*a) (y-d*mid) (t-d*zLast) = (-ai*bi)*x := by
  dsimp only
  have w := factoredDual ha hb charge x y t
  have normal := endOfVector (bi:=bi) ha zLast mid
  constructor
  · rw [w]
    linear_combination (-x)*ha
  constructor
  · linear_combination (w0*x+y+b*t)*Z*ha
  · rw [endAdd,normal,w]
    linear_combination (-endValue ai bi zLast mid x y t)*hb

theorem centralUnits {a ai b bi : R} (ha : a*ai=1) (hb:b*bi=1) :
    (-a*b)*(-ai*bi)=1 := by
  calc
    _ = (a*ai)*(b*bi) := by ring
    _ = 1 := by rw [ha,hb,mul_one]

/-- A true weighted interchange is the diagonal conjugate of the bare one.
    This controls the number of inherited row weights per recursive label. -/
theorem diagonalPair {a ai : R} (ha : ai*a=1) (x y : R) :
    (a*y, ai*(a*x)) = (a*y, x) := by
  rw [← mul_assoc, ha, one_mul]

/-- The physical before and after change of the two banks realizes the
    full placed projector, for any ring-linear invertible basis and bank weight.
    Taking p to project onto one coordinate gives the single direct child. -/
theorem directCoordinate {V : Type*} [AddCommGroup V] [Module R V]
    (basis weight : V ≃ₗ[R] V) (p : V →ₗ[R] V) (h t : V) :
    let movedH := weight (basis.symm (weight.symm h))
    let movedT := basis.symm t
    let q := p (movedT - weight.symm movedH)
    let wanted := basis (p (basis.symm (t - weight.symm h)))
    (weight (basis (weight.symm (movedH+weight q))), basis (movedT-q)) =
      (h+weight wanted, t-wanted) := by
  simp

/-- A full low has one, three, or five children. Singletons that miss one
    outside coordinate add no more than the two specified exceptional sets. -/
theorem weightedChartSum {x one three five total : ℚ} (sizes : one+three+five=total)
    (both : one=4*x) (all : total=9*x-1) (exceptions : five≤x-1+4) :
    one+3*three+5*five ≤ 21*x+3 := by linarith

#print axioms diagonalPair
#print axioms directCoordinate
#print axioms weightedChartSum

#print axioms loweredReflection
#print axioms centralUnits
#print axioms shearPair

end FiveExchange
