/-
Y-relay, lane LEAN-NEXT11, Nov 16. See YRelay.md.
Sources: cards/WILD/BIG/JUNKLB3/THEORY.md (L2 Y-RELAY), cards/WILD/BIG/YRELAY/RESULT.md (necessary condition).

Op model: TokenCancel's (`Ev`, `St`, `step`, `run`); rows in initial-row coordinates.
(1) `relay`: Y_q reads −c·Y_p at chart 0 and +c·Y_p at a later chart. If the window between is QUIET for
    q (nobody reads q; q is written only by ADDs), the end state is the relay-free state with
    c·(row_p(t2) − row_p(t1)) added to q and nothing else changed.
(2) `win_delta`: if in the window p is written only by ADDs and every row it reads lies in N, then
    row_p(t2) − row_p(t1) ∈ N. With N = token-free rows (`tokFree {p, x}`) this is "no net token":
    the precise form of "no crossing arrival in between" is the hypothesis `Win p (tokFree T)`.
(3) Findings (prose too strong): a SCALE of Y_p in the window, or a read of Y_q in the window, leaks
    the token e_p (`scale_leak`, `read_leak`).
(4) `cone_inv`: YRELAY's necessary condition. The reach cone of a Y main, built forward in time from
    its own birth, the non-Y rows it reads, and the cones of Y mains it reads at a meeting chart,
    contains its row modulo G, provided Y-Y reads at non-meeting charts carry only G-content.

Build (imports the TokenCancel olean):
  lake env lean -o .lake/build/lib/lean/Nov15/TokenCancel.olean Nov15/TokenCancel.lean
  lake env lean Nov15/YRelay.lean
-/
import Nov15.TokenCancel

set_option linter.unusedSectionVars false

namespace YRelay
open TokenCancel Submodule

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

theorem run_append (s : St K Reg C) (p q : List (Ev K Reg C)) :
    run s (p ++ q) = run (run s p) q := by
  induction p generalizing s with
  | nil => rfl
  | cons e p ih => exact ih (step s e)

/-! ## (1) The relay pair -/

/-- `q` is quiet in event `e`: nobody reads `q`, and `q` is written only by ADDs. -/
def Quiet (q : Reg) : Ev K Reg C → Prop
  | .born i _ => i ≠ q
  | .init i _ => i ≠ q
  | .move _ _ => True
  | .add _ j _ _ => j ≠ q
  | .scale i _ _ => i ≠ q
  | .clear i _ => i ≠ q
  | .copy i j _ => i ≠ q ∧ j ≠ q

/-- One quiet step keeps a difference `d` sitting on row `q` only. -/
theorem quiet_step (q : Reg) (d : Reg → K) (s : St K Reg C) (e : Ev K Reg C) (hq : Quiet q e) :
    step ⟨Function.update s.row q (s.row q + d), s.loc⟩ e =
      ⟨Function.update (step s e).row q ((step s e).row q + d), (step s e).loc⟩ := by
  cases e with
  | born i c =>
    have hi : i ≠ q := hq
    simp only [step, St.mk.injEq, and_true]
    funext r; by_cases hr : r = q
    · subst hr; simp [Function.update_of_ne hi.symm]
    · by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hr]
      · simp [Function.update_of_ne hr, Function.update_of_ne hri]
  | init i c =>
    have hi : i ≠ q := hq
    simp only [step, St.mk.injEq, and_true]
    funext r; by_cases hr : r = q
    · subst hr; simp [Function.update_of_ne hi.symm]
    · by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hr]
      · simp [Function.update_of_ne hr, Function.update_of_ne hri]
  | move i c => rfl
  | add i j a c =>
    have hj : j ≠ q := hq
    simp only [step, St.mk.injEq, and_true]
    funext r
    by_cases hr : r = q
    · subst hr
      by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hj]; abel
      · simp [Function.update_of_ne hri, Function.update_of_ne (Ne.symm hri)]
    · by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hr, Function.update_of_ne hj]
      · simp [Function.update_of_ne hr, Function.update_of_ne hri]
  | scale i u c =>
    have hi : i ≠ q := hq
    simp only [step, St.mk.injEq, and_true]
    funext r; by_cases hr : r = q
    · subst hr; simp [Function.update_of_ne hi.symm]
    · by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hr]
      · simp [Function.update_of_ne hr, Function.update_of_ne hri]
  | clear i c =>
    have hi : i ≠ q := hq
    simp only [step, St.mk.injEq, and_true]
    funext r; by_cases hr : r = q
    · subst hr; simp [Function.update_of_ne hi.symm]
    · by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hr]
      · simp [Function.update_of_ne hr, Function.update_of_ne hri]
  | copy i j c =>
    obtain ⟨hi, hj⟩ : i ≠ q ∧ j ≠ q := hq
    simp only [step, St.mk.injEq, and_true]
    funext r; by_cases hr : r = q
    · subst hr; simp [Function.update_of_ne hi.symm]
    · by_cases hri : r = i
      · subst hri; simp [Function.update_of_ne hr, Function.update_of_ne hj]
      · simp [Function.update_of_ne hr, Function.update_of_ne hri]

