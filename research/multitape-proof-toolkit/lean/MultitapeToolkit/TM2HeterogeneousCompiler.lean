import MultitapeToolkit.TM2Compiler
import Mathlib.Data.Fintype.Sigma

/-!
# Constant-overhead compilation for heterogeneous finite TM2 alphabets

A stack symbol is tagged by its fixed stack index. Reads decode that index by
finite case analysis; a wrong tag yields `none`, so the transition table is total.
Every actual source configuration is embedded with the correct tags. The exact
step-commutation theorem preserves that invariant without an assumed reverse map.
No extra source macrosteps or syntax depth are introduced by tagging.
-/

set_option autoImplicit false

namespace MultitapeToolkit.TM2HeterogeneousCompiler

open Turing

variable {K Λ σ : Type} {Γ : K → Type} [Fintype K] [DecidableEq K]
  [∀ k, Fintype (Γ k)] [Fintype Λ] [Fintype σ]

abbrev Common (Γ : K → Type) := Sigma Γ

/-- A symbol's stack address is part of the fixed finite tape alphabet. -/
def tagged (k : K) (a : Γ k) : Common Γ := ⟨k, a⟩

/-- Total finite tag decoder. It requires no inhabited source alphabet. -/
def decode (k : K) (a : Common Γ) : Option (Γ k) :=
  if h : a.1 = k then some (h ▸ a.2) else none

@[simp] theorem decode_tagged (k : K) (a : Γ k) :
    decode k (tagged k a) = some a := by simp [decode, tagged]

/-- The optional top of a correctly tagged stack is decoded exactly. -/
theorem decode_head (k : K) (s : List (Γ k)) :
    ((s.map (tagged k)).head?).bind (decode k) = s.head? := by
  cases s <;> simp

/-- The finite output-symbol decoder recovers every source symbol. -/
theorem decode_list (k : K) (s : List (Γ k)) :
    (s.map (tagged k)).filterMap (decode k) = s := by
  induction s with
  | nil => rfl
  | cons a s ih => simp [ih]

/-- Tag every alphabet-dependent instruction, preserving its syntax tree. -/
def flattenStmt : TM2.Stmt Γ Λ σ → TM2.Stmt (fun _ : K => Common Γ) Λ σ
  | .push k f q => .push k (fun v => tagged k (f v)) (flattenStmt q)
  | .peek k f q => .peek k (fun v a => f v (a.bind (decode k))) (flattenStmt q)
  | .pop k f q => .pop k (fun v a => f v (a.bind (decode k))) (flattenStmt q)
  | .load f q => .load f (flattenStmt q)
  | .branch f p q => .branch f (flattenStmt p) (flattenStmt q)
  | .goto f => .goto f
  | .halt => .halt

/-- All symbols in stack `k` have tag `k`. -/
def flattenStacks (S : ∀ k, List (Γ k)) : K → List (Common Γ) :=
  fun k => (S k).map (tagged k)

/-- Every nonblank symbol on stack `k` carries exactly tag `k`. -/
def WellTagged (S : K → List (Common Γ)) : Prop :=
  ∀ k a, a ∈ S k → a.1 = k

/-- The embedding establishes the tag invariant for every typed source stack store. -/
theorem flattenStacks_wellTagged (S : ∀ k, List (Γ k)) : WellTagged (flattenStacks S) := by
  intro k a h
  change a ∈ (S k).map (tagged k) at h
  rcases List.mem_map.mp h with ⟨b, hb, rfl⟩
  rfl
/-- The typed source state is unchanged and all stacks are embedded explicitly. -/
def flattenCfg (c : TM2.Cfg Γ Λ σ) : TM2.Cfg (fun _ : K => Common Γ) Λ σ :=
  ⟨c.l, c.var, flattenStacks c.stk⟩

theorem update_flattenStacks (S : ∀ k, List (Γ k)) (k : K) (s : List (Γ k)) :
    Function.update (flattenStacks S) k (s.map (tagged k)) =
      flattenStacks (Function.update S k s) := by
  funext j
  by_cases h : j = k
  · subst j; simp [flattenStacks]
  · simp [flattenStacks, h]

