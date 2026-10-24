import FrameMoveData
import FrameLabelData
import SelectedGeometry
import FrameTraceRoutes

/-!
The actual MOVE records execute the source operation D_(Pnew-Pold).
Every used absorption equation is selected by membership in the literal
19,002-event word. The common stage-2 exterior swap E2 is present in the
gauges and cancels explicitly. No payload is assumed zero or independent.

The full replay equality below replaces MOVE by its matrix residual action
and COPY by the checked full-local-eight-coordinate transport.
The native-step equality additionally includes conjugation by the common
invocation chart d; it retains every physical stream other than the target.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
-/
namespace SourceMoveGeometry
open FrameGeometry SourceFrameMoves
open scoped Matrix BigOperators
set_option maxRecDepth 100000
set_option maxHeartbeats 0

/-- Both nesting equations follow from the checked pair of this MOVE. -/
theorem move_projectors (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 0) :
    projector K (oldIndex e) * projector K (newIndex e) = projector K (oldIndex e) ∧
    projector K (newIndex e) * projector K (oldIndex e) = projector K (oldIndex e) := by
  have h := move_absorbs e he hop
  constructor
  · apply normalized_absorption K h2
    ext i j
    simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, dot8, scaledMatrix] using h.1 i j
  · apply normalized_absorption K h2
    ext i j
    simpa [Matrix.mul_apply, Fin.sum_univ_succ, Matrix.smul_apply, dot8, scaledMatrix] using h.2 i j

/-- D of the new-minus-old local projector, identity on the other 56 axes. -/
def residual64 (K : Type) [Field K] (e : FrameTrace.Entry) :
    AddressPairs.Vectors (Fin 64) K → AddressPairs.Vectors (Fin 64) K :=
  liftPair (partialSwap (projector K (newIndex e) - projector K (oldIndex e)))

theorem move_stage2_relative (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 0)
    (p : AddressPairs.Vectors (Fin 64) K) :
    (gaugeStage2 K h2 (oldIndex e)).forward
      ((gaugeStage2 K h2 (newIndex e)).inverse p) = residual64 K e p := by
  rw [stage2_relative_transport]
  change liftPair (partialSwap (projector K (oldIndex e)))
    (liftPair (partialSwap (projector K (newIndex e))) p) = _
  rw [liftPair_comp]
  have h : partialSwap (projector K (oldIndex e)) ∘
      partialSwap (projector K (newIndex e)) =
      partialSwap (projector K (newIndex e) - projector K (oldIndex e)) := by
    funext q
    exact partialSwap_nested_reverse _ _ (move_projectors K h2 e he hop).1 q
  rw [h]
  rfl

def residualAddress (K : Type) [Field K] (e : FrameTrace.Entry)
    (a : PhysicalSourceConnection.Address64 K) : PhysicalSourceConnection.Address64 K :=
  AddressPairs.join (residual64 K e (AddressPairs.split a))

/-- Exact relative map used by the selected source gauge provider. -/
theorem move_relative (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 0)
    (a : PhysicalSourceConnection.Address64 K) :
    (SelectedGeometry.gauges K h2 e.oldFrame).forward
      ((SelectedGeometry.gauges K h2 e.newFrame).inverse a) = residualAddress K e a := by
  change (AddressPairs.gauge (gaugeStage2 K h2 (oldIndex e))).forward
    ((AddressPairs.gauge (gaugeStage2 K h2 (newIndex e))).inverse a) = _
  rw [AddressPairs.relative_gauge, move_stage2_relative K h2 e he hop]
  rfl

def fullSwap64 (K : Type) : AddressPairs.Vectors (Fin 64) K → AddressPairs.Vectors (Fin 64) K :=
  liftPair (fun p => (p.2, p.1))

def fullSwapAddress (K : Type) (a : PhysicalSourceConnection.Address64 K) :=
  AddressPairs.join (fullSwap64 K (AddressPairs.split a))

