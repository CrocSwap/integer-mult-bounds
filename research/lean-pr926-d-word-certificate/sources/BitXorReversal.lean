import BitXorTargetTranslation

/-!
Structural inverse and cleanup laws for the accepted ordered multi-source Boolean
XOR interpreter. Every initial register may be dirty. No finite word, frame
transport, temporary lifecycle, multiplier theorem or kappa value is established
by this generic source. Source-specific instantiations require their own exact
literal binding, register-domain and no-self-read/no-target-read certificates.
Prepared with OpenAI assistance; reuses the accepted BitXor adapter and Lean core.
-/
namespace CurrentMain.BitXorReversal
open BitXor
set_option Elab.async false
variable {Reg : Type} [DecidableEq Reg]

/-- Frame metadata is retained by the raw adapter but has no Boolean scalar effect. -/
def scalarize (g : Gate Reg) : Gate Reg :=
  { frame := 0, dst := g.dst, sources := g.sources }

theorem run_append (xs ys : List (Gate Reg)) (s : State Reg) :
    run (xs ++ ys) s = run ys (run xs s) := by
  induction xs generalizing s with
  | nil => rfl
  | cons g xs ih =>
    exact ih (step g s)

theorem run_scalarize (gs : List (Gate Reg)) (s : State Reg) :
    run (gs.map scalarize) s = run gs s := by
  induction gs generalizing s with
  | nil => rfl
  | cons g gs ih =>
    exact ih (step g s)

/-- A gate may repeat operands. Only reading its own destination is excluded. -/
theorem step_involutive (g : Gate Reg) (h : g.dst ∉ g.sources) (s : State Reg) :
    step g (step g s) = s := by
  have hreads : ∀ q ∈ [g], ∀ r ∈ q.sources, ¬ (r = g.dst) := by
    intro q hq r hr he
    have hq' : q = g := List.mem_singleton.mp hq
    subst q
    exact h (he ▸ hr)
  have herase : eraseTargets (fun r => r = g.dst) (step g s) =
      eraseTargets (fun r => r = g.dst) s :=
    erased_eq_of_agree_off_target (fun r => r = g.dst) (step g s) s
      (fun r hr => sourcesRun_untouched g.dst g.sources s r hr)
  have hfirst : step g s g.dst =
      (s g.dst ^^ step g (eraseTargets (fun r => r = g.dst) s) g.dst) := by
    simpa only [run] using
      (target_identity (fun r => r = g.dst) [g] hreads s g.dst rfl)
  have hsecond : step g (step g s) g.dst =
      (step g s g.dst ^^
        step g (eraseTargets (fun r => r = g.dst) (step g s)) g.dst) := by
    simpa only [run] using
      (target_identity (fun r => r = g.dst) [g] hreads (step g s) g.dst rfl)
  rw [herase, hfirst] at hsecond
  funext r
  by_cases hr : r = g.dst
  · subst r
    simpa only [Bool.xor_assoc, Bool.xor_self, Bool.xor_false] using hsecond
  · change sourcesRun g.dst g.sources (step g s) r = s r
    rw [sourcesRun_untouched g.dst g.sources (step g s) r hr]
    exact sourcesRun_untouched g.dst g.sources s r hr

/-- Reverse the gate list, without reversing or deduplicating any operand list. -/
theorem run_reverse_cancel (gs : List (Gate Reg))
    (h : ∀ g ∈ gs, g.dst ∉ g.sources) (s : State Reg) :
    run gs.reverse (run gs s) = s := by
  induction gs generalizing s with
  | nil => rfl
  | cons g gs ih =>
    have hg := h g List.mem_cons_self
    have ht : ∀ q ∈ gs, q.dst ∉ q.sources :=
      fun q hq => h q (List.mem_cons_of_mem g hq)
    change run (g :: gs).reverse (run gs (step g s)) = s
    rw [List.reverse_cons, run_append]
    change step g (run gs.reverse (run gs (step g s))) = s
    rw [ih ht (step g s)]
    exact step_involutive g hg s

variable (target : Reg → Prop) [DecidablePred target]

private theorem shifted_comparison (s t : State Reg)
    (h : ∀ r, ¬ target r → s r = t r) :
    shift target s (fun r => s r ^^ t r) = t := by
  funext r
  by_cases hr : target r
  · simp only [shift, if_pos hr]
    exact Bool.bne_self_left (s r) (t r)
  · simp only [shift, if_neg hr]
    exact h r hr

/-- Agreement outside a never-read target set persists outside that set. -/
theorem run_agree_off_target (gs : List (Gate Reg))
    (hreads : ∀ g ∈ gs, ∀ r ∈ g.sources, ¬ target r)
    (s t : State Reg) (h : ∀ r, ¬ target r → s r = t r)
    (r : Reg) (hr : ¬ target r) : run gs s r = run gs t r := by
  have heq := run_shift target gs hreads s (fun q => s q ^^ t q)
  rw [shifted_comparison target s t h] at heq
  have heqr := congrFun heq r
  simpa only [shift, if_neg hr] using heqr.symm

/-- An arbitrary intervening map may change targets, while cleanup restores every
other coordinate. No cleanliness, linearity or zero contribution is assumed. -/
theorem cleanup_off_target (gs : List (Gate Reg))
    (hself : ∀ g ∈ gs, g.dst ∉ g.sources)
    (hreads : ∀ g ∈ gs, ∀ r ∈ g.sources, ¬ target r)
    (middle : State Reg → State Reg)
    (hmiddle : ∀ s r, ¬ target r → middle s r = s r)
    (s : State Reg) (r : Reg) (hr : ¬ target r) :
    run gs.reverse (middle (run gs s)) r = s r := by
  have hreverse : ∀ g ∈ gs.reverse, ∀ q ∈ g.sources, ¬ target q := by
    intro g hg
    exact hreads g (List.mem_reverse.mp hg)
  calc
    run gs.reverse (middle (run gs s)) r = run gs.reverse (run gs s) r :=
      run_agree_off_target target gs.reverse hreverse _ _
        (fun q hq => hmiddle (run gs s) q hq) r hr
    _ = s r := congrFun (run_reverse_cancel gs hself s) r

/-- If the cleanup word also never writes targets, its target result is exactly
the intervening map's result, with no claim that this result vanishes. -/
theorem cleanup_target_value (gs : List (Gate Reg))
    (hdst : ∀ g ∈ gs, ¬ target g.dst)
    (middle : State Reg → State Reg) (s : State Reg)
    (r : Reg) (hr : target r) :
    run gs.reverse (middle (run gs s)) r = middle (run gs s) r := by
  exact run_off_target (fun q => ¬ target q) gs.reverse
    (fun g hg => hdst g (List.mem_reverse.mp hg))
    (middle (run gs s)) r (fun hn => hn hr)

end CurrentMain.BitXorReversal
#print axioms CurrentMain.BitXorReversal.run_append
#print axioms CurrentMain.BitXorReversal.run_scalarize
#print axioms CurrentMain.BitXorReversal.step_involutive
#print axioms CurrentMain.BitXorReversal.run_reverse_cancel
#print axioms CurrentMain.BitXorReversal.run_agree_off_target
#print axioms CurrentMain.BitXorReversal.cleanup_off_target
#print axioms CurrentMain.BitXorReversal.cleanup_target_value
