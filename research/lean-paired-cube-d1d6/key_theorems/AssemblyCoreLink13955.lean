import AssemblySummary13955
import PairedCubeCore
namespace PairedCubeAssembly13955
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

/-! The imported 124-declaration Core source is unchanged. These identities
link its Nat cross-product interfaces to the full assembly expression graph.
The final scalar guard is reused as a proved dependency rather than recomputed. -/

def coreA : Pair := ⟨(PairedCubeCore.aNum : Int), (PairedCubeCore.aDen : Int)⟩
def coreQ : Pair := ⟨(PairedCubeCore.qNum : Int), (PairedCubeCore.qDen : Int)⟩
def coreEps : Pair := ⟨(PairedCubeCore.epsNum : Int), (PairedCubeCore.epsDen : Int)⟩
def coreMinimum : Pair := ⟨(PairedCubeCore.minimumNum : Int), (PairedCubeCore.minimumDen : Int)⟩
def coreKappa : Pair := ⟨(PairedCubeCore.kappaNum : Int), (PairedCubeCore.kappaDen : Int)⟩

theorem bit_saving_matches_core : SameValue a coreA := by
  decide

theorem q_matches_core : SameValue q coreQ := by
  decide

theorem epsilon_matches_core : SameValue eps coreEps := by
  decide

theorem minimum_matches_core : SameValue minimum coreMinimum := by
  decide

theorem explicit_kappa_unchanged : KAPPA.num = 4609169 ∧ KAPPA.den = 10000000000 ∧
    SameValue KAPPA coreKappa := by
  decide

theorem row_coefficient_retains_core_derivation :
    (72^3 ≤ 2*60^3 ∧ 2*60^4 < 72^4 ∧ 4*2571+9909+252 = (20445 : Nat)) ∧
    ExactValue rowCoefficient 20445 1 := by
  exact ⟨PairedCubeCore.halving_and_row_coefficient, row_coefficient_derived⟩

theorem core_absorption_unchanged : SameValue minimum coreMinimum ∧
    SameValue KAPPA coreKappa ∧
    PairedCubeCore.kappaNum*PairedCubeCore.minimumDen <
      PairedCubeCore.minimumNum*PairedCubeCore.kappaDen := by
  exact ⟨minimum_matches_core, explicit_kappa_unchanged.2.2,
    PairedCubeCore.selected_strict_absorption_cross⟩

theorem all_47_strict_formula_checks : AllSlacksLinked ∧
    PairedCubeCore.literalCharge < PairedCubeCore.guardE := by
  exact ⟨all_46_slack_formulas_linked, PairedCubeCore.full_scalar_guard⟩

theorem complete_finite_assembly_interface : AllSlacksLinked ∧ AllMarginsLinked ∧
    SameValue minimum coreMinimum ∧ SameValue KAPPA coreKappa ∧
    Below KAPPA minimum ∧ PairedCubeCore.literalCharge < PairedCubeCore.guardE := by
  exact ⟨all_46_slack_formulas_linked, all_seven_margin_formulas_linked,
    minimum_matches_core, explicit_kappa_unchanged.2.2, strict_absorption,
    PairedCubeCore.full_scalar_guard⟩

end PairedCubeAssembly13955
#print axioms PairedCubeAssembly13955.bit_saving_matches_core
#print axioms PairedCubeAssembly13955.q_matches_core
#print axioms PairedCubeAssembly13955.epsilon_matches_core
#print axioms PairedCubeAssembly13955.minimum_matches_core
#print axioms PairedCubeAssembly13955.explicit_kappa_unchanged
#print axioms PairedCubeAssembly13955.row_coefficient_retains_core_derivation
#print axioms PairedCubeAssembly13955.core_absorption_unchanged
#print axioms PairedCubeAssembly13955.all_47_strict_formula_checks
#print axioms PairedCubeAssembly13955.complete_finite_assembly_interface
