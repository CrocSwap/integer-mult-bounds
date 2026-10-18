import MultitapeToolkit.TM2AnchoredCompiler
import MultitapeToolkit.TM2HeterogeneousCompiler

set_option autoImplicit false

/-!
# Exact invoices for the concrete anchored TM2 compiler

The invoice follows the actual branch and register/stack updates. Push, load,
branch, goto and halt cost one physical transition; peek and pop cost two.
Soundness runs the existing finite machine at every fixed physical bottom anchor.
-/
namespace MultitapeToolkit.TM2Compiler.Certificates
open Turing
open MultitapeToolkit.TM2Compiler.Anchored
variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K] [Fintype Γ] [Fintype Λ] [Fintype σ]

/-- Exact instruction cost, including the branch actually selected by registers. -/
def statementCost : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ) → σ → (K → List Γ) → ℕ
  | .push k f q, v, S => statementCost q v (Function.update S k (f v::S k)) + 1
  | .peek k f q, v, S => statementCost q (f v (S k).head?) S + 2
  | .pop k f q, v, S => statementCost q (f v (S k).head?) (Function.update S k (S k).tail) + 2
  | .load f q, v, S => statementCost q (f v) S + 1
  | .branch f p q, v, S => (if f v then statementCost p v S else statementCost q v S) + 1
  | .goto _, _, _ => 1
  | .halt, _, _ => 1

