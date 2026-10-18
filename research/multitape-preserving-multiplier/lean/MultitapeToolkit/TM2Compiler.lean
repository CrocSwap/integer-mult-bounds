import MultitapeToolkit.Model
import Mathlib.Computability.TuringMachine.StackTuringMachine
import Mathlib.Data.Fintype.Sum
import Mathlib.Data.Finset.Lattice.Fold
import Lean.Elab.Tactic.Omega

set_option autoImplicit false

namespace MultitapeToolkit.TM2Compiler

open Turing

variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

abbrev Statement := TM2.Stmt (fun _ : K => Γ) Λ σ

/-- All syntax nodes in the fixed finite program, including the halted node. -/
noncomputable def nodes (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :
    Finset (Option (Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))) := by
  classical
  exact TM2.stmts M Finset.univ

abbrev Node (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :=
  { q // q ∈ nodes M }

/-- Finite control: a syntax-node address, a three-way microphase, and finite registers. -/
abbrev Control (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :=
  Node M × Fin 3 × σ

noncomputable instance (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :
    Fintype (Node M) := by
  classical
  exact Fintype.ofFinset (nodes M) (fun _ => Iff.rfl)

noncomputable instance (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :
    Fintype (Control M) := inferInstance

@[simp] theorem none_mem_nodes (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :
    none ∈ nodes M := by
  classical
  simp [nodes, TM2.stmts]

theorem root_mem_nodes (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) (l : Λ) :
    some (M l) ∈ nodes M := by
  classical
  simp only [nodes, TM2.stmts, Finset.some_mem_insertNone, Finset.mem_biUnion,
    Finset.mem_univ, true_and]
  exact ⟨l, TM2.stmts₁_self⟩

theorem child_mem_nodes (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    {p q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)}
    (hp : some p ∈ nodes M) (hq : q ∈ TM2.stmts₁ p) : some q ∈ nodes M :=
  TM2.stmts_trans hq hp

/-- Total finite address construction. The fallback is used only for unreachable syntax. -/
noncomputable def address (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (q : Option (Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))) : Node M := by
  classical
  exact if h : q ∈ nodes M then ⟨q, h⟩ else ⟨none, none_mem_nodes M⟩

@[simp] theorem address_val (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    {q : Option (Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))}
    (hq : q ∈ nodes M) : (address M q).val = q := by
  classical
  simp [address, hq]

/-- Maximum single-path syntax depth; each syntax action requires at most two tape steps. -/
def depth : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ) → Nat
  | .push _ _ q => depth q + 1
  | .peek _ _ q => depth q + 1
  | .pop _ _ q => depth q + 1
  | .load _ q => depth q + 1
  | .branch _ p q => max (depth p) (depth q) + 1
  | .goto _ => 1
  | .halt => 1

noncomputable def overhead (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) : Nat :=
  2 * Finset.univ.sup (fun l => depth (M l))

end MultitapeToolkit.TM2Compiler

namespace MultitapeToolkit.TM2Compiler

open Turing MultitapeToolkit

variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

/-- A stationary, non-writing tape action. -/
def idle : Action (Option Γ) := ⟨none, .stay⟩

/-- Only the selected tape is changed. -/
def onTape (k : K) (a : Action (Option Γ)) : K → Action (Option Γ) :=
  Function.update (fun _ => idle) k a

noncomputable def active (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) (v : σ) : Control M :=
  ⟨address M (some q), 0, v⟩

noncomputable def stopped (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) : Control M := ⟨address M none, 0, v⟩

/-- Finite table expansion of one stack action into at most two tape actions.
The read-only phase and destructive-read phase inspect only the current heads. -/
noncomputable def transition (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (c : Control M) (heads : K → Option Γ) : Option (Control M × (K → Action (Option Γ))) :=
  match c.1.val with
  | none => none
  | some p =>
    if c.2.1 = 0 then
      match p with
      | .push k f q => some (active M q c.2.2, onTape k ⟨some (some (f c.2.2)), .left⟩)
      | .peek k _ _ => some (⟨c.1, 1, c.2.2⟩, onTape k ⟨none, .right⟩)
      | .pop k _ _ => some (⟨c.1, 2, c.2.2⟩, onTape k ⟨none, .right⟩)
      | .load f q => some (active M q (f c.2.2), fun _ => idle)
      | .branch f p q => some (active M (if f c.2.2 then p else q) c.2.2, fun _ => idle)
      | .goto f => some (active M (M (f c.2.2)) c.2.2, fun _ => idle)
      | .halt => some (stopped M c.2.2, fun _ => idle)
    else if c.2.1 = 1 then
      match p with
      | .peek k f q => some (active M q (f c.2.2 (heads k)), onTape k ⟨none, .left⟩)
      | _ => none
    else
      match p with
      | .pop k f q => some (active M q (f c.2.2 (heads k)),
          onTape k (if (heads k).isNone then ⟨none, .left⟩ else ⟨some none, .stay⟩))
      | _ => none

noncomputable def compile (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) :
    Machine K (Option Γ) (Control M) := ⟨transition M⟩

noncomputable def atStmt (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) (v : σ)
    (S : K → List Γ) : Config K (Option Γ) (Control M) :=
  ⟨active M q v, fun k => stackTape (S k)⟩

/-- Every stack head is represented by the blank immediately to its left. -/
noncomputable def encode (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (c : TM2.Cfg (fun _ : K => Γ) Λ σ) : Config K (Option Γ) (Control M) :=
  ⟨⟨address M (c.l.map M), 0, c.var⟩, fun k => stackTape (c.stk k)⟩

@[simp] theorem encode_some (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (l : Λ) (v : σ) (S : K → List Γ) :
    encode M ⟨some l, v, S⟩ = atStmt M (M l) v S := rfl

@[simp] theorem encode_tapes (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (c : TM2.Cfg (fun _ : K => Γ) Λ σ) (k : K) :
    (encode M c).tapes k = stackTape (c.stk k) := rfl

end MultitapeToolkit.TM2Compiler


namespace MultitapeToolkit.TM2Compiler

open Turing MultitapeToolkit

variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

@[simp] theorem act_idle (t : Tape (Option Γ)) : act idle t = t := rfl

 theorem act_onTape (k : K) (a : Action (Option Γ)) (T : K → Tape (Option Γ)) :
    (fun j => act (onTape k a j) (T j)) = Function.update T k (act a (T k)) := by
  funext j
  by_cases h : j = k
  · subst j; simp [onTape]
  · simp [onTape, Function.update_of_ne h]

 theorem tapes_update (S : K → List Γ) (k : K) (s : List Γ) :
    (fun j => stackTape (Function.update S k s j)) =
      Function.update (fun j => stackTape (S j)) k (stackTape s) := by
  funext j
  by_cases h : j = k
  · subst j; simp
  · simp [Function.update_of_ne h]

noncomputable def scan (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (p : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ)) (phase : Fin 3)
    (v : σ) (S : K → List Γ) (k : K) : Config K (Option Γ) (Control M) :=
  ⟨⟨address M (some p), phase, v⟩,
    Function.update (fun j => stackTape (S j)) k ((stackTape (S k)).move .right)⟩

 theorem step_push (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (k : K) (f : σ → Γ) (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.push k f q) ∈ nodes M) :
    step (compile M) (atStmt M (.push k f q) v S) =
      some (atStmt M q v (Function.update S k (f v :: S k))) := by
  simp only [step, compile, transition, atStmt, active, address_val M hp, ite_true, ite_false, Option.map_some]
  congr 1
  rw [act_onTape, tapes_update]
  congr 2

 theorem step_peek_start (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.peek k f q) ∈ nodes M) :
    step (compile M) (atStmt M (.peek k f q) v S) =
      some (scan M (.peek k f q) 1 v S k) := by
  simp only [step, compile, transition, atStmt, active, address_val M hp, ite_true, ite_false, Option.map_some]
  congr 1
  exact congrArg (Config.mk _) (act_onTape k _ _)

 theorem step_pop_start (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.pop k f q) ∈ nodes M) :
    step (compile M) (atStmt M (.pop k f q) v S) =
      some (scan M (.pop k f q) 2 v S k) := by
  simp only [step, compile, transition, atStmt, active, address_val M hp, ite_true, ite_false, Option.map_some]
  congr 1
  exact congrArg (Config.mk _) (act_onTape k _ _)

 theorem step_peek_finish (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.peek k f q) ∈ nodes M) :
    step (compile M) (scan M (.peek k f q) 1 v S k) =
      some (atStmt M q (f v (S k).head?) S) := by
  simp only [step, compile, transition, scan, address_val M hp]
  simp only [Prod.fst, Prod.snd, show (1 : Fin 3) ≠ 0 by decide,
    if_neg, if_pos rfl, ite_true, ite_false, Function.update_self, stackTape_move_right_head, Option.map_some]
  congr 1
  apply congrArg (Config.mk _)
  change (fun j => act (onTape k ⟨none, .left⟩ j)
    (Function.update (fun i => stackTape (S i)) k ((stackTape (S k)).move .right) j)) = _
  rw [act_onTape]
  simp only [Function.update_self, act, moveTape, stackTape_peek_restore,
    Function.update_idem]
  exact Function.update_eq_self k _

 theorem step_pop_finish (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.pop k f q) ∈ nodes M) :
    step (compile M) (scan M (.pop k f q) 2 v S k) =
      some (atStmt M q (f v (S k).head?) (Function.update S k (S k).tail)) := by
  simp only [step, compile, transition, scan, address_val M hp]
  simp only [Prod.fst, Prod.snd, show (2 : Fin 3) ≠ 0 by decide,
    show (2 : Fin 3) ≠ 1 by decide, if_neg, ite_true, ite_false, Function.update_self,
    stackTape_move_right_head, Option.map_some]
  congr 1
  apply congrArg (Config.mk _)
  change (fun j => act (onTape k
      (if (S k).head?.isNone then ⟨none, .left⟩ else ⟨some none, .stay⟩) j)
    (Function.update (fun i => stackTape (S i)) k ((stackTape (S k)).move .right) j)) = _
  rw [act_onTape, tapes_update]
  simp only [Function.update_self, Function.update_idem]
  congr 2
  cases h : S k with
  | nil => simp [h, act, moveTape, stackTape_pop_nil]
  | cons a s => simp [h, act, moveTape, stackTape_pop_cons]

end MultitapeToolkit.TM2Compiler

namespace MultitapeToolkit.TM2Compiler

open Turing MultitapeToolkit

variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

 theorem step_load (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (f : σ → σ) (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.load f q) ∈ nodes M) :
    step (compile M) (atStmt M (.load f q) v S) = some (atStmt M q (f v) S) := by
  simp [step, compile, transition, atStmt, active, address_val M hp]

 theorem step_branch (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (f : σ → Bool) (p q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some (.branch f p q) ∈ nodes M) :
    step (compile M) (atStmt M (.branch f p q) v S) =
      some (atStmt M (if f v then p else q) v S) := by
  simp [step, compile, transition, atStmt, active, address_val M hp]

 theorem step_goto (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (f : σ → Λ) (v : σ) (S : K → List Γ)
    (hp : some (.goto f) ∈ nodes M) :
    step (compile M) (atStmt M (.goto f) v S) = some (encode M ⟨some (f v), v, S⟩) := by
  simp [step, compile, transition, atStmt, active, encode, address_val M hp]

 theorem step_halt (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hp : some .halt ∈ nodes M) :
    step (compile M) (atStmt M .halt v S) = some (encode M ⟨none, v, S⟩) := by
  simp [step, compile, transition, atStmt, active, stopped, encode, address_val M hp]

/-- Every fixed TM2 statement has a checked linear-in-syntax tape implementation. -/
 theorem statement_runs (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (q : Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) (hq : some q ∈ nodes M) :
    RunsWithin (compile M) (2 * depth q) (atStmt M q v S)
      (encode M (TM2.stepAux q v S)) := by
  induction q generalizing v S with
  | push k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁, TM2.stmts₁_self])
    rcases ih v (Function.update S k (f v :: S k)) hc with ⟨n, hn, hr⟩
    refine ⟨n + 1, ?_, ?_⟩
    · simp only [depth]; omega
    · exact Runs.cons (step_push M k f q v S hq) hr
  | peek k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁, TM2.stmts₁_self])
    rcases ih (f v (S k).head?) S hc with ⟨n, hn, hr⟩
    refine ⟨n + 2, ?_, ?_⟩
    · simp only [depth]; omega
    · simpa only [Nat.add_assoc, TM2.stepAux] using
        Runs.cons (step_peek_start M k f q v S hq)
          (Runs.cons (step_peek_finish M k f q v S hq) hr)
  | pop k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁, TM2.stmts₁_self])
    rcases ih (f v (S k).head?) (Function.update S k (S k).tail) hc with ⟨n, hn, hr⟩
    refine ⟨n + 2, ?_, ?_⟩
    · simp only [depth]; omega
    · simpa only [Nat.add_assoc, TM2.stepAux] using
        Runs.cons (step_pop_start M k f q v S hq)
          (Runs.cons (step_pop_finish M k f q v S hq) hr)
  | load f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁, TM2.stmts₁_self])
    rcases ih (f v) S hc with ⟨n, hn, hr⟩
    refine ⟨n + 1, ?_, ?_⟩
    · simp only [depth]; omega
    · exact Runs.cons (step_load M f q v S hq) hr
  | branch f p q ihp ihq =>
    have hp : some p ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁, TM2.stmts₁_self])
    have hq' : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁, TM2.stmts₁_self])
    cases hf : f v with
    | false =>
      rcases ihq v S hq' with ⟨n, hn, hr⟩
      refine ⟨n + 1, ?_, ?_⟩
      · simp only [depth]; omega
      · have hs := step_branch M f p q v S hq
        simp [hf] at hs
        simpa [hf, TM2.stepAux] using Runs.cons hs hr
    | true =>
      rcases ihp v S hp with ⟨n, hn, hr⟩
      refine ⟨n + 1, ?_, ?_⟩
      · simp only [depth]; omega
      · have hs := step_branch M f p q v S hq
        simp [hf] at hs
        simpa [hf, TM2.stepAux] using Runs.cons hs hr
  | goto f =>
    exact ⟨1, by simp [depth], Runs.one (step_goto M f v S hq)⟩
  | halt =>
    exact ⟨1, by simp [depth], Runs.one (step_halt M v S hq)⟩