theorem quiet_run (q : Reg) (d : Reg → K) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), (∀ e ∈ evs, Quiet q e) →
      run ⟨Function.update s.row q (s.row q + d), s.loc⟩ evs =
        ⟨Function.update (run s evs).row q ((run s evs).row q + d), (run s evs).loc⟩
  | [], s, _ => rfl
  | e :: es, s, h => by
    simp only [run]
    rw [quiet_step q d s e (h e List.mem_cons_self)]
    exact quiet_run q d es (step s e) (fun e' he' => h e' (List.mem_cons_of_mem _ he'))

/-- **L2 (relay pair).** `q` reads `−c·p` at chart `c0`, the window `mid` runs, then `q` reads `+c·p`
at chart `cF`. If `mid` is quiet for `q`, the result is the relay-free run with
`c·(row_p after mid − row_p before mid)` added to row `q`; every other row and every location is
unchanged. -/
theorem relay (s : St K Reg C) (p q : Reg) (hpq : p ≠ q) (c : K) (c0 cF : C)
    (mid : List (Ev K Reg C)) (hQ : ∀ e ∈ mid, Quiet q e) :
    run s (.add q p (-c) c0 :: mid ++ [.add q p c cF]) =
      ⟨Function.update (run s mid).row q
          ((run s mid).row q + c • ((run s mid).row p - s.row p)), (run s mid).loc⟩ := by
  rw [List.cons_append, run, run_append]
  have h1 : step s (.add q p (-c) c0) =
      ⟨Function.update s.row q (s.row q + (-c) • s.row p), s.loc⟩ := rfl
  rw [h1, quiet_run q _ mid s hQ]
  simp only [run, step, St.mk.injEq, and_true]
  funext r; by_cases hr : r = q
  · subst hr; simp [Function.update_of_ne hpq, smul_sub]; abel
  · simp [Function.update_of_ne hr]

/-! ## (2) What the window delivers -/

/-- Window condition for `p`: `p` is written only by ADDs, and every row an ADD into `p` reads lies in `N`. -/
def WinEv (p : Reg) (N : Submodule K (Reg → K)) (s : St K Reg C) : Ev K Reg C → Prop
  | .add i j _ _ => i = p → s.row j ∈ N
  | .born i _ | .init i _ | .scale i _ _ | .clear i _ | .copy i _ _ => i ≠ p
  | .move _ _ => True

def Win (p : Reg) (N : Submodule K (Reg → K)) : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => WinEv p N s e ∧ Win p N (step s e) es

