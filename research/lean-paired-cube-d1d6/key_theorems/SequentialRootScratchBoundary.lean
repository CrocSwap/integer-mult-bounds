import PreparedSequentialRootEvent
import CountedScratchWrapper13955
namespace SequentialRootScratchBoundary
open BinarySpace24 SequentialCXKernel SuppliedQuarterTable FiniteScratchStoreLoad13955 CountedScratchWrapper13955 Lean.Grind
attribute [local instance] Semiring.natCast Ring.intCast
variable {F : Type u} [Field F]
abbrev Payload (F : Type u) := (Vec → F) × Bool
abbrev BankState (F : Type u) := Payload F × (Fin 4 → F)

def body (t : Table F) (a b : F) (s : BankState F) : BankState F × Traffic :=
  let out:=SequentialRootEvent.run t a b ⟨⟨s.1.1,s.2⟩,s.1.2⟩
  (((out.1.work.memory,out.1.control),out.1.work.registers),
    ⟨out.2.right.loads+out.2.child.loads+out.2.left.loads,
      out.2.right.stores+out.2.child.stores+out.2.left.stores⟩)

def lifted (t : Table F) (a b : F) := liftCountedBody (body t a b)
def wrapped (t : Table F) (a b : F) (s : Machine (Payload F) F 4) := countedWrapper (lifted t a b) s

theorem body_traffic (t : Table F) (a b : F) (s : BankState F) : (body t a b s).2=⟨486539264,486539264⟩ := by
  simp only [body,SequentialRootEvent.run_cost]
  rfl

theorem lifted_traffic (t : Table F) (a b : F) (s : Machine (Payload F) F 4) :
    (lifted t a b s).2=⟨486539264,486539264⟩ := body_traffic t a b s.1

theorem field_scratch_restored (t : Table F) (a b : F) (s : Machine (Payload F) F 4) :
    (wrapped t a b s).1.1.2=s.1.2 :=
  countedWrapper_scratch_restored (lifted t a b) (liftCountedBody_preserves_spill (body t a b)) s

theorem spill_preserved_iff (t : Table F) (a b : F) (s : Machine (Payload F) F 4) :
    (wrapped t a b s).1.2=s.2 ↔ s.1.2=s.2 :=
  countedWrapper_original_spill_iff (lifted t a b) (liftCountedBody_preserves_spill (body t a b)) s

theorem unequal_banks_obstruction (t : Table F) (a b : F) (s : Machine (Payload F) F 4) (h : s.1.2≠s.2) :
    ¬((wrapped t a b s).1.1.2=s.1.2 ∧ (wrapped t a b s).1.2=s.2) :=
  countedWrapper_full_restoration_obstruction (lifted t a b) s h

theorem wrapper_receipt (t : Table F) (a b : F) (s : Machine (Payload F) F 4) :
    (wrapped t a b s).2=⟨486539268,486539268⟩ ∧
      (spillCells 4).length=4 ∧ (residentCells 4).length=8 :=
  four_register_receipt (lifted t a b) _ (lifted_traffic t a b) s

end SequentialRootScratchBoundary
#print axioms SequentialRootScratchBoundary.body_traffic
#print axioms SequentialRootScratchBoundary.lifted_traffic
#print axioms SequentialRootScratchBoundary.field_scratch_restored
#print axioms SequentialRootScratchBoundary.spill_preserved_iff
#print axioms SequentialRootScratchBoundary.unequal_banks_obstruction
#print axioms SequentialRootScratchBoundary.wrapper_receipt
