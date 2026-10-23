import BitXorTargetTranslation

/-! Boolean scalar projection of a retained-centre COPY/ADD/ERASE window.
COPY overwrites the temporary and ERASE writes false. No physical allocation,
frame transport, or restoration of an arbitrary incoming temporary is asserted.
The overwrite/clear statement shapes parallel the accepted F19 scalar adapter;
its rational Module instance is not imported or treated as Boolean semantics. -/
namespace CurrentMain.BitCopyScatter
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]
abbrev State (Reg : Type) := Reg → Bool

def copy (temp centre : Reg) (s : State Reg) : State Reg :=
  fun r => if r = temp then s centre else s r

def clear (temp : Reg) (s : State Reg) : State Reg :=
  fun r => if r = temp then false else s r

/-- Ordered destination loop, using the accepted scalar XOR ADD. -/
def adds (src : Reg) : List Reg → State Reg → State Reg
  | [], s => s
  | d :: ds, s => adds src ds (BitXor.single d src s)

def window (temp centre : Reg) (ds : List Reg) (s : State Reg) : State Reg :=
  clear temp (adds temp ds (copy temp centre s))

structure Window (Reg : Type) where
  centre : Reg
  targets : List Reg

def WellFormed (temp : Reg) (w : Window Reg) : Prop :=
  w.centre ≠ temp ∧ ∀ d ∈ w.targets, d ≠ temp ∧ d ≠ w.centre

def runWindows (temp : Reg) : List (Window Reg) → State Reg → State Reg
  | [], s => s
  | w :: ws, s => runWindows temp ws (window temp w.centre w.targets s)

def directWindows : List (Window Reg) → State Reg → State Reg
  | [], s => s
  | w :: ws, s => directWindows ws (adds w.centre w.targets s)

theorem copy_at_temp (temp centre : Reg) (s : State Reg) :
    copy temp centre s temp = s centre := by simp [copy]

theorem clear_at_temp (temp : Reg) (s : State Reg) :
    clear temp s temp = false := by simp [clear]

private theorem single_copy (temp centre dst : Reg)
    (hdt : dst ≠ temp) (hdc : dst ≠ centre) (s : State Reg) :
    BitXor.single dst temp (copy temp centre s) =
      copy temp centre (BitXor.single dst centre s) := by
  funext r
  by_cases hr : r = temp
  · subst r
    simp [copy, BitXor.single, Ne.symm hdt, Ne.symm hdc]
  · simp [copy, BitXor.single, hr]

private theorem adds_copy (temp centre : Reg) (ds : List Reg) :
    (∀ d ∈ ds, d ≠ temp ∧ d ≠ centre) → ∀ s,
    adds temp ds (copy temp centre s) = copy temp centre (adds centre ds s) := by
  induction ds with
  | nil => intro h s; rfl
  | cons d ds ih =>
    intro h s
    change adds temp ds (BitXor.single d temp (copy temp centre s)) =
      copy temp centre (adds centre ds (BitXor.single d centre s))
    rw [single_copy temp centre d (h d List.mem_cons_self).1
      (h d List.mem_cons_self).2 s]
    exact ih (fun r hr => h r (List.mem_cons_of_mem d hr)) (BitXor.single d centre s)

private theorem clear_copy (temp centre : Reg) (s : State Reg) :
    clear temp (copy temp centre s) = clear temp s := by
  funext r
  by_cases hr : r = temp <;> simp [clear, copy, hr]

private theorem clear_clear (temp : Reg) (s : State Reg) :
    clear temp (clear temp s) = clear temp s := by
  funext r
  by_cases hr : r = temp <;> simp [clear, hr]

theorem window_eq_clear_direct (temp centre : Reg) (ds : List Reg)
    (h : ∀ d ∈ ds, d ≠ temp ∧ d ≠ centre) (s : State Reg) :
    window temp centre ds s = clear temp (adds centre ds s) := by
  unfold window
  rw [adds_copy temp centre ds h s, clear_copy]

private theorem single_clear (temp src dst : Reg)
    (hst : src ≠ temp) (hdt : dst ≠ temp) (s : State Reg) :
    BitXor.single dst src (clear temp s) = clear temp (BitXor.single dst src s) := by
  funext r
  by_cases hr : r = temp
  · subst r
    simp [clear, BitXor.single, Ne.symm hdt]
  · simp [clear, BitXor.single, hr, hst]

private theorem adds_clear (temp src : Reg) (ds : List Reg) (hst : src ≠ temp) :
    (∀ d ∈ ds, d ≠ temp) → ∀ s,
    adds src ds (clear temp s) = clear temp (adds src ds s) := by
  induction ds with
  | nil => intro h s; rfl
  | cons d ds ih =>
    intro h s
    change adds src ds (BitXor.single d src (clear temp s)) =
      clear temp (adds src ds (BitXor.single d src s))
    rw [single_clear temp src d hst (h d List.mem_cons_self) s]
    exact ih (fun r hr => h r (List.mem_cons_of_mem d hr)) (BitXor.single d src s)

