import EncodedDyadicAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.
Whole-run eleven-tape space closure for the unchanged executed controller.
Split the actual run at exponent completion, the two marker writes, and the
charged route switch. Reuse both accepted stage bounds. All original tapes,
consumed work and new markers remain counted, including post-halt prefixes.
The private trace observer is repeated solely because its predecessor is private.
No extra execution, endpoint, encoded-width or cost supplier is assumed.
Author-checked context kappa=836330098538459/500000000000000000.
-/
set_option Elab.async false
set_option autoImplicit false
namespace EncodedDyadicAdditionSpace
open EncodedDyadicAddition
open SequentialBitAddition (Registers)

private theorem trace_sound {n:Nat} {s t:State} (h:Trace n s t) : run n s=t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih

private theorem run_add (a b:Nat) (s:State) : run (a+b) s=run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ a ih => simpa only [Nat.succ_add,run] using ih (step s)

private theorem finished_iff (s:EncodedExponentControl.State) :
    exponentFinished s=true ↔ EncodedExponentControl.Halted s := by
  cases s with
  | layout => simp [exponentFinished,EncodedExponentControl.Halted]
  | control l r sx sy s => cases s with
    | difference => simp [exponentFinished,EncodedExponentControl.Halted,PairedDifferenceUnary.Halted]
    | conversion => simp [exponentFinished,EncodedExponentControl.Halted,PairedDifferenceUnary.Halted]

private theorem computing_prefix (c:Cargo) {n:Nat} {s t:EncodedExponentControl.State}
    (h:EncodedExponentControl.Trace n s t) (k:Nat) (hk:k≤n) :
    run k (.computing s c)=.computing (EncodedExponentControl.run k s) c := by
  induction h generalizing k with
  | nil s =>
      have he:k=0:=by omega
      subst k
      rfl
  | @next n s t live tail ih =>
      cases k with
      | zero => rfl
      | succ k =>
          have hn:exponentFinished s=false := by
            cases he:exponentFinished s
            · rfl
            · exact False.elim (live ((finished_iff s).mp he))
          simpa only [run,step,hn,Bool.false_eq_true,if_false,EncodedExponentControl.run] using
            ih k (by omega)

def bound (xp yp xs ys:List Bool) (er:Registers) : Nat :=
  frameCells (finalFrame xp yp er)+
    2*((leftShift xp yp er+xs.length)+(rightShift xp yp er+ys.length))+
    max (leftShift xp yp er+xs.length) (rightShift xp yp er+ys.length)+16

theorem frame_cells (xp yp:List Bool) (er:Registers) :
    frameCells (finalFrame xp yp er)=xp.length+yp.length+2*max xp.length yp.length+12 := by
  simp only [frameCells,finalFrame,BinaryToUnaryControl.tapeCells,
    MarkedBitDifference.tapeCells,BinaryToUnaryControl.zeroCounter,MarkedZeroPadding.marked,
    MarkedZeroPadding.bits,MarkedBitAddition.marked,List.length_nil,List.length_cons,
    List.length_append,List.length_map,List.length_replicate,MarkedBitDifference.chosen_length,
    EncodedExponentControl.rows_length]
  omega

private theorem cargo_cells (xs ys:List Bool) (sx sy bl br:Bool) (ar:Registers) :
    cargoCells (cargo xs ys sx sy bl br ar)=xs.length+ys.length+4 := by
  simp [cargoCells,cargo,BinaryToUnaryControl.tapeCells,MarkedBitDifference.tapeCells,
    MarkedZeroPadding.marked,MarkedZeroPadding.bits]
  omega

private theorem shifts_sum (xp yp:List Bool) (er:Registers) :
    leftShift xp yp er+rightShift xp yp er=EncodedExponentControl.magnitude xp yp er := by
  cases h:EncodedExponentControl.reverseFlag xp yp er <;> simp [leftShift,rightShift,h]

