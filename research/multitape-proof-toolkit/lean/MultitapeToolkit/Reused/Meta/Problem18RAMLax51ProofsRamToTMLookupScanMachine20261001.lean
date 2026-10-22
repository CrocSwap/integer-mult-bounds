import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSparseRunBounds20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

inductive LookupScanStack
  | source | address | value | cellBackup | query | addressBackup | queryBackup
  | processed | trash
  deriving DecidableEq, Fintype, Inhabited

inductive LookupScanLabel
  | scan | address | value | cellEnd | compare | decide
  | restoreQuery | discardAddress | discardValue | preserveCell | moveCell
  | afterCleanup | afterMove
  | restoreFound | restoreMissing | found | missing
  deriving DecidableEq, Fintype, Inhabited

def lookupScanMoveIteration {K Λ : Type} [DecidableEq K]
    (source target : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ LookupCellControl :=
  .pop source (fun s a => { s with held := a }) <|
    .branch (fun s => s.held.isNone)
      (.load LookupCellControl.clearHeld <| .goto fun _ => done)
      (.push target (fun s => s.held.getD (.bit false)) <|
        .load LookupCellControl.clearHeld <| .goto fun _ => loop)

def lookupScanDiscardIteration {K Λ : Type} [DecidableEq K]
    (source : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ LookupCellControl :=
  .pop source (fun s a => { s with held := a }) <|
    .branch (fun s => s.held.isNone)
      (.load LookupCellControl.clearHeld <| .goto fun _ => done)
      (.load LookupCellControl.clearHeld <| .goto fun _ => loop)

def lookupScanMachine : Turing.FinTM2 where
  K := LookupScanStack
  k₀ := .source
  k₁ := .value
  Γ _ := SparseSymbol
  Λ := LookupScanLabel
  main := .scan
  σ := LookupCellControl
  initialState := ⟨none, true, none, none⟩
  m
    | .scan =>
        .peek .source (fun s a => { s with held := a }) <|
          .branch (fun s => s.held = some .memoryEnd)
            (.load LookupCellControl.clearHeld <| .goto fun _ => .restoreMissing)
            (.load (fun s => { (LookupCellControl.clearHeld s) with equal := true }) <|
              .goto fun _ => .address)
    | .address => lookupCellWordIteration .source .address .cellBackup .address .value
    | .value => lookupCellWordIteration .source .value .cellBackup .value .cellEnd
    | .cellEnd =>
        .pop .source (fun s a => { s with held := a }) <|
          .push .cellBackup (fun s => s.held.getD .cellEnd) <|
            .load LookupCellControl.clearHeld <| .goto fun _ => .compare
    | .compare => lookupCellCompareIteration .address .query
        .addressBackup .queryBackup .compare .decide
    | .decide => .branch LookupCellControl.equal
        (.goto fun _ => .restoreQuery) (.goto fun _ => .restoreQuery)
    | .restoreQuery => lookupScanMoveIteration .queryBackup .query
        .restoreQuery .discardAddress
    | .discardAddress => lookupScanDiscardIteration .addressBackup
        .discardAddress .afterCleanup
    | .afterCleanup => .branch LookupCellControl.equal
        (.goto fun _ => .preserveCell) (.goto fun _ => .discardValue)
    | .discardValue => lookupScanDiscardIteration .value .discardValue .preserveCell
    | .preserveCell => lookupScanMoveIteration .cellBackup .trash
        .preserveCell .moveCell
    | .moveCell => lookupScanMoveIteration .trash .processed .moveCell .afterMove
    | .afterMove => .branch LookupCellControl.equal
        (.goto fun _ => .restoreFound) (.goto fun _ => .scan)
    | .restoreFound => lookupScanMoveIteration .processed .source .restoreFound .found
    | .restoreMissing => lookupScanMoveIteration .processed .source .restoreMissing .missing
    | .found => .halt
    | .missing => .halt

def lookupScanStacks (source address value cellBackup query addressBackup queryBackup
    processed trash : List SparseSymbol) : LookupScanStack → List SparseSymbol
  | .source => source
  | .address => address
  | .value => value
  | .cellBackup => cellBackup
  | .query => query
  | .addressBackup => addressBackup
  | .queryBackup => queryBackup
  | .processed => processed
  | .trash => trash

def lookupScanCfg (label : LookupScanLabel) (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) : lookupScanMachine.Cfg where
  l := some label
  var := ⟨none, equal, none, none⟩
  stk := lookupScanStacks source address value cellBackup query addressBackup queryBackup
    processed trash

@[simp] theorem lookupScan_step_empty_memory (equal : Bool)
    (address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .scan equal [.memoryEnd] address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .restoreMissing equal [.memoryEnd] address value cellBackup
      query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (.peek LookupScanStack.source
      (fun s a => { s with held := a }) <|
      .branch (fun s => s.held = some SparseSymbol.memoryEnd)
        (.load LookupCellControl.clearHeld <| .goto fun _ => LookupScanLabel.restoreMissing)
        (.load (fun s => { (LookupCellControl.clearHeld s) with equal := true }) <|
          .goto fun _ => LookupScanLabel.address))
    ⟨none, equal, none, none⟩
    (lookupScanStacks [.memoryEnd] address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [LookupCellControl.clearHeld, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

@[simp] theorem lookupScan_step_nonempty (equal : Bool) (b : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .scan equal (.bit b :: source) address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .address true (.bit b :: source) address value cellBackup
      query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (.peek LookupScanStack.source
      (fun s a => { s with held := a }) <|
      .branch (fun s => s.held = some SparseSymbol.memoryEnd)
        (.load LookupCellControl.clearHeld <| .goto fun _ => LookupScanLabel.restoreMissing)
        (.load (fun s => { (LookupCellControl.clearHeld s) with equal := true }) <|
          .goto fun _ => LookupScanLabel.address))
    ⟨none, equal, none, none⟩
    (lookupScanStacks (.bit b :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [LookupCellControl.clearHeld, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

theorem lookupScan_step_cell_start (equal : Bool) (a : SparseSymbol)
    (ha : a ≠ .memoryEnd)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .scan equal (a :: source) address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .address true (a :: source) address value cellBackup query
      addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (.peek LookupScanStack.source (fun s a => { s with held := a }) <|
      .branch (fun s => s.held = some SparseSymbol.memoryEnd)
        (.load LookupCellControl.clearHeld <| .goto fun _ => LookupScanLabel.restoreMissing)
        (.load (fun s => { (LookupCellControl.clearHeld s) with equal := true }) <|
          .goto fun _ => LookupScanLabel.address))
    ⟨none, equal, none, none⟩
    (lookupScanStacks (a :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [ha, LookupCellControl.clearHeld, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

theorem lookupScan_step_encoded_cell (equal : Bool) (w a v : ℕ)
    (suffix address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .scan equal
      (encodeSparseCell w (a, v) ++ suffix) address value cellBackup query addressBackup
      queryBackup processed trash) =
    some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix) address
      value cellBackup query addressBackup queryBackup processed trash) := by
  cases w with
  | zero =>
      simpa [encodeSparseCell, encodeFixedWord, fixedBits] using
        lookupScan_step_cell_start equal SparseSymbol.wordEnd (by simp)
          (encodeFixedWord 0 v ++ .cellEnd :: suffix) address value cellBackup query
          addressBackup queryBackup processed trash
  | succ w =>
      simpa [encodeSparseCell, encodeFixedWord, fixedBits] using
        lookupScan_step_cell_start equal (.bit a.bodd) (by simp)
          ((fixedBits w a.div2).map SparseSymbol.bit ++ .wordEnd ::
            (encodeFixedWord (w + 1) v ++ .cellEnd :: suffix))
          address value cellBackup query addressBackup queryBackup processed trash

@[simp] theorem lookupScan_step_address_bit (equal : Bool) (b : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .address equal (.bit b :: source) address
      value cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .address equal source (.bit b :: address) value
      (.bit b :: cellBackup) query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupScanStack.source LookupScanStack.address
      LookupScanStack.cellBackup LookupScanLabel.address LookupScanLabel.value)
    ⟨none, equal, none, none⟩
    (lookupScanStacks (.bit b :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_address_end (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .address equal (.wordEnd :: source) address
      value cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .value equal source address value (.wordEnd :: cellBackup)
      query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupScanStack.source LookupScanStack.address
      LookupScanStack.cellBackup LookupScanLabel.address LookupScanLabel.value)
    ⟨none, equal, none, none⟩
    (lookupScanStacks (.wordEnd :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_value_bit (equal : Bool) (b : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .value equal (.bit b :: source) address
      value cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .value equal source address (.bit b :: value)
      (.bit b :: cellBackup) query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupScanStack.source LookupScanStack.value
      LookupScanStack.cellBackup LookupScanLabel.value LookupScanLabel.cellEnd)
    ⟨none, equal, none, none⟩
    (lookupScanStacks (.bit b :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_value_end (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .value equal (.wordEnd :: source) address
      value cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .cellEnd equal source address value (.wordEnd :: cellBackup)
      query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupScanStack.source LookupScanStack.value
      LookupScanStack.cellBackup LookupScanLabel.value LookupScanLabel.cellEnd)
    ⟨none, equal, none, none⟩
    (lookupScanStacks (.wordEnd :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_cellEnd (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .cellEnd equal (.cellEnd :: source) address
      value cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .compare equal source address value (.cellEnd :: cellBackup)
      query addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (.pop LookupScanStack.source (fun s a => { s with held := a }) <|
      .push LookupScanStack.cellBackup (fun s => s.held.getD .cellEnd) <|
        .load LookupCellControl.clearHeld <| .goto fun _ => LookupScanLabel.compare)
    ⟨none, equal, none, none⟩
    (lookupScanStacks (.cellEnd :: source) address value cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [LookupCellControl.clearHeld, lookupScanCfg, lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_compare_cons (equal : Bool) (a b : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .compare equal source (a :: address) value
      cellBackup (b :: query) addressBackup queryBackup processed trash) =
    some (lookupScanCfg .compare (equal && decide (a = b)) source address value
      cellBackup query (a :: addressBackup) (b :: queryBackup) processed trash) := by
  change some (TM2.stepAux
    (lookupCellCompareIteration LookupScanStack.address LookupScanStack.query
      LookupScanStack.addressBackup LookupScanStack.queryBackup LookupScanLabel.compare
      LookupScanLabel.decide)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source (a :: address) value cellBackup (b :: query)
      addressBackup queryBackup processed trash)) = _
  simp [lookupCellCompareIteration, LookupCellControl.compareAdvance, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_compare_nil (equal : Bool)
    (source value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .compare equal source [] value cellBackup
      query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .decide equal source [] value cellBackup query addressBackup
      queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupCellCompareIteration LookupScanStack.address LookupScanStack.query
      LookupScanStack.addressBackup LookupScanStack.queryBackup LookupScanLabel.compare
      LookupScanLabel.decide)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source [] value cellBackup query addressBackup queryBackup
      processed trash)) = _
  simp [lookupCellCompareIteration, lookupScanCfg, lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_address_iterate (equal : Bool) (xs : List Bool)
    (suffix address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[xs.length])
      (some (lookupScanCfg .address equal
        (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .address equal (.wordEnd :: suffix)
      (xs.reverse.map SparseSymbol.bit ++ address) value
      (xs.reverse.map SparseSymbol.bit ++ cellBackup) query addressBackup queryBackup
      processed trash) := by
  induction xs generalizing address cellBackup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        lookupScan_step_address_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem lookupScan_value_iterate (equal : Bool) (xs : List Bool)
    (suffix address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[xs.length])
      (some (lookupScanCfg .value equal
        (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .value equal (.wordEnd :: suffix) address
      (xs.reverse.map SparseSymbol.bit ++ value)
      (xs.reverse.map SparseSymbol.bit ++ cellBackup) query addressBackup queryBackup
      processed trash) := by
  induction xs generalizing value cellBackup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        lookupScan_step_value_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem lookupScan_compare_iterate (equal : Bool)
    (address query source value cellBackup addressBackup queryBackup processed trash :
      List SparseSymbol) (hlen : address.length = query.length) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      address.length])
      (some (lookupScanCfg .compare equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .compare (symbolsEqual address query equal) source [] value
      cellBackup [] (address.reverse ++ addressBackup) (query.reverse ++ queryBackup)
      processed trash) := by
  induction address generalizing query equal addressBackup queryBackup with
  | nil =>
      cases query with
      | nil => rfl
      | cons q query => simp at hlen
  | cons a address ih =>
      cases query with
      | nil => simp at hlen
      | cons b query =>
        simp at hlen
        rw [List.length_cons, Function.iterate_succ_apply]
        simp only [Option.bind_some, lookupScan_step_compare_cons]
        rw [ih (query := query) (equal := equal && decide (a = b))
          (addressBackup := a :: addressBackup)
          (queryBackup := b :: queryBackup) hlen]
        simp [symbolsEqual, List.reverse_cons, List.append_assoc]

theorem lookupScan_compare_reaches_decide (equal : Bool)
    (address query source value cellBackup addressBackup queryBackup processed trash :
      List SparseSymbol) (hlen : address.length = query.length) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      address.length + 1])
      (some (lookupScanCfg .compare equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .decide (symbolsEqual address query equal) source [] value
      cellBackup [] (address.reverse ++ addressBackup) (query.reverse ++ queryBackup)
      processed trash) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    lookupScan_compare_iterate equal address query source value cellBackup
      addressBackup queryBackup processed trash hlen]
  simp only [Function.iterate_one, Option.bind_some, lookupScan_step_compare_nil]

theorem lookupScan_parse_fixed (equal : Bool) (w a v : ℕ)
    (suffix query processed trash : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      2 * w + 3])
      (some (lookupScanCfg .address equal (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] query [] [] processed trash)) =
    some (lookupScanCfg .compare equal suffix
      ((fixedBits w a).reverse.map SparseSymbol.bit)
      ((fixedBits w v).reverse.map SparseSymbol.bit)
      (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
        .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)
      query [] [] processed trash) := by
  let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
  have haRun := lookupScan_address_iterate equal (fixedBits w a)
    (encodeFixedWord w v ++ .cellEnd :: suffix) [] [] [] query [] [] processed trash
  have haEnd : (stepO^[1])
      (some (lookupScanCfg .address equal
        (.wordEnd :: (encodeFixedWord w v ++ .cellEnd :: suffix))
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        ((fixedBits w a).reverse.map SparseSymbol.bit) query [] [] processed trash)) =
      some (lookupScanCfg .value equal
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) query [] []
        processed trash) := by
    simpa [stepO, List.map_reverse] using
      lookupScan_step_address_end equal
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        ((fixedBits w a).reverse.map SparseSymbol.bit) query [] [] processed trash
  have hvRun := lookupScan_value_iterate equal (fixedBits w v) (.cellEnd :: suffix)
    ((fixedBits w a).reverse.map SparseSymbol.bit) []
    (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) query [] [] processed trash
  have hvRun' : (stepO^[w])
      (some (lookupScanCfg .value equal
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) query [] []
        processed trash)) =
      some (lookupScanCfg .value equal (.wordEnd :: .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)) query [] []
        processed trash) := by
    simpa [stepO, encodeFixedWord, List.append_assoc] using hvRun
  have hvEnd : (stepO^[1])
      (some (lookupScanCfg .value equal (.wordEnd :: .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)) query [] []
        processed trash)) =
      some (lookupScanCfg .cellEnd equal (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []
        processed trash) := by
    simpa [stepO, List.map_reverse] using
      lookupScan_step_value_end equal (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)) query [] []
        processed trash
  have hcEnd : (stepO^[1])
      (some (lookupScanCfg .cellEnd equal (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []
        processed trash)) =
      some (lookupScanCfg .compare equal suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.cellEnd :: .wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []
        processed trash) := by
    simpa [stepO, List.map_reverse] using
      lookupScan_step_cellEnd equal suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []
        processed trash
  simp only [fixedBits_length, List.append_nil] at haRun hvRun
  have chain {m n : ℕ} {x y z : Option lookupScanMachine.Cfg}
      (h₁ : (stepO^[m]) x = y) (h₂ : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, h₁, h₂]
  have hrun := chain (chain (chain (chain haRun haEnd) hvRun') hvEnd) hcEnd
  have hexp : 1 + (1 + (w + (1 + w))) = 2 * w + 3 := by omega
  rw [hexp] at hrun
  simpa [stepO, encodeSparseCell, encodeFixedWord, List.append_assoc] using hrun

theorem lookupScan_fixed_reaches_decide (w a v query : ℕ)
    (ha : a < 2 ^ w) (hq : query < 2 ^ w)
    (suffix processed trash : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      3 * w + 4])
      (some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] []
        processed trash)) =
    some (lookupScanCfg .decide (decide (a = query)) suffix []
      ((fixedBits w v).reverse.map SparseSymbol.bit)
      (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
        .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)
      [] ((fixedBits w a).map SparseSymbol.bit)
      ((fixedBits w query).map SparseSymbol.bit) processed trash) := by
  let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
  have hparse := lookupScan_parse_fixed true w a v suffix
    ((fixedBits w query).reverse.map SparseSymbol.bit) processed trash
  have hcompare := lookupScan_compare_reaches_decide true
    ((fixedBits w a).reverse.map SparseSymbol.bit)
    ((fixedBits w query).reverse.map SparseSymbol.bit) suffix
    ((fixedBits w v).reverse.map SparseSymbol.bit)
    (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
      .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) [] [] processed trash
    (by simp)
  simp only [List.length_map, List.length_reverse, fixedBits_length] at hcompare
  have chain {m n : ℕ} {x y z : Option lookupScanMachine.Cfg}
      (h₁ : (stepO^[m]) x = y) (h₂ : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, h₁, h₂]
  have hrun := chain hparse hcompare
  have hexp : (w + 1) + (2 * w + 3) = 3 * w + 4 := by omega
  rw [hexp] at hrun
  change (stepO^[3 * w + 4])
      (some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] []
        processed trash)) = _
  rw [hrun, symbolsEqual_true_of_length _ _ (by simp)]
  have heq :
      decide ((fixedBits w a).reverse.map SparseSymbol.bit =
        (fixedBits w query).reverse.map SparseSymbol.bit) = decide (a = query) := by
    by_cases h : a = query
    · subst query
      simp
    · have hplain : ¬((fixedBits w a).map SparseSymbol.bit =
          (fixedBits w query).map SparseSymbol.bit) := by
        intro hm
        apply h
        have hv := congrArg (List.map SparseSymbol.bitValue) hm
        have hfun : SparseSymbol.bitValue ∘ SparseSymbol.bit = id := by
          funext bit
          cases bit <;> rfl
        have hbits : fixedBits w a = fixedBits w query := by
          simpa only [List.map_map, hfun, List.map_id] using hv
        have hvalues := congrArg bitsValue hbits
        simpa [bitsValue_fixedBits_of_lt ha, bitsValue_fixedBits_of_lt hq] using hvalues
      simp [h, hplain]
  rw [heq]
  simp

@[simp] theorem lookupScan_step_preserveCell_nil (equal : Bool)
    (source address value query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .preserveCell equal source address value []
      query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .moveCell equal source address value [] query addressBackup
      queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.cellBackup LookupScanStack.trash
      LookupScanLabel.preserveCell LookupScanLabel.moveCell)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value [] query addressBackup queryBackup processed
      trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_preserveCell_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .preserveCell equal source address value
      (a :: cellBackup) query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .preserveCell equal source address value cellBackup query
      addressBackup queryBackup processed (a :: trash)) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.cellBackup LookupScanStack.trash
      LookupScanLabel.preserveCell LookupScanLabel.moveCell)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value (a :: cellBackup) query addressBackup
      queryBackup processed trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_preserveCell_reaches_moveCell (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      cellBackup.length + 1])
      (some (lookupScanCfg .preserveCell equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .moveCell equal source address value [] query addressBackup
      queryBackup processed (cellBackup.reverse ++ trash)) := by
  induction cellBackup generalizing trash with
  | nil =>
      simp only [List.length_nil, Nat.zero_add, Function.iterate_one,
        Option.bind_some, lookupScan_step_preserveCell_nil, List.reverse_nil,
        List.nil_append]
  | cons a cellBackup ih =>
      rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_preserveCell_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

@[simp] theorem lookupScan_step_moveCell_nil (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .moveCell equal source address value cellBackup
      query addressBackup queryBackup processed []) =
    some (lookupScanCfg .afterMove equal source address value cellBackup query
      addressBackup queryBackup processed []) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.trash LookupScanStack.processed
      LookupScanLabel.moveCell LookupScanLabel.afterMove)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup queryBackup
      processed [])) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_moveCell_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .moveCell equal source address value
      cellBackup query addressBackup queryBackup processed (a :: trash)) =
    some (lookupScanCfg .moveCell equal source address value cellBackup query
      addressBackup queryBackup (a :: processed) trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.trash LookupScanStack.processed
      LookupScanLabel.moveCell LookupScanLabel.afterMove)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup
      queryBackup processed (a :: trash))) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_moveCell_iterate (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      trash.length])
      (some (lookupScanCfg .moveCell equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .moveCell equal source address value cellBackup query addressBackup
      queryBackup (trash.reverse ++ processed) []) := by
  induction trash generalizing processed with
  | nil => rfl
  | cons a trash ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_moveCell_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem lookupScan_moveCell_reaches_afterMove (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      trash.length + 1])
      (some (lookupScanCfg .moveCell equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .afterMove equal source address value cellBackup query addressBackup
      queryBackup (trash.reverse ++ processed) []) := by
  rw [Nat.add_comm, Function.iterate_add_apply, lookupScan_moveCell_iterate]
  simp only [Function.iterate_one, Option.bind_some, lookupScan_step_moveCell_nil]

@[simp] theorem lookupScan_step_discardValue_nil (equal : Bool)
    (source address cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .discardValue equal source address []
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .preserveCell equal source address [] cellBackup query
      addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanDiscardIteration LookupScanStack.value LookupScanLabel.discardValue
      LookupScanLabel.preserveCell)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address [] cellBackup query addressBackup queryBackup
      processed trash)) = _
  simp [lookupScanDiscardIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_discardValue_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .discardValue equal source address
      (a :: value) cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .discardValue equal source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanDiscardIteration LookupScanStack.value LookupScanLabel.discardValue
      LookupScanLabel.preserveCell)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address (a :: value) cellBackup query addressBackup
      queryBackup processed trash)) = _
  simp [lookupScanDiscardIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_discardValue_reaches_preserveCell (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      value.length + 1])
      (some (lookupScanCfg .discardValue equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .preserveCell equal source address [] cellBackup query
      addressBackup queryBackup processed trash) := by
  induction value with
  | nil =>
      simp only [List.length_nil, Nat.zero_add, Function.iterate_one,
        Option.bind_some, lookupScan_step_discardValue_nil]
  | cons a value ih =>
      rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_discardValue_cons]
      exact ih

@[simp] theorem lookupScan_step_decide (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .decide equal source address value cellBackup
      query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .restoreQuery equal source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  cases equal <;> simp [lookupScanMachine, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

@[simp] theorem lookupScan_step_restoreQuery_nil (equal : Bool)
    (source address value cellBackup query addressBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .restoreQuery equal source address value
      cellBackup query addressBackup [] processed trash) =
    some (lookupScanCfg .discardAddress equal source address value cellBackup query
      addressBackup [] processed trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.queryBackup LookupScanStack.query
      LookupScanLabel.restoreQuery LookupScanLabel.discardAddress)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup [] processed
      trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_restoreQuery_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .restoreQuery equal source address value
      cellBackup query addressBackup (a :: queryBackup) processed trash) =
    some (lookupScanCfg .restoreQuery equal source address value cellBackup
      (a :: query) addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.queryBackup LookupScanStack.query
      LookupScanLabel.restoreQuery LookupScanLabel.discardAddress)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup
      (a :: queryBackup) processed trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_restoreQuery_reaches_discardAddress (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      queryBackup.length + 1])
      (some (lookupScanCfg .restoreQuery equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .discardAddress equal source address value cellBackup
      (queryBackup.reverse ++ query) addressBackup [] processed trash) := by
  induction queryBackup generalizing query with
  | nil =>
      simp only [List.length_nil, Nat.zero_add, Function.iterate_one,
        Option.bind_some, lookupScan_step_restoreQuery_nil, List.reverse_nil,
        List.nil_append]
  | cons a queryBackup ih =>
      rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_restoreQuery_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

@[simp] theorem lookupScan_step_discardAddress_nil (equal : Bool)
    (source address value cellBackup query queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .discardAddress equal source address value
      cellBackup query [] queryBackup processed trash) =
    some (lookupScanCfg .afterCleanup equal source address value cellBackup query []
      queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanDiscardIteration LookupScanStack.addressBackup
      LookupScanLabel.discardAddress LookupScanLabel.afterCleanup)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query [] queryBackup processed
      trash)) = _
  simp [lookupScanDiscardIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_discardAddress_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .discardAddress equal source address value
      cellBackup query (a :: addressBackup) queryBackup processed trash) =
    some (lookupScanCfg .discardAddress equal source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanDiscardIteration LookupScanStack.addressBackup
      LookupScanLabel.discardAddress LookupScanLabel.afterCleanup)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query (a :: addressBackup)
      queryBackup processed trash)) = _
  simp [lookupScanDiscardIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_discardAddress_reaches_afterCleanup (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      addressBackup.length + 1])
      (some (lookupScanCfg .discardAddress equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .afterCleanup equal source address value cellBackup query []
      queryBackup processed trash) := by
  induction addressBackup with
  | nil =>
      simp only [List.length_nil, Nat.zero_add, Function.iterate_one,
        Option.bind_some, lookupScan_step_discardAddress_nil]
  | cons a addressBackup ih =>
      rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_discardAddress_cons]
      exact ih