private theorem copy_clear_input (temp centre : Reg) (hct : centre ≠ temp)
    (s : State Reg) : copy temp centre (clear temp s) = copy temp centre s := by
  funext r
  by_cases hr : r = temp <;> simp [copy, clear, hr, hct]

private theorem runWindows_clear (temp : Reg) (ws : List (Window Reg)) :
    (∀ w ∈ ws, WellFormed temp w) → ∀ s,
    runWindows temp ws (clear temp s) = clear temp (directWindows ws s) := by
  induction ws with
  | nil => intro h s; rfl
  | cons w ws ih =>
    intro h s
    have hw := h w List.mem_cons_self
    change runWindows temp ws (window temp w.centre w.targets (clear temp s)) =
      clear temp (directWindows ws (adds w.centre w.targets s))
    rw [window_eq_clear_direct temp w.centre w.targets hw.2,
      adds_clear temp w.centre w.targets hw.1 (fun d hd => (hw.2 d hd).1),
      clear_clear]
    exact ih (fun q hq => h q (List.mem_cons_of_mem w hq)) (adds w.centre w.targets s)

/-- Nonempty copy windows dispose of the incoming temporary and end it at zero.
All other coordinates agree with the direct retained-centre XOR word. -/
theorem runWindows_eq_clear_direct (temp : Reg) (ws : List (Window Reg))
    (hne : ws ≠ []) (h : ∀ w ∈ ws, WellFormed temp w) (s : State Reg) :
    runWindows temp ws s = clear temp (directWindows ws s) := by
  cases ws with
  | nil => exact False.elim (hne rfl)
  | cons w ws =>
    have hw := h w List.mem_cons_self
    calc
      runWindows temp (w :: ws) s = runWindows temp (w :: ws) (clear temp s) := by
        change runWindows temp ws (window temp w.centre w.targets s) =
          runWindows temp ws (window temp w.centre w.targets (clear temp s))
        simp only [window, copy_clear_input temp w.centre hw.1 s]
      _ = clear temp (directWindows (w :: ws) s) := runWindows_clear temp (w :: ws) h s

private theorem adds_untouched (src : Reg) (ds : List Reg) :
    ∀ s r, r ∉ ds → adds src ds s r = s r := by
  induction ds with
  | nil => intro s r h; rfl
  | cons d ds ih =>
    intro s r h
    have hrd : r ≠ d := fun he => h (by simp [he])
    have hrs : r ∉ ds := fun hr => h (List.mem_cons_of_mem d hr)
    change adds src ds (BitXor.single d src s) r = s r
    rw [ih (BitXor.single d src s) r hrs]
    simp [BitXor.single, hrd]

theorem directWindows_untouched (ws : List (Window Reg)) :
    ∀ s r, (∀ w ∈ ws, r ∉ w.targets) → directWindows ws s r = s r := by
  induction ws with
  | nil => intro s r h; rfl
  | cons w ws ih =>
    intro s r h
    change directWindows ws (adds w.centre w.targets s) r = s r
    rw [ih (adds w.centre w.targets s) r (fun q hq => h q (List.mem_cons_of_mem w hq))]
    exact adds_untouched w.centre w.targets s r (h w List.mem_cons_self)

/-- Equality away from the disposable slot suffices, even if the two incoming
slots differ. This is loss of the temporary's old value, not its restoration. -/
theorem runWindows_independent_of_temp (temp : Reg) (ws : List (Window Reg))
    (hne : ws ≠ []) (h : ∀ w ∈ ws, WellFormed temp w)
    (s t : State Reg) (hst : ∀ r, r ≠ temp → s r = t r) :
    runWindows temp ws s = runWindows temp ws t := by
  cases ws with
  | nil => exact False.elim (hne rfl)
  | cons w ws =>
    have hct := (h w List.mem_cons_self).1
    have hc : copy temp w.centre s = copy temp w.centre t := by
      funext r
      by_cases hr : r = temp
      · simp [copy, hr, hst w.centre hct]
      · simp [copy, hr, hst r hr]
    change runWindows temp ws (window temp w.centre w.targets s) =
      runWindows temp ws (window temp w.centre w.targets t)
    simp only [window, hc]

end CurrentMain.BitCopyScatter
#print axioms CurrentMain.BitCopyScatter.copy_at_temp
#print axioms CurrentMain.BitCopyScatter.clear_at_temp
#print axioms CurrentMain.BitCopyScatter.window_eq_clear_direct
#print axioms CurrentMain.BitCopyScatter.runWindows_eq_clear_direct
#print axioms CurrentMain.BitCopyScatter.directWindows_untouched
#print axioms CurrentMain.BitCopyScatter.runWindows_independent_of_temp
