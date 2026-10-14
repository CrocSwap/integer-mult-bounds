import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSparseLookup20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

inductive CellTransferStack | source | address | value | backup
  deriving DecidableEq, Fintype, Inhabited

inductive CellTransferLabel | address | value | cellEnd | done
  deriving DecidableEq, Fintype, Inhabited

def cellWordIteration {K Λ : Type} [DecidableEq K]
    (source target backup : K) (loop next : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ WordTransferControl :=
  .pop source (fun s a => { s with held := a }) <|
    .branch (fun s => s.held = some .wordEnd)
      (.push backup (fun _ => .wordEnd) <|
        .load (fun _ => default) <| .goto fun _ => next)
      (.push target (fun s => s.held.getD (.bit false)) <|
        .push backup (fun s => s.held.getD (.bit false)) <|
          .load (fun _ => default) <| .goto fun _ => loop)

def cellTransferMachine : Turing.FinTM2 where
  K := CellTransferStack
  k₀ := .source
  k₁ := .value
  Γ _ := SparseSymbol
  Λ := CellTransferLabel
  main := .address
  σ := WordTransferControl
  initialState := default
  m
    | .address => cellWordIteration .source .address .backup .address .value
    | .value => cellWordIteration .source .value .backup .value .cellEnd
    | .cellEnd =>
        .pop .source (fun s a => { s with held := a }) <|
          .push .backup (fun s => s.held.getD .cellEnd) <|
            .load (fun _ => default) <| .goto fun _ => .done
    | .done => .halt

def cellTransferStacks (source address value backup : List SparseSymbol) :
    CellTransferStack → List SparseSymbol
  | .source => source
  | .address => address
  | .value => value
  | .backup => backup

def cellTransferCfg (label : CellTransferLabel)
    (source address value backup : List SparseSymbol) : cellTransferMachine.Cfg where
  l := some label
  var := default
  stk := cellTransferStacks source address value backup

@[simp] theorem cellTransfer_step_address_bit (b : Bool)
    (source address value backup : List SparseSymbol) :
    cellTransferMachine.step
        (cellTransferCfg .address (.bit b :: source) address value backup) =
      some (cellTransferCfg .address source (.bit b :: address) value
        (.bit b :: backup)) := by
  change some (TM2.stepAux
    (cellWordIteration CellTransferStack.source CellTransferStack.address
      CellTransferStack.backup CellTransferLabel.address CellTransferLabel.value)
    default (cellTransferStacks (.bit b :: source) address value backup)) = _
  simp [cellWordIteration, cellTransferCfg, cellTransferStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem cellTransfer_step_address_end
    (source address value backup : List SparseSymbol) :
    cellTransferMachine.step
        (cellTransferCfg .address (.wordEnd :: source) address value backup) =
      some (cellTransferCfg .value source address value (.wordEnd :: backup)) := by
  change some (TM2.stepAux
    (cellWordIteration CellTransferStack.source CellTransferStack.address
      CellTransferStack.backup CellTransferLabel.address CellTransferLabel.value)
    default (cellTransferStacks (.wordEnd :: source) address value backup)) = _
  simp [cellWordIteration, cellTransferCfg, cellTransferStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem cellTransfer_step_value_bit (b : Bool)
    (source address value backup : List SparseSymbol) :
    cellTransferMachine.step
        (cellTransferCfg .value (.bit b :: source) address value backup) =
      some (cellTransferCfg .value source address (.bit b :: value)
        (.bit b :: backup)) := by
  change some (TM2.stepAux
    (cellWordIteration CellTransferStack.source CellTransferStack.value
      CellTransferStack.backup CellTransferLabel.value CellTransferLabel.cellEnd)
    default (cellTransferStacks (.bit b :: source) address value backup)) = _
  simp [cellWordIteration, cellTransferCfg, cellTransferStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem cellTransfer_step_value_end
    (source address value backup : List SparseSymbol) :
    cellTransferMachine.step
        (cellTransferCfg .value (.wordEnd :: source) address value backup) =
      some (cellTransferCfg .cellEnd source address value (.wordEnd :: backup)) := by
  change some (TM2.stepAux
    (cellWordIteration CellTransferStack.source CellTransferStack.value
      CellTransferStack.backup CellTransferLabel.value CellTransferLabel.cellEnd)
    default (cellTransferStacks (.wordEnd :: source) address value backup)) = _
  simp [cellWordIteration, cellTransferCfg, cellTransferStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem cellTransfer_step_cell_end
    (source address value backup : List SparseSymbol) :
    cellTransferMachine.step
        (cellTransferCfg .cellEnd (.cellEnd :: source) address value backup) =
      some (cellTransferCfg .done source address value (.cellEnd :: backup)) := by
  change some (TM2.stepAux
    (.pop CellTransferStack.source (fun (s : WordTransferControl) a => { s with held := a }) <|
      .push CellTransferStack.backup (fun (s : WordTransferControl) => s.held.getD .cellEnd) <|
        .load (fun _ => default) <| .goto fun _ => CellTransferLabel.done)
    default (cellTransferStacks (.cellEnd :: source) address value backup)) = _
  simp [cellTransferCfg, cellTransferStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem cellTransfer_address_iterate (xs : List Bool)
    (suffix address value backup : List SparseSymbol) :
    ((fun o : Option cellTransferMachine.Cfg => o.bind cellTransferMachine.step)^[xs.length])
        (some (cellTransferCfg .address
          (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) address value backup)) =
      some (cellTransferCfg .address (.wordEnd :: suffix)
        (xs.reverse.map SparseSymbol.bit ++ address) value
        (xs.reverse.map SparseSymbol.bit ++ backup)) := by
  induction xs generalizing address backup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        cellTransfer_step_address_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem cellTransfer_value_iterate (xs : List Bool)
    (suffix address value backup : List SparseSymbol) :
    ((fun o : Option cellTransferMachine.Cfg => o.bind cellTransferMachine.step)^[xs.length])
        (some (cellTransferCfg .value
          (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) address value backup)) =
      some (cellTransferCfg .value (.wordEnd :: suffix) address
        (xs.reverse.map SparseSymbol.bit ++ value)
        (xs.reverse.map SparseSymbol.bit ++ backup)) := by
  induction xs generalizing value backup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        cellTransfer_step_value_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem cellTransfer_fixed_correct (w a v : ℕ)
    (suffix address value backup : List SparseSymbol) :
    ((fun o : Option cellTransferMachine.Cfg => o.bind cellTransferMachine.step)^[2 * w + 3])
        (some (cellTransferCfg .address
          (encodeSparseCell w (a, v) ++ suffix) address value backup)) =
      some (cellTransferCfg .done suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
          .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)) := by
  let stepO := fun o : Option cellTransferMachine.Cfg => o.bind cellTransferMachine.step
  have haRun := cellTransfer_address_iterate (fixedBits w a)
    (encodeFixedWord w v ++ .cellEnd :: suffix) address value backup
  have haEnd : (stepO^[1])
      (some (cellTransferCfg .address
        (.wordEnd :: (encodeFixedWord w v ++ .cellEnd :: suffix))
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address) value
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ backup))) =
      some (cellTransferCfg .value
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address) value
        (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)) := by
    simpa [stepO, List.map_reverse] using
      cellTransfer_step_address_end
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address) value
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ backup)
  have hvRun := cellTransfer_value_iterate (fixedBits w v) (.cellEnd :: suffix)
    ((fixedBits w a).reverse.map SparseSymbol.bit ++ address) value
    (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)
  have hvEnd : (stepO^[1])
      (some (cellTransferCfg .value (.wordEnd :: (.cellEnd :: suffix))
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)))) =
      some (cellTransferCfg .cellEnd (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)))) := by
    simpa [stepO, List.map_reverse] using
      cellTransfer_step_value_end (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup))
  have hcEnd : (stepO^[1])
      (some (cellTransferCfg .cellEnd (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup))))) =
      some (cellTransferCfg .done suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        (.cellEnd :: .wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)))) := by
    simpa [stepO, List.map_reverse] using
      cellTransfer_step_cell_end suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup)))
  simp only [fixedBits_length] at haRun hvRun
  have chain {m n : ℕ} {x y z : Option cellTransferMachine.Cfg}
      (h₁ : (stepO^[m]) x = y) (h₂ : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, h₁, h₂]
  have h01 := chain haRun haEnd
  have hvRun' : (stepO^[w])
      (some (cellTransferCfg .value (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address) value
        (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup))) =
      some (cellTransferCfg .value (.wordEnd :: .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit ++ address)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++ value)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit ++ backup))) := by
    simpa [stepO, encodeFixedWord, List.append_assoc] using hvRun
  have h02 := chain h01 hvRun'
  have h03 := chain h02 hvEnd
  have h04 := chain h03 hcEnd
  dsimp [stepO] at h04
  have hexp : 1 + (1 + (w + (1 + w))) = 2 * w + 3 := by omega
  rw [hexp] at h04
  simpa [encodeSparseCell, encodeFixedWord, List.append_assoc] using h04

end Lax51Proofs.RamToTM