theorem win_step (p : Reg) (N : Submodule K (Reg → K)) (s : St K Reg C) (e : Ev K Reg C)
    (h : WinEv p N s e) : (step s e).row p - s.row p ∈ N := by
  cases e with
  | add i j a c =>
    by_cases hi : i = p
    · subst hi; simpa [step] using N.smul_mem a (h rfl)
    · simp [step, Function.update_of_ne (Ne.symm hi)]
  | born i c => have : i ≠ p := h; simp [step, Function.update_of_ne this.symm]
  | init i c => have : i ≠ p := h; simp [step, Function.update_of_ne this.symm]
  | scale i u c => have : i ≠ p := h; simp [step, Function.update_of_ne this.symm]
  | clear i c => have : i ≠ p := h; simp [step, Function.update_of_ne this.symm]
  | copy i j c => have : i ≠ p := h; simp [step, Function.update_of_ne this.symm]
  | move i c => simp [step]

/-- **What Y_p read in between.** Under `Win p N`, row_p(t2) − row_p(t1) ∈ N. -/
theorem win_delta (p : Reg) (N : Submodule K (Reg → K)) :
    ∀ (evs : List (Ev K Reg C)) (s : St K Reg C), Win p N s evs → (run s evs).row p - s.row p ∈ N
  | [], s, _ => by simp [run]
  | e :: es, s, ⟨h1, h2⟩ => by
    have := N.add_mem (win_delta p N es (step s e) h2) (win_step p N s e h1)
    simpa [run] using this

/-- Rows with zero coefficient on every token column in `T`. -/
def tokFree (T : Set Reg) : Submodule K (Reg → K) where
  carrier := {v | ∀ k ∈ T, v k = 0}
  add_mem' ha hb k hk := by simp [ha k hk, hb k hk]
  zero_mem' k _ := rfl
  smul_mem' a v hv k hk := by simp [hv k hk]

/-- **L2, token form.** With `T = {p's own token, p's crossing token}`: if every row Y_p reads in the
window is token-free on `T` (no crossing arrival, no own-token read) and Y_p is written only by
ADDs, Y_q's end row differs from the relay-free one by a vector that is token-free on `T`, and the
difference is `c·(sum of what Y_p read)`. -/
theorem relay_no_token (s : St K Reg C) (p q : Reg) (hpq : p ≠ q) (c : K) (c0 cF : C)
    (mid : List (Ev K Reg C)) (hQ : ∀ e ∈ mid, Quiet q e) (N : Submodule K (Reg → K))
    (hW : Win p N s mid) :
    (run s (.add q p (-c) c0 :: mid ++ [.add q p c cF])).row q - (run s mid).row q ∈ N ∧
      ∀ r, r ≠ q → (run s (.add q p (-c) c0 :: mid ++ [.add q p c cF])).row r = (run s mid).row r := by
  rw [relay s p q hpq c c0 cF mid hQ]
  refine ⟨?_, fun r hr => by simp [Function.update_of_ne hr]⟩
  simpa using N.smul_mem c (win_delta p N mid s hW)

/-! ## (3) Findings: the hypotheses are needed -/

/-- Two registers: p = 0 (row e_0), q = 1 (row 0). -/
def s2 : St ℚ (Fin 2) Unit := ⟨fun r => if r = 0 then Pi.single 0 1 else 0, fun _ => some ()⟩

/-- **Finding (SCALE of Y_p).** The window holds no read into Y_p, only `p *= 2`; relay with c = 1
leaves e_p-coefficient 1 in Y_q: the token leaks. So "Y_p' receives exactly c·(what Y_p read)" needs
Y_p written only by ADDs in the window. -/
theorem scale_leak :
    (run s2 (.add 1 0 (-1) () :: [Ev.scale (0 : Fin 2) 2 ()] ++ [.add 1 0 1 ()])).row 1 0 = 1 := by
  simp [run, step, s2]
  norm_num

/-- Three registers: p = 0 (row e_0), q = 1, a third register 2 (rows 0). -/
def s3 : St ℚ (Fin 3) Unit := ⟨fun r => if r = 0 then Pi.single 0 1 else 0, fun _ => some ()⟩

/-- **Finding (read of Y_q in the window).** Register 2 reads Y_q in the window and keeps −e_p:
the premixed −c·Y_p leaks to third parties. So the window must be quiet for Y_q. -/
theorem read_leak :
    (run s3 (.add 1 0 (-1) () :: [Ev.add (2 : Fin 3) 1 1 ()] ++ [.add 1 0 1 ()])).row 2 0 = -1 := by
  simp [run, step, s3]