theorem copy_stage2_relative (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (p : AddressPairs.Vectors (Fin 64) K) :
    (gaugeStage2 K h2 1).forward ((gaugeStage2 K h2 0).inverse p) = fullSwap64 K p := by
  rw [stage2_relative_transport]
  change liftPair (partialSwap (projector K 1))
    (liftPair (partialSwap (projector K 0)) p) = _
  rw [liftPair_comp]
  have h : partialSwap (projector K 1) ∘ partialSwap (projector K 0) =
      fun p => (p.2, p.1) := by
    funext q
    rw [projector_full K h2, projector_zero K]
    apply Prod.ext <;> funext i <;>
      simp only [Function.comp_apply, partialSwap, Matrix.zero_mulVec, add_zero,
        sub_zero, Matrix.one_mulVec, Pi.add_apply, Pi.sub_apply] <;> ring
  rw [h]
  rfl

/-- Actual COPY records have old frame 1 and new frame 0, checked on the
literal word. Their full E2 factors cancel, leaving exactly eight axes. -/
theorem copy_relative (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 2)
    (a : PhysicalSourceConnection.Address64 K) :
    (SelectedGeometry.gauges K h2 e.oldFrame).forward
      ((SelectedGeometry.gauges K h2 e.newFrame).inverse a) = fullSwapAddress K a := by
  obtain ⟨ho, hn⟩ := SourceFrameLabels.copy_frames e he hop
  rw [ho, hn]
  change (AddressPairs.gauge (gaugeStage2 K h2 1)).forward
    ((AddressPairs.gauge (gaugeStage2 K h2 0)).inverse a) = _
  rw [AddressPairs.relative_gauge, copy_stage2_relative K h2]
  rfl

/-- The source row and temporary at each actual ERASE use the same full/zero
pair. This identifies the transport appearing in the equality guard. -/
theorem erase_relative (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 3)
    (a : PhysicalSourceConnection.Address64 K) :
    (SelectedGeometry.gauges K h2 e.oldFrame).forward
      ((SelectedGeometry.gauges K h2 e.newFrame).inverse a) = fullSwapAddress K a := by
  obtain ⟨ho, hn⟩ := SourceFrameLabels.erase_frames e he hop
  rw [ho, hn]
  change (AddressPairs.gauge (gaugeStage2 K h2 1)).forward
    ((AddressPairs.gauge (gaugeStage2 K h2 0)).inverse a) = _
  rw [AddressPairs.relative_gauge, copy_stage2_relative K h2]
  rfl

def matrixMove (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K)) (e : FrameTrace.Entry) :=
  s.put e.scalar.x (SelectedGeometry.gauges K h2 e.newFrame,
    fun a => (s.get e.scalar.x).2 (residualAddress K e a))

/-- At a checked occurrence, the old frame is the actual current row frame.
Consequently reframe executes D_(Pnew-Pold) on every arbitrary dirty payload. -/
theorem physicalStep_move (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 0)
    (labels : FrameTrace.State) (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K))
    (same : FrameTrace.Matches (SelectedGeometry.gauges K h2) labels s)
    (checked : FrameTrace.check labels e = true) :
    FramedReplay.physicalStep s (FrameTrace.toPhysical (SelectedGeometry.gauges K h2) e) =
      matrixMove K h2 s e := by
  have old : labels.frames.get e.scalar.x = e.oldFrame := by
    simp only [FrameTrace.check, hop, Bool.and_eq_true, beq_iff_eq] at checked
    exact checked.1.2
  have hf := FrameTrace.matches_get _ _ _ same e.scalar.x
  rw [old] at hf
  simp only [FramedReplay.physicalStep, FrameTrace.toPhysical, hop, Nat.zero_lt_succ,
    ↓reduceIte, FramedReplay.reframe, hf, matrixMove]
  congr 1
  apply Prod.ext
  · rfl
  · funext a
    exact congrArg (s.get e.scalar.x).2 (move_relative K h2 e he hop a)

def matrixCopy (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K)) (e : FrameTrace.Entry) :=
  s.put e.scalar.y (SelectedGeometry.gauges K h2 e.newFrame,
    fun a => (s.get e.scalar.x).2 (fullSwapAddress K a))

/-- Operational COPY equality. Legality also requires the destination to be
blank; SourceFramed.actual_valid proves that separate guard at every COPY. -/
theorem physicalStep_copy (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 2)
    (labels : FrameTrace.State) (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K))
    (same : FrameTrace.Matches (SelectedGeometry.gauges K h2) labels s)
    (checked : FrameTrace.check labels e = true) :
    FramedReplay.physicalStep s (FrameTrace.toPhysical (SelectedGeometry.gauges K h2) e) =
      matrixCopy K h2 s e := by
  have old : labels.frames.get e.scalar.x = e.oldFrame := by
    simp only [FrameTrace.check, hop, Bool.and_eq_true, beq_iff_eq] at checked
    omega
  have hf := FrameTrace.matches_get _ _ _ same e.scalar.x
  rw [old] at hf
  simp only [FramedReplay.physicalStep, FrameTrace.toPhysical, hop, Nat.reduceLT,
    ↓reduceIte, FramedReplay.reframe, hf, matrixCopy]
  congr 1
  apply Prod.ext
  · rfl
  · funext a
    exact congrArg (s.get e.scalar.x).2 (copy_relative K h2 e he hop a)

