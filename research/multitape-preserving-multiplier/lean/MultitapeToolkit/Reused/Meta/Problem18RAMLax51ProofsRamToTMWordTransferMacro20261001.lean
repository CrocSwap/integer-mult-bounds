import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSparseParsing20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure WordTransferControl where
  held : Option SparseSymbol
  deriving DecidableEq, Fintype, Inhabited

inductive WordTransferStack | source | bits | backup
  deriving DecidableEq, Fintype, Inhabited

inductive WordTransferLabel | loop | done
  deriving DecidableEq, Fintype, Inhabited

def wordTransferIteration {K Λ : Type} [DecidableEq K]
    (source bits backup : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ WordTransferControl :=
  .pop source (fun s a => { s with held := a }) <|
    .branch (fun s => s.held = some .wordEnd)
      (.push backup (fun _ => .wordEnd) <|
        .load (fun _ => default) <| .goto fun _ => done)
      (.push bits (fun s => s.held.getD (.bit false)) <|
        .push backup (fun s => s.held.getD (.bit false)) <|
          .load (fun _ => default) <| .goto fun _ => loop)

def wordTransferMachine : Turing.FinTM2 where
  K := WordTransferStack
  k₀ := .source
  k₁ := .bits
  Γ _ := SparseSymbol
  Λ := WordTransferLabel
  main := .loop
  σ := WordTransferControl
  initialState := default
  m
    | .loop => wordTransferIteration .source .bits .backup .loop .done
    | .done => .halt

def wordTransferStacks (source bits backup : List SparseSymbol) :
    WordTransferStack → List SparseSymbol
  | .source => source
  | .bits => bits
  | .backup => backup

def wordTransferCfg (source bits backup : List SparseSymbol) :
    wordTransferMachine.Cfg where
  l := some .loop
  var := default
  stk := wordTransferStacks source bits backup

def wordTransferDoneCfg (source bits backup : List SparseSymbol) :
    wordTransferMachine.Cfg where
  l := some .done
  var := default
  stk := wordTransferStacks source bits backup

@[simp] theorem wordTransfer_step_bit (b : Bool) (source bits backup : List SparseSymbol) :
    wordTransferMachine.step
        (wordTransferCfg (.bit b :: source) bits backup) =
      some (wordTransferCfg source (.bit b :: bits) (.bit b :: backup)) := by
  change some (TM2.stepAux
    (wordTransferIteration WordTransferStack.source WordTransferStack.bits
      WordTransferStack.backup WordTransferLabel.loop WordTransferLabel.done)
    default (wordTransferStacks (.bit b :: source) bits backup)) = _
  simp [wordTransferIteration, wordTransferCfg, wordTransferStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem wordTransfer_step_end (source bits backup : List SparseSymbol) :
    wordTransferMachine.step
        (wordTransferCfg (.wordEnd :: source) bits backup) =
      some (wordTransferDoneCfg source bits (.wordEnd :: backup)) := by
  change some (TM2.stepAux
    (wordTransferIteration WordTransferStack.source WordTransferStack.bits
      WordTransferStack.backup WordTransferLabel.loop WordTransferLabel.done)
    default (wordTransferStacks (.wordEnd :: source) bits backup)) = _
  simp [wordTransferIteration, wordTransferDoneCfg, wordTransferStacks,
    Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem wordTransfer_bits_iterate (xs : List Bool)
    (suffix bits backup : List SparseSymbol) :
    ((fun o : Option wordTransferMachine.Cfg => o.bind wordTransferMachine.step)^[xs.length])
        (some (wordTransferCfg
          (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) bits backup)) =
      some (wordTransferCfg (.wordEnd :: suffix)
        (xs.reverse.map SparseSymbol.bit ++ bits)
        (xs.reverse.map SparseSymbol.bit ++ backup)) := by
  induction xs generalizing bits backup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        wordTransfer_step_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem wordTransfer_reaches_done (xs : List Bool)
    (suffix bits backup : List SparseSymbol) :
    ((fun o : Option wordTransferMachine.Cfg => o.bind wordTransferMachine.step)^[xs.length + 1])
        (some (wordTransferCfg
          (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) bits backup)) =
      some (wordTransferDoneCfg suffix
        (xs.reverse.map SparseSymbol.bit ++ bits)
        (.wordEnd :: xs.reverse.map SparseSymbol.bit ++ backup)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    wordTransfer_bits_iterate xs suffix bits backup]
  simp only [Function.iterate_one, Option.bind_some, wordTransfer_step_end]
  rfl

theorem wordTransfer_fixed_correct (w n : ℕ)
    (suffix bits backup : List SparseSymbol) :
    ((fun o : Option wordTransferMachine.Cfg => o.bind wordTransferMachine.step)^[w + 1])
        (some (wordTransferCfg (encodeFixedWord w n ++ suffix) bits backup)) =
      some (wordTransferDoneCfg suffix
        ((fixedBits w n).reverse.map SparseSymbol.bit ++ bits)
        (.wordEnd :: (fixedBits w n).reverse.map SparseSymbol.bit ++ backup)) := by
  simpa [encodeFixedWord] using
    wordTransfer_reaches_done (fixedBits w n) suffix bits backup

end Lax51Proofs.RamToTM