/-! ## (4) YRELAY: the reach cone -/

section Cone
variable (Ys : Set Reg) [DecidablePred (· ∈ Ys)] (Meet : C → Prop) [DecidablePred Meet]
  (G : Submodule K (Reg → K))

/-- Forward update of the reach cones. A Y main's cone gains the non-Y rows it reads (at their read
time) and, at a meeting chart, the cone of the Y main it reads. Y-Y reads off meeting charts add
nothing (their content must lie in `G`, hypothesis `HubG`). -/
def coneStep (s : St K Reg C) (M : Reg → Submodule K (Reg → K)) :
    Ev K Reg C → Reg → Submodule K (Reg → K)
  | .born i _ => Function.update M i (K ∙ Pi.single i 1)
  | .init i _ => Function.update M i ⊥
  | .add i j _ c =>
    if i ∈ Ys then
      (if j ∈ Ys then (if Meet c then Function.update M i (M i ⊔ M j) else M)
       else Function.update M i (M i ⊔ K ∙ s.row j))
    else M
  | .copy i j c =>
    if i ∈ Ys then
      (if j ∈ Ys then (if Meet c then Function.update M i (M j) else M)
       else Function.update M i (K ∙ s.row j))
    else M
  | _ => M

/-- Off-meeting Y-Y reads carry only `G`-content (YRELAY: the {0} hub fixes G0 tokens only). -/
def HubG (s : St K Reg C) : Ev K Reg C → Prop
  | .add i j _ c | .copy i j c => i ∈ Ys → j ∈ Ys → ¬ Meet c → s.row j ∈ G
  | _ => True

def coneRun (s : St K Reg C) (M : Reg → Submodule K (Reg → K)) :
    List (Ev K Reg C) → St K Reg C × (Reg → Submodule K (Reg → K))
  | [] => (s, M)
  | e :: es => coneRun (step s e) (coneStep Ys Meet s M e) es

def HubGRun : St K Reg C → List (Ev K Reg C) → Prop
  | _, [] => True
  | s, e :: es => HubG Ys Meet G s e ∧ HubGRun (step s e) es

theorem coneRun_fst (s : St K Reg C) (M : Reg → Submodule K (Reg → K)) :
    ∀ evs, (coneRun Ys Meet s M evs).1 = run s evs
  | [] => rfl
  | e :: es => coneRun_fst (step s e) _ es

def ConeInv (s : St K Reg C) (M : Reg → Submodule K (Reg → K)) : Prop :=
  ∀ i ∈ Ys, s.row i ∈ M i ⊔ G