/-- All source configurations, including arbitrary finite typed stacks, commute with execution. -/
theorem stepAux_flattenStmt (q : TM2.Stmt Γ Λ σ) (v : σ) (S : ∀ k, List (Γ k)) :
    TM2.stepAux (flattenStmt q) v (flattenStacks S) =
      flattenCfg (TM2.stepAux q v S) := by
  induction q generalizing v S with
  | push k f q ih =>
    simp only [flattenStmt, TM2.stepAux]
    change TM2.stepAux (flattenStmt q) v
      (Function.update (flattenStacks S) k ((f v :: S k).map (tagged k))) = _
    rw [update_flattenStacks]
    exact ih v (Function.update S k (f v :: S k))
  | peek k f q ih =>
    simp only [flattenStmt, TM2.stepAux]
    change TM2.stepAux (flattenStmt q)
      (f v (((S k).map (tagged k)).head?.bind (decode k))) (flattenStacks S) = _
    rw [decode_head]
    exact ih (f v (S k).head?) S
  | pop k f q ih =>
    simp only [flattenStmt, TM2.stepAux]
    change TM2.stepAux (flattenStmt q)
      (f v (((S k).map (tagged k)).head?.bind (decode k)))
      (Function.update (flattenStacks S) k ((S k).map (tagged k)).tail) = _
    rw [decode_head]
    rw [show ((S k).map (tagged k)).tail = (S k).tail.map (tagged k) by
      cases S k <;> rfl]
    rw [update_flattenStacks]
    exact ih (f v (S k).head?) (Function.update S k (S k).tail)
  | load f q ih =>
    simp only [flattenStmt, TM2.stepAux]
    exact ih (f v) S
  | branch f p q ihp ihq =>
    simp only [flattenStmt, TM2.stepAux]
    cases hf : f v <;> simp
    · exact ihq v S
    · exact ihp v S
  | goto f => rfl
  | halt => rfl

/-- Executing a tagged source configuration preserves the tag invariant. -/
theorem stepAux_wellTagged (q : TM2.Stmt Γ Λ σ) (v : σ) (S : ∀ k, List (Γ k)) :
    WellTagged (TM2.stepAux (flattenStmt q) v (flattenStacks S)).stk := by
  rw [stepAux_flattenStmt]
  exact flattenStacks_wellTagged _
/-- Source syntax depth, independent of its heterogeneous alphabets. -/
def depth : TM2.Stmt Γ Λ σ → Nat
  | .push _ _ q => depth q + 1
  | .peek _ _ q => depth q + 1
  | .pop _ _ q => depth q + 1
  | .load _ q => depth q + 1
  | .branch _ p q => max (depth p) (depth q) + 1
  | .goto _ => 1
  | .halt => 1

/-- Tagging introduces no extra syntax or macrostep cost. -/
theorem depth_flattenStmt (q : TM2.Stmt Γ Λ σ) :
    TM2Compiler.depth (flattenStmt q) = depth q := by
  induction q <;> simp [flattenStmt, TM2Compiler.depth, depth, *]

def flattenProgram (M : Λ → TM2.Stmt Γ Λ σ) :
    Λ → TM2.Stmt (fun _ : K => Common Γ) Λ σ := fun l => flattenStmt (M l)

/-- Exact one-step simulation, including the source halted state. -/
theorem step_flattenProgram (M : Λ → TM2.Stmt Γ Λ σ) (c : TM2.Cfg Γ Λ σ) :
    TM2.step (flattenProgram M) (flattenCfg c) = (TM2.step M c).map flattenCfg := by
  cases c with
  | mk l v S =>
    cases l with
    | none => rfl
    | some l =>
      simp only [flattenCfg, TM2.step, flattenProgram, Option.map_some]
      rw [stepAux_flattenStmt]
      rfl

