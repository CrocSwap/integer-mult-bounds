import MultitapeToolkit.FrameRule

/-!
# Cost-preserving injection into a larger physical tape bank

The partial inverse is a lookup in a fixed finite tape index table. It is not
stored in control and never depends on input lengths or head coordinates.
Extra tapes may contain arbitrary dirty data; every literal step leaves them
stationary and rewrites their scanned symbol.
-/
namespace MultitapeToolkit.Absolute.TapeEmbedding
open MultitapeToolkit.Locality FrameRule
variable {I J Γ Q : Type*} [Fintype I] [Fintype J] [Fintype Γ] [Fintype Q]

noncomputable def decode (e : I ↪ J) (j : J) : Option I :=
  by
    classical
    exact if h : ∃ i, e i=j then some (Classical.choose h) else none

@[simp] theorem decode_image (e : I ↪ J) (i : I) : decode e (e i) = some i := by
  classical
  have h : ∃ k, e k=e i := ⟨i,rfl⟩
  have he : Classical.choose h=i := e.injective (Classical.choose_spec h)
  simp [decode,h,he]

theorem decode_some {e : I ↪ J} {j : J} {i : I} (h : decode e j=some i) : e i=j := by
  classical
  unfold decode at h
  split at h
  · next hex =>
    have he : Classical.choose hex=i := Option.some.inj h
    simpa [he] using Classical.choose_spec hex
  · contradiction

@[simp] theorem decode_none (e : I ↪ J) (j : J) : decode e j=none ↔ j ∉ Set.range e := by
  classical
  simp [decode,Set.mem_range]

/-- Selected tapes come from the source configuration; all others remain literal. -/
noncomputable def liftCfg (e : I ↪ J) (c : Config I Γ Q)
    (heads : J → ℤ) (cells : J → ℤ → Γ) : Config J Γ Q :=
  ⟨c.state,fun j => match decode e j with | some i => c.head i | none => heads j,
    fun j => match decode e j with | some i => c.cell i | none => cells j⟩

noncomputable def liftProgram (e : I ↪ J) (P : Program I Γ Q) : Program J Γ Q where
  transition q scanned := (P.transition q (fun i => scanned (e i))).map fun p =>
    (p.1,fun j => match decode e j with | some i => p.2 i | none => (scanned j,.stay))

@[simp] theorem liftCfg_state (e : I ↪ J) (c : Config I Γ Q) (H : J → ℤ) (C : J → ℤ → Γ) :
    (liftCfg e c H C).state=c.state := rfl
@[simp] theorem liftCfg_head_image (e : I ↪ J) (c : Config I Γ Q) (H : J → ℤ) (C : J → ℤ → Γ) (i : I) :
    (liftCfg e c H C).head (e i)=c.head i := by simp [liftCfg]
@[simp] theorem liftCfg_cell_image (e : I ↪ J) (c : Config I Γ Q) (H : J → ℤ) (C : J → ℤ → Γ) (i : I) :
    (liftCfg e c H C).cell (e i)=c.cell i := by simp [liftCfg]

theorem lift_step (e : I ↪ J) (P : Program I Γ Q) (c : Config I Γ Q)
    (H : J → ℤ) (C : J → ℤ → Γ) :
    step (liftProgram e P) (liftCfg e c H C) = (step P c).map (fun d => liftCfg e d H C) := by
  have hscan : (fun i => (liftCfg e c H C).cell (e i) ((liftCfg e c H C).head (e i))) =
      (fun i => c.cell i (c.head i)) := by funext i; simp
  simp only [step,liftProgram,liftCfg_state,hscan]
  cases ht : P.transition c.state (fun i => c.cell i (c.head i)) with
  | none => simp
  | some p =>
    simp only [Option.map_some]
    congr 1
    apply Config.ext
    · rfl
    · funext j
      cases hj : decode e j with
      | none => simp [liftCfg,hj,moveOffset]
      | some i => simp [liftCfg,hj]
    · funext j x
      cases hj : decode e j with
      | none =>
        by_cases hx : x=H j <;> simp [liftCfg,hj,hx]
      | some i => simp [liftCfg,hj]

theorem lift_runs (e : I ↪ J) (P : Program I Γ Q) {n : ℕ} {c d : Config I Γ Q}
    (hr : Runs P n c d) (H : J → ℤ) (C : J → ℤ → Γ) :
    Runs (liftProgram e P) n (liftCfg e c H C) (liftCfg e d H C) := by
  induction hr with
  | refl c => exact .refl _
  | cons hs hr ih =>
    apply Runs.cons (d := liftCfg e _ H C)
    · rw [lift_step,hs]; rfl
    · exact ih

theorem lift_halts (e : I ↪ J) (P : Program I Γ Q) (c : Config I Γ Q)
    (H : J → ℤ) (C : J → ℤ → Γ) :
    Halts (liftProgram e P) (liftCfg e c H C) ↔ Halts P c := by
  rw [Halts,lift_step,Halts]
  cases step P c <;> simp

theorem lift_idle (e : I ↪ J) (P : Program I Γ Q) (j : J) (hj : j ∉ Set.range e) :
    Trace.IdleOn (liftProgram e P) j := by
  intro q scanned next actions ht
  have hd : decode e j=none := (decode_none e j).2 hj
  cases hs : P.transition q (fun i => scanned (e i)) with
  | none => simp [liftProgram,hs] at ht
  | some p =>
    have ha : (fun k => match decode e k with | some i => p.2 i | none => (scanned k,Move.stay)) = actions := by
      have hp : p.1 = next ∧ (fun k => match decode e k with | some i => p.2 i | none => (scanned k,Move.stay)) = actions := by
        simpa [liftProgram,hs] using ht
      exact hp.2
    rw [← ha]
    simp [hd]

/-- Entire dirty extra tapes, not merely out-of-cone cells, survive every prefix. -/
theorem preserves_extra [Inhabited Γ] (e : I ↪ J) (P : Program I Γ Q) (j : J) (hj : j ∉ Set.range e)
    {n : ℕ} {c d : Config J Γ Q} (hr : Runs (liftProgram e P) n c d) :
    d.head j=c.head j ∧ ∀ x, d.cell j x=c.cell j x :=
  Trace.runs_idle_tape _ j (lift_idle e P j hj) hr

end MultitapeToolkit.Absolute.TapeEmbedding


