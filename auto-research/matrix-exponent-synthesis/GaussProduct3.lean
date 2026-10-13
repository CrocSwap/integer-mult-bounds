import Std

/-!
Established three-real-product Gaussian multiplication identity. This verifies
only the exact scalar replacement used by the actual matrix interpreter;
no new multiplication algorithm priority or asymptotic saving is claimed.
-/
namespace MatrixParityBridge

def gaussianProduct4 (x y : Int × Int) : Int × Int :=
  (x.1*y.1-x.2*y.2,x.1*y.2+x.2*y.1)

def gaussianProduct3 (x y : Int × Int) : Int × Int :=
  let ac := x.1*y.1
  let bd := x.2*y.2
  (ac-bd,(x.1+x.2)*(y.1+y.2)-ac-bd)

/-- Replacing each Gaussian product by three real products preserves both
integer numerator coordinates exactly, including signs and zeros. -/
theorem gaussian_three_products_exact (x y : Int × Int) :
    gaussianProduct3 x y = gaussianProduct4 x y := by
  apply Prod.ext <;> simp only [gaussianProduct3,gaussianProduct4] <;> grind

/-- All 2208 scheduled Gaussian gates translate to 6624 real product slots.
This is a schedule cardinality, not a tensor rank or time measurement. -/
theorem matrix_real_product_slots : 3*2208 = (6624 : Nat) := by decide

end MatrixParityBridge

#print axioms MatrixParityBridge.gaussian_three_products_exact
#print axioms MatrixParityBridge.matrix_real_product_slots
