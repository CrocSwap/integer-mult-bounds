import PreparedPairXor

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Conservative actual-transition footprint for the accepted five-tape PR488,
backward-pairing and marked-XOR controller. A historical multitape step can
extend each of four tape representations by at most one cell. Each later
single-head step extends by at most one; the two handoffs retain every cell.
The resulting uniform four-cell growth bound and actual halt stuttering close
the whole pipeline's formerly separate prefix-space obligation.

The entrance measure counts represented finite-alphabet tape cells, including
one explicit blank head for each empty PR488 tape. It is not a logical payload
bit count or an encoding of unbounded coordinates. Fixed control/scratch are
additional constants. The conservative bounds 18*V time and 73*V cells need
no extra runtime/space premise and include empty inputs. No optimality,
Nat-to-bits conversion, physical allocation or dirty-state inverse is claimed.
Reuses PR488's exact implementation and the accepted PreparedPairXor theorem;
no preparation, pairing, XOR or spectator-confinement algorithm is repeated.
Author-checked context kappa=836330098538459/500000000000000000.
Fresh compiler acceptance is recorded separately from this source proposal.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.PreparedPairXorSpace
open PairedBitXorScan (Tape)
open BackwardPairedInput (inputCells outputCells)
open PreparedPairXor (State PrepConfig run step Halted initial final)

/-- All five represented tapes, independent of the active controller phase. -/
def cells : State → Nat
  | .prepare c out _ _ => inputCells (c.tapes (0 : Fin 4)) +
      inputCells (c.tapes (1 : Fin 4)) + inputCells (c.tapes (2 : Fin 4)) +
      inputCells (c.tapes (3 : Fin 4)) + outputCells out
  | .pairing left right s => inputCells left + inputCells right + BackwardPairedInput.cells s
  | .xor left right wl wr _ s => inputCells left + inputCells right +
      inputCells wl + inputCells wr + MarkedBitXorScan.cells s

private theorem input_update_growth (t : FixedTapeMachine.Tape)
    (a : FixedTapeMachine.Symbol) (d : FixedTapeMachine.Move) :
    inputCells ((t.write a).move d) ≤ inputCells t + 1 := by
  rcases t with ⟨ls,b,rs⟩
  cases d <;> cases ls <;> cases rs <;>
    simp [inputCells,FixedTapeMachine.Tape.write,FixedTapeMachine.Tape.move] <;> omega

private theorem input_move_growth (t : FixedTapeMachine.Tape) (d : FixedTapeMachine.Move) :
    inputCells (t.move d) ≤ inputCells t + 1 := by
  simpa only [FixedTapeMachine.Tape.write] using input_update_growth t t.head d

private theorem output_write_growth (t : BackwardPairedInput.OutputTape)
    (a : MarkedBitXorScan.Symbol) : outputCells (t.writeHead a) ≤ outputCells t + 1 := by
  rcases t with ⟨ls,rs⟩
  cases rs <;> simp [outputCells,Tape.writeHead] <;> omega

private theorem output_right_growth (t : BackwardPairedInput.OutputTape) :
    outputCells (t.moveRight .blank) ≤ outputCells t + 1 := by
  rcases t with ⟨ls,rs⟩
  cases rs <;> simp [outputCells,Tape.moveRight] <;> omega

private theorem output_left_growth (t : BackwardPairedInput.OutputTape) :
    outputCells (t.moveLeft .blank) ≤ outputCells t + 1 := by
  rcases t with ⟨ls,rs⟩
  cases ls <;> simp [outputCells,Tape.moveLeft] <;> omega

/-- Pointwise consequence of the actual PR488 write/move implementation. -/
theorem preparation_tape_growth {c d : PrepConfig}
    (h : FixedTapeMachine.step BinaryInputPreparation.machine c = some d) (i : Fin 4) :
    inputCells (d.tapes i) ≤ inputCells (c.tapes i) + 1 := by
  cases ht : BinaryInputPreparation.machine.transition c.state (fun j => (c.tapes j).head) with
  | none => simp [FixedTapeMachine.step,ht] at h
  | some a =>
      simp only [FixedTapeMachine.step,ht,Option.some.injEq] at h
      subst d
      exact input_update_growth (c.tapes i) (a.writes i) (a.moves i)

private theorem pairing_growth (s : BackwardPairedInput.State) :
    BackwardPairedInput.cells (BackwardPairedInput.step s) ≤ BackwardPairedInput.cells s + 1 := by
  have hl := input_move_growth s.leftInput .left
  have hr := input_move_growth s.rightInput .left
  have hwL := output_write_growth s.output .leftMarker
  have hwR := output_write_growth s.output .rightMarker
  have hwP := output_write_growth s.output (.data s.leftBit s.rightBit)
  have hm := output_right_growth s.output
  have hb := output_left_growth s.output
  cases hp : s.phase <;> simp only [BackwardPairedInput.step,hp]
  all_goals repeat first | split
  all_goals simp only [BackwardPairedInput.cells]
  all_goals first | exact Nat.le_add_right _ _ | omega

private theorem xor_growth (s : MarkedBitXorScan.State) :
    MarkedBitXorScan.cells (MarkedBitXorScan.step s) ≤ MarkedBitXorScan.cells s + 1 := by
  have hw := output_write_growth s.tape
  have hm := output_right_growth s.tape
  have hb := output_left_growth s.tape
  change outputCells (MarkedBitXorScan.step s).tape ≤ outputCells s.tape + 1
  cases hp : s.phase <;> simp only [MarkedBitXorScan.step,hp]
  all_goals repeat first | split
  all_goals first | exact Nat.le_add_right _ _ | apply hw | exact hm | exact hb

