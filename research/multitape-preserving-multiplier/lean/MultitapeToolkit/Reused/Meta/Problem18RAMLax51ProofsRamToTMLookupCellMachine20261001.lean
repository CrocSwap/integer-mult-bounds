import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMSymbolMoveMacro20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

structure LookupCellControl where
  held : Option SparseSymbol
  equal : Bool
  left : Option SparseSymbol
  right : Option SparseSymbol
  deriving DecidableEq, Fintype, Inhabited

inductive LookupCellStack
  | source | address | value | cellBackup | query | addressBackup | queryBackup
  deriving DecidableEq, Fintype, Inhabited

inductive LookupCellLabel | address | value | cellEnd | compare | done
  deriving DecidableEq, Fintype, Inhabited

def LookupCellControl.clearHeld (s : LookupCellControl) : LookupCellControl :=
  { s with held := none }

def LookupCellControl.compareAdvance (s : LookupCellControl) : LookupCellControl :=
  { held := none, equal := s.equal && decide (s.left = s.right),
    left := none, right := none }

def lookupCellWordIteration {K Λ : Type} [DecidableEq K]
    (source target backup : K) (loop next : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ LookupCellControl :=
  .pop source (fun s a => { s with held := a }) <|
    .branch (fun s => s.held = some .wordEnd)
      (.push backup (fun _ => .wordEnd) <|
        .load LookupCellControl.clearHeld <| .goto fun _ => next)
      (.push target (fun s => s.held.getD (.bit false)) <|
        .push backup (fun s => s.held.getD (.bit false)) <|
          .load LookupCellControl.clearHeld <| .goto fun _ => loop)

def lookupCellCompareIteration {K Λ : Type} [DecidableEq K]
    (left right leftBackup rightBackup : K) (loop done : Λ) :
    TM2.Stmt (fun _ : K => SparseSymbol) Λ LookupCellControl :=
  .pop left (fun s a => { s with left := a }) <|
    .branch (fun s => s.left.isNone)
      (.goto fun _ => done)
      (.pop right (fun s b => { s with right := b }) <|
        .push leftBackup (fun s => s.left.getD (.bit false)) <|
          .push rightBackup (fun s => s.right.getD (.bit false)) <|
            .load LookupCellControl.compareAdvance <| .goto fun _ => loop)

def lookupCellMachine : Turing.FinTM2 where
  K := LookupCellStack
  k₀ := .source
  k₁ := .value
  Γ _ := SparseSymbol
  Λ := LookupCellLabel
  main := .address
  σ := LookupCellControl
  initialState := ⟨none, true, none, none⟩
  m
    | .address => lookupCellWordIteration .source .address .cellBackup .address .value
    | .value => lookupCellWordIteration .source .value .cellBackup .value .cellEnd
    | .cellEnd =>
        .pop .source (fun s a => { s with held := a }) <|
          .push .cellBackup (fun s => s.held.getD .cellEnd) <|
            .load LookupCellControl.clearHeld <| .goto fun _ => .compare
    | .compare => lookupCellCompareIteration .address .query
        .addressBackup .queryBackup .compare .done
    | .done => .halt

def lookupCellStacks (source address value cellBackup query addressBackup queryBackup :
    List SparseSymbol) : LookupCellStack → List SparseSymbol
  | .source => source
  | .address => address
  | .value => value
  | .cellBackup => cellBackup
  | .query => query
  | .addressBackup => addressBackup
  | .queryBackup => queryBackup

def lookupCellCfg (label : LookupCellLabel) (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup :
      List SparseSymbol) : lookupCellMachine.Cfg where
  l := some label
  var := ⟨none, equal, none, none⟩
  stk := lookupCellStacks source address value cellBackup query addressBackup queryBackup

@[simp] theorem lookupCell_step_address_bit (equal : Bool) (b : Bool)
    (source address value cellBackup query addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .address equal (.bit b :: source)
      address value cellBackup query addressBackup queryBackup) =
    some (lookupCellCfg .address equal source (.bit b :: address) value
      (.bit b :: cellBackup) query addressBackup queryBackup) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupCellStack.source LookupCellStack.address
      LookupCellStack.cellBackup LookupCellLabel.address LookupCellLabel.value)
    ⟨none, equal, none, none⟩
    (lookupCellStacks (.bit b :: source) address value cellBackup query
      addressBackup queryBackup)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupCellCfg,
    lookupCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupCell_step_address_end (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .address equal (.wordEnd :: source)
      address value cellBackup query addressBackup queryBackup) =
    some (lookupCellCfg .value equal source address value (.wordEnd :: cellBackup)
      query addressBackup queryBackup) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupCellStack.source LookupCellStack.address
      LookupCellStack.cellBackup LookupCellLabel.address LookupCellLabel.value)
    ⟨none, equal, none, none⟩
    (lookupCellStacks (.wordEnd :: source) address value cellBackup query
      addressBackup queryBackup)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupCellCfg,
    lookupCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupCell_step_value_bit (equal : Bool) (b : Bool)
    (source address value cellBackup query addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .value equal (.bit b :: source)
      address value cellBackup query addressBackup queryBackup) =
    some (lookupCellCfg .value equal source address (.bit b :: value)
      (.bit b :: cellBackup) query addressBackup queryBackup) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupCellStack.source LookupCellStack.value
      LookupCellStack.cellBackup LookupCellLabel.value LookupCellLabel.cellEnd)
    ⟨none, equal, none, none⟩
    (lookupCellStacks (.bit b :: source) address value cellBackup query
      addressBackup queryBackup)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupCellCfg,
    lookupCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupCell_step_value_end (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .value equal (.wordEnd :: source)
      address value cellBackup query addressBackup queryBackup) =
    some (lookupCellCfg .cellEnd equal source address value (.wordEnd :: cellBackup)
      query addressBackup queryBackup) := by
  change some (TM2.stepAux
    (lookupCellWordIteration LookupCellStack.source LookupCellStack.value
      LookupCellStack.cellBackup LookupCellLabel.value LookupCellLabel.cellEnd)
    ⟨none, equal, none, none⟩
    (lookupCellStacks (.wordEnd :: source) address value cellBackup query
      addressBackup queryBackup)) = _
  simp [lookupCellWordIteration, LookupCellControl.clearHeld, lookupCellCfg,
    lookupCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupCell_step_cell_end (equal : Bool)
    (source address value cellBackup query addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .cellEnd equal (.cellEnd :: source)
      address value cellBackup query addressBackup queryBackup) =
    some (lookupCellCfg .compare equal source address value (.cellEnd :: cellBackup)
      query addressBackup queryBackup) := by
  change some (TM2.stepAux
    (.pop LookupCellStack.source
      (fun (s : LookupCellControl) a => { s with held := a }) <|
      .push LookupCellStack.cellBackup
        (fun (s : LookupCellControl) => s.held.getD .cellEnd) <|
        .load LookupCellControl.clearHeld <| .goto fun _ => LookupCellLabel.compare)
    ⟨none, equal, none, none⟩
    (lookupCellStacks (.cellEnd :: source) address value cellBackup query
      addressBackup queryBackup)) = _
  simp [LookupCellControl.clearHeld, lookupCellCfg, lookupCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupCell_step_compare_cons (equal : Bool) (a b : SparseSymbol)
    (address query source value cellBackup addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .compare equal source (a :: address) value
      cellBackup (b :: query) addressBackup queryBackup) =
    some (lookupCellCfg .compare (equal && decide (a = b)) source address value
      cellBackup query (a :: addressBackup) (b :: queryBackup)) := by
  change some (TM2.stepAux
    (lookupCellCompareIteration LookupCellStack.address LookupCellStack.query
      LookupCellStack.addressBackup LookupCellStack.queryBackup
      LookupCellLabel.compare LookupCellLabel.done)
    ⟨none, equal, none, none⟩
    (lookupCellStacks source (a :: address) value cellBackup (b :: query)
      addressBackup queryBackup)) = _
  simp [lookupCellCompareIteration, LookupCellControl.compareAdvance,
    lookupCellCfg, lookupCellStacks, Function.update]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

@[simp] theorem lookupCell_step_compare_nil (equal : Bool)
    (source value cellBackup query addressBackup queryBackup : List SparseSymbol) :
    lookupCellMachine.step (lookupCellCfg .compare equal source [] value
      cellBackup query addressBackup queryBackup) =
    some (lookupCellCfg .done equal source [] value cellBackup query
      addressBackup queryBackup) := by
  change some (TM2.stepAux
    (lookupCellCompareIteration LookupCellStack.address LookupCellStack.query
      LookupCellStack.addressBackup LookupCellStack.queryBackup
      LookupCellLabel.compare LookupCellLabel.done)
    ⟨none, equal, none, none⟩
    (lookupCellStacks source [] value cellBackup query addressBackup queryBackup)) = _
  simp [lookupCellCompareIteration, lookupCellCfg, lookupCellStacks]
  all_goals (congr 2 <;> funext k <;> cases k <;> rfl)

theorem lookupCell_address_iterate (equal : Bool) (xs : List Bool)
    (suffix address value cellBackup query addressBackup queryBackup :
      List SparseSymbol) :
    ((fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step)^[xs.length])
      (some (lookupCellCfg .address equal
        (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) address value cellBackup
        query addressBackup queryBackup)) =
    some (lookupCellCfg .address equal (.wordEnd :: suffix)
      (xs.reverse.map SparseSymbol.bit ++ address) value
      (xs.reverse.map SparseSymbol.bit ++ cellBackup) query addressBackup queryBackup) := by
  induction xs generalizing address cellBackup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        lookupCell_step_address_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem lookupCell_value_iterate (equal : Bool) (xs : List Bool)
    (suffix address value cellBackup query addressBackup queryBackup :
      List SparseSymbol) :
    ((fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step)^[xs.length])
      (some (lookupCellCfg .value equal
        (xs.map SparseSymbol.bit ++ .wordEnd :: suffix) address value cellBackup
        query addressBackup queryBackup)) =
    some (lookupCellCfg .value equal (.wordEnd :: suffix) address
      (xs.reverse.map SparseSymbol.bit ++ value)
      (xs.reverse.map SparseSymbol.bit ++ cellBackup) query addressBackup queryBackup) := by
  induction xs generalizing value cellBackup with
  | nil => rfl
  | cons b xs ih =>
      rw [List.length_cons, Function.iterate_succ_apply]
      simp only [List.map_cons, List.cons_append, Option.bind_some,
        lookupCell_step_value_bit]
      rw [ih]
      simp [List.reverse_cons, List.map_append, List.append_assoc]

theorem lookupCell_compare_iterate (equal : Bool)
    (address query source value cellBackup addressBackup queryBackup :
      List SparseSymbol) (hlen : address.length = query.length) :
    ((fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step)^[address.length])
      (some (lookupCellCfg .compare equal source address value cellBackup query
        addressBackup queryBackup)) =
    some (lookupCellCfg .compare (symbolsEqual address query equal) source [] value
      cellBackup [] (address.reverse ++ addressBackup)
      (query.reverse ++ queryBackup)) := by
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
        simp only [Option.bind_some, lookupCell_step_compare_cons]
        rw [ih (query := query) (equal := equal && decide (a = b))
          (addressBackup := a :: addressBackup)
          (queryBackup := b :: queryBackup) hlen]
        simp [symbolsEqual, List.reverse_cons, List.append_assoc]

theorem lookupCell_compare_reaches_done (equal : Bool)
    (address query source value cellBackup addressBackup queryBackup :
      List SparseSymbol) (hlen : address.length = query.length) :
    ((fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step)^[address.length + 1])
      (some (lookupCellCfg .compare equal source address value cellBackup query
        addressBackup queryBackup)) =
    some (lookupCellCfg .done (symbolsEqual address query equal) source [] value
      cellBackup [] (address.reverse ++ addressBackup)
      (query.reverse ++ queryBackup)) := by
  rw [Nat.add_comm, Function.iterate_add_apply,
    lookupCell_compare_iterate equal address query source value cellBackup
      addressBackup queryBackup hlen]
  simp only [Function.iterate_one, Option.bind_some, lookupCell_step_compare_nil]

theorem lookupCell_parse_fixed (equal : Bool) (w a v : ℕ)
    (suffix query : List SparseSymbol) :
    ((fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step)^[2 * w + 3])
      (some (lookupCellCfg .address equal (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] query [] [])) =
    some (lookupCellCfg .compare equal suffix
      ((fixedBits w a).reverse.map SparseSymbol.bit)
      ((fixedBits w v).reverse.map SparseSymbol.bit)
      (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
        .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)
      query [] []) := by
  let stepO := fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step
  have haRun := lookupCell_address_iterate equal (fixedBits w a)
    (encodeFixedWord w v ++ .cellEnd :: suffix) [] [] [] query [] []
  have haEnd : (stepO^[1])
      (some (lookupCellCfg .address equal
        (.wordEnd :: (encodeFixedWord w v ++ .cellEnd :: suffix))
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        ((fixedBits w a).reverse.map SparseSymbol.bit) query [] [])) =
      some (lookupCellCfg .value equal
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) query [] []) := by
    simpa [stepO, List.map_reverse] using
      lookupCell_step_address_end equal
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        ((fixedBits w a).reverse.map SparseSymbol.bit) query [] []
  have hvRun := lookupCell_value_iterate equal (fixedBits w v) (.cellEnd :: suffix)
    ((fixedBits w a).reverse.map SparseSymbol.bit) []
    (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) query [] []
  have hvRun' : (stepO^[w])
      (some (lookupCellCfg .value equal
        (encodeFixedWord w v ++ .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit) []
        (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) query [] [])) =
      some (lookupCellCfg .value equal (.wordEnd :: .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)) query [] []) := by
    simpa [stepO, encodeFixedWord, List.append_assoc] using hvRun
  have hvEnd : (stepO^[1])
      (some (lookupCellCfg .value equal (.wordEnd :: .cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)) query [] [])) =
      some (lookupCellCfg .cellEnd equal (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []) := by
    simpa [stepO, List.map_reverse] using
      lookupCell_step_value_end equal (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)) query [] []
  have hcEnd : (stepO^[1])
      (some (lookupCellCfg .cellEnd equal (.cellEnd :: suffix)
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] [])) =
      some (lookupCellCfg .compare equal suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.cellEnd :: .wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []) := by
    simpa [stepO, List.map_reverse] using
      lookupCell_step_cell_end equal suffix
        ((fixedBits w a).reverse.map SparseSymbol.bit)
        ((fixedBits w v).reverse.map SparseSymbol.bit)
        (.wordEnd :: ((fixedBits w v).reverse.map SparseSymbol.bit ++
          (.wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit))) query [] []
  simp only [fixedBits_length, List.append_nil] at haRun hvRun
  have chain {m n : ℕ} {x y z : Option lookupCellMachine.Cfg}
      (h₁ : (stepO^[m]) x = y) (h₂ : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, h₁, h₂]
  have h01 := chain haRun haEnd
  have h02 := chain h01 hvRun'
  have h03 := chain h02 hvEnd
  have h04 := chain h03 hcEnd
  dsimp [stepO] at h04
  have hexp : 1 + (1 + (w + (1 + w))) = 2 * w + 3 := by omega
  rw [hexp] at h04
  simpa [encodeSparseCell, encodeFixedWord, List.append_assoc] using h04

