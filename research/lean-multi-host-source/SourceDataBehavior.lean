import SourceInvocationComparison

/-!
The data operation of the selected call, with its actual unequal entrance
and exit frames displayed. The scalar certificate adds source i to target
120+i. Physical streams additionally undergo the stated frame and port-chart
pullbacks; this file does not identify those pullbacks with identity maps.
All data and helper payloads are arbitrary Boolean functions.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceDataBehavior
open SourceConnection FramedReplay
set_option maxRecDepth 100000
set_option maxHeartbeats 0
attribute [local irreducible] SourceFramed.final SourceRaw.final

def first (i : Fin 120) : Data := ⟨i.val, by omega⟩
def second (i : Fin 120) : Data := ⟨120 + i.val, by omega⟩

theorem first_initial_frame : ∀ i : Fin 120,
    SourceFrameTrace.state0.frames.get (first i).val = i.val + 2 := by decide
theorem second_initial_frame : ∀ i : Fin 120,
    SourceFrameTrace.state0.frames.get (second i).val = 0 := by decide
theorem first_final_frame : ∀ i : Fin 120,
    SourceFrameTrace.state96.frames.get (first i).val = 1 := by decide
theorem second_final_frame : ∀ i : Fin 120,
    SourceFrameTrace.state96.frames.get (second i).val = i.val + 824 := by decide

theorem framed_first {K : Type} (gauges : PhysicalSourceConnection.Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) (i : Fin 120) :
    PhysicalSourceConnection.physicalData gauges data helpers (first i) =
      fun a => data (first i)
        ((gauges (i.val + 2)).forward ((gauges 1).inverse a)) := by
  have he := congrFun
    (PhysicalSourceConnection.physical_data_endpoints gauges data helpers) (first i)
  apply he.trans
  funext a
  have hi : (first i).val < 987 := by simp only [first]; omega
  have hn : ¬ 120 ≤ (first i).val := by simp only [first]; omega
  simp only [SourceMatrix.endpointPayload, hi, hn, false_and, ↓reduceIte,
    SourceFramed.normalizedInput, packed_data, first_initial_frame, first_final_frame]

theorem framed_second {K : Type} (gauges : PhysicalSourceConnection.Gauges K)
    (data : Data → Streams K) (helpers : Host → Streams K) (i : Fin 120) :
    PhysicalSourceConnection.physicalData gauges data helpers (second i) =
      fun a => data (second i)
        ((gauges 0).forward ((gauges (i.val + 824)).inverse a)) ^^
        data (first i)
          ((gauges (i.val + 2)).forward ((gauges (i.val + 824)).inverse a)) := by
  have he := congrFun
    (PhysicalSourceConnection.physical_data_endpoints gauges data helpers) (second i)
  apply he.trans
  funext a
  have hi : (second i).val < 987 := by simp only [second]; omega
  have ht : 120 ≤ (second i).val ∧ (second i).val < 240 := by simp only [second]; omega
  have hs : (second i).val - 120 = (first i).val := by simp only [first, second]; omega
  simp only [SourceMatrix.endpointPayload, hi, ht, and_self, ↓reduceIte, hs,
    SourceFramed.normalizedInput, packed_data, first_initial_frame,
    second_initial_frame, second_final_frame]

/-- Complete output data function, in the actual owner-coordinate chart. -/
def dataFormula (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (gauges : SourceInvocation.Gauges K) (data : Data → Streams K) (i : Data) : Streams K :=
  SourceInvocation.dataOutput K h2 i
    (fun a => if ht : 120 ≤ i.val then
      SourceInvocation.dataInput K h2 i (data i)
        ((gauges 0).forward ((gauges (i.val - 120 + 824)).inverse a)) ^^
      SourceInvocation.dataInput K h2 ⟨i.val - 120, by omega⟩ (data ⟨i.val - 120, by omega⟩)
        ((gauges (i.val - 120 + 2)).forward
          ((gauges (i.val - 120 + 824)).inverse a))
    else SourceInvocation.dataInput K h2 i (data i)
      ((gauges (i.val + 2)).forward ((gauges 1).inverse a)))

theorem framed_data_formula (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (gauges : SourceInvocation.Gauges K) (data : Data → Streams K)
    (helpers : Host → Streams K) (i : Data) :
    SourceInvocation.dataOutput K h2 i
      (PhysicalSourceConnection.physicalData gauges
        (fun j => SourceInvocation.dataInput K h2 j (data j)) helpers i) =
      dataFormula K h2 gauges data i := by
  by_cases ht : 120 ≤ i.val
  · let j : Fin 120 := ⟨i.val - 120, by omega⟩
    have hj : second j = i := by apply Fin.ext; simp only [second, j]; omega
    rw [← hj, framed_second]
    unfold dataFormula
    have hjt : 120 ≤ (second j).val := by simp only [second]; omega
    simp only [dif_pos hjt]
    simp only [second, Nat.add_sub_cancel_left]
    rfl
  · let j : Fin 120 := ⟨i.val, by omega⟩
    have hj : first j = i := rfl
    rw [← hj, framed_first]
    unfold dataFormula
    have hjt : ¬ 120 ≤ (first j).val := ht
    simp only [hjt, ↓reduceDIte]
    rfl

/-- The actual old-bank invocation has this exact data endpoint, for every
independent dirty bank input. -/
theorem old_data_formula (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)
    (gauges : SourceInvocation.Gauges K) (s : SourceInvocation.State K h2 d)
    (bank : Host → Streams K) (i : Data) :
    (SourceInvocation.oldRaw K h2 d gauges s bank
      (SourceInvocation.oldOwner K h2 d (SourceLayouts.dataRole i))).2 =
      dataFormula K h2 gauges s.2.1 i :=
  (SourceInvocation.oldRaw_data K h2 d gauges s bank i).trans
    (framed_data_formula K h2 gauges s.2.1 _ i)

/-- The actual hosted invocation has the identical formula for all data,
despite every retained host carrying an arbitrary dirty stream. -/
theorem new_data_formula (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (d : SourceOwnership.Vec K ≃ SourceOwnership.Vec K)
    (gauges : SourceInvocation.Gauges K) (s : SourceInvocation.State K h2 d) (i : Data) :
    (SourceInvocation.newRaw K h2 d gauges s
      (SourceInvocation.newOwner K h2 d (SourceLayouts.dataRole i))).2 =
      dataFormula K h2 gauges s.2.1 i :=
  (SourceInvocation.newRaw_data K h2 d gauges s i).trans
    (framed_data_formula K h2 gauges s.2.1 _ i)

#print axioms first_initial_frame
#print axioms second_initial_frame
#print axioms first_final_frame
#print axioms second_final_frame
#print axioms framed_first
#print axioms framed_second
#print axioms framed_data_formula
#print axioms old_data_formula
#print axioms new_data_formula
end SourceDataBehavior
