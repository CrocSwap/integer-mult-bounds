import MultitapeToolkit.ParkStack

set_option autoImplicit false

/-!
# Actual parking-pop footprints and all-prefix ancestor safety

The fixed retained pop table is unchanged. An inductive marker/phase invariant
proves lower bounds at every successful transition, then annotates the actual
exact run with its read/write footprint. No endpoint-only inference is used.
-/
namespace MultitapeToolkit.Absolute.ParkFootprints
open MultitapeToolkit.Locality MarkedStreams ParkStack FrameRule
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def popFloors (q : PopPhase) (source temporary parking base : ℤ) : Prop :=
  match q with
  | .enterDelimiter => base+1 ≤ parking ∧ 0 ≤ temporary ∧ 0 ≤ source
  | .enterPayload => base ≤ parking ∧ 0 ≤ temporary ∧ 0 ≤ source
  | .copyPark => base-1 ≤ parking ∧ 0 ≤ temporary ∧ 0 ≤ source
  | .copyOutput => base ≤ parking ∧ -1 ≤ temporary ∧ 0 ≤ source
  | .rewindOutput => base ≤ parking ∧ 0 ≤ temporary ∧ -1 ≤ source
  | .done => base-1 ≤ parking ∧ -1 ≤ temporary ∧ -1 ≤ source

structure PopSafe (s t p : ι) (base : ℤ) (c : Config ι Symbol PopPhase) : Prop where
  sourceMarker : c.cell s (-1) = .separator
  temporaryMarker : c.cell t (-1) = .separator
  parkingMarker : c.cell p (base-1) = .separator
  floors : popFloors c.state (c.head s) (c.head t) (c.head p) base

omit [Fintype ι] [DecidableEq ι] in
theorem PopSafe.basic {s t p : ι} {base : ℤ} {c : Config ι Symbol PopPhase}
    (h : PopSafe s t p base c) :
    base-1 ≤ c.head p ∧ -1 ≤ c.head t ∧ -1 ≤ c.head s := by
  have hf := h.floors
  cases hq : c.state <;> simp only [hq,popFloors] at hf <;> omega

def nextCfg (s t p : ι) (c : Config ι Symbol PopPhase) (q : PopPhase)
    (a b d : Symbol × Move) : Config ι Symbol PopPhase :=
  let actions := actions3 s t p a b d (fun i => c.cell i (c.head i))
  ⟨q,fun i => c.head i+moveOffset (actions i).2,
    fun i x => if x=c.head i then (actions i).1 else c.cell i x⟩

theorem marker_write (head marker : ℤ) (cell : ℤ → Symbol) (v : Symbol)
    (hm : cell marker = .separator) (hw : head=marker → v=.separator) :
    (if marker=head then v else cell marker) = .separator := by
  by_cases hh : marker=head
  · exact (if_pos hh).trans (hw hh.symm)
  · simp [hh,hm]