/-- The operational replay uses the explicit matrix operation at each MOVE. -/
def matrixStep (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K)) (e : FrameTrace.Entry) :=
  if e.scalar.op = 0 then matrixMove K h2 s e
  else if e.scalar.op = 2 then matrixCopy K h2 s e
  else FramedReplay.physicalStep s (FrameTrace.toPhysical (SelectedGeometry.gauges K h2) e)

def matrixRun (K : Type) [Field K] (h2 : (2 : K) ≠ 0) (es : List FrameTrace.Entry)
    (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K)) :=
  es.foldl (matrixStep K h2) s

theorem matrix_run_eq (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (es : List FrameTrace.Entry) (members : ∀ e ∈ es, e ∈ SourceFrameTrace.forward)
    (labels : FrameTrace.State) (s : FramedReplay.Store (PhysicalSourceConnection.Address64 K))
    (same : FrameTrace.Matches (SelectedGeometry.gauges K h2) labels s)
    (checked : FrameTrace.Valid es labels) :
    matrixRun K h2 es s = FramedReplay.runPhysical
      (es.map (FrameTrace.toPhysical (SelectedGeometry.gauges K h2))) s := by
  induction es generalizing labels s with
  | nil => rfl
  | cons e es ih =>
      have step : matrixStep K h2 s e = FramedReplay.physicalStep s
          (FrameTrace.toPhysical (SelectedGeometry.gauges K h2) e) := by
        unfold matrixStep
        split
        · exact (physicalStep_move K h2 e (members e (by simp)) ‹_› labels s same checked.1).symm
        · split
          · exact (physicalStep_copy K h2 e (members e (by simp)) ‹_› labels s same checked.1).symm
          · rfl
      change matrixRun K h2 es (matrixStep K h2 s e) =
        FramedReplay.runPhysical (es.map (FrameTrace.toPhysical (SelectedGeometry.gauges K h2)))
          (FramedReplay.physicalStep s (FrameTrace.toPhysical (SelectedGeometry.gauges K h2) e))
      rw [step]
      exact ih (fun a ha => members a (by simp [ha])) (FrameTrace.next labels e) _
        (FrameTrace.matches_step _ _ _ _ same) checked.2

/-- The actual 19,002-event run is the same run with all MOVE/COPY operations
interpreted by their certified matrix operators, for every dirty input. -/
theorem actual_matrix_run (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    (input : Nat → PhysicalSourceConnection.Address64 K → Bool) :
    matrixRun K h2 SourceFrameTrace.forward
      (SourceFramed.initial (SelectedGeometry.gauges K h2) input) =
      SourceFramed.final (SelectedGeometry.gauges K h2) input :=
  matrix_run_eq K h2 _ (fun _ h => h) SourceFrameTrace.state0 _
    (SourceFramed.initial_matches _ _) SourceFrameTrace.forward_valid

/-- Native physical MOVE: pull back the dirty target by d D_(new-old) d⁻¹.
Only the target stream changes; the frame metadata records the new frame. -/
noncomputable def nativeMatrixMove (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    {R S : Type} (owner : R → S) (d : FramedReplay.Gauge (PhysicalSourceConnection.Address64 K))
    (native : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K)) (x : R)
    (e : FrameTrace.Entry) : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K) := by
  classical
  exact fun s => if s = owner x then
    (SelectedGeometry.gauges K h2 e.newFrame, fun a => (native s).2
      (d.forward (residualAddress K e (d.inverse a))))
    else native s

/-- The owner-routing interpreter's MOVE is exactly the physical conjugate,
not an abstract reframe operation disconnected from the source projector. -/
theorem nativeStep_move (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    {R S : Type} (owner : R → S) (d : FramedReplay.Gauge (PhysicalSourceConnection.Address64 K))
    (native : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K)) (x y : R)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 0)
    (old : (native (owner x)).1 = SelectedGeometry.gauges K h2 e.oldFrame) :
    OwnerTransport.nativeStep owner d native e.scalar.op x y e.scalar.odd
      (SelectedGeometry.gauges K h2 e.newFrame) = nativeMatrixMove K h2 owner d native x e := by
  classical
  funext s
  by_cases hs : s = owner x
  · subst s
    simp only [OwnerTransport.nativeStep, hop, OwnerTransport.nativeTransport,
      nativeMatrixMove, ↓reduceIte, old]
    apply Prod.ext
    · rfl
    · funext a
      exact congrArg (fun b => (native (owner x)).2 (d.forward b))
        (move_relative K h2 e he hop (d.inverse a))
  · simp only [OwnerTransport.nativeStep, hop, OwnerTransport.nativeTransport,
      nativeMatrixMove, if_neg hs]

