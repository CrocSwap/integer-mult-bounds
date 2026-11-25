import MultitapeToolkit.Reused.Meta.Problem18RAMLax51ProofsRamToTMLookupScanMachine20261001

set_option backward.isDefEq.respectTransparency false


set_option autoImplicit false

namespace Lax51Proofs.RamToTM

open Turing TM2

/-- A normalized prefix containing no requested address is skipped exactly,
leaving its reversed serialization on the processed stack. -/
theorem lookupScan_skip_missing_prefix (w query : ℕ) (hq : query < 2 ^ w)
    (m : SparseMemory) (hm : m.Normalized w)
    (hmissing : SparseMemory.find? m query = none)
    (equal : Bool) (suffix processed : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      m.length * (10 * w + 19)])
      (some (lookupScanCfg .scan equal (encodeSparseMemory w m ++ suffix) [] [] []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .scan (equal && decide m.isEmpty) suffix [] [] []
      ((fixedBits w query).reverse.map SparseSymbol.bit) [] []
      ((encodeSparseMemory w m).reverse ++ processed) []) := by
  induction m generalizing equal processed with
  | nil => simp [encodeSparseMemory]
  | cons cell m ih =>
      rcases cell with ⟨a, v⟩
      rcases hm with ⟨ha, hv, hm⟩
      have hqa : query ≠ a := by
        intro h
        simp [SparseMemory.find?, h] at hmissing
      have hne : a ≠ query := Ne.symm hqa
      have htail : SparseMemory.find? m query = none := by
        simpa [SparseMemory.find?, hqa] using hmissing
      let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
      let rest := encodeSparseMemory w m ++ suffix
      have hscan := lookupScan_step_encoded_cell equal w a v rest [] [] []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
      have hscan' : (stepO^[1])
          (some (lookupScanCfg .scan equal (encodeSparseCell w (a, v) ++ rest)
            [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
          some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ rest)
            [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []) := by
        simpa [stepO] using hscan
      have hcell := lookupScan_failed_cell w a v query ha hq hne rest processed
      have htailRun := ih hm htail false
        ((encodeSparseCell w (a, v)).reverse ++ processed)
      have chain {r s : ℕ} {x y z : Option lookupScanMachine.Cfg}
          (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
          (stepO^[s + r]) x = z := by
        rw [Function.iterate_add_apply, hr, hs]
      have hrun := chain (chain hscan' hcell) htailRun
      have hexp : m.length * (10 * w + 19) + ((10 * w + 18) + 1) =
          (m.length + 1) * (10 * w + 19) := by
        rw [Nat.add_mul, Nat.one_mul]
      rw [hexp] at hrun
      simpa [stepO, rest, encodeSparseMemory, List.reverse_append,
        List.append_assoc] using hrun

/-- After a nonmatching prefix, the first matching cell is returned and the
entire prefix-plus-cell serialization is restored in its original order. -/
theorem lookupScan_found_after_prefix (w query v : ℕ) (hq : query < 2 ^ w)
    (pref : SparseMemory) (hp : pref.Normalized w)
    (hmissing : SparseMemory.find? pref query = none)
    (suffix processed : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      pref.length * (12 * w + 22) + 11 * w + processed.length + 22])
      (some (lookupScanCfg .scan true
        (encodeSparseMemory w pref ++ encodeSparseCell w (query, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .found true
      (processed.reverse ++ encodeSparseMemory w pref ++
        encodeSparseCell w (query, v) ++ suffix)
      [] ((fixedBits w v).reverse.map SparseSymbol.bit) []
      ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] [] []) := by
  let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
  let rest := encodeSparseCell w (query, v) ++ suffix
  let processed' := (encodeSparseMemory w pref).reverse ++ processed
  let scanEqual := true && decide pref.isEmpty
  have hprefix := lookupScan_skip_missing_prefix w query hq pref hp hmissing true
    rest processed
  have hscan := lookupScan_step_encoded_cell scanEqual w query v suffix [] [] []
    ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed' []
  have hscan' : (stepO^[1])
      (some (lookupScanCfg .scan scanEqual (encodeSparseCell w (query, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed' [])) =
      some (lookupScanCfg .address true (encodeSparseCell w (query, v) ++ suffix)
        [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed' []) := by
    simpa [stepO] using hscan
  have hmatch := lookupScan_matching_cell w query v hq suffix processed'
  have chain {r s : ℕ} {x y z : Option lookupScanMachine.Cfg}
      (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
      (stepO^[s + r]) x = z := by
    rw [Function.iterate_add_apply, hr, hs]
  have hrun := chain (chain hprefix hscan') hmatch
  dsimp only [processed'] at hrun
  simp only [List.length_append, List.length_reverse,
    encodeSparseMemory_length] at hrun
  have hexp :
      (11 * w + (pref.length * (2 * w + 3) + processed.length) + 21) +
          (1 + pref.length * (10 * w + 19)) =
        pref.length * (12 * w + 22) + 11 * w + processed.length + 22 := by
    ring
  rw [hexp] at hrun
  simpa [stepO, rest, processed', List.reverse_append, List.reverse_reverse,
    List.append_assoc] using hrun

theorem SparseMemory.normalized_append_left {w : ℕ} (p s : SparseMemory)
    (h : SparseMemory.Normalized w (List.append p s)) : p.Normalized w := by
  induction p with
  | nil => exact SparseMemory.normalized_nil w
  | cons cell p ih =>
      rcases cell with ⟨a, v⟩
      rcases h with ⟨ha, hv, htail⟩
      exact ⟨ha, hv, ih htail⟩

theorem SparseMemory.find?_eq_some_decompose {m : SparseMemory} {query value : ℕ}
    (h : SparseMemory.find? m query = some value) :
    ∃ p s : SparseMemory,
      m = List.append p ((query, value) :: s) ∧
        SparseMemory.find? p query = none := by
  induction m with
  | nil => simp [SparseMemory.find?] at h
  | cons cell m ih =>
      rcases cell with ⟨a, v⟩
      by_cases hqa : query = a
      · subst a
        simp [SparseMemory.find?] at h
        subst v
        exact ⟨[], m, by simp, by simp [SparseMemory.find?]⟩
      · have htail : SparseMemory.find? m query = some value := by
          simpa [SparseMemory.find?, hqa] using h
        rcases ih htail with ⟨p, s, hm, hp⟩
        refine ⟨(a, v) :: p, s, ?_, ?_⟩
        · simp [hm]
        · simp [SparseMemory.find?, hqa, hp]

/-- Extensional successful lookup theorem with a bound depending only on the
whole sparse-memory length, rather than the unknown first-match position. -/
theorem lookupScan_found (w query value : ℕ) (hq : query < 2 ^ w)
    (m : SparseMemory) (hm : m.Normalized w)
    (hfind : m.find? query = some value) (processed : List SparseSymbol) :
    ∃ n ≤ m.length * (12 * w + 22) + 11 * w + processed.length + 22,
      ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[n])
        (some (lookupScanCfg .scan true
          (encodeSparseMemory w m ++ [.memoryEnd]) [] [] []
          ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
      some (lookupScanCfg .found true
        (processed.reverse ++ encodeSparseMemory w m ++ [.memoryEnd]) []
        ((fixedBits w value).reverse.map SparseSymbol.bit) []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] [] []) := by
  rcases SparseMemory.find?_eq_some_decompose hfind with ⟨p, s, rfl, hpfind⟩
  have hp : p.Normalized w :=
    SparseMemory.normalized_append_left p ((query, value) :: s) hm
  let n := p.length * (12 * w + 22) + 11 * w + processed.length + 22
  refine ⟨n, ?_, ?_⟩
  · dsimp [n]
    have hlen : p.length ≤ (List.append p ((query, value) :: s)).length := by simp
    exact Nat.add_le_add_right
      (Nat.add_le_add_right (Nat.mul_le_mul_right _ hlen) (11 * w))
      (processed.length + 22)
  · have hrun := lookupScan_found_after_prefix w query value hq p hp hpfind
      (encodeSparseMemory w s ++ [.memoryEnd]) processed
    simpa [n, encodeSparseMemory, List.append_assoc] using hrun

/-- If no encoded cell has the requested address, the concrete scanner restores
the complete memory tape and reaches its missing exit. -/
theorem lookupScan_all_missing (w query : ℕ) (hq : query < 2 ^ w)
    (m : SparseMemory) (hm : m.Normalized w)
    (hmissing : SparseMemory.find? m query = none)
    (equal : Bool) (processed : List SparseSymbol) :
    ((fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step)^[
      m.length * (12 * w + 22) + processed.length + 2])
      (some (lookupScanCfg .scan equal
        (encodeSparseMemory w m ++ [.memoryEnd]) [] [] []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
    some (lookupScanCfg .missing (equal && decide m.isEmpty)
      (processed.reverse ++ encodeSparseMemory w m ++ [.memoryEnd]) [] [] []
      ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] [] []) := by
  induction m generalizing equal processed with
  | nil =>
      let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
      have h0 := lookupScan_step_empty_memory equal [] [] []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
      have h0' : (stepO^[1])
          (some (lookupScanCfg .scan equal [.memoryEnd] [] [] []
            ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
          some (lookupScanCfg .restoreMissing equal [.memoryEnd] [] [] []
            ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []) := by
        simpa [stepO] using h0
      have h1 := lookupScan_restoreMissing_reaches_missing equal [.memoryEnd] [] [] []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
      have chain {r s : ℕ} {x y z : Option lookupScanMachine.Cfg}
          (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
          (stepO^[s + r]) x = z := by
        rw [Function.iterate_add_apply, hr, hs]
      have hrun := chain h0' h1
      simpa [stepO, encodeSparseMemory, List.append_assoc, Nat.add_comm, Nat.add_left_comm,
        Nat.add_assoc] using hrun
  | cons cell m ih =>
      rcases cell with ⟨a, v⟩
      rcases hm with ⟨ha, hv, hm⟩
      have hqa : query ≠ a := by
        intro h
        simp [SparseMemory.find?, h] at hmissing
      have hne : a ≠ query := Ne.symm hqa
      have htail : SparseMemory.find? m query = none := by
        simpa [SparseMemory.find?, hqa] using hmissing
      let stepO := fun o : Option lookupScanMachine.Cfg => o.bind lookupScanMachine.step
      let suffix := encodeSparseMemory w m ++ [.memoryEnd]
      have hscan := lookupScan_step_encoded_cell equal w a v suffix [] [] []
        ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []
      have hscan' : (stepO^[1])
          (some (lookupScanCfg .scan equal (encodeSparseCell w (a, v) ++ suffix)
            [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed [])) =
          some (lookupScanCfg .address true (encodeSparseCell w (a, v) ++ suffix)
            [] [] [] ((fixedBits w query).reverse.map SparseSymbol.bit) [] [] processed []) := by
        simpa [stepO] using hscan
      have hcell := lookupScan_failed_cell w a v query ha hq hne suffix processed
      have htailRun := ih hm htail false
        ((encodeSparseCell w (a, v)).reverse ++ processed)
      have chain {r s : ℕ} {x y z : Option lookupScanMachine.Cfg}
          (hr : (stepO^[r]) x = y) (hs : (stepO^[s]) y = z) :
          (stepO^[s + r]) x = z := by
        rw [Function.iterate_add_apply, hr, hs]
      have hrun := chain (chain hscan' hcell) htailRun
      simp only [List.length_append, List.length_reverse, encodeSparseCell_length] at hrun
      have hexp :
          (m.length * (12 * w + 22) + (2 * w + 3 + processed.length) + 2) +
              ((10 * w + 18) + 1) =
            (m.length + 1) * (12 * w + 22) + processed.length + 2 := by
        rw [Nat.add_mul, Nat.one_mul]
        omega
      rw [hexp] at hrun
      simpa [stepO, suffix, encodeSparseMemory, List.reverse_append,
        List.reverse_reverse, List.append_assoc] using hrun

end Lax51Proofs.RamToTM
