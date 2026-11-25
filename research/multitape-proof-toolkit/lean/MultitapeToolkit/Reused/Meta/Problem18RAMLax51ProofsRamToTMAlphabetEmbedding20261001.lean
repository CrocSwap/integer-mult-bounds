import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMStatementEmbedding20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

/-! Transport a TM2 statement across a split injection/retraction of its
alphabet.  Correct executions only see encoded symbols; the retraction makes
the transported statement total on arbitrary ambient configurations. -/

def mapAlphabetStmt {α β K Λ σ : Type} [DecidableEq K]
    (encode : α → β) (decode : β → α) :
    TM2.Stmt (fun _ : K => α) Λ σ → TM2.Stmt (fun _ : K => β) Λ σ
  | .push k f q => .push k (fun s => encode (f s))
      (mapAlphabetStmt encode decode q)
  | .peek k f q => .peek k (fun s a => f s (a.map decode))
      (mapAlphabetStmt encode decode q)
  | .pop k f q => .pop k (fun s a => f s (a.map decode))
      (mapAlphabetStmt encode decode q)
  | .load f q => .load f (mapAlphabetStmt encode decode q)
  | .branch f q₁ q₂ => .branch f
      (mapAlphabetStmt encode decode q₁) (mapAlphabetStmt encode decode q₂)
  | .goto f => .goto f
  | .halt => .halt

def mapAlphabetStacks {α β K : Type} (encode : α → β)
    (stk : K → List α) : K → List β :=
  fun k => (stk k).map encode

def mapAlphabetCfg {α β K Λ σ : Type} (encode : α → β)
    (c : TM2.Cfg (fun _ : K => α) Λ σ) :
    TM2.Cfg (fun _ : K => β) Λ σ where
  l := c.l
  var := c.var
  stk := mapAlphabetStacks encode c.stk

theorem update_mapAlphabetStacks {α β K : Type} [DecidableEq K]
    (encode : α → β) (stk : K → List α) (k : K) (xs : List α) :
    Function.update (mapAlphabetStacks encode stk) k (xs.map encode) =
      mapAlphabetStacks encode (Function.update stk k xs) := by
  funext j
  by_cases h : j = k
  · subst j; simp [mapAlphabetStacks]
  · simp [mapAlphabetStacks, h]

theorem stepAux_mapAlphabetStmt {α β K Λ σ : Type} [DecidableEq K]
    (encode : α → β) (decode : β → α)
    (hleft : ∀ a, decode (encode a) = a)
    (q : TM2.Stmt (fun _ : K => α) Λ σ) (v : σ)
    (stk : K → List α) :
    TM2.stepAux (mapAlphabetStmt encode decode q) v
        (mapAlphabetStacks encode stk) =
      mapAlphabetCfg encode (TM2.stepAux q v stk) := by
  induction q generalizing v stk with
  | push k f q ih =>
      simp only [mapAlphabetStmt, TM2.stepAux]
      change TM2.stepAux (mapAlphabetStmt encode decode q) v
          (Function.update (mapAlphabetStacks encode stk) k
            ((f v :: stk k).map encode)) = _
      rw [update_mapAlphabetStacks]
      exact ih v (Function.update stk k (f v :: stk k))
  | peek k f q ih =>
      simp only [mapAlphabetStmt, TM2.stepAux, mapAlphabetStacks]
      rw [List.head?_map]
      simp only [Option.map_map]
      have hmap : (stk k).head?.map (decode ∘ encode) = (stk k).head? := by
        cases (stk k).head? <;> simp [hleft]
      rw [hmap]
      exact ih (f v (stk k).head?) stk
  | pop k f q ih =>
      simp only [mapAlphabetStmt, TM2.stepAux, mapAlphabetStacks]
      rw [List.head?_map]
      simp only [Option.map_map]
      have hmap : (stk k).head?.map (decode ∘ encode) = (stk k).head? := by
        cases (stk k).head? <;> simp [hleft]
      rw [hmap]
      rw [show ((stk k).map encode).tail = (stk k).tail.map encode by
        cases stk k <;> rfl]
      rw [update_mapAlphabetStacks]
      exact ih (f v (stk k).head?)
        (Function.update stk k (stk k).tail)
  | load f q ih =>
      simp only [mapAlphabetStmt, TM2.stepAux]
      exact ih (f v) stk
  | branch f q₁ q₂ ih₁ ih₂ =>
      simp only [mapAlphabetStmt, TM2.stepAux]
      cases h : f v <;> simp
      · exact ih₂ v stk
      · exact ih₁ v stk
  | goto f => rfl
  | halt => rfl