/-- A single macrostep uses a constant depending only on the finite program. -/
 theorem macrostep_runs (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (c d : TM2.Cfg (fun _ : K => Γ) Λ σ) (h : TM2.step M c = some d) :
    RunsWithin (compile M) (overhead M) (encode M c) (encode M d) := by
  classical
  obtain ⟨l, v, S⟩ := c
  cases l with
  | none => simp [TM2.step] at h
  | some l =>
    have hd : d = TM2.stepAux (M l) v S := by simpa [TM2.step] using h.symm
    subst d
    rcases statement_runs M (M l) v S (root_mem_nodes M l) with ⟨n, hn, hr⟩
    refine ⟨n, hn.trans ?_, hr⟩
    exact Nat.mul_le_mul_left 2 (Finset.le_sup (f := fun l => depth (M l)) (Finset.mem_univ l))

/-- A genuinely halted TM2 configuration becomes a genuinely halted multitape configuration. -/
 theorem encode_halts (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (v : σ) (S : K → List Γ) : Halts (compile M) (encode M ⟨none, v, S⟩) := by
  simp [Halts, step, compile, transition, encode, address_val M (none_mem_nodes M)]

end MultitapeToolkit.TM2Compiler

namespace MultitapeToolkit.TM2Compiler

open Turing MultitapeToolkit

variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

/-- Exact source executions lift with a uniform, input-independent linear time overhead. -/
 theorem compile_run (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (n : Nat) (c d : TM2.Cfg (fun _ : K => Γ) Λ σ)
    (h : ((fun s : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => s.bind (TM2.step M))^[n])
      (some c) = some d) :
    RunsWithin (compile M) (overhead M * n) (encode M c) (encode M d) := by
  induction n generalizing c with
  | zero =>
    have hc : c = d := Option.some.inj (by simpa using h)
    subst d
    exact ⟨0, by simp, Runs.refl _⟩
  | succ n ih =>
    have hnext :
        ((fun s : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => s.bind (TM2.step M))^[n])
          (TM2.step M c) = some d := by
      simpa only [Function.iterate_succ_apply, Option.bind_some] using h
    cases hs : TM2.step M c with
    | none =>
      rw [hs] at hnext
      have hf :
          ((fun s : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => s.bind (TM2.step M))^[n])
            none = none := Function.iterate_fixed (by rfl) n
      rw [hf] at hnext
      cases hnext
    | some middle =>
      have ht := ih middle (by simpa only [hs] using hnext)
      have hc := macrostep_runs M c middle hs
      simpa [Nat.mul_succ, Nat.add_comm] using hc.trans ht

/-- The compiler preserves the actual output symbols, without an assumed decoding oracle. -/
 theorem read_output (M : Λ → Statement (K := K) (Γ := Γ) (Λ := Λ) (σ := σ))
    (c : TM2.Cfg (fun _ : K => Γ) Λ σ) (k : K) :
    readStack (c.stk k).length ((encode M c).tapes k) = c.stk k :=
  readStack_stackTape _

end MultitapeToolkit.TM2Compiler