@[simp] theorem lookupScan_step_afterCleanup_true
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .afterCleanup true source address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .preserveCell true source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  simp [lookupScanMachine, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

@[simp] theorem lookupScan_step_afterCleanup_false
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .afterCleanup false source address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .discardValue false source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  simp [lookupScanMachine, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

@[simp] theorem lookupScan_step_afterMove_true
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .afterMove true source address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .restoreFound true source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  simp [lookupScanMachine, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

@[simp] theorem lookupScan_step_afterMove_false
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .afterMove false source address value
      cellBackup query addressBackup queryBackup processed trash) =
    some (lookupScanCfg .scan false source address value cellBackup query
      addressBackup queryBackup processed trash) := by
  simp [lookupScanMachine, lookupScanCfg, lookupScanStacks]
  all_goals congr 2

@[simp] theorem lookupScan_step_restoreFound_nil (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .restoreFound equal source address value
      cellBackup query addressBackup queryBackup [] trash) =
    some (lookupScanCfg .found equal source address value cellBackup query
      addressBackup queryBackup [] trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.processed LookupScanStack.source
      LookupScanLabel.restoreFound LookupScanLabel.found)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup queryBackup []
      trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_restoreFound_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .restoreFound equal source address value
      cellBackup query addressBackup queryBackup (a :: processed) trash) =
    some (lookupScanCfg .restoreFound equal (a :: source) address value cellBackup query
      addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.processed LookupScanStack.source
      LookupScanLabel.restoreFound LookupScanLabel.found)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup queryBackup
      (a :: processed) trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_restoreFound_reaches_found (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      processed.length + 1])
      (some (lookupScanCfg .restoreFound equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .found equal (processed.reverse ++ source) address value
      cellBackup query addressBackup queryBackup [] trash) := by
  induction processed generalizing source with
  | nil =>
      simp only [List.length_nil, Nat.zero_add, Function.iterate_one,
        Option.bind_some, lookupScan_step_restoreFound_nil, List.reverse_nil,
        List.nil_append]
  | cons a processed ih =>
      rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_restoreFound_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

@[simp] theorem lookupScan_step_restoreMissing_nil (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .restoreMissing equal source address value
      cellBackup query addressBackup queryBackup [] trash) =
    some (lookupScanCfg .missing equal source address value cellBackup query
      addressBackup queryBackup [] trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.processed LookupScanStack.source
      LookupScanLabel.restoreMissing LookupScanLabel.missing)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup queryBackup []
      trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupScan_step_restoreMissing_cons (equal : Bool) (a : SparseSymbol)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    lookupScanMachine.step (lookupScanCfg .restoreMissing equal source address value
      cellBackup query addressBackup queryBackup (a :: processed) trash) =
    some (lookupScanCfg .restoreMissing equal (a :: source) address value cellBackup query
      addressBackup queryBackup processed trash) := by
  change some (TM2.stepAux
    (lookupScanMoveIteration LookupScanStack.processed LookupScanStack.source
      LookupScanLabel.restoreMissing LookupScanLabel.missing)
    ⟨none, equal, none, none⟩
    (lookupScanStacks source address value cellBackup query addressBackup queryBackup
      (a :: processed) trash)) = _
  simp [lookupScanMoveIteration, LookupCellControl.clearHeld, lookupScanCfg,
    lookupScanStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupScan_restoreMissing_reaches_missing (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup processed trash :
      List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      processed.length + 1])
      (some (lookupScanCfg .restoreMissing equal source address value cellBackup query
        addressBackup queryBackup processed trash)) =
    some (lookupScanCfg .missing equal (processed.reverse ++ source) address value
      cellBackup query addressBackup queryBackup [] trash) := by
  induction processed generalizing source with
  | nil =>
      simp only [List.length_nil, Nat.zero_add, Function.iterate_one,
        Option.bind_some, lookupScan_step_restoreMissing_nil, List.reverse_nil,
        List.nil_append]
  | cons a processed ih =>
      rw [List.length_cons, Nat.succ_add, Function.iterate_succ_apply]
      simp only [Option.bind_some, lookupScan_step_restoreMissing_cons]
      rw [ih]
      simp [List.reverse_cons, List.append_assoc]

theorem lookupScan_failed_cell (w a v query : ℕ)
    (ha : a < 2 ^ w) (hq : query < 2 ^ w) (hne : a ≠ query)
    (suffix processed : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      10 * w + 18])
      (some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .scan false suffix [] [] []
      ((fixedBits w query).reverse.map SparseSymbol.bit) [] []
      ((encodeSparseCell w (a, v)).reverse ++ processed) []) := by
  let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
  let backup : List SparseSymbol :=
    .cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
      .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit
  have hbackup : backup = (encodeSparseCell w (a, v)).reverse := by
    simp [backup, encodeSparseCell, encodeFixedWord, List.reverse_append,
      List.map_reverse, List.append_assoc]
  have h0 := lookupScan_fixed_reaches_decide w a v query ha hq suffix processed []
  simp only [hne, decide_false] at h0
  change (stepO^[3 * w + 4])
      (some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .decide false suffix []
      ((fixedBits w v).reverse.map SparseSymbol.bit) backup []
      ((fixedBits w a).map SparseSymbol.bit) ((fixedBits w query).map SparseSymbol.bit)
      processed []) at h0
  have oneStep {x y : lookupScanMachine.Cfg}
      (h : lookupScanMachine.step x = some y) :
      (stepO^[1]) (some x) = some y := by
    simpa [stepO] using h
  have h1 := lookupScan_step_decide false suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup []
    ((fixedBits w a).map SparseSymbol.bit) ((fixedBits w query).map SparseSymbol.bit)
    processed []
  have h1' := oneStep h1
  have h2 := lookupScan_restoreQuery_reaches_discardAddress false suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup []
    ((fixedBits w a).map SparseSymbol.bit) ((fixedBits w query).map SparseSymbol.bit)
    processed []
  have h2' := h2
  simp only [List.append_nil, List.map_reverse] at h2'
  have h3 := lookupScan_discardAddress_reaches_afterCleanup false suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup
    ((fixedBits w query).reverse.map SparseSymbol.bit)
    ((fixedBits w a).map SparseSymbol.bit) [] processed []
  have h4 := lookupScan_step_afterCleanup_false suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup
    ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
  have h4' := oneStep h4
  have h5 := lookupScan_discardValue_reaches_preserveCell false suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup
    ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
  have h6 := lookupScan_preserveCell_reaches_moveCell false suffix [] [] backup
    ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
  have h7 := lookupScan_moveCell_reaches_afterMove false suffix [] [] []
    ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed backup.reverse
  have h6' := h6
  simp only [List.append_nil] at h6'
  have h7' := h7
  simp only [List.reverse_reverse] at h7'
  have h8 := lookupScan_step_afterMove_false suffix [] [] []
    ((fixedBits w query).reverse.map SparseSymbol.bit) [] []
    (backup ++ processed) []
  have h8' := oneStep h8
  have chain {m n : ℕ} {x y z : Option lookupScanMachine.Cfg}
      (hm : (stepO^[m]) x = y) (hn : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, hm, hn]
  simp only [← List.map_reverse] at h0 h1' h2' h3 h4' h5 h6' h7' h8'
  have hrun := chain (chain (chain (chain (chain (chain (chain (chain h0 h1') h2') h3)
    h4') h5) h6') h7') h8'
  simp only [List.length_map, List.length_reverse, fixedBits_length] at hrun
  rw [hbackup] at hrun
  simp only [List.length_reverse, encodeSparseCell_length] at hrun
  have hexp : 1 + ((2 * w + 3 + 1) + ((2 * w + 3 + 1) +
      ((w + 1) + (1 + ((w + 1) + ((w + 1) + (1 + (3 * w + 4)))))))) =
      10 * w + 18 := by omega
  rw [hexp] at hrun
  simpa [stepO, List.map_reverse, List.append_assoc] using hrun

theorem lookupScan_matching_cell (w a v : ℕ) (ha : a < 2 ^ w)
    (suffix processed : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      11 * w + processed.length + 21])
      (some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .found true
      (processed.reverse ++ encodeSparseCell w (a, v) ++ suffix) []
      ((fixedBits w v).reverse.map SparseSymbol.bit) []
      ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] [] []) := by
  let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
  let backup : List SparseSymbol :=
    .cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
      .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit
  have hbackup : backup = (encodeSparseCell w (a, v)).reverse := by
    simp [backup, encodeSparseCell, encodeFixedWord, List.reverse_append,
      List.map_reverse, List.append_assoc]
  have h0 := lookupScan_fixed_reaches_decide w a v a ha ha suffix processed []
  simp only [decide_true] at h0
  change (stepO^[3 * w + 4])
      (some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .decide true suffix []
      ((fixedBits w v).reverse.map SparseSymbol.bit) backup []
      ((fixedBits w a).map SparseSymbol.bit) ((fixedBits w a).map SparseSymbol.bit)
      processed []) at h0
  have oneStep {x y : lookupScanMachine.Cfg}
      (h : lookupScanMachine.step x = some y) :
      (stepO^[1]) (some x) = some y := by
    simpa [stepO] using h
  have h1 := oneStep (lookupScan_step_decide true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup []
    ((fixedBits w a).map SparseSymbol.bit) ((fixedBits w a).map SparseSymbol.bit)
    processed [])
  have h2 := lookupScan_restoreQuery_reaches_discardAddress true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup []
    ((fixedBits w a).map SparseSymbol.bit) ((fixedBits w a).map SparseSymbol.bit)
    processed []
  have h2' := h2
  simp only [List.append_nil, List.map_reverse] at h2'
  have h3 := lookupScan_discardAddress_reaches_afterCleanup true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup
    ((fixedBits w a).reverse.map SparseSymbol.bit)
    ((fixedBits w a).map SparseSymbol.bit) [] processed []
  have h4 := oneStep (lookupScan_step_afterCleanup_true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup
    ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] processed [])
  have h5 := lookupScan_preserveCell_reaches_moveCell true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) backup
    ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] processed []
  have h5' := h5
  simp only [List.append_nil] at h5'
  have h6 := lookupScan_moveCell_reaches_afterMove true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) []
    ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] processed backup.reverse
  have h6' := h6
  simp only [List.reverse_reverse] at h6'
  have h7 := oneStep (lookupScan_step_afterMove_true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) []
    ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] (backup ++ processed) [])
  have h8 := lookupScan_restoreFound_reaches_found true suffix []
    ((fixedBits w v).reverse.map SparseSymbol.bit) []
    ((fixedBits w a).reverse.map SparseSymbol.bit) [] [] (backup ++ processed) []
  have chain {m n : ℕ} {x y z : Option lookupScanMachine.Cfg}
      (hm : (stepO^[m]) x = y) (hn : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, hm, hn]
  simp only [← List.map_reverse] at h0 h1 h2' h3 h4 h5' h6' h7 h8
  have hrun := chain (chain (chain (chain (chain (chain (chain (chain h0 h1) h2') h3)
    h4) h5') h6') h7) h8
  simp only [List.length_map, List.length_reverse, fixedBits_length,
    List.length_append] at hrun
  rw [hbackup] at hrun
  simp only [List.length_reverse, encodeSparseCell_length, List.reverse_append,
    List.reverse_reverse] at hrun
  have hexp : (2 * w + 3 + processed.length + 1) +
      (1 + (2 * w + 3 + 1 + (2 * w + 3 + 1 +
        (1 + (w + 1 + (w + 1 + (1 + (3 * w + 4)))))))) =
      11 * w + processed.length + 21 := by omega
  rw [hexp] at hrun
  simpa [stepO, List.map_reverse, List.append_assoc] using hrun

end Lax51Proofs.RamToTM
