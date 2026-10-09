import SequentialRootEvent
import ConstantSetupBridge13955
import SequentialStreamedPairs
namespace PreparedSequentialRootEvent
open BinarySpace24 SequentialCXKernel CountedConstantSetup13955 Lean.Grind
attribute [local instance] Semiring.natCast Ring.intCast
variable {F : Type u} [Field F]

theorem actual_event (i : F) (hi : i*i= -1) (htwo : (2:F)≠0)
    (pool : Memory F) (g : GaugeKeyTrace.State) (s : State Vec F) :
    CommonExactFrame.adapter (CompleteFrameSelector.select i hi htwo (ActualRootLifecycle.afterRoots 3 g 17326))
      (CompleteFrameSelector.select i hi htwo (ActualRootLifecycle.afterRoots 4 g 17326)) s.work.memory=
    (SequentialRootEvent.run (table (setup i pool)) (coefficientA (setup i pool)) (coefficientB (setup i pool)) s).1.work.memory :=
  SequentialRootEvent.actual_event i hi htwo _ (table_exact i pool) _ _ (coefficient_a_exact i pool) (coefficient_b_exact i pool) g s

theorem setup_and_run_receipts (i : F) (pool : Memory F) (s : State Vec F) :
    runCounted i program pool=(setup i pool,⟨1,1,13,10,2,3,1,2⟩) ∧
    (SequentialRootEvent.run (table (setup i pool)) (coefficientA (setup i pool)) (coefficientB (setup i pool)) s).2=SequentialRootEvent.receipt :=
  ⟨counted_setup i pool,SequentialRootEvent.run_cost _ _ _ s⟩

theorem prepared_sequential_child (i : F) (pool : Memory F) (s : SequentialPairKernel.State Vec F) :
    (SequentialStreamedPairs.cStream (coefficientA (setup i pool)) (coefficientB (setup i pool)) s).state.memory=
      CoordinateChild.gate i 21 s.memory :=
  SequentialStreamedPairs.c_gate i _ _ (coefficient_a_exact i pool) (coefficient_b_exact i pool) s

theorem prepared_denominator_safe (i : F) (pool : Memory F) (htwo : (2:F)≠0) :
    CountedConstantSetup13955.run i preparation pool 4≠0 := prepared_denominator_nonzero i pool htwo

end PreparedSequentialRootEvent
#print axioms PreparedSequentialRootEvent.actual_event
#print axioms PreparedSequentialRootEvent.setup_and_run_receipts
#print axioms PreparedSequentialRootEvent.prepared_sequential_child
#print axioms PreparedSequentialRootEvent.prepared_denominator_safe