/-- The same equality for the exact finite-role event encoding consumed by
the checked source native run. Membership ranges were checked separately by
FrameTraceRoutes; the encoded role below is the actual target role. -/
theorem nativeRoute_move (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    {S : Type} (owner : Fin 988 → S)
    (d : FramedReplay.Gauge (PhysicalSourceConnection.Address64 K))
    (native : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K))
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 0)
    (old : (native (owner (SourceFrameTrace.toRoute (SelectedGeometry.gauges K h2) e).x)).1 =
      SelectedGeometry.gauges K h2 e.oldFrame) :
    let routed := SourceFrameTrace.toRoute (SelectedGeometry.gauges K h2) e
    OwnerTransport.nativeStep owner d native routed.op routed.x routed.y routed.odd routed.newFrame =
      nativeMatrixMove K h2 owner d native routed.x e := by
  dsimp only
  have h := nativeStep_move K h2 owner d native
    (SourceFrameTrace.toRoute (SelectedGeometry.gauges K h2) e).x
    (SourceFrameTrace.toRoute (SelectedGeometry.gauges K h2) e).y e he hop old
  simpa only [SourceFrameTrace.toRoute, hop, Nat.zero_lt_succ, ↓reduceIte] using h

noncomputable def nativeMatrixCopy (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    {R S : Type} (owner : R → S) (d : FramedReplay.Gauge (PhysicalSourceConnection.Address64 K))
    (native : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K)) (x y : R)
    (e : FrameTrace.Entry) : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K) := by
  classical
  exact fun s => if s = owner y then
    (SelectedGeometry.gauges K h2 e.newFrame, fun a => (native (owner x)).2
      (d.forward (fullSwapAddress K (d.inverse a))))
    else native s

/-- Native COPY is conjugation of the full eight-coordinate swap. The
separate native clean-work guard remains mandatory for a legal COPY. -/
theorem nativeStep_copy (K : Type) [Field K] (h2 : (2 : K) ≠ 0)
    {R S : Type} (owner : R → S) (d : FramedReplay.Gauge (PhysicalSourceConnection.Address64 K))
    (native : OwnerTransport.Raw S (PhysicalSourceConnection.Address64 K)) (x y : R)
    (e : FrameTrace.Entry) (he : e ∈ SourceFrameTrace.forward) (hop : e.scalar.op = 2)
    (old : (native (owner x)).1 = SelectedGeometry.gauges K h2 e.oldFrame) :
    OwnerTransport.nativeStep owner d native e.scalar.op x y e.scalar.odd
      (SelectedGeometry.gauges K h2 e.newFrame) = nativeMatrixCopy K h2 owner d native x y e := by
  classical
  funext s
  by_cases hs : s = owner y
  · subst s
    simp only [OwnerTransport.nativeStep, hop, OwnerTransport.nativeTransport,
      nativeMatrixCopy, ↓reduceIte, old]
    apply Prod.ext
    · rfl
    · funext a
      exact congrArg (fun b => (native (owner x)).2 (d.forward b))
        (copy_relative K h2 e he hop (d.inverse a))
  · simp only [OwnerTransport.nativeStep, hop, OwnerTransport.nativeTransport,
      nativeMatrixCopy, if_neg hs]

end SourceMoveGeometry

#print axioms SourceMoveGeometry.move_projectors
#print axioms SourceMoveGeometry.move_stage2_relative
#print axioms SourceMoveGeometry.move_relative
#print axioms SourceMoveGeometry.copy_stage2_relative
#print axioms SourceMoveGeometry.copy_relative
#print axioms SourceMoveGeometry.erase_relative
#print axioms SourceMoveGeometry.physicalStep_move
#print axioms SourceMoveGeometry.physicalStep_copy
#print axioms SourceMoveGeometry.matrix_run_eq
#print axioms SourceMoveGeometry.actual_matrix_run
#print axioms SourceMoveGeometry.nativeStep_move
#print axioms SourceMoveGeometry.nativeRoute_move
#print axioms SourceMoveGeometry.nativeStep_copy
