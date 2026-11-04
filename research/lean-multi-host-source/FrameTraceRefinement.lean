import FrameTraceCore
import PayloadGuards

/-!
Static frame labels and normalized whole-payload cleanliness imply the
chronological admissibility of the framed interpreter. The labels may be
interpreted by any supplied actual gauge family. Concrete projector and
owner-chart realization are separate from this interpreter theorem.
-/
namespace FrameTrace
open TreeReplay (Tree)

def Matches {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (labels : State) (physical : FramedReplay.Store X) : Prop :=
  physical.map Prod.fst = labels.frames.map gauges

theorem matches_get {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (labels : State) (physical : FramedReplay.Store X)
    (same : Matches gauges labels physical) (i : Nat) :
    (physical.get i).1 = gauges (labels.frames.get i) := by
  have h := congrArg (fun s => Tree.get s i) same
  simpa only [Tree.map_get] using h

theorem matches_step {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (labels : State) (physical : FramedReplay.Store X) (e : Entry)
    (same : Matches gauges labels physical) :
    Matches gauges (next labels e)
      (FramedReplay.physicalStep physical (toPhysical gauges e)) := by
  obtain ⟨⟨op, x, y, odd⟩, oldFrame, newFrame, rank⟩ := e
  change physical.map Prod.fst = labels.frames.map gauges at same
  cases op with
  | zero =>
      simpa only [Matches, next, toPhysical, FramedReplay.physicalStep,
        FramedReplay.reframe, Tree.map_put, Nat.zero_lt_succ, ↓reduceIte] using
        congrArg (fun s => s.put x (gauges newFrame)) same
  | succ op =>
      cases op with
      | zero =>
          cases odd with
          | false => exact same
          | true =>
              change (physical.put x _).map Prod.fst = labels.frames.map gauges
              rw [Tree.map_put]
              change (physical.map Prod.fst).put x ((physical.get x).1) = _
              rw [← Tree.map_get Prod.fst physical x, FramedReplay.put_get]
              exact same
      | succ op =>
          cases op with
          | zero =>
              simpa [Matches, next, toPhysical, FramedReplay.physicalStep,
                FramedReplay.reframe, Tree.map_put] using
                congrArg (fun s => s.put y (gauges newFrame)) same
          | succ op =>
              have hn : ¬ op + 1 + 1 + 1 < 3 := by omega
              simpa [Matches, next, toPhysical, FramedReplay.physicalStep,
                Tree.map_put, hn] using congrArg (fun s => s.put y (gauges 0)) same

theorem add_frames_equal (labels : State) (e : Entry)
    (checked : check labels e = true) (isAdd : e.scalar.op = 1) :
    labels.frames.get e.scalar.x = labels.frames.get e.scalar.y := by
  simp only [check, isAdd, Bool.and_eq_true, beq_iff_eq] at checked
  omega

/-- The gauge labels at the endpoint are obtained from the same chronological
trace, including the virtual reset on each erased blank temporary. -/
theorem matches_run {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (entries : List Entry) (labels : State) (physical : FramedReplay.Store X)
    (same : Matches gauges labels physical) (flag : Bool) :
    Matches gauges (runChecked entries (labels, flag)).1
      (FramedReplay.runPhysical (entries.map (toPhysical gauges)) physical) := by
  induction entries generalizing labels physical flag with
  | nil => exact same
  | cons e es ih =>
      exact ih (next labels e) (FramedReplay.physicalStep physical (toPhysical gauges e))
        (matches_step _ _ _ _ same) (flag && check labels e)

theorem valid_step {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (labels : State) (physical : FramedReplay.Store X) (e : Entry)
    (same : Matches gauges labels physical) (checked : check labels e = true)
    (clean : TreeReplay.PayloadClean (FramedReplay.decode physical) e.scalar) :
    FramedReplay.ValidStep physical (toPhysical gauges e) := by
  obtain ⟨⟨op, x, y, odd⟩, oldFrame, newFrame, rank⟩ := e
  cases op with
  | zero => trivial
  | succ op =>
      cases op with
      | zero =>
          change (physical.get x).1 = (physical.get y).1
          rw [matches_get _ _ _ same x, matches_get _ _ _ same y]
          exact congrArg gauges (add_frames_equal _ _ checked rfl)
      | succ op =>
          cases op with
          | zero =>
              have h := clean.1 rfl
              simpa only [FramedReplay.ValidStep, toPhysical, FramedReplay.decode,
                Tree.map_get] using h
          | succ op =>
              cases op with
              | zero =>
                  have h := clean.2 rfl
                  simpa only [FramedReplay.ValidStep, toPhysical, FramedReplay.decode,
                    Tree.map_get] using h
              | succ op =>
                  change false = true at checked
                  cases checked

theorem valid_trace {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (entries : List Entry) (labels : State) (physical : FramedReplay.Store X)
    (same : Matches gauges labels physical) (checked : Valid entries labels)
    (clean : TreeReplay.PayloadCleanRun (entries.map Entry.scalar)
      (FramedReplay.decode physical)) :
    FramedReplay.ValidTrace (entries.map (toPhysical gauges)) physical := by
  induction entries generalizing labels physical with
  | nil => trivial
  | cons e es ih =>
      have first := valid_step gauges labels physical e same checked.1 clean.1
      refine ⟨first, ?_⟩
      apply ih (next labels e) (FramedReplay.physicalStep physical (toPhysical gauges e))
        (matches_step _ _ _ _ same) checked.2
      rw [FramedReplay.decode_step _ _ first]
      exact clean.2

theorem decoded_run {X : Type} (gauges : Nat → FramedReplay.Gauge X)
    (entries : List Entry) (labels : State) (physical : FramedReplay.Store X)
    (same : Matches gauges labels physical) (checked : Valid entries labels)
    (clean : TreeReplay.PayloadCleanRun (entries.map Entry.scalar)
      (FramedReplay.decode physical)) :
    FramedReplay.decode (FramedReplay.runPhysical (entries.map (toPhysical gauges)) physical) =
      TreeReplay.runPayloads (entries.map Entry.scalar) (FramedReplay.decode physical) := by
  have h := FramedReplay.decode_run _ _ (valid_trace gauges entries labels physical same checked clean)
  simpa only [scalar_projection] using h

end FrameTrace

#print axioms FrameTrace.matches_get
#print axioms FrameTrace.matches_step
#print axioms FrameTrace.add_frames_equal
#print axioms FrameTrace.matches_run
#print axioms FrameTrace.valid_step
#print axioms FrameTrace.valid_trace
#print axioms FrameTrace.decoded_run