theorem cone_step (s : St K Reg C) (M : Reg → Submodule K (Reg → K)) (e : Ev K Reg C)
    (hI : ConeInv Ys G s M) (hH : HubG Ys Meet G s e) :
    ConeInv Ys G (step s e) (coneStep Ys Meet s M e) := by
  intro r hr
  have keep : ∀ (M' : Reg → Submodule K (Reg → K)), M' r = M r → s.row r ∈ M' r ⊔ G :=
    fun M' h => h ▸ hI r hr
  cases e with
  | born i c =>
    by_cases hri : r = i
    · subst hri; simp only [step, coneStep, Function.update_self]
      exact mem_sup_left (mem_span_singleton_self _)
    · simp only [step, coneStep, Function.update_of_ne hri]; exact hI r hr
  | init i c =>
    by_cases hri : r = i
    · subst hri; simp [step, coneStep]
    · simp only [step, coneStep, Function.update_of_ne hri]; exact hI r hr
  | move i c => exact hI r hr
  | scale i u c =>
    by_cases hri : r = i
    · subst hri; simpa [step, coneStep] using (M r ⊔ G).smul_mem u (hI r hr)
    · simp only [step, coneStep, Function.update_of_ne hri]; exact hI r hr
  | clear i c =>
    by_cases hri : r = i
    · subst hri; simp [step, coneStep]
    · simp only [step, coneStep, Function.update_of_ne hri]; exact hI r hr
  | add i j a c =>
    by_cases hri : r = i
    · subst hri
      simp only [step, Function.update_self, coneStep, if_pos hr]
      have hr0 := hI r hr
      by_cases hj : j ∈ Ys
      · rw [if_pos hj]
        by_cases hm : Meet c
        · rw [if_pos hm, Function.update_self]
          have hj0 := hI j hj
          refine add_mem ((sup_le_sup_right le_sup_left G) hr0) (smul_mem _ a ?_)
          by_cases hjr : j = r
          · subst hjr; exact (sup_le_sup_right le_sup_left G) hr0
          · exact (sup_le_sup_right le_sup_right G) hj0
        · rw [if_neg hm]
          exact add_mem hr0 (smul_mem _ a (mem_sup_right (hH hr hj hm)))
      · rw [if_neg hj, Function.update_self]
        exact add_mem ((sup_le_sup_right le_sup_left G) hr0)
          (smul_mem _ a (mem_sup_left (mem_sup_right (mem_span_singleton_self _))))
    · simp only [step, Function.update_of_ne hri]
      simp only [coneStep]
      split_ifs <;> first | exact hI r hr | (rw [Function.update_of_ne hri]; exact hI r hr)
  | copy i j c =>
    by_cases hri : r = i
    · subst hri
      simp only [step, Function.update_self, coneStep, if_pos hr]
      by_cases hj : j ∈ Ys
      · rw [if_pos hj]
        by_cases hm : Meet c
        · rw [if_pos hm, Function.update_self]; exact hI j hj
        · rw [if_neg hm]; exact mem_sup_right (hH hr hj hm)
      · rw [if_neg hj, Function.update_self]
        exact mem_sup_left (mem_span_singleton_self _)
    · simp only [step, Function.update_of_ne hri]
      simp only [coneStep]
      split_ifs <;> first | exact hI r hr | (rw [Function.update_of_ne hri]; exact hI r hr)

/-- **YRELAY necessary condition.** Along any run satisfying `HubG`, every Y main's row lies in its
reach cone plus `G`. The cone is built forward in time, so content reaches Y_a only from non-Y
rows read (at that time) by some Y_b joined to Y_a by a time-ordered chain of Y-Y reads at meeting
charts. A relay therefore copies only content some Y main already holds. -/
theorem cone_inv : ∀ (evs : List (Ev K Reg C)) (s : St K Reg C) (M : Reg → Submodule K (Reg → K)),
    ConeInv Ys G s M → HubGRun Ys Meet G s evs →
      ConeInv Ys G (coneRun Ys Meet s M evs).1 (coneRun Ys Meet s M evs).2
  | [], _, _, hI, _ => hI
  | e :: es, s, M, hI, ⟨h1, h2⟩ =>
    cone_inv es (step s e) (coneStep Ys Meet s M e) (cone_step Ys Meet G s M e hI h1) h2

/-- Contrapositive form used by YRELAY's reach test: a target content outside the final cone (+ G)
cannot be the final row of that Y main. -/
theorem not_reach (evs : List (Ev K Reg C)) (s : St K Reg C) (M : Reg → Submodule K (Reg → K))
    (hI : ConeInv Ys G s M) (hH : HubGRun Ys Meet G s evs) (a : Reg) (ha : a ∈ Ys)
    (v : Reg → K) (hv : v ∉ (coneRun Ys Meet s M evs).2 a ⊔ G) : (run s evs).row a ≠ v := by
  rw [← coneRun_fst Ys Meet s M evs]
  exact fun h => hv (h ▸ cone_inv Ys Meet G evs s M hI hH a ha)

end Cone

end YRelay

#print axioms YRelay.relay
#print axioms YRelay.relay_no_token
#print axioms YRelay.win_delta
#print axioms YRelay.scale_leak
#print axioms YRelay.read_leak
#print axioms YRelay.cone_inv
#print axioms YRelay.not_reach