omit [Fintype ι] in
theorem next_safe (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (base : ℤ) (c : Config ι Symbol PopPhase) (q : PopPhase) (a b d : Symbol × Move)
    (hi : PopSafe s t p base c)
    (ha : c.head s = -1 → a.1 = .separator)
    (hb : c.head t = -1 → b.1 = .separator)
    (hd : c.head p = base-1 → d.1 = .separator)
    (hf : popFloors q (c.head s+moveOffset a.2) (c.head t+moveOffset b.2)
      (c.head p+moveOffset d.2) base) :
    PopSafe s t p base (nextCfg s t p c q a b d) := by
  constructor
  · simpa [nextCfg,actions3] using marker_write (c.head s) (-1) (c.cell s) a.1 hi.sourceMarker ha
  · simpa [nextCfg,actions3,Ne.symm hst,htp] using
      marker_write (c.head t) (-1) (c.cell t) b.1 hi.temporaryMarker hb
  · simpa [nextCfg,actions3,Ne.symm hsp] using
      marker_write (c.head p) (base-1) (c.cell p) d.1 hi.parkingMarker hd
  · simpa [nextCfg,actions3,Ne.symm hst,Ne.symm hsp,htp] using hf

theorem step_safe_of_table (s t p : ι) (base : ℤ)
    {c e : Config ι Symbol PopPhase} (q : PopPhase) (a b d : Symbol × Move)
    (ht : (popProgram s t p).transition c.state (fun i => c.cell i (c.head i)) =
      some (q,actions3 s t p a b d (fun i => c.cell i (c.head i))))
    (hs : step (popProgram s t p) c = some e)
    (hi : PopSafe s t p base (nextCfg s t p c q a b d)) : PopSafe s t p base e := by
  have he : e = nextCfg s t p c q a b d := by
    simpa [step,ht,nextCfg] using hs.symm
  rw [he]
  exact hi

theorem bit_above_marker (head marker : ℤ) (cell : ℤ → Symbol) (b : Bool)
    (hf : marker ≤ head) (hm : cell marker = .separator) (hb : cell head = .bit b) : marker < head := by
  have hn : head ≠ marker := by
    intro he
    rw [he,hm] at hb
    cases hb
  omega

theorem pop_step_safe (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (base : ℤ) {c e : Config ι Symbol PopPhase}
    (hi : PopSafe s t p base c) (hs : step (popProgram s t p) c = some e) :
    PopSafe s t p base e := by
  have hmS := hi.sourceMarker
  have hmT := hi.temporaryMarker
  have hmP := hi.parkingMarker
  have hf := hi.floors
  cases hq : c.state with
  | done => simp [step,popProgram,hq] at hs
  | enterDelimiter =>
    simp only [hq,popFloors] at hf
    apply step_safe_of_table s t p base .enterPayload
      (c.cell s (c.head s),.stay) (c.cell t (c.head t),.stay) (c.cell p (c.head p),.left)
      (by simp [popProgram,hq]) hs
    apply next_safe s t p hst hsp htp base c .enterPayload _ _ _ hi
    · intro h; simpa [h] using hmS
    · intro h; simpa [h] using hmT
    · intro h; simpa [h] using hmP
    · simp only [popFloors,moveOffset]; omega
  | enterPayload =>
    simp only [hq,popFloors] at hf
    apply step_safe_of_table s t p base .copyPark
      (c.cell s (c.head s),.stay) (c.cell t (c.head t),.stay) (.blank,.left)
      (by simp [popProgram,hq]) hs
    apply next_safe s t p hst hsp htp base c .copyPark _ _ _ hi
    · intro h; simpa [h] using hmS
    · intro h; simpa [h] using hmT
    · intro h; omega
    · simp only [popFloors,moveOffset]; omega
  | copyPark =>
    simp only [hq,popFloors] at hf
    cases hb : c.cell p (c.head p) with
    | blank =>
      apply step_safe_of_table s t p base .done
        (c.cell s (c.head s),.stay) (c.cell t (c.head t),.stay) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .done _ _ _ hi
      · intro h; simpa [h] using hmS
      · intro h; simpa [h] using hmT
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega
    | separator =>
      apply step_safe_of_table s t p base .copyOutput
        (c.cell s (c.head s),.stay) (c.cell t (c.head t),.left) (.separator,.right)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .copyOutput _ _ _ hi
      · intro h; simpa [h] using hmS
      · intro h; simpa [h] using hmT
      · intro _; rfl
      · simp only [popFloors,moveOffset]; omega
    | bit b =>
      have hp := bit_above_marker (c.head p) (base-1) (c.cell p) b hf.1 hmP hb
      apply step_safe_of_table s t p base .copyPark
        (c.cell s (c.head s),.stay) (.bit b,.right) (.blank,.left)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .copyPark _ _ _ hi
      · intro h; simpa [h] using hmS
      · intro h; omega
      · intro h; omega
      · simp only [popFloors,moveOffset]; omega
  | copyOutput =>
    simp only [hq,popFloors] at hf
    cases hb : c.cell t (c.head t) with
    | blank =>
      apply step_safe_of_table s t p base .done
        (c.cell s (c.head s),.stay) (c.cell t (c.head t),.stay) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .done _ _ _ hi
      · intro h; simpa [h] using hmS
      · intro h; simpa [h] using hmT
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega
    | separator =>
      apply step_safe_of_table s t p base .rewindOutput
        (c.cell s (c.head s),.left) (.separator,.right) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .rewindOutput _ _ _ hi
      · intro h; simpa [h] using hmS
      · intro _; rfl
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega
    | bit b =>
      have ht := bit_above_marker (c.head t) (-1) (c.cell t) b hf.2.1 hmT hb
      apply step_safe_of_table s t p base .copyOutput
        (.bit b,.right) (.blank,.left) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .copyOutput _ _ _ hi
      · intro h; omega
      · intro h; omega
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega
  | rewindOutput =>
    simp only [hq,popFloors] at hf
    cases hb : c.cell s (c.head s) with
    | blank =>
      apply step_safe_of_table s t p base .done
        (c.cell s (c.head s),.stay) (c.cell t (c.head t),.stay) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .done _ _ _ hi
      · intro h; simpa [h] using hmS
      · intro h; simpa [h] using hmT
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega
    | separator =>
      apply step_safe_of_table s t p base .done
        (.separator,.right) (c.cell t (c.head t),.stay) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .done _ _ _ hi
      · intro _; rfl
      · intro h; simpa [h] using hmT
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega
    | bit b =>
      have hsrc := bit_above_marker (c.head s) (-1) (c.cell s) b hf.2.2 hmS hb
      apply step_safe_of_table s t p base .rewindOutput
        (.bit b,.left) (c.cell t (c.head t),.stay) (c.cell p (c.head p),.stay)
        (by simp [popProgram,hq,hb]) hs
      apply next_safe s t p hst hsp htp base c .rewindOutput _ _ _ hi
      · intro h; rw [h,hmS] at hb; cases hb
      · intro h; simpa [h] using hmT
      · intro h; simpa [h] using hmP
      · simp only [popFloors,moveOffset]; omega

end MultitapeToolkit.Absolute.ParkFootprints

namespace MultitapeToolkit.Absolute.ParkFootprints
open MultitapeToolkit.Locality MarkedStreams ParkStack FrameRule
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Every actual prefix preserves all marker facts and the phase floors. -/
theorem pop_runs_safe (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (base : ℤ) {n : ℕ} {c e : Config ι Symbol PopPhase}
    (hr : Runs (popProgram s t p) n c e) : PopSafe s t p base c → PopSafe s t p base e := by
  induction hr with
  | refl c => exact fun h => h
  | cons hs hr ih => exact fun hi => ih (pop_step_safe s t p hst hsp htp base hi hs)

@[simp] theorem empty_word_marker : word [] (-1) = .separator := by
  simp [word,markedStream,cellView]

@[simp] theorem parkRecord_marker (bits : List Bool) (base : ℤ) (past : ℤ → Symbol) :
    parkRecord bits base past (base-1) = .separator := by
  have hh : base-1 < base+bits.length+1 := by omega
  have hi : (base+bits.length+1-(base-1)-1).toNat = bits.length+1 := by omega
  have hl : (.separator::(bits.reverse.map Symbol.bit ++ [.separator])).length = bits.length+2 := by simp
  have hb : bits.length+1 < bits.length+2 := by omega
  simp only [parkRecord,cellView,if_pos hh,hi,hl,if_pos hb,List.getD_cons_succ]
  rw [List.getD_append_right _ _ _ _ (by simp)]
  simp

theorem popInput_safe (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    PopSafe s t p base (popInput s t p bits base past heads cells) := by
  constructor
  · simp only [popInput,bank3,bank2,ite_true,empty_cell,empty_word_marker]
  · simp only [popInput,bank3,bank2,if_neg (Ne.symm hst),if_neg htp,ite_true,empty_cell,empty_word_marker]
  · simpa only [popInput,bank3,bank2,if_neg (Ne.symm hsp),ite_true,record_cell] using
      parkRecord_marker bits base past
  · simp [popInput,bank3,bank2,popFloors,atEnd,Ne.symm hst,Ne.symm hsp,htp] <;> omega

/-- Universal all-prefix read bounds of the actual retained pop machine. -/
theorem pop_prefix_read_floor (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) {n : ℕ} {e : Config ι Symbol PopPhase}
    (hr : Runs (popProgram s t p) n (popInput s t p bits base past heads cells) e) :
    base-1 ≤ e.head p ∧ -1 ≤ e.head t ∧ -1 ≤ e.head s :=
  (pop_runs_safe s t p hst hsp htp base hr
    (popInput_safe s t p hst hsp htp bits base past heads cells)).basic

/-- Decorating an actual run does not change its count; every recorded selected
read/write coordinate satisfies the proven invariant's lower bound. -/
theorem pop_runs_footprint (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (base : ℤ) {n : ℕ} {c e : Config ι Symbol PopPhase}
    (hr : Runs (popProgram s t p) n c e) : PopSafe s t p base c →
    ∃ F : ι → Finset ℤ, FootprintedRuns (popProgram s t p) n c e F ∧
      (F p : Set ℤ) ⊆ Set.Ici (base-1) ∧ (F t : Set ℤ) ⊆ Set.Ici (-1) ∧
      (F s : Set ℤ) ⊆ Set.Ici (-1) := by
  induction hr with
  | refl c =>
    intro _
    exact ⟨fun _ => ∅,.refl c,by simp,by simp,by simp⟩
  | @cons n c d e hs hr ih =>
    intro hi
    rcases ih (pop_step_safe s t p hst hsp htp base hi hs) with ⟨F,hF,hp,ht,hsrc⟩
    refine ⟨fun i => insert (c.head i) (F i),.cons hs hF,?_,?_,?_⟩
    · intro x hx
      rcases Finset.mem_insert.mp hx with he | hx
      · subst x; exact hi.basic.1
      · exact hp hx
    · intro x hx
      rcases Finset.mem_insert.mp hx with he | hx
      · subst x; exact hi.basic.2.1
      · exact ht hx
    · intro x hx
      rcases Finset.mem_insert.mp hx with he | hx
      · subst x; exact hi.basic.2.2
      · exact hsrc hx

/-- Exact completed pop with an actual bounded footprint and a cell-by-cell
ancestor frame. The arbitrary prefix is protected throughout execution. -/
theorem pop_completed_footprint (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    ∃ F : ι → Finset ℤ,
      FootprintedRuns (popProgram s t p) (3*bits.length+5)
        (popInput s t p bits base past heads cells) (popFinal s t p bits base past heads cells) F ∧
      Halts (popProgram s t p) (popFinal s t p bits base past heads cells) ∧
      (F p : Set ℤ) ⊆ Set.Ici (base-1) ∧ (F t : Set ℤ) ⊆ Set.Ici (-1) ∧
      (F s : Set ℤ) ⊆ Set.Ici (-1) ∧
      ∀ x, x < base-1 →
        (popFinal s t p bits base past heads cells).cell p x =
        (popInput s t p bits base past heads cells).cell p x := by
  rcases pop_runs_footprint s t p hst hsp htp base
    (pop_correct s t p hst hsp htp bits base past heads cells)
    (popInput_safe s t p hst hsp htp bits base past heads cells) with ⟨F,hF,hp,ht,hs⟩
  refine ⟨F,hF,popFinal_halts s t p bits base past heads cells,hp,ht,hs,?_⟩
  intro x hx
  exact hF.frame p x (by intro hm; have hb := hp hm; change base-1 ≤ x at hb; omega)

/-- Every actual prefix leaves every strict parked-ancestor cell unchanged. -/
theorem pop_prefix_ancestor_frame (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) {n : ℕ} {e : Config ι Symbol PopPhase}
    (hr : Runs (popProgram s t p) n (popInput s t p bits base past heads cells) e) :
    ∀ x, x < base-1 → e.cell p x = (popInput s t p bits base past heads cells).cell p x := by
  rcases pop_runs_footprint s t p hst hsp htp base hr
    (popInput_safe s t p hst hsp htp bits base past heads cells) with ⟨F,hF,hp,_,_⟩
  intro x hx
  exact hF.frame p x (by intro hm; have hb := hp hm; change base-1 ≤ x at hb; omega)

end MultitapeToolkit.Absolute.ParkFootprints
namespace MultitapeToolkit.Absolute.ParkFootprints
open MultitapeToolkit.Locality MarkedStreams ParkStack FrameRule
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- The whole old parking prefix, including its separator, is semantically
unchanged after every actual prefix. Marker rewrites are charged but harmless. -/
theorem pop_prefix_full_ancestor_frame (s t p : ι) (hst : s ≠ t) (hsp : s ≠ p) (htp : t ≠ p)
    (bits : List Bool) (base : ℤ) (past : ℤ → Symbol)
    (heads : ι → ℤ) (cells : ι → ℤ → Symbol) {n : ℕ} {e : Config ι Symbol PopPhase}
    (hr : Runs (popProgram s t p) n (popInput s t p bits base past heads cells) e) :
    ∀ x, x < base → e.cell p x = (popInput s t p bits base past heads cells).cell p x := by
  have hi := popInput_safe s t p hst hsp htp bits base past heads cells
  have he := pop_runs_safe s t p hst hsp htp base hr hi
  intro x hx
  by_cases hm : x=base-1
  · rw [hm,he.parkingMarker,hi.parkingMarker]
  · exact pop_prefix_ancestor_frame s t p hst hsp htp bits base past heads cells hr x (by omega)

def pushFloors (q : PushPhase) (source parking base : ℤ) : Prop :=
  base ≤ parking ∧ match q with
    | .copy => 0 ≤ source
    | .rewind | .done => -1 ≤ source

structure PushSafe (s p : ι) (base : ℤ) (c : Config ι Symbol PushPhase) : Prop where
  sourceMarker : c.cell s (-1) = .separator
  floors : pushFloors c.state (c.head s) (c.head p) base

omit [Fintype ι] [DecidableEq ι] in
theorem PushSafe.basic {s p : ι} {base : ℤ} {c : Config ι Symbol PushPhase}
    (h : PushSafe s p base c) : base ≤ c.head p ∧ -1 ≤ c.head s := by
  have hf := h.floors
  cases hq : c.state <;> simp only [hq,pushFloors] at hf <;> omega

def nextPushCfg (s p : ι) (c : Config ι Symbol PushPhase) (q : PushPhase)
    (a b : Symbol × Move) : Config ι Symbol PushPhase :=
  let actions := actions2 s p a b (fun i => c.cell i (c.head i))
  ⟨q,fun i => c.head i+moveOffset (actions i).2,
    fun i x => if x=c.head i then (actions i).1 else c.cell i x⟩

omit [Fintype ι] in
theorem next_push_safe (s p : ι) (hsp : s ≠ p) (base : ℤ)
    (c : Config ι Symbol PushPhase) (q : PushPhase) (a b : Symbol × Move)
    (hi : PushSafe s p base c) (ha : c.head s = -1 → a.1 = .separator)
    (hf : pushFloors q (c.head s+moveOffset a.2) (c.head p+moveOffset b.2) base) :
    PushSafe s p base (nextPushCfg s p c q a b) := by
  constructor
  · simpa [nextPushCfg,actions2] using marker_write (c.head s) (-1) (c.cell s) a.1 hi.sourceMarker ha
  · simpa [nextPushCfg,actions2,Ne.symm hsp] using hf

theorem push_step_safe_of_table (s p : ι) (base : ℤ)
    {c e : Config ι Symbol PushPhase} (q : PushPhase) (a b : Symbol × Move)
    (ht : (pushProgram s p).transition c.state (fun i => c.cell i (c.head i)) =
      some (q,actions2 s p a b (fun i => c.cell i (c.head i))))
    (hs : step (pushProgram s p) c = some e)
    (hi : PushSafe s p base (nextPushCfg s p c q a b)) : PushSafe s p base e := by
  have he : e = nextPushCfg s p c q a b := by simpa [step,ht,nextPushCfg] using hs.symm
  rw [he]
  exact hi

theorem push_step_safe (s p : ι) (hsp : s ≠ p) (base : ℤ)
    {c e : Config ι Symbol PushPhase} (hi : PushSafe s p base c)
    (hs : step (pushProgram s p) c = some e) : PushSafe s p base e := by
  have hm := hi.sourceMarker
  have hf := hi.floors
  cases hq : c.state with
  | done => simp [step,pushProgram,hq] at hs
  | copy =>
    simp only [hq,pushFloors] at hf
    cases hb : c.cell s (c.head s) with
    | blank =>
      apply push_step_safe_of_table s p base .rewind (.blank,.left) (.separator,.right)
        (by simp [pushProgram,hq,hb]) hs
      apply next_push_safe s p hsp base c .rewind _ _ hi
      · intro h; omega
      · simp only [pushFloors,moveOffset]; omega
    | separator =>
      apply push_step_safe_of_table s p base .done
        (c.cell s (c.head s),.stay) (c.cell p (c.head p),.stay)
        (by simp [pushProgram,hq,hb]) hs
      apply next_push_safe s p hsp base c .done _ _ hi
      · intro h; simpa [h] using hm
      · simp only [pushFloors,moveOffset]; omega
    | bit b =>
      apply push_step_safe_of_table s p base .copy (.blank,.right) (.bit b,.right)
        (by simp [pushProgram,hq,hb]) hs
      apply next_push_safe s p hsp base c .copy _ _ hi
      · intro h; omega
      · simp only [pushFloors,moveOffset]; omega
  | rewind =>
    simp only [hq,pushFloors] at hf
    cases hb : c.cell s (c.head s) with
    | blank =>
      have hh : -1 < c.head s := by
        have hn : c.head s ≠ -1 := by intro h; rw [h,hm] at hb; cases hb
        omega
      apply push_step_safe_of_table s p base .rewind (.blank,.left) (c.cell p (c.head p),.stay)
        (by simp [pushProgram,hq,hb]) hs
      apply next_push_safe s p hsp base c .rewind _ _ hi
      · intro h; omega
      · simp only [pushFloors,moveOffset]; omega
    | separator =>
      apply push_step_safe_of_table s p base .done (.separator,.right) (c.cell p (c.head p),.stay)
        (by simp [pushProgram,hq,hb]) hs
      apply next_push_safe s p hsp base c .done _ _ hi
      · intro _; rfl
      · simp only [pushFloors,moveOffset]; omega
    | bit b =>
      apply push_step_safe_of_table s p base .done
        (c.cell s (c.head s),.stay) (c.cell p (c.head p),.stay)
        (by simp [pushProgram,hq,hb]) hs
      apply next_push_safe s p hsp base c .done _ _ hi
      · intro h; simpa [h] using hm
      · simp only [pushFloors,moveOffset]; omega

end MultitapeToolkit.Absolute.ParkFootprints
namespace MultitapeToolkit.Absolute.ParkFootprints
open MultitapeToolkit.Locality MarkedStreams ParkStack FrameRule
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

@[simp] theorem word_marker (bits : List Bool) : word bits (-1) = .separator := by
  simp [word,markedStream,cellView]

omit [Fintype ι] in
theorem pushInput_safe (s p : ι) (hsp : s ≠ p) (bits : List Bool) (base : ℤ)
    (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    PushSafe s p base (pushInput s p bits base past heads cells) := by
  constructor
  · simp [pushInput,bank2]
  · simp [pushInput,bank2,pushFloors,reading,atEnd,Ne.symm hsp]

theorem push_runs_safe (s p : ι) (hsp : s ≠ p) (base : ℤ)
    {n : ℕ} {c e : Config ι Symbol PushPhase} (hr : Runs (pushProgram s p) n c e) :
    PushSafe s p base c → PushSafe s p base e := by
  induction hr with
  | refl c => exact fun h => h
  | cons hs hr ih => exact fun hi => ih (push_step_safe s p hsp base hi hs)

theorem push_prefix_read_floor (s p : ι) (hsp : s ≠ p) (bits : List Bool) (base : ℤ)
    (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol)
    {n : ℕ} {e : Config ι Symbol PushPhase}
    (hr : Runs (pushProgram s p) n (pushInput s p bits base past heads cells) e) :
    base ≤ e.head p ∧ -1 ≤ e.head s :=
  (push_runs_safe s p hsp base hr (pushInput_safe s p hsp bits base past heads cells)).basic

theorem push_runs_footprint (s p : ι) (hsp : s ≠ p) (base : ℤ)
    {n : ℕ} {c e : Config ι Symbol PushPhase} (hr : Runs (pushProgram s p) n c e) :
    PushSafe s p base c → ∃ F : ι → Finset ℤ,
      FootprintedRuns (pushProgram s p) n c e F ∧
      (F p : Set ℤ) ⊆ Set.Ici base ∧ (F s : Set ℤ) ⊆ Set.Ici (-1) := by
  induction hr with
  | refl c =>
    intro _
    exact ⟨fun _ => ∅,.refl c,by simp,by simp⟩
  | @cons n c d e hs hr ih =>
    intro hi
    rcases ih (push_step_safe s p hsp base hi hs) with ⟨F,hF,hp,hsrc⟩
    refine ⟨fun i => insert (c.head i) (F i),.cons hs hF,?_,?_⟩
    · intro x hx
      rcases Finset.mem_insert.mp hx with he | hx
      · subst x; exact hi.basic.1
      · exact hp hx
    · intro x hx
      rcases Finset.mem_insert.mp hx with he | hx
      · subst x; exact hi.basic.2
      · exact hsrc hx

/-- Every actual push prefix protects the entire old parked prefix. -/
theorem push_prefix_ancestor_frame (s p : ι) (hsp : s ≠ p) (bits : List Bool) (base : ℤ)
    (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol)
    {n : ℕ} {e : Config ι Symbol PushPhase}
    (hr : Runs (pushProgram s p) n (pushInput s p bits base past heads cells) e) :
    ∀ x, x < base → e.cell p x = (pushInput s p bits base past heads cells).cell p x := by
  rcases push_runs_footprint s p hsp base hr
    (pushInput_safe s p hsp bits base past heads cells) with ⟨F,hF,hp,_⟩
  intro x hx
  exact hF.frame p x (by intro hm; have hb := hp hm; change base ≤ x at hb; omega)

theorem push_completed_footprint (s p : ι) (hsp : s ≠ p) (bits : List Bool) (base : ℤ)
    (past : ℤ → Symbol) (heads : ι → ℤ) (cells : ι → ℤ → Symbol) :
    ∃ F : ι → Finset ℤ,
      FootprintedRuns (pushProgram s p) (2*bits.length+2)
        (pushInput s p bits base past heads cells) (pushFinal s p bits base past heads cells) F ∧
      Halts (pushProgram s p) (pushFinal s p bits base past heads cells) ∧
      (F p : Set ℤ) ⊆ Set.Ici base ∧ (F s : Set ℤ) ⊆ Set.Ici (-1) ∧
      ∀ x, x < base → (pushFinal s p bits base past heads cells).cell p x =
        (pushInput s p bits base past heads cells).cell p x := by
  rcases push_runs_footprint s p hsp base (push_correct s p hsp bits base past heads cells)
    (pushInput_safe s p hsp bits base past heads cells) with ⟨F,hF,hp,hs⟩
  refine ⟨F,hF,pushFinal_halts s p bits base past heads cells,hp,hs,?_⟩
  intro x hx
  exact hF.frame p x (by intro hm; have hb := hp hm; change base ≤ x at hb; omega)

end MultitapeToolkit.Absolute.ParkFootprints


