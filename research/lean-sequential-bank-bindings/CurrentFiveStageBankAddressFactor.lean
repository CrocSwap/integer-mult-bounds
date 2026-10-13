import BankRouting

/-!
Inactive source adapter for integer-mult-bounds at
12a4934d15006e8c10f9b2264f13f8f341be802b:
research/five-stage-gen4-banks/bank_template.py, BankPlan.address.

The source address is d * tau * N^-1.  This file identifies its effective
embedding for the existing BankRouting interface.  It does not instantiate
GL120, rational normalizers, reduction, separated roles, or a physical core.
All group, inverse, fiber, and uniqueness machinery is reused from BankRouting.
-/
namespace CurrentMain.FiveStageBankAddress
open CurrentMain.BankRouting

universe u v
variable {G : Type u} {L : Type v}

def sourceAddress (A : GroupLaws G) (d tau N : G) : G :=
  route A (A.mul d tau) N

def effectiveEmbedding (A : GroupLaws G) (tau N : G) : G :=
  A.mul N (A.inv tau)

/-- The literal source factor order, with no commutation or involution premise. -/
theorem address_factor (A : GroupLaws G) (d tau N : G) :
    sourceAddress A d tau N = route A d (effectiveEmbedding A tau N) := by
  apply cancel_right A (A.mul N (A.inv tau))
  calc
    A.mul (sourceAddress A d tau N) (A.mul N (A.inv tau)) =
        A.mul (A.mul (sourceAddress A d tau N) N) (A.inv tau) :=
      (A.assoc _ _ _).symm
    _ = A.mul (A.mul d tau) (A.inv tau) :=
      congrArg (fun b => A.mul b (A.inv tau)) (origin_route A (A.mul d tau) N)
    _ = d := by rw [A.assoc, A.mul_inv, A.mul_one]
    _ = A.mul (route A d (effectiveEmbedding A tau N)) (A.mul N (A.inv tau)) :=
      (origin_route A d (effectiveEmbedding A tau N)).symm

/-- The exact inverse cover class is obtained from the old origin map. -/
theorem address_origin (A : GroupLaws G) (tau N b : G) :
    sourceAddress A (origin A b (effectiveEmbedding A tau N)) tau N = b := by
  rw [address_factor, route_origin]

theorem address_every_bank_once (A : GroupLaws G) (tau N b : G) :
    ∃ d, sourceAddress A d tau N = b ∧
      ∀ d', sourceAddress A d' tau N = b → d' = d := by
  simpa only [address_factor] using every_bank_once A (effectiveEmbedding A tau N) b

theorem address_reduction {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (d tau N : G) :
    r.map (sourceAddress A d tau N) =
      sourceAddress B (r.map d) (r.map tau) (r.map N) := by
  simp only [sourceAddress, reduction_route, r.map_mul]

theorem address_complete_fiber {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (tau N : G) (d₀ : L) (b : G) :
    r.map b = route B d₀ (r.map (effectiveEmbedding A tau N)) ↔
      ∃ d, r.map d = d₀ ∧ sourceAddress A d tau N = b := by
  simpa only [address_factor] using complete_fiber r (effectiveEmbedding A tau N) d₀ b

end CurrentMain.FiveStageBankAddress

#print axioms CurrentMain.FiveStageBankAddress.address_factor
#print axioms CurrentMain.FiveStageBankAddress.address_origin
#print axioms CurrentMain.FiveStageBankAddress.address_every_bank_once
#print axioms CurrentMain.FiveStageBankAddress.address_reduction
#print axioms CurrentMain.FiveStageBankAddress.address_complete_fiber