theorem lookupCell_fixed_correct (w a v query : ℕ)
    (ha : a < 2 ^ w) (hq : query < 2 ^ w) (suffix : List SparseSymbol) :
    ((fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step)^[3 * w + 4])
      (some (lookupCellCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [])) =
    some (lookupCellCfg .done (decide (a = query)) suffix []
      ((fixedBits w v).reverse.map SparseSymbol.bit)
      (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
        .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit)
      [] ((fixedBits w a).map SparseSymbol.bit)
      ((fixedBits w query).map SparseSymbol.bit)) := by
  let stepO := fun o : Option lookupCellMachine.Cfg => o.bind lookupCellMachine.step
  have hparse := lookupCell_parse_fixed true w a v suffix
    ((fixedBits w query).reverse.map SparseSymbol.bit)
  have hcompare := lookupCell_compare_reaches_done true
    ((fixedBits w a).reverse.map SparseSymbol.bit)
    ((fixedBits w query).reverse.map SparseSymbol.bit) suffix
    ((fixedBits w v).reverse.map SparseSymbol.bit)
    (.cellEnd :: .wordEnd :: (fixedBits w v).reverse.map SparseSymbol.bit ++
      .wordEnd :: (fixedBits w a).reverse.map SparseSymbol.bit) [] [] (by simp)
  simp only [List.length_map, List.length_reverse, fixedBits_length] at hcompare
  have chain {m n : ℕ} {x y z : Option lookupCellMachine.Cfg}
      (h₁ : (stepO^[m]) x = y) (h₂ : (stepO^[n]) y = z) :
      (stepO^[n + m]) x = z := by
    rw [Function.iterate_add_apply, h₁, h₂]
  have hrun := chain hparse hcompare
  have hexp : (w + 1) + (2 * w + 3) = 3 * w + 4 := by omega
  rw [hexp] at hrun
  change (stepO^[3 * w + 4])
      (some (lookupCellCfg .address true (encodeSparseCell w (a, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [])) = _
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
        have := congrArg bitsValue hbits
        simpa [bitsValue_fixedBits_of_lt ha, bitsValue_fixedBits_of_lt hq] using this
      simp [h, hplain]
  rw [heq]
  simp

end Lax51Proofs.RamToTM
