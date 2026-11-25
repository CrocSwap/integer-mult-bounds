import MultitapeToolkit.TM2Compiler
import MultitapeToolkit.Trace

set_option autoImplicit false

/-!
# Absolute stack anchors for the actual finite TM2 compiler

Each stack's fixed right-bottom anchor is preserved by every source macrostep.
At macro boundaries its physical head is anchor minus stack length. Compiler
microphases are real transitions; peek/pop's temporary right scan is explicit.
-/
namespace MultitapeToolkit.TM2Compiler.Anchored
open Turing MultitapeToolkit.Locality

section Physical
variable {ι α Q : Type*} [Fintype ι] [Fintype α] [Fintype Q] [Inhabited α]

theorem realize_step_heads (P : MultitapeToolkit.Machine ι α Q)
    {c d : MultitapeToolkit.Config ι α Q} {q : Q}
    {actions : ι → MultitapeToolkit.Action α}
    (ht : P.transition c.state (fun i => (c.tapes i).head) = some (q,actions))
    (hr : MultitapeToolkit.step P c = some d) (heads heads' : ι → ℤ)
    (hh : ∀ i, heads' i = heads i + moveOffset (actions i).move) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine P)
      (MultitapeToolkit.Absolute.realize c heads) =
      some (MultitapeToolkit.Absolute.realize d heads') := by
  rcases MultitapeToolkit.Absolute.step_simulation P hr heads with ⟨actual,ha,_⟩
  have hp := congrArg (fun o => o.map (fun e => e.head)) ha
  have he : (fun i => heads i+moveOffset (actions i).move) = actual := by
    simpa [MultitapeToolkit.Absolute.step,MultitapeToolkit.Absolute.ofMachine,
      MultitapeToolkit.Absolute.realize,absoluteCell,ht,Tape.nth_zero] using hp
  have hf : heads' = actual := (funext hh).trans he
  rw [←hf] at ha
  exact ha
end Physical

variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

/-- Fixed physical bottom coordinates; lengths are proof data, never control. -/
def stackHeads (anchors : K → ℤ) (S : K → List Γ) : K → ℤ :=
  fun k => anchors k - (S k).length

noncomputable def anchoredEncode (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (c : TM2.Cfg (fun _ : K => Γ) Λ σ) :=
  MultitapeToolkit.Absolute.realize (encode M c) (stackHeads anchors c.stk)

noncomputable def anchoredStmt (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (v : σ) (S : K → List Γ) :=
  MultitapeToolkit.Absolute.realize (atStmt M q v S) (stackHeads anchors S)

noncomputable def anchoredScan (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (phase : Fin 3) (v : σ) (S : K → List Γ) (k : K) :=
  MultitapeToolkit.Absolute.realize (scan M q phase v S k)
    (fun i => stackHeads anchors S i + if i=k then 1 else 0)

@[simp] theorem anchoredEncode_head
    (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (c : TM2.Cfg (fun _ : K => Γ) Λ σ) (k : K) :
    (anchoredEncode M anchors c).head k = anchors k-(c.stk k).length := rfl

 theorem anchored_step_push (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (k : K) (f : σ → Γ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.push k f q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors (.push k f q) v S) =
      some (anchoredStmt M anchors q v (Function.update S k (f v::S k))) := by
  apply realize_step_heads (compile M)
    (q := active M q v) (actions := onTape k ⟨some (some (f v)),.left⟩)
    (by simp [compile,transition,atStmt,active,address_val M hp])
    (step_push M k f q v S hp)
  intro i
  by_cases hi : i=k
  · subst i; simp [stackHeads,onTape,moveOffset]; omega
  · simp [stackHeads,onTape,hi,idle,moveOffset]

 theorem anchored_step_peek_start (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.peek k f q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors (.peek k f q) v S) =
      some (anchoredScan M anchors (.peek k f q) 1 v S k) := by
  apply realize_step_heads (compile M)
    (q := ⟨address M (some (.peek k f q)),1,v⟩) (actions := onTape k ⟨none,.right⟩)
    (by simp [compile,transition,atStmt,active,address_val M hp])
    (step_peek_start M k f q v S hp)
  intro i
  by_cases hi : i=k <;> simp [stackHeads,onTape,hi,idle,moveOffset]

 theorem anchored_step_pop_start (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.pop k f q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors (.pop k f q) v S) =
      some (anchoredScan M anchors (.pop k f q) 2 v S k) := by
  apply realize_step_heads (compile M)
    (q := ⟨address M (some (.pop k f q)),2,v⟩) (actions := onTape k ⟨none,.right⟩)
    (by simp [compile,transition,atStmt,active,address_val M hp])
    (step_pop_start M k f q v S hp)
  intro i
  by_cases hi : i=k <;> simp [stackHeads,onTape,hi,idle,moveOffset]

 theorem anchored_step_peek_finish (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.peek k f q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredScan M anchors (.peek k f q) 1 v S k) =
      some (anchoredStmt M anchors q (f v (S k).head?) S) := by
  apply realize_step_heads (compile M)
    (q := active M q (f v (S k).head?)) (actions := onTape k ⟨none,.left⟩)
    (by simp [compile,transition,scan,address_val M hp])
    (step_peek_finish M k f q v S hp)
  intro i
  by_cases hi : i=k
  · subst i; simp [onTape,moveOffset]
  · simp [onTape,hi,idle,moveOffset]

 theorem anchored_step_pop_finish (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (k : K) (f : σ → Option Γ → σ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.pop k f q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredScan M anchors (.pop k f q) 2 v S k) =
      some (anchoredStmt M anchors q (f v (S k).head?) (Function.update S k (S k).tail)) := by
  apply realize_step_heads (compile M)
    (q := active M q (f v (S k).head?))
    (actions := onTape k (if (S k).head?.isNone then ⟨none,.left⟩ else ⟨some none,.stay⟩))
    (by simp [compile,transition,scan,address_val M hp])
    (step_pop_finish M k f q v S hp)
  intro i
  by_cases hi : i=k
  · subst i
    cases hb : S k with
    | nil => simp [stackHeads,onTape,hb,moveOffset]
    | cons b bs => simp [stackHeads,onTape,hb,moveOffset]; omega
  · simp [stackHeads,onTape,hi,idle,moveOffset]

end MultitapeToolkit.TM2Compiler.Anchored

namespace MultitapeToolkit.TM2Compiler.Anchored
open Turing MultitapeToolkit.Locality
variable {K Γ Λ σ : Type} [Fintype K] [DecidableEq K]
  [Fintype Γ] [Fintype Λ] [Fintype σ]

 theorem anchored_step_load (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (f : σ → σ)
    (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.load f q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors (.load f q) v S) = some (anchoredStmt M anchors q (f v) S) := by
  apply realize_step_heads (compile M) (q := active M q (f v)) (actions := fun _ => idle)
    (by simp [compile,transition,atStmt,active,address_val M hp]) (step_load M f q v S hp)
  intro i; simp [idle,moveOffset]

 theorem anchored_step_branch (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (f : σ → Bool)
    (p q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ)) (v : σ) (S : K → List Γ)
    (hp : some (.branch f p q) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors (.branch f p q) v S) =
      some (anchoredStmt M anchors (if f v then p else q) v S) := by
  apply realize_step_heads (compile M) (q := active M (if f v then p else q) v)
    (actions := fun _ => idle)
    (by simp [compile,transition,atStmt,active,address_val M hp]) (step_branch M f p q v S hp)
  intro i; simp [idle,moveOffset]

 theorem anchored_step_goto (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (f : σ → Λ) (v : σ) (S : K → List Γ)
    (hp : some (.goto f) ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors (.goto f) v S) =
      some (anchoredEncode M anchors ⟨some (f v),v,S⟩) := by
  apply realize_step_heads (compile M) (q := active M (M (f v)) v) (actions := fun _ => idle)
    (by simp [compile,transition,atStmt,active,address_val M hp]) (step_goto M f v S hp)
  intro i; simp [idle,moveOffset]

 theorem anchored_step_halt (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (v : σ) (S : K → List Γ) (hp : some .halt ∈ nodes M) :
    MultitapeToolkit.Absolute.step (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredStmt M anchors .halt v S) = some (anchoredEncode M anchors ⟨none,v,S⟩) := by
  apply realize_step_heads (compile M) (q := stopped M v) (actions := fun _ => idle)
    (by simp [compile,transition,atStmt,active,address_val M hp]) (step_halt M v S hp)
  intro i; simp [idle,moveOffset]

/-- Every syntax action is charged; its exact endpoint retains fixed physical
bottom anchors. Peek and pop pay both real scan transitions. -/
theorem anchored_statement_runs (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (q : Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (v : σ) (S : K → List Γ) (hq : some q ∈ nodes M) :
    ∃ t, t ≤ 2*depth q ∧
      MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M)) t
        (anchoredStmt M anchors q v S) (anchoredEncode M anchors (TM2.stepAux q v S)) := by
  induction q generalizing v S with
  | push k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    rcases ih v (Function.update S k (f v::S k)) hc with ⟨t,ht,hr⟩
    refine ⟨t+1,by simp only [depth]; omega,?_⟩
    exact .cons (anchored_step_push M anchors k f q v S hq) hr
  | peek k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    rcases ih (f v (S k).head?) S hc with ⟨t,ht,hr⟩
    refine ⟨t+2,by simp only [depth]; omega,?_⟩
    simpa only [Nat.add_assoc,TM2.stepAux] using
      MultitapeToolkit.Absolute.Runs.cons (anchored_step_peek_start M anchors k f q v S hq)
        (MultitapeToolkit.Absolute.Runs.cons (anchored_step_peek_finish M anchors k f q v S hq) hr)
  | pop k f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    rcases ih (f v (S k).head?) (Function.update S k (S k).tail) hc with ⟨t,ht,hr⟩
    refine ⟨t+2,by simp only [depth]; omega,?_⟩
    simpa only [Nat.add_assoc,TM2.stepAux] using
      MultitapeToolkit.Absolute.Runs.cons (anchored_step_pop_start M anchors k f q v S hq)
        (MultitapeToolkit.Absolute.Runs.cons (anchored_step_pop_finish M anchors k f q v S hq) hr)
  | load f q ih =>
    have hc : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    rcases ih (f v) S hc with ⟨t,ht,hr⟩
    refine ⟨t+1,by simp only [depth]; omega,?_⟩
    exact .cons (anchored_step_load M anchors f q v S hq) hr
  | branch f p q ihp ihq =>
    have hp : some p ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    have hq' : some q ∈ nodes M := child_mem_nodes M hq (by simp [TM2.stmts₁,TM2.stmts₁_self])
    cases hf : f v with
    | false =>
      rcases ihq v S hq' with ⟨t,ht,hr⟩
      refine ⟨t+1,by simp only [depth]; omega,?_⟩
      have hs := anchored_step_branch M anchors f p q v S hq
      simp [hf] at hs
      simpa [hf,TM2.stepAux] using MultitapeToolkit.Absolute.Runs.cons hs hr
    | true =>
      rcases ihp v S hp with ⟨t,ht,hr⟩
      refine ⟨t+1,by simp only [depth]; omega,?_⟩
      have hs := anchored_step_branch M anchors f p q v S hq
      simp [hf] at hs
      simpa [hf,TM2.stepAux] using MultitapeToolkit.Absolute.Runs.cons hs hr
  | goto f =>
    exact ⟨1,by simp [depth],.cons (anchored_step_goto M anchors f v S hq) (.refl _)⟩
  | halt =>
    exact ⟨1,by simp [depth],.cons (anchored_step_halt M anchors v S hq) (.refl _)⟩

theorem anchored_macrostep_runs (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (c d : TM2.Cfg (fun _ : K => Γ) Λ σ) (h : TM2.step M c = some d) :
    ∃ t, t ≤ overhead M ∧
      MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M)) t
        (anchoredEncode M anchors c) (anchoredEncode M anchors d) := by
  obtain ⟨l,v,S⟩ := c
  cases l with
  | none => simp [TM2.step] at h
  | some l =>
    have hd : d = TM2.stepAux (M l) v S := by simpa [TM2.step] using h.symm
    subst d
    rcases anchored_statement_runs M anchors (M l) v S (root_mem_nodes M l) with ⟨t,ht,hr⟩
    refine ⟨t,ht.trans ?_,hr⟩
    exact Nat.mul_le_mul_left 2 (Finset.le_sup (f:=fun l => depth (M l)) (Finset.mem_univ l))

/-- Universal actual compilation with the original overhead and exact absolute
heads/cells at every macro boundary. No tape origin is reset for free. -/
theorem anchored_compile_run (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (n : ℕ) (c d : TM2.Cfg (fun _ : K => Γ) Λ σ)
    (h : ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
      (some c) = some d) :
    ∃ t, t ≤ overhead M*n ∧
      MultitapeToolkit.Absolute.Runs (MultitapeToolkit.Absolute.ofMachine (compile M)) t
        (anchoredEncode M anchors c) (anchoredEncode M anchors d) := by
  induction n generalizing c with
  | zero =>
    have he : c=d := Option.some.inj (by simpa using h)
    subst d
    exact ⟨0,by simp,.refl _⟩
  | succ n ih =>
    have hnext :
        ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n])
          (TM2.step M c) = some d := by
      simpa only [Function.iterate_succ_apply,Option.bind_some] using h
    cases hs : TM2.step M c with
    | none =>
      rw [hs] at hnext
      have hn : ((fun o : Option (TM2.Cfg (fun _ : K => Γ) Λ σ) => o.bind (TM2.step M))^[n]) none = none :=
        Function.iterate_fixed (by rfl) n
      rw [hn] at hnext
      cases hnext
    | some middle =>
      rcases ih middle (by simpa only [hs] using hnext) with ⟨t,ht,hr⟩
      rcases anchored_macrostep_runs M anchors c middle hs with ⟨s,hb,hs⟩
      refine ⟨s+t,?_,MultitapeToolkit.Absolute.Trace.runs_trans _ hs hr⟩
      simp only [Nat.mul_succ]
      omega

/-- Genuine source halt transfers at the physically anchored terminal bank. -/
theorem anchored_halts (M : Λ → Statement (K:=K) (Γ:=Γ) (Λ:=Λ) (σ:=σ))
    (anchors : K → ℤ) (v : σ) (S : K → List Γ) :
    MultitapeToolkit.Absolute.Halts (MultitapeToolkit.Absolute.ofMachine (compile M))
      (anchoredEncode M anchors ⟨none,v,S⟩) := by
  exact (MultitapeToolkit.Absolute.halts_iff (compile M) (encode M ⟨none,v,S⟩)
    (stackHeads anchors S)).2 (encode_halts M v S)

end MultitapeToolkit.TM2Compiler.Anchored