theorem statementCost_pos (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (v : σ) (S : K → List Γ) : 0 < statementCost q v S := by
  cases q <;> simp only [statementCost] <;> omega

theorem statementCost_le (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (v : σ) (S : K → List Γ) : statementCost q v S ≤ 2*depth q := by
  induction q generalizing v S with
  | push k f q ih =>
    have h := ih v (Function.update S k (f v::S k))
    simp only [statementCost,depth]; omega
  | peek k f q ih =>
    have h := ih (f v (S k).head?) S
    simp only [statementCost,depth]; omega
  | pop k f q ih =>
    have h := ih (f v (S k).head?) (Function.update S k (S k).tail)
    simp only [statementCost,depth]; omega
  | load f q ih =>
    have h := ih (f v) S
    simp only [statementCost,depth]; omega
  | branch f p q ihp ihq =>
    have hp := ihp v S
    have hq := ihq v S
    cases hf : f v <;> simp only [statementCost,depth,hf,Bool.false_eq_true,if_false,if_true] <;> omega
  | goto f => simp [statementCost,depth]
  | halt => simp [statementCost,depth]

/-- Exact lowering charges both physical transitions of every peek and pop. -/
theorem statement_exact (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (anchors : K → ℤ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hq : some q ∈ nodes M) :
    MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M))
      (statementCost q v S) (anchoredStmt M anchors q v S)
      (anchoredEncode M anchors (TM2.stepAux q v S)) := by
  induction q generalizing v S with
  | push k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    exact .cons (anchored_step_push M anchors k f q v S hq) (ih v (Function.update S k (f v::S k)) hc)
  | peek k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    simpa only [statementCost,Nat.add_assoc,TM2.stepAux] using
      MultitapeToolkit.Absolute.Runs.cons (anchored_step_peek_start M anchors k f q v S hq)
        (MultitapeToolkit.Absolute.Runs.cons (anchored_step_peek_finish M anchors k f q v S hq)
          (ih (f v (S k).head?) S hc))
  | pop k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    simpa only [statementCost,Nat.add_assoc,TM2.stepAux] using
      MultitapeToolkit.Absolute.Runs.cons (anchored_step_pop_start M anchors k f q v S hq)
        (MultitapeToolkit.Absolute.Runs.cons (anchored_step_pop_finish M anchors k f q v S hq)
          (ih (f v (S k).head?) (Function.update S k (S k).tail) hc))
  | load f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    exact .cons (anchored_step_load M anchors f q v S hq) (ih (f v) S hc)
  | branch f p q ihp ihq =>
    have hp : some p ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    have hq' : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    cases hf : f v with
    | false =>
      have hs := anchored_step_branch M anchors f p q v S hq
      simp [hf] at hs
      simpa [statementCost,hf,TM2.stepAux] using MultitapeToolkit.Absolute.Runs.cons hs (ihq v S hq')
    | true =>
      have hs := anchored_step_branch M anchors f p q v S hq
      simp [hf] at hs
      simpa [statementCost,hf,TM2.stepAux] using MultitapeToolkit.Absolute.Runs.cons hs (ihp v S hp)
  | goto f => exact .cons (anchored_step_goto M anchors f v S hq) (.refl _)
  | halt => exact .cons (anchored_step_halt M anchors v S hq) (.refl _)

/-- The next macrostep's invoice; a halted source has no next macrostep. -/
def macroCost (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (c : TM2.Cfg (fun _ : K => Γ) Λ σ) : ℕ :=
  match c.l with
  | none => 0
  | some l => statementCost (M l) c.var c.stk

theorem macroCost_pos (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    {c d : TM2.Cfg (fun _ : K => Γ) Λ σ} (h : TM2.step M c = some d) : 0 < macroCost M c := by
  obtain ⟨l,v,S⟩ := c
  cases l with
  | none => simp [TM2.step] at h
  | some l => exact statementCost_pos (M l) v S

theorem macroCost_le (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (c : TM2.Cfg (fun _ : K => Γ) Λ σ) : macroCost M c ≤ overhead M := by
  obtain ⟨l,v,S⟩ := c
  cases l with
  | none => simp [macroCost]
  | some l =>
    exact (statementCost_le (M l) v S).trans
      (Nat.mul_le_mul_left 2 (Finset.le_sup (f:=fun l => depth (M l)) (Finset.mem_univ l)))

theorem macrostep_exact (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) {c d : TM2.Cfg (fun _ : K => Γ) Λ σ} (h : TM2.step M c = some d) :
    MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M))
      (macroCost M c) (anchoredEncode M anchors c) (anchoredEncode M anchors d) := by
  obtain ⟨l,v,S⟩ := c
  cases l with
  | none => simp [TM2.step] at h
  | some l =>
    have hd : d = TM2.stepAux (M l) v S := by simpa [TM2.step] using h.symm
    subst d
    exact statement_exact M anchors (M l) v S (root_mem_nodes M l)

/-- Source certificates retain both macrostep count and exact physical invoice. -/
inductive ChargedRun (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) :
    ℕ → ℕ → TM2.Cfg (fun _ : K => Γ) Λ σ → TM2.Cfg (fun _ : K => Γ) Λ σ → Prop
  | refl (c) : ChargedRun M 0 0 c c
  | cons {n t c d e} (hs : TM2.step M c = some d) (hr : ChargedRun M n t d e) :
      ChargedRun M (n+1) (macroCost M c+t) c e

theorem ChargedRun.sound (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) {n t : ℕ} {c d : TM2.Cfg (fun _ : K => Γ) Λ σ}
    (h : ChargedRun M n t c d) :
    MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M))
      t (anchoredEncode M anchors c) (anchoredEncode M anchors d) := by
  induction h with
  | refl c => exact .refl _
  | cons hs hr ih => exact MultitapeToolkit.Absolute.Trace.runs_trans _ (macrostep_exact M anchors hs) ih

theorem ChargedRun.bounds (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    {n t : ℕ} {c d : TM2.Cfg (fun _ : K => Γ) Λ σ} (h : ChargedRun M n t c d) :
    n ≤ t ∧ t ≤ overhead M*n := by
  induction h with
  | refl c => simp
  | @cons n t c d e hs hr ih =>
    have hp := macroCost_pos M hs
    have hb := macroCost_le M c
    simp only [Nat.mul_succ]
    omega

/-- Every successful source execution has an exact invoice, without an extra hypothesis. -/
theorem chargedRun_of_iterate (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (n : ℕ) (c d : TM2.Cfg (fun _ : K => Γ) Λ σ)
    (h : ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
      (some c) = some d) : ∃ t, ChargedRun M n t c d := by
  induction n generalizing c with
  | zero =>
    have he : c=d := Option.some.inj (by simpa using h)
    subst d
    exact ⟨0,.refl _⟩
  | succ n ih =>
    have hnext :
        ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
          (TM2.step M c) = some d := by
      simpa only [Function.iterate_succ_apply,Option.bind_some] using h
    cases hs : TM2.step M c with
    | none =>
      rw [hs] at hnext
      have hn : ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
          none = none := Function.iterate_fixed (by rfl) n
      rw [hn] at hnext
      cases hnext
    | some middle =>
      rcases ih middle (by simpa only [hs] using hnext) with ⟨t,ht⟩
      exact ⟨macroCost M c+t,.cons hs ht⟩

/-- One invoice compiles at every physical anchor, with both time bounds. -/
theorem compile_exact_invoice (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (n : ℕ) (c d : TM2.Cfg (fun _ : K => Γ) Λ σ)
    (h : ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
      (some c) = some d) :
    ∃ t, n ≤ t ∧ t ≤ overhead M*n ∧ ∀ anchors : K → ℤ,
      MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M))
        t (anchoredEncode M anchors c) (anchoredEncode M anchors d) := by
  rcases chargedRun_of_iterate M n c d h with ⟨t,ht⟩
  exact ⟨t,(ChargedRun.bounds M ht).1,(ChargedRun.bounds M ht).2,
    fun anchors => ChargedRun.sound M anchors ht⟩

/-- A genuinely halted source gives an exact execution and genuine physical halt. -/
theorem compile_halted_invoice (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (n : ℕ) (c : TM2.Cfg (fun _ : K => Γ) Λ σ) (v : σ) (S : K → List Γ)
    (h : ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
      (some c) = some ⟨none,v,S⟩) :
    ∃ t, n ≤ t ∧ t ≤ overhead M*n ∧ ∀ anchors : K → ℤ,
      MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M))
        t (anchoredEncode M anchors c) (anchoredEncode M anchors ⟨none,v,S⟩) ∧
      MultitapeToolkit.Absolute.Halts (MultitapeToolkit.Absolute.ofMachine (compile M))
        (anchoredEncode M anchors ⟨none,v,S⟩) := by
  rcases compile_exact_invoice M n c ⟨none,v,S⟩ h with ⟨t,hl,hu,hr⟩
  exact ⟨t,hl,hu,fun anchors => ⟨hr anchors,anchored_halts M anchors v S⟩⟩

end MultitapeToolkit.TM2Compiler.Certificates