/-- Every exact heterogeneous source run is reproduced with exactly the same macrostep count. -/
theorem flatten_run (M : Λ → TM2.Stmt Γ Λ σ) (n : Nat) (c d : TM2.Cfg Γ Λ σ)
    (h : ((fun s : Option (TM2.Cfg Γ Λ σ) => s.bind (TM2.step M))^[n])
      (some c) = some d) :
    ((fun s => s.bind (TM2.step (flattenProgram M)))^[n])
      (some (flattenCfg c)) = some (flattenCfg d) := by
  induction n generalizing c with
  | zero =>
    have hc : c = d := Option.some.inj (by simpa using h)
    subst d
    rfl
  | succ n ih =>
    have hnext : ((fun s : Option (TM2.Cfg Γ Λ σ) => s.bind (TM2.step M))^[n])
        (TM2.step M c) = some d := by
      simpa only [Function.iterate_succ_apply, Option.bind_some] using h
    cases hs : TM2.step M c with
    | none =>
      rw [hs] at hnext
      have hf : ((fun s : Option (TM2.Cfg Γ Λ σ) => s.bind (TM2.step M))^[n])
          none = none := Function.iterate_fixed (by rfl) n
      rw [hf] at hnext
      cases hnext
    | some middle =>
      have ht := ih middle (by simpa only [hs] using hnext)
      have hstep : TM2.step (flattenProgram M) (flattenCfg c) = some (flattenCfg middle) := by
        rw [step_flattenProgram, hs]
        rfl
      simpa only [Function.iterate_succ_apply, Option.bind_some, hstep] using ht

/-- Finite control of the concrete local multitape implementation. -/
abbrev Control (M : Λ → TM2.Stmt Γ Λ σ) := TM2Compiler.Control (flattenProgram M)

noncomputable def compile (M : Λ → TM2.Stmt Γ Λ σ) :
    MultitapeToolkit.Machine K (Option (Common Γ)) (Control M) :=
  TM2Compiler.compile (flattenProgram M)

noncomputable def encode (M : Λ → TM2.Stmt Γ Λ σ) (c : TM2.Cfg Γ Λ σ) :
    MultitapeToolkit.Config K (Option (Common Γ)) (Control M) :=
  TM2Compiler.encode (flattenProgram M) (flattenCfg c)

noncomputable def overhead (M : Λ → TM2.Stmt Γ Λ σ) : Nat :=
  2 * Finset.univ.sup (fun l => depth (M l))

theorem overhead_flattenProgram (M : Λ → TM2.Stmt Γ Λ σ) :
    TM2Compiler.overhead (flattenProgram M) = overhead M := by
  simp [TM2Compiler.overhead, overhead, flattenProgram, depth_flattenStmt]

/-- Universal constructive constant-overhead compilation for finite heterogeneous stack alphabets. -/
theorem compile_run (M : Λ → TM2.Stmt Γ Λ σ) (n : Nat) (c d : TM2.Cfg Γ Λ σ)
    (h : ((fun s : Option (TM2.Cfg Γ Λ σ) => s.bind (TM2.step M))^[n])
      (some c) = some d) :
    MultitapeToolkit.RunsWithin (compile M) (overhead M * n) (encode M c) (encode M d) := by
  have hr := TM2Compiler.compile_run (flattenProgram M) n (flattenCfg c) (flattenCfg d)
    (flatten_run M n c d h)
  simpa only [compile, encode, overhead_flattenProgram] using hr

/-- A halted source configuration is implemented by a genuinely halted multitape configuration. -/
theorem encode_halts (M : Λ → TM2.Stmt Γ Λ σ) (v : σ) (S : ∀ k, List (Γ k)) :
    MultitapeToolkit.Halts (compile M) (encode M ⟨none, v, S⟩) := by
  exact TM2Compiler.encode_halts (flattenProgram M) v (flattenStacks S)

/-- The actual tape contains exactly the source list with its fixed stack tag. -/
theorem read_output (M : Λ → TM2.Stmt Γ Λ σ) (c : TM2.Cfg Γ Λ σ) (k : K) :
    MultitapeToolkit.readStack (c.stk k).length ((encode M c).tapes k) =
      (c.stk k).map (tagged k) := by
  simpa only [encode, flattenCfg, flattenStacks, List.length_map] using
    TM2Compiler.read_output (flattenProgram M) (flattenCfg c) k

/-- A fixed finite output-symbol relabeling recovers the original heterogeneous output. -/
theorem decode_output (M : Λ → TM2.Stmt Γ Λ σ) (c : TM2.Cfg Γ Λ σ) (k : K) :
    (MultitapeToolkit.readStack (c.stk k).length ((encode M c).tapes k)).filterMap (decode k) =
      c.stk k := by
  rw [read_output, decode_list]

end MultitapeToolkit.TM2HeterogeneousCompiler


