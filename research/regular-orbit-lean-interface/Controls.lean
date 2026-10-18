import RegularOrbit

namespace RegularOrbit.Controls

def sameAddress : PermFamily Bool Bool where
  forward := fun _ x => x
  inverse := fun _ x => x
  left_inverse := by intros; rfl
  right_inverse := by intros; rfl

def flipAddress : PermFamily Bool Bool where
  forward := fun g x => g ^^ x
  inverse := fun g x => g ^^ x
  left_inverse := by intro g x; cases g <;> cases x <;> rfl
  right_inverse := by intro g x; cases g <;> cases x <;> rfl

def coeffA (g : Bool) := g
def coeffB (g : Bool) := !g

theorem collision_operators_equal (payload : Bool → Bool) (y : Bool) :
    action [false, true] sameAddress coeffA payload y =
    action [false, true] sameAddress coeffB payload y := by
  simp [action, xorSum, sameAddress, coeffA, coeffB]

theorem collision_coefficients_differ : coeffA false ≠ coeffB false := by decide

theorem duplicate_operators_equal (payload : Bool → Bool) (y : Bool) :
    action [false, false, true] flipAddress coeffB payload y =
    action [false, false, true] flipAddress (fun _ => false) payload y := by
  simp [action, xorSum, flipAddress, coeffB]

theorem duplicate_coefficients_differ : coeffB false ≠ false := by decide

theorem omitted_label_operators_equal (payload : Bool → Bool) (y : Bool) :
    action [false] flipAddress coeffA payload y =
    action [false] flipAddress (fun _ => false) payload y := by
  simp [action, xorSum, flipAddress, coeffA]

theorem omitted_label_coefficients_differ : coeffA true ≠ false := by decide

def identityAddress : PermFamily Unit Bool where
  forward := fun _ x => x
  inverse := fun _ x => x
  left_inverse := by intros; rfl
  right_inverse := by intros; rfl

def diagonal (i j : Bool) (_ : Unit) : Bool := decide (i = j)
def withLeak (i j : Bool) (g : Unit) : Bool := diagonal i j g ^^ ((!i) && j)
def dirty (j : Bool) (_ : Bool) : Bool := j

theorem clean_role_hides_leak (payload : Bool → Bool → Bool)
    (clean : ∀ y, payload true y = false) (i y : Bool) :
    matrixAction [false, true] [()] identityAddress diagonal payload i y =
    matrixAction [false, true] [()] identityAddress withLeak payload i y := by
  cases i <;> simp [matrixAction, action, xorSum, identityAddress, diagonal, withLeak, clean]

theorem dirty_role_exposes_leak :
    matrixAction [false, true] [()] identityAddress diagonal dirty false false ≠
    matrixAction [false, true] [()] identityAddress withLeak dirty false false := by decide

-- A small actual separating action is also checked, rather than only failures.
theorem flip_separates : Separates flipAddress false := by
  intro g h same
  simpa [flipAddress] using same

theorem concrete_complete_endpoint {R : Type} [DecidableEq R]
    (rs : List R) (nd : rs.Nodup) (complete : ∀ j, j ∈ rs)
    (a b : R → R → Bool → Bool)
    (same : ∀ payload i y,
      matrixAction rs [false, true] flipAddress a payload i y =
      matrixAction rs [false, true] flipAddress b payload i y) : a = b := by
  apply complete_endpoint_faithful rs [false, true] flipAddress false flip_separates nd complete
  · decide
  · intro g; cases g <;> simp
  · exact same

#print axioms collision_operators_equal
#print axioms duplicate_operators_equal
#print axioms omitted_label_operators_equal
#print axioms clean_role_hides_leak
#print axioms dirty_role_exposes_leak
#print axioms concrete_complete_endpoint

end RegularOrbit.Controls
