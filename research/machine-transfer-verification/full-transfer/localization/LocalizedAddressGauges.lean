import LocalizedMatrixTransfer
import AddressGauges

/-! Direct semantic interface: rationally checked localized projectors produce
actual bijective address gauges on ZMod(p^f) vectors for every eligible p.
No reduced idempotence or reduced absorption equation is supplied by callers.
-/
namespace LocalizedAddressGauges
open EligibleLocalization LocalizedMatrixTransfer

variable {n : Type} [Fintype n] [DecidableEq n]

noncomputable def primePowerGauge (D : ℕ) (hD : 0 < D) (p f : ℕ)
    (coprime : D.Coprime p) (P : Matrix n n (Coeff D))
    (rational_idempotent : (rationalView D hD).mapMatrix P * (rationalView D hD).mapMatrix P =
      (rationalView D hD).mapMatrix P) :
    FramedXor.Gauge ((n → ZMod (p ^ f)) × (n → ZMod (p ^ f))) :=
  AddressGauges.matrixPartialSwapGauge ((reducePrimePower D p f coprime).mapMatrix P)
    (rational_projector_reduces D hD _ (eligible_prime_power D p f coprime) P rational_idempotent)

theorem primePowerGauge_involution (D : ℕ) (hD : 0 < D) (p f : ℕ)
    (coprime : D.Coprime p) (P : Matrix n n (Coeff D))
    (rational_idempotent : (rationalView D hD).mapMatrix P * (rationalView D hD).mapMatrix P =
      (rationalView D hD).mapMatrix P)
    (x : (n → ZMod (p ^ f)) × (n → ZMod (p ^ f))) :
    (primePowerGauge D hD p f coprime P rational_idempotent).forward
      ((primePowerGauge D hD p f coprime P rational_idempotent).forward x) = x :=
  AddressGauges.matrix_partialSwap_involution _ _ x

omit [DecidableEq n] in
theorem matrixEndomorphism_sub {K : Type} [CommRing K] (A B : Matrix n n K) :
    AddressGauges.matrixEndomorphism (A - B) =
      AddressGauges.matrixEndomorphism A - AddressGauges.matrixEndomorphism B := by
  apply AddMonoidHom.ext
  intro x
  change (A - B).mulVec x = A.mulVec x - B.mulVec x
  exact Matrix.sub_mulVec A B x

/-- The nested transport law follows from a rational absorption identity and
prime eligibility, so the modular equation is no longer an external premise. -/
theorem primePower_nested_transport (D : ℕ) (hD : 0 < D) (p f : ℕ)
    (coprime : D.Coprime p) (small large : Matrix n n (Coeff D))
    (rational_absorption : (rationalView D hD).mapMatrix large *
      (rationalView D hD).mapMatrix small = (rationalView D hD).mapMatrix small)
    (x : (n → ZMod (p ^ f)) × (n → ZMod (p ^ f))) :
    let P := (reducePrimePower D p f coprime).mapMatrix small
    let Q := (reducePrimePower D p f coprime).mapMatrix large
    AddressGauges.partialSwap (AddressGauges.matrixEndomorphism Q)
      (AddressGauges.partialSwap (AddressGauges.matrixEndomorphism P) x) =
      AddressGauges.partialSwap (AddressGauges.matrixEndomorphism (Q - P)) x := by
  dsimp only
  rw [matrixEndomorphism_sub]
  apply AddressGauges.partialSwap_nested
  intro v
  exact AddressGauges.matrix_absorption _ _
    (rational_product_reduces D hD _ (eligible_prime_power D p f coprime)
      large small small rational_absorption) v

end LocalizedAddressGauges

#print axioms LocalizedAddressGauges.primePowerGauge_involution
#print axioms LocalizedAddressGauges.matrixEndomorphism_sub
#print axioms LocalizedAddressGauges.primePower_nested_transport