/-- Handoffs retain all represented tapes; no abstract footprint premise. -/
theorem step_growth (s : State) : cells (step s) ≤ cells s + 4 := by
  cases s with
  | prepare c out a b =>
      cases hs : FixedTapeMachine.step BinaryInputPreparation.machine c with
      | none =>
          simp only [step,hs,PreparedPairXor.enterPair,cells,BackwardPairedInput.cells]
          omega
      | some d =>
          have h0 := preparation_tape_growth hs (0 : Fin 4)
          have h1 := preparation_tape_growth hs (1 : Fin 4)
          have h2 := preparation_tape_growth hs (2 : Fin 4)
          have h3 := preparation_tape_growth hs (3 : Fin 4)
          simp only [step,hs,cells]
          omega
  | pairing left right s =>
      have h := pairing_growth s
      simp only [step]
      split
      · simp only [cells,BackwardPairedInput.cells,BackwardPairedInput.xorEntrance,
          MarkedBitXorScan.cells,outputCells]
        omega
      · simp only [cells]
        omega
  | xor left right wl wr spare s =>
      have h := xor_growth s
      simp only [step,cells]
      omega

theorem run_growth (k : Nat) (s : State) : cells (run k s) ≤ cells s + 4*k := by
  induction k generalizing s with
  | zero => simp only [run,Nat.mul_zero,Nat.add_zero,Nat.le_refl]
  | succ k ih =>
      have h := ih (step s)
      have g := step_growth s
      change cells (run k (step s)) ≤ cells s + 4*(k+1)
      omega

/-- Global halt really stutters, so arbitrarily large observation fuel does
not add a fictitious allocation allowance after the actual stopping time. -/
theorem halt_stutters (s : State) (h : Halted s) (k : Nat) : run k s = s := by
  have hs : step s = s := by
    cases s with
    | prepare => exact False.elim h
    | pairing => exact False.elim h
    | xor left right wl wr spare s =>
        change s.phase = .halt at h
        simp only [step,MarkedBitXorScan.step,h]
  induction k with
  | zero => rfl
  | succ k ih => simpa only [run,hs] using ih

private theorem run_add (m n : Nat) (s : State) : run (m+n) s = run n (run m s) := by
  induction m generalizing s with
  | zero => simp only [Nat.zero_add,run]
  | succ m ih => simpa only [Nat.succ_add,run] using ih (step s)

private theorem ofWord_cells (xs : List Bool) :
    inputCells (FixedTapeMachine.Tape.ofWord xs) = max 1 xs.length := by
  cases xs <;> simp [FixedTapeMachine.Tape.ofWord,FixedTapeMachine.Tape.blank,inputCells] <;> omega

/-- The actual five-tape entrance representation; both empty words still
have their explicit blank head cells. The newly allocated output is empty. -/
theorem initial_cells (xs ys : List Bool) (a b : Bool) :
    cells (initial xs ys a b) = max 1 xs.length + max 1 ys.length + 2 := by
  change inputCells (FixedTapeMachine.Tape.ofWord xs) +
    inputCells (FixedTapeMachine.Tape.ofWord ys) + 1 + 1 + 0 = _
  rw [ofWord_cells,ofWord_cells]

private theorem width_volume (xs ys : List Bool) (a b : Bool) :
    max xs.length ys.length + 3 ≤ cells (initial xs ys a b) := by
  rw [initial_cells]
  omega

/-- Derived actual-volume invoice. Includes the original PR488 preparation,
both real mode switches, backward pairing and marked XOR, every prefix and
post-halt observation. The bound counts finite-alphabet represented cells. -/
theorem machine_linear_resources (xs ys : List Bool) (a b : Bool) :
    ∃ t ≤ 18*cells (initial xs ys a b),
      run t (initial xs ys a b) = final xs ys ∧ Halted (final xs ys) ∧
      (∀ k<t, ¬ Halted (run k (initial xs ys a b))) ∧
      ∀ k, cells (run k (initial xs ys a b)) ≤ 73*cells (initial xs ys a b) := by
  obtain ⟨t,ht,hr,hh,hl⟩ := PreparedPairXor.machine_result xs ys a b
  have hv := width_volume xs ys a b
  have htV : t ≤ 18*cells (initial xs ys a b) := by omega
  refine ⟨t,htV,hr,hh,hl,?_⟩
  intro k
  by_cases hk : k ≤ t
  · have h := run_growth k (initial xs ys a b)
    omega
  · have he : k = t+(k-t) := by omega
    rw [he,run_add,hr,halt_stutters _ hh]
    have h := run_growth t (initial xs ys a b)
    rw [hr] at h
    omega

end CurrentMain.PreparedPairXorSpace

#print axioms CurrentMain.PreparedPairXorSpace.preparation_tape_growth
#print axioms CurrentMain.PreparedPairXorSpace.step_growth
#print axioms CurrentMain.PreparedPairXorSpace.run_growth
#print axioms CurrentMain.PreparedPairXorSpace.halt_stutters
#print axioms CurrentMain.PreparedPairXorSpace.initial_cells
#print axioms CurrentMain.PreparedPairXorSpace.machine_linear_resources
#check @CurrentMain.PreparedPairXorSpace.machine_linear_resources