def mapAlphabetProgram {α β K Λ σ : Type} [DecidableEq K]
    (encode : α → β) (decode : β → α)
    (program : Λ → TM2.Stmt (fun _ : K => α) Λ σ) :
    Λ → TM2.Stmt (fun _ : K => β) Λ σ :=
  fun l => mapAlphabetStmt encode decode (program l)

theorem step_mapAlphabetProgram {α β K Λ σ : Type} [DecidableEq K]
    (encode : α → β) (decode : β → α)
    (hleft : ∀ a, decode (encode a) = a)
    (program : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    (c : TM2.Cfg (fun _ : K => α) Λ σ) :
    TM2.step (mapAlphabetProgram encode decode program) (mapAlphabetCfg encode c) =
      (TM2.step program c).map (mapAlphabetCfg encode) := by
  cases c with
  | mk label v stk =>
      cases label with
      | none => rfl
      | some label =>
          simp only [mapAlphabetCfg, TM2.step, mapAlphabetProgram, Option.map_some]
          rw [stepAux_mapAlphabetStmt encode decode hleft]
          rfl

theorem iterate_mapAlphabetProgram {α β K Λ σ : Type} [DecidableEq K]
    (encode : α → β) (decode : β → α)
    (hleft : ∀ a, decode (encode a) = a)
    (program : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    (n : ℕ) (c : TM2.Cfg (fun _ : K => α) Λ σ) :
    ((fun o => o.bind (TM2.step (mapAlphabetProgram encode decode program)))^[n])
        (some (mapAlphabetCfg encode c)) =
      (((fun o => o.bind (TM2.step program))^[n]) (some c)).map
        (mapAlphabetCfg encode) := by
  induction n generalizing c with
  | zero => rfl
  | succ n ih =>
      rw [Function.iterate_succ_apply, Function.iterate_succ_apply]
      simp only [Option.bind_some, step_mapAlphabetProgram encode decode hleft]
      cases h : TM2.step program c with
      | none =>
          simp only [Option.map_none]
          rw [iterate_optionBind_none, iterate_optionBind_none]
          rfl
      | some c' =>
          simp only [Option.map_some, Option.bind_some]
          exact ih c'

theorem transport_iterate_mapAlphabetProgram {α β K Λ σ : Type} [DecidableEq K]
    (encode : α → β) (decode : β → α)
    (hleft : ∀ a, decode (encode a) = a)
    (program : Λ → TM2.Stmt (fun _ : K => α) Λ σ)
    {n : ℕ} {c d : TM2.Cfg (fun _ : K => α) Λ σ}
    (h : ((fun o => o.bind (TM2.step program))^[n]) (some c) = some d) :
    ((fun o => o.bind (TM2.step (mapAlphabetProgram encode decode program)))^[n])
        (some (mapAlphabetCfg encode c)) =
      some (mapAlphabetCfg encode d) := by
  rw [iterate_mapAlphabetProgram encode decode hleft]
  simp [h]

def sparseBitEncode (b : Bool) : SparseSymbol := .bit b

def sparseBitDecode : SparseSymbol → Bool
  | .bit b => b
  | _ => false

@[simp] theorem sparseBitDecode_encode (b : Bool) :
    sparseBitDecode (sparseBitEncode b) = b := rfl

end Lax51Proofs.RamToTM