private theorem run_exponent_end (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    run (EncodedExponentControl.totalTime xp yp er) (initial xp yp xs ys sx sy bl br er ar)=
      .computing (EncodedExponentControl.final xp yp er) (cargo xs ys sx sy bl br ar) := by
  change run _ (.computing _ _)=_
  rw [computing_prefix _ (EncodedExponentControl.machine_exact xp yp er) _ (Nat.le_refl _),
    (EncodedExponentControl.machine_result xp yp er).1]

private theorem run_handoff (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    run (EncodedExponentControl.totalTime xp yp er+3) (initial xp yp xs ys sx sy bl br er ar)=
      .adding (finalFrame xp yp er) (EncodedExponentControl.reverseFlag xp yp er)
        (route (EncodedExponentControl.reverseFlag xp yp er)
          (PaddedSignedAddition.initial (leftShift xp yp er) xs sx (rightShift xp yp er) ys sy bl br ar)) := by
  rw [run_add,run_exponent_end]
  exact trace_sound (control_handoff xp yp xs ys sx sy bl br er ar)

/-- Each newly written zero-control marker contributes one represented cell.
Both statements concern actual run prefixes, not an output-ready assumption. -/
theorem marker_prefix_cells (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) :
    cells (run (EncodedExponentControl.totalTime xp yp er+1) (initial xp yp xs ys sx sy bl br er ar))=
      EncodedExponentControl.cells (EncodedExponentControl.final xp yp er)+xs.length+ys.length+5 ∧
    cells (run (EncodedExponentControl.totalTime xp yp er+2) (initial xp yp xs ys sx sy bl br er ar))=
      EncodedExponentControl.cells (EncodedExponentControl.final xp yp er)+xs.length+ys.length+6 := by
  constructor
  all_goals
    rw [run_add,run_exponent_end]
    simp [run,step,exponentFinished,EncodedExponentControl.final,PairedDifferenceUnary.final,
      BinaryToUnaryControl.final,cargo,cells,cargoCells,
      CurrentMain.PairedBitXorScan.Tape.writeHead,CurrentMain.PairedBitXorScan.Tape.moveRight,
      CurrentMain.PairedBitXorScan.Tape.moveLeft,BinaryToUnaryControl.tapeCells,
      MarkedBitDifference.tapeCells,MarkedZeroPadding.marked,MarkedZeroPadding.bits]
    omega

/-- Every prefix of the unchanged complete computation, including both new
marker states, the route transition, and the stuttering terminal tail. -/
theorem machine_prefix_storage (xp yp xs ys:List Bool) (sx sy bl br:Bool) (er ar:Registers) (k:Nat) :
    cells (run k (initial xp yp xs ys sx sy bl br er ar))≤bound xp yp xs ys er := by
  have hf:=frame_cells xp yp er
  have hd:=shifts_sum xp yp er
  have he:=EncodedExponentControl.machine_prefix_storage xp yp er
  have heFinal:=he (EncodedExponentControl.totalTime xp yp er)
  rw [(EncodedExponentControl.machine_result xp yp er).1] at heFinal
  by_cases hk:k≤EncodedExponentControl.totalTime xp yp er
  · change cells (run k (.computing _ _))≤_
    rw [computing_prefix _ (EncodedExponentControl.machine_exact xp yp er) k hk]
    simp only [cells,cargo_cells]
    have hh:=he k
    unfold bound
    omega
  · by_cases hm:k≤EncodedExponentControl.totalTime xp yp er+2
    · have hx:=marker_prefix_cells xp yp xs ys sx sy bl br er ar
      have hcases:k=EncodedExponentControl.totalTime xp yp er+1 ∨ k=EncodedExponentControl.totalTime xp yp er+2 := by omega
      rcases hcases with h|h
      · rw [h,hx.1];unfold bound;omega
      · rw [h,hx.2];unfold bound;omega
    · have hsplit:k=(EncodedExponentControl.totalTime xp yp er+3)+(k-(EncodedExponentControl.totalTime xp yp er+3)) := by omega
      rw [hsplit,run_add,run_handoff]
      exact addition_prefix_storage xp yp xs ys sx sy bl br er ar _

end EncodedDyadicAdditionSpace
#print axioms EncodedDyadicAdditionSpace.frame_cells
#print axioms EncodedDyadicAdditionSpace.marker_prefix_cells
#print axioms EncodedDyadicAdditionSpace.machine_prefix_storage
#check @EncodedDyadicAdditionSpace.machine_prefix_storage
