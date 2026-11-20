import CliffordHead
import DenseTemplates

/-! The dense assembly consumes the value supplied by the signed Clifford
traversals. The short cross products sum the shifts selected by literal bits. -/
namespace CompleteProduct
open TernaryCollect BooleanGauss BinaryDelivery

def shifts : List Bool → ℕ → ℕ
  | [], _ => 0
  | b::bs, w => (if b then w else 0) + 2 * shifts bs w

theorem shifts_value (xs : List Bool) (w : ℕ) : shifts xs w = binary xs * w := by
  induction xs with
  | nil => simp [shifts,binary]
  | cons b bs ih => cases b <;> simp [shifts,binary,TernaryCollect.value,ih] <;> ring

noncomputable def defectProduct {h k : ℕ} (A B : Bits h → Model (Fin k)) : ℕ :=
  PrefixBlocks.deliver (2^(3^k)) (PrefixBlocks.binCoeffs (fun x y ↦ binary
    (SignedEvents.finish (CliffordHead.products (A x) (B y)))))

noncomputable def deliver {h k : ℕ} (A B : Bits h → Model (Fin k))
    (a b : Fin (3^h) → Fin (3^k) → Bool) (P Q : List Bool)
    (u count ea eb : ℕ) (sa sb : ℤ) : ℤ :=
  let rep := fun z ↦ DenseTemplates.repeatWord z u count
  (rep (rep (shifts P (binary Q))) : ℤ) +
    sa*sb*((2:ℤ)^ea*(2:ℤ)^eb)*(defectProduct A B : ℤ) +
    sa*(2:ℤ)^ea*(rep (shifts (PhysicalBlocks.strip a) (binary Q)) : ℤ) +
    sb*(2:ℤ)^eb*(rep (shifts (PhysicalBlocks.strip b) (binary P)) : ℤ)

/-- Each high hole and each low literal has passed the producer's equality
check. P and Q are the two recovered short words, with independent signs. -/
theorem ordinary_product {h k : ℕ} (A B : Bits h → Model (Fin k))
    (a b : Fin (3^h) → Fin (3^k) → Bool)
    (ah : PhysicalBlocks.HighHoles a) (bh : PhysicalBlocks.HighHoles b)
    (av : ∀ x, PhysicalInput.Valid (A x) (PhysicalBlocks.block a x))
    (bv : ∀ y, PhysicalInput.Valid (B y) (PhysicalBlocks.block b y))
    (P Q : List Bool) (u count ea eb : ℕ) (hu : 0 < u) (sa sb : ℤ) :
    let G : ℤ := DenseTemplates.geometric (2^u) count
    deliver A B a b P Q u count ea eb sa sb =
      ((binary P : ℤ)*G + sa*2^ea*binary (PhysicalBlocks.strip a)) *
      ((binary Q : ℤ)*G + sb*2^eb*binary (PhysicalBlocks.strip b)) := by
  dsimp only [deliver,defectProduct]
  rw [CliffordHead.physical_mixture A B a b ah bh av bv]
  simp only [shifts_value]
  exact DenseTemplates.assembled_signed_product u count (binary P) (binary Q)
    (binary (PhysicalBlocks.strip a)) (binary (PhysicalBlocks.strip b)) ea eb hu sa sb

#print axioms shifts_value
#print axioms ordinary_product
end CompleteProduct
