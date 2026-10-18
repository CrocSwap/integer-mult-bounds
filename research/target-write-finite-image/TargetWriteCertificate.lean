/-
SPDX-License-Identifier: Apache-2.0

Concrete target-write row certificates for Discussion1548.

STATUS: Locally kernel checked with Lean 4.30.0, import Std only.
The artifact producer supplied source only and did not run Lean. Subsequent
local execution accepted this proof and all 78 theorem axiom reports.
See README.md and REPLAY.json for the separate source-bound execution record.

Mathematical source (not a new prose lemma): Andrey Mas, with substantial
GPT-6 Pro research assistance and Codex coordination/local replay,
PR1546, commit prefix 0980a7c2,
research/projected-three-cycle-minimum/proof.md, section 2; Discussion1503.
Precursor: Gareth Davidson / @bitplane, PR1420,
d19a944897714f2ecae72720b7dafc3e256f2f8d (mathematical commit
 dc6ba012c92470ea830e3b0ff2dab28fbd8126d8); earlier @woklerx PR1105 feedback
lineage. No predecessor Lean source has been copied.

This formalization was developed with substantial GPT-6 Pro assistance
through ChatGPT, as identified in the browser UI. Codex supplied source
briefs, audited and replayed the result, and packaged it without proof repair.
The producer's self-reported variant label was not independently verified.

Conventions:
* M r c is the coefficient of initial register c in output register r.
* Every initial register is independent and dirty: the start is the FULL
  n-by-n identity, including the target's input column.
* Lists are chronological. rawFrom executes the HEAD gate FIRST.
* projectedFrom omits precisely target-DESTINATION gates, not target-source
  gates and not columns or rows of the raw endpoint.
* donorsFrom reads M g.src BEFORE executing g, and collects chronologically.
* Masks have one Boolean coefficient per donor OCCURRENCE, not per distinct
  donor value. Repeated rows are allowed.
* No numeric rank or field/dimension API is defined or claimed here.
-/

import Std

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

namespace TargetWriteCertificate

abbrev Row (n : Nat) := Fin n → Bool
abbrev Matrix (n : Nat) := Fin n → Row n

variable {n : Nat}

def zeroRow : Row n := fun _ => false

def rowXor (u v : Row n) : Row n := fun c => Bool.xor (u c) (v c)

def bitScale (b : Bool) (v : Row n) : Row n := fun c => b && v c

def identity (n : Nat) : Matrix n := fun r c => decide (r = c)

/- Elementary Boolean algebra, proved by constructor cases. -/

private theorem bx_zero (a : Bool) : Bool.xor a false = a := by
  cases a <;> rfl

private theorem bx_left_zero (a : Bool) : Bool.xor false a = a := by
  cases a <;> rfl

private theorem bx_self (a : Bool) : Bool.xor a a = false := by
  cases a <;> rfl

private theorem bx_assoc (a b c : Bool) :
    Bool.xor (Bool.xor a b) c = Bool.xor a (Bool.xor b c) := by
  cases a <;> cases b <;> cases c <;> rfl

private theorem bx_cancel (a b : Bool) : Bool.xor a (Bool.xor a b) = b := by
  cases a <;> cases b <;> rfl

private theorem bx_right_comm (a b c : Bool) :
    Bool.xor (Bool.xor a b) c = Bool.xor (Bool.xor a c) b := by
  cases a <;> cases b <;> cases c <;> rfl

private theorem bx_interchange (a b c d : Bool) :
    Bool.xor (Bool.xor a b) (Bool.xor c d) =
      Bool.xor (Bool.xor a c) (Bool.xor b d) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

private theorem ba_false (a : Bool) : (false && a) = false := by
  cases a <;> rfl

private theorem ba_true (a : Bool) : (true && a) = a := by
  cases a <;> rfl

private theorem ba_xor (b c a : Bool) :
    (Bool.xor b c && a) = Bool.xor (b && a) (c && a) := by
  cases b <;> cases c <;> cases a <;> rfl

private theorem ba_not (b a : Bool) :
    (Bool.not b && a) = Bool.xor a (b && a) := by
  cases b <;> cases a <;> rfl

@[simp] theorem rowXor_zero (u : Row n) : rowXor u zeroRow = u := by
  funext c
  exact bx_zero (u c)

@[simp] theorem zero_rowXor (u : Row n) : rowXor zeroRow u = u := by
  funext c
  exact bx_left_zero (u c)

@[simp] theorem rowXor_self (u : Row n) : rowXor u u = zeroRow := by
  funext c
  exact bx_self (u c)

theorem rowXor_assoc (u v t : Row n) :
    rowXor (rowXor u v) t = rowXor u (rowXor v t) := by
  funext c
  exact bx_assoc (u c) (v c) (t c)

@[simp] theorem rowXor_cancel (u v : Row n) : rowXor u (rowXor u v) = v := by
  funext c
  exact bx_cancel (u c) (v c)

theorem rowXor_right_comm (u v t : Row n) :
    rowXor (rowXor u v) t = rowXor (rowXor u t) v := by
  funext c
  exact bx_right_comm (u c) (v c) (t c)

theorem rowXor_interchange (u v t z : Row n) :
    rowXor (rowXor u v) (rowXor t z) =
      rowXor (rowXor u t) (rowXor v z) := by
  funext c
  exact bx_interchange (u c) (v c) (t c) (z c)

theorem rowXor_eq_zero {u v : Row n} (h : rowXor u v = zeroRow) : u = v := by
  have h' := congrArg (rowXor u) h
  have h'' : v = u := by simpa only [rowXor_cancel, rowXor_zero] using h'
  exact h''.symm

@[simp] theorem bitScale_false (v : Row n) : bitScale false v = zeroRow := by
  funext c
  exact ba_false (v c)

@[simp] theorem bitScale_true (v : Row n) : bitScale true v = v := by
  funext c
  exact ba_true (v c)

theorem bitScale_xor (b c : Bool) (v : Row n) :
    bitScale (Bool.xor b c) v = rowXor (bitScale b v) (bitScale c v) := by
  funext j
  exact ba_xor b c (v j)

theorem bitScale_not (b : Bool) (v : Row n) :
    bitScale (Bool.not b) v = rowXor v (bitScale b v) := by
  funext j
  exact ba_not b (v j)

/- Concrete finite combinations. Mismatched masks are totalized by truncation;
   every advertised certificate proves EXACT equality of lengths. -/

def combination : List (Row n) → List Bool → Row n
  | [], _ => zeroRow
  | _ :: _, [] => zeroRow
  | v :: vs, b :: bs => rowXor (bitScale b v) (combination vs bs)

def sumRows : List (Row n) → Row n
  | [] => zeroRow
  | v :: vs => rowXor v (sumRows vs)

def xorMasks : List Bool → List Bool → List Bool
  | b :: bs, c :: cs => Bool.xor b c :: xorMasks bs cs
  | _, _ => []

private theorem list_nil_of_length_zero {α : Type} (xs : List α)
    (h : xs.length = 0) : xs = [] := by
  cases xs with
  | nil => rfl
  | cons x xs => simp at h

theorem sumRows_append (vs ws : List (Row n)) :
    sumRows (vs ++ ws) = rowXor (sumRows vs) (sumRows ws) := by
  induction vs with
  | nil => simp [sumRows]
  | cons v vs ih =>
      change rowXor v (sumRows (vs ++ ws)) =
        rowXor (rowXor v (sumRows vs)) (sumRows ws)
      rw [ih]
      exact (rowXor_assoc v (sumRows vs) (sumRows ws)).symm

theorem sumRows_snoc (vs : List (Row n)) (v : Row n) :
    sumRows (vs ++ [v]) = rowXor (sumRows vs) v := by
  simp [sumRows_append, sumRows]

theorem combination_append (vs : List (Row n)) (bs : List Bool)
    (hlen : bs.length = vs.length) (ws : List (Row n)) (cs : List Bool) :
    combination (vs ++ ws) (bs ++ cs) =
      rowXor (combination vs bs) (combination ws cs) := by
  induction vs generalizing bs with
  | nil =>
      have hb : bs = [] := list_nil_of_length_zero bs hlen
      subst bs
      simp [combination]
  | cons v vs ih =>
      cases bs with
      | nil => simp at hlen
      | cons b bs =>
          have ht : bs.length = vs.length := Nat.succ.inj hlen
          change rowXor (bitScale b v) (combination (vs ++ ws) (bs ++ cs)) =
            rowXor (rowXor (bitScale b v) (combination vs bs)) (combination ws cs)
          rw [ih bs ht]
          exact (rowXor_assoc (bitScale b v) (combination vs bs)
            (combination ws cs)).symm

theorem combination_snoc (vs : List (Row n)) (bs : List Bool)
    (hlen : bs.length = vs.length) (v : Row n) (b : Bool) :
    combination (vs ++ [v]) (bs ++ [b]) =
      rowXor (combination vs bs) (bitScale b v) := by
  simpa only [combination, rowXor_zero] using
    combination_append vs bs hlen [v] [b]

/-- Same-length masks are combined by pointwise Boolean XOR. -/
theorem combination_xorMasks (vs : List (Row n)) (bs cs : List Bool)
    (hb : bs.length = vs.length) (hc : cs.length = vs.length) :
    (xorMasks bs cs).length = vs.length ∧
      combination vs (xorMasks bs cs) =
        rowXor (combination vs bs) (combination vs cs) := by
  induction vs generalizing bs cs with
  | nil =>
      have hb0 : bs = [] := list_nil_of_length_zero bs hb
      have hc0 : cs = [] := list_nil_of_length_zero cs hc
      subst bs
      subst cs
      constructor
      · rfl
      · rfl
  | cons v vs ih =>
      cases bs with
      | nil => simp at hb
      | cons b bs =>
          cases cs with
          | nil => simp at hc
          | cons c cs =>
              have hb' : bs.length = vs.length := Nat.succ.inj hb
              have hc' : cs.length = vs.length := Nat.succ.inj hc
              rcases ih bs cs hb' hc' with ⟨hsize, hvalue⟩
              constructor
              · change (xorMasks bs cs).length + 1 = vs.length + 1
                exact congrArg (fun k : Nat => k + 1) hsize
              · change
                  rowXor (bitScale (Bool.xor b c) v)
                    (combination vs (xorMasks bs cs)) =
                  rowXor (rowXor (bitScale b v) (combination vs bs))
                    (rowXor (bitScale c v) (combination vs cs))
                rw [hvalue, bitScale_xor]
                exact rowXor_interchange (bitScale b v) (bitScale c v)
                  (combination vs bs) (combination vs cs)

/-- Complementing a mask adds the XOR of ALL donor occurrences. -/
theorem combination_not (vs : List (Row n)) (bs : List Bool)
    (hlen : bs.length = vs.length) :
    combination vs (bs.map Bool.not) =
      rowXor (sumRows vs) (combination vs bs) := by
  induction vs generalizing bs with
  | nil =>
      have hb : bs = [] := list_nil_of_length_zero bs hlen
      subst bs
      rfl
  | cons v vs ih =>
      cases bs with
      | nil => simp at hlen
      | cons b bs =>
          have ht : bs.length = vs.length := Nat.succ.inj hlen
          change
            rowXor (bitScale (Bool.not b) v) (combination vs (bs.map Bool.not)) =
            rowXor (rowXor v (sumRows vs))
              (rowXor (bitScale b v) (combination vs bs))
          rw [ih bs ht, bitScale_not]
          exact rowXor_interchange v (bitScale b v) (sumRows vs) (combination vs bs)

/-- Deterministic deletion of the first coefficient under a zero-sum relation.
    A selected first donor is replaced by the sum of all remaining donors. -/
def eraseFirstCoefficient : List Bool → List Bool
  | [] => []
  | false :: bs => bs
  | true :: bs => bs.map Bool.not

theorem eliminate_first_donor (v : Row n) (vs : List (Row n)) (bs : List Bool)
    (hlen : bs.length = (v :: vs).length)
    (hzero : sumRows (v :: vs) = zeroRow) :
    (eraseFirstCoefficient bs).length = vs.length ∧
      combination vs (eraseFirstCoefficient bs) = combination (v :: vs) bs := by
  have hv : v = sumRows vs := rowXor_eq_zero hzero
  cases bs with
  | nil => simp at hlen
  | cons b bs =>
      have ht : bs.length = vs.length := Nat.succ.inj hlen
      cases b with
      | false =>
          constructor
          · exact ht
          · simp [eraseFirstCoefficient, combination]
      | true =>
          constructor
          · simpa only [eraseFirstCoefficient, List.length_map] using ht
          · change combination vs (bs.map Bool.not) =
              rowXor (bitScale true v) (combination vs bs)
            rw [combination_not vs bs ht, bitScale_true, hv]

/- Concrete gate-word semantics; no histories are assumed. -/

structure Gate (n : Nat) where
  dst : Fin n
  src : Fin n
  distinct : dst ≠ src

def applyGate (g : Gate n) (M : Matrix n) : Matrix n := fun r =>
  if r = g.dst then rowXor (M r) (M g.src) else M r

/-- The donor itself is unchanged by this single distinct-register gate.
    Thus immediately-after-the-SAME-gate donor sampling is equivalent; later
    sampling, or projected-state sampling, need not be equivalent. -/
theorem applyGate_donor_unchanged (g : Gate n) (M : Matrix n) :
    applyGate g M g.src = M g.src := by
  have h : g.src ≠ g.dst := fun e => g.distinct e.symm
  simp [applyGate, h]

def projectedStep (y : Fin n) (g : Gate n) (M : Matrix n) : Matrix n :=
  if g.dst = y then M else applyGate g M

def rawFrom : List (Gate n) → Matrix n → Matrix n
  | [], M => M
  | g :: w, M => rawFrom w (applyGate g M)

def projectedFrom (y : Fin n) : List (Gate n) → Matrix n → Matrix n
  | [], M => M
  | g :: w, M => projectedFrom y w (projectedStep y g M)

def donorsFrom (y : Fin n) : List (Gate n) → Matrix n → List (Row n)
  | [], _ => []
  | g :: w, M =>
      if g.dst = y then M g.src :: donorsFrom y w (applyGate g M)
      else donorsFrom y w (applyGate g M)

def targetCount (y : Fin n) : List (Gate n) → Nat
  | [] => 0
  | g :: w => if g.dst = y then targetCount y w + 1 else targetCount y w

def raw (w : List (Gate n)) : Matrix n := rawFrom w (identity n)

def projected (y : Fin n) (w : List (Gate n)) : Matrix n :=
  projectedFrom y w (identity n)

def donors (y : Fin n) (w : List (Gate n)) : List (Row n) :=
  donorsFrom y w (identity n)

def defect (R P : Matrix n) : Matrix n := fun r => rowXor (R r) (P r)

/-- Chronological projection is literally replay of the filtered word. -/
theorem projectedFrom_eq_filter (y : Fin n) (w : List (Gate n)) (M : Matrix n) :
    projectedFrom y w M = rawFrom (w.filter (fun g => decide (g.dst ≠ y))) M := by
  induction w generalizing M with
  | nil => rfl
  | cons g w ih =>
      by_cases h : g.dst = y <;>
        simp [projectedFrom, projectedStep, List.filter, rawFrom, h, ih]

theorem projected_eq_filter (y : Fin n) (w : List (Gate n)) :
    projected y w = raw (w.filter (fun g => decide (g.dst ≠ y))) := by
  exact projectedFrom_eq_filter y w (identity n)

theorem rawFrom_append (u v : List (Gate n)) (M : Matrix n) :
    rawFrom (u ++ v) M = rawFrom v (rawFrom u M) := by
  induction u generalizing M with
  | nil => rfl
  | cons g u ih => simp [rawFrom, ih]

theorem projectedFrom_append (y : Fin n) (u v : List (Gate n)) (M : Matrix n) :
    projectedFrom y (u ++ v) M = projectedFrom y v (projectedFrom y u M) := by
  induction u generalizing M with
  | nil => rfl
  | cons g u ih => simp [projectedFrom, ih]

theorem donorsFrom_append (y : Fin n) (u v : List (Gate n)) (M : Matrix n) :
    donorsFrom y (u ++ v) M =
      donorsFrom y u M ++ donorsFrom y v (rawFrom u M) := by
  induction u generalizing M with
  | nil => simp [donorsFrom, rawFrom]
  | cons g u ih =>
      by_cases h : g.dst = y <;>
        simp [donorsFrom, rawFrom, h, ih]

/-- Appending a target write records precisely its full raw PRE-gate donor. -/
theorem donors_target_snoc (y : Fin n) (u : List (Gate n)) (g : Gate n)
    (h : g.dst = y) :
    donors y (u ++ [g]) = donors y u ++ [(raw u) g.src] := by
  simp [donors, donorsFrom_append, donorsFrom, raw, h]

theorem donors_retained_snoc (y : Fin n) (u : List (Gate n)) (g : Gate n)
    (h : g.dst ≠ y) : donors y (u ++ [g]) = donors y u := by
  simp [donors, donorsFrom_append, donorsFrom, h]

theorem donorsFrom_length (y : Fin n) (w : List (Gate n)) (M : Matrix n) :
    (donorsFrom y w M).length = targetCount y w := by
  induction w generalizing M with
  | nil => rfl
  | cons g w ih =>
      by_cases h : g.dst = y <;> simp [donorsFrom, targetCount, h, ih]

theorem donors_length (y : Fin n) (w : List (Gate n)) :
    (donors y w).length = targetCount y w :=
  donorsFrom_length y w (identity n)

theorem targetCount_eq_filter_length (y : Fin n) (w : List (Gate n)) :
    targetCount y w = (w.filter (fun g => decide (g.dst = y))).length := by
  induction w with
  | nil => rfl
  | cons g w ih =>
      by_cases h : g.dst = y <;> simp [targetCount, List.filter, h, ih]

/-- Retained row operation, with row/column conventions exposed. -/
theorem defect_retained (g : Gate n) (R P : Matrix n) :
    defect (applyGate g R) (applyGate g P) = applyGate g (defect R P) := by
  funext r
  by_cases h : r = g.dst
  · simpa only [defect, applyGate, if_pos h] using
      rowXor_interchange (R r) (R g.src) (P r) (P g.src)
  · simp [defect, applyGate, h]

/-- A skipped target write injects precisely the raw pre-gate donor. -/
theorem defect_target_write (y : Fin n) (g : Gate n) (R P : Matrix n)
    (r : Fin n) (hg : g.dst = y) :
    defect (applyGate g R) P r =
      if r = y then rowXor (defect R P r) (R g.src) else defect R P r := by
  by_cases hr : r = y
  · subst r
    simpa [defect, applyGate, hg] using
      rowXor_right_comm (R y) (R g.src) (P y)
  · simp [defect, applyGate, hg, hr]

/- Paired executable scanner with COMPUTED coefficient masks.
   The state has data fields only: no assumed invariant or certificate fields. -/

structure ScanState (n : Nat) where
  rawState : Matrix n
  projectedState : Matrix n
  recorded : List (Row n)
  coefficients : Fin n → List Bool

def initialState (n : Nat) : ScanState n where
  rawState := identity n
  projectedState := identity n
  recorded := []
  coefficients := fun _ => []

def scanStep (y : Fin n) (g : Gate n) (S : ScanState n) : ScanState n :=
  if g.dst = y then
    { rawState := applyGate g S.rawState
      projectedState := S.projectedState
      recorded := S.recorded ++ [S.rawState g.src]
      coefficients := fun r => S.coefficients r ++ [decide (r = y)] }
  else
    { rawState := applyGate g S.rawState
      projectedState := applyGate g S.projectedState
      recorded := S.recorded
      coefficients := fun r =>
        if r = g.dst then xorMasks (S.coefficients r) (S.coefficients g.src)
        else S.coefficients r }

def scanFrom (y : Fin n) : List (Gate n) → ScanState n → ScanState n
  | [], S => S
  | g :: w, S => scanFrom y w (scanStep y g S)

def scan (y : Fin n) (w : List (Gate n)) : ScanState n :=
  scanFrom y w (initialState n)

theorem scanFrom_append (y : Fin n) (u v : List (Gate n)) (S : ScanState n) :
    scanFrom y (u ++ v) S = scanFrom y v (scanFrom y u S) := by
  induction u generalizing S with
  | nil => rfl
  | cons g u ih => simp [scanFrom, ih]

theorem scanFrom_raw (y : Fin n) (w : List (Gate n)) (S : ScanState n) :
    (scanFrom y w S).rawState = rawFrom w S.rawState := by
  induction w generalizing S with
  | nil => rfl
  | cons g w ih =>
      by_cases h : g.dst = y <;> simp [scanFrom, scanStep, rawFrom, h, ih]

theorem scanFrom_projected (y : Fin n) (w : List (Gate n)) (S : ScanState n) :
    (scanFrom y w S).projectedState = projectedFrom y w S.projectedState := by
  induction w generalizing S with
  | nil => rfl
  | cons g w ih =>
      by_cases h : g.dst = y <;>
        simp [scanFrom, scanStep, projectedFrom, projectedStep, h, ih]

theorem scanFrom_recorded (y : Fin n) (w : List (Gate n)) (S : ScanState n) :
    (scanFrom y w S).recorded = S.recorded ++ donorsFrom y w S.rawState := by
  induction w generalizing S with
  | nil => simp [scanFrom, donorsFrom]
  | cons g w ih =>
      by_cases h : g.dst = y <;>
        simp [scanFrom, scanStep, donorsFrom, h, ih, List.append_assoc]

theorem scan_raw (y : Fin n) (w : List (Gate n)) :
    (scan y w).rawState = raw w := by
  simpa [scan, initialState, raw] using scanFrom_raw y w (initialState n)

theorem scan_projected (y : Fin n) (w : List (Gate n)) :
    (scan y w).projectedState = projected y w := by
  simpa [scan, initialState, projected] using scanFrom_projected y w (initialState n)

theorem scan_recorded (y : Fin n) (w : List (Gate n)) :
    (scan y w).recorded = donors y w := by
  simpa [scan, initialState, donors] using scanFrom_recorded y w (initialState n)

/-- A proposition PROVED below from execution, not a field assumed of a word. -/
def ScanInvariant (y : Fin n) (S : ScanState n) : Prop :=
  (∀ r, (S.coefficients r).length = S.recorded.length) ∧
  (∀ r, combination S.recorded (S.coefficients r) =
    defect S.rawState S.projectedState r) ∧
  S.rawState y = rowXor ((identity n) y) (sumRows S.recorded)

theorem initial_invariant (y : Fin n) : ScanInvariant y (initialState n) := by
  simp [ScanInvariant, initialState, combination, defect, sumRows]

/-- Concrete one-gate preservation, including target-source feedback. -/
theorem scanStep_invariant (y : Fin n) (g : Gate n) (S : ScanState n)
    (hS : ScanInvariant y S) : ScanInvariant y (scanStep y g S) := by
  rcases hS with ⟨hlen, hrep, htarget⟩
  by_cases hg : g.dst = y
  · simp only [scanStep, if_pos hg, ScanInvariant]
    refine ⟨?_, ?_, ?_⟩
    · intro r
      simpa only [List.length_append, List.length_singleton] using
        congrArg (fun k : Nat => k + 1) (hlen r)
    · intro r
      rw [combination_snoc S.recorded (S.coefficients r) (hlen r)
        (S.rawState g.src) (decide (r = y))]
      rw [hrep r, defect_target_write y g S.rawState S.projectedState r hg]
      by_cases hr : r = y <;> simp [hr]
    · have hupdate : applyGate g S.rawState y =
          rowXor (S.rawState y) (S.rawState g.src) := by
        simp [applyGate, hg]
      rw [hupdate, htarget, sumRows_snoc]
      exact rowXor_assoc ((identity n) y) (sumRows S.recorded) (S.rawState g.src)
  · simp only [scanStep, if_neg hg, ScanInvariant]
    refine ⟨?_, ?_, ?_⟩
    · intro r
      by_cases hr : r = g.dst
      · simp only [if_pos hr]
        exact (combination_xorMasks S.recorded (S.coefficients r)
          (S.coefficients g.src) (hlen r) (hlen g.src)).1
      · simpa only [if_neg hr] using hlen r
    · intro r
      rw [defect_retained g S.rawState S.projectedState]
      by_cases hr : r = g.dst
      · simp only [if_pos hr, applyGate]
        rw [(combination_xorMasks S.recorded (S.coefficients r)
          (S.coefficients g.src) (hlen r) (hlen g.src)).2, hrep r, hrep g.src]
      · simpa only [applyGate, if_neg hr] using hrep r
    · have hy : y ≠ g.dst := fun h => hg h.symm
      simpa [applyGate, hy] using htarget

theorem scanFrom_invariant (y : Fin n) (w : List (Gate n)) (S : ScanState n)
    (hS : ScanInvariant y S) : ScanInvariant y (scanFrom y w S) := by
  induction w generalizing S with
  | nil => exact hS
  | cons g w ih =>
      exact ih (scanStep y g S) (scanStep_invariant y g S hS)

theorem scan_invariant (y : Fin n) (w : List (Gate n)) :
    ScanInvariant y (scan y w) :=
  scanFrom_invariant y w (initialState n) (initial_invariant y)

/-- Universal computed m-donor certificate, before any restoration assumption. -/
theorem row_generation (y : Fin n) (w : List (Gate n)) (r : Fin n) :
    ((scan y w).coefficients r).length = (donors y w).length ∧
      combination (donors y w) ((scan y w).coefficients r) =
        defect (raw w) (projected y w) r := by
  have h := scan_invariant y w
  rcases h with ⟨hlen, hrep, _⟩
  constructor
  · simpa only [scan_recorded] using hlen r
  · simpa only [scan_recorded, scan_raw, scan_projected] using hrep r

/-- The same theorem at EVERY actual chronological prefix. -/
theorem prefix_row_generation (y : Fin n) (w : List (Gate n)) (t : Nat)
    (r : Fin n) :
    ((scan y (w.take t)).coefficients r).length = (donors y (w.take t)).length ∧
      combination (donors y (w.take t)) ((scan y (w.take t)).coefficients r) =
        defect (raw (w.take t)) (projected y (w.take t)) r :=
  row_generation y (w.take t) r

theorem target_telescope (y : Fin n) (w : List (Gate n)) :
    (raw w) y = rowXor ((identity n) y) (sumRows (donors y w)) := by
  have h := (scan_invariant y w).2.2
  simpa only [scan_raw, scan_recorded] using h

/-- Raw restoration forces XOR of all actual recorded donors to be zero. -/
theorem restored_donor_sum_zero (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) : sumRows (donors y w) = zeroRow := by
  have ht := target_telescope y w
  rw [hraw] at ht
  have h := congrArg (rowXor ((identity n) y)) ht.symm
  simpa only [rowXor_cancel, rowXor_self] using h

/- Deterministic final output: drop the first ACTUAL donor occurrence and
   eliminate its coefficient separately in every computed row mask. -/

def retainedDonors (y : Fin n) (w : List (Gate n)) : List (Row n) :=
  (donors y w).tail

def reducedCoefficients (y : Fin n) (w : List (Gate n)) (r : Fin n) : List Bool :=
  eraseFirstCoefficient ((scan y w).coefficients r)

/-- MAIN DETERMINISTIC THEOREM.
    Exactly m-1 actual donor occurrences suffice, with computed masks.
    This is NOT a numeric-rank theorem. -/
theorem restored_row_certificate (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hpos : 0 < targetCount y w) :
    (∃ first : Row n, donors y w = first :: retainedDonors y w) ∧
    (retainedDonors y w).length = targetCount y w - 1 ∧
    (∀ r, (reducedCoefficients y w r).length = (retainedDonors y w).length ∧
      combination (retainedDonors y w) (reducedCoefficients y w r) =
        rowXor ((identity n) r) (projected y w r)) := by
  have hzero := restored_donor_sum_zero y w hraw
  have hcount := donors_length y w
  cases hd : donors y w with
  | nil =>
      have hz : targetCount y w = 0 := by
        simpa only [hd, List.length_nil] using hcount.symm
      simp [hz] at hpos
  | cons v vs =>
      have hrest : retainedDonors y w = vs := by
        simp only [retainedDonors, hd, List.tail_cons]
      refine ⟨?_, ?_, ?_⟩
      · refine ⟨v, ?_⟩
        simpa only [hd, hrest] using (rfl : v :: vs = v :: vs)
      · have hc : vs.length + 1 = targetCount y w := by
          simpa only [hd, List.length_cons] using hcount
        simpa [hrest] using congrArg (fun k : Nat => k - 1) hc
      · intro r
        have hg := row_generation y w r
        have hl : ((scan y w).coefficients r).length = (v :: vs).length := by
          simpa only [hd] using hg.1
        have hz : sumRows (v :: vs) = zeroRow := by
          simpa only [hd] using hzero
        have he := eliminate_first_donor v vs ((scan y w).coefficients r) hl hz
        have hfull : combination (v :: vs) ((scan y w).coefficients r) =
            rowXor ((identity n) r) (projected y w r) := by
          simpa only [hd, defect, hraw] using hg.2
        constructor
        · simpa only [reducedCoefficients, hrest] using he.1
        · simpa only [reducedCoefficients, hrest] using he.2.trans hfull

/-- Existential packaging of the same COMPUTED certificate, with an at-most
    bound and occurrence-level connection to the collected donor list. -/
theorem restored_at_most_certificate (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hpos : 0 < targetCount y w) :
    ∃ G : List (Row n), ∃ C : Fin n → List Bool,
      (∃ first : Row n, donors y w = first :: G) ∧
      G.length ≤ targetCount y w - 1 ∧
      (∀ r, (C r).length = G.length ∧
        combination G (C r) = rowXor ((identity n) r) (projected y w r)) := by
  rcases restored_row_certificate y w hraw hpos with ⟨hactual, hsize, hrows⟩
  refine ⟨retainedDonors y w, reducedCoefficients y w, hactual, ?_, hrows⟩
  simpa only [hsize] using Nat.le_refl (targetCount y w - 1)

/-- No-target case, even WITHOUT the raw-restoration assumption. -/
theorem zero_target_projected_eq_raw (y : Fin n) (w : List (Gate n))
    (hzero : targetCount y w = 0) : projected y w = raw w := by
  have hd : donors y w = [] := by
    apply list_nil_of_length_zero
    rw [donors_length, hzero]
  funext r
  have hg := (row_generation y w r).2
  rw [hd] at hg
  have heq : raw w r = projected y w r := rowXor_eq_zero hg.symm
  exact heq.symm

theorem zero_target_restored (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hzero : targetCount y w = 0) :
    projected y w = identity n :=
  (zero_target_projected_eq_raw y w hzero).trans hraw

/- Small kernel-decision fixtures. These are proof DECLARATIONS, not reports
   of execution. `decide` uses ordinary kernel reduction, not native_decide.
   The whole file still needs the exact-version kernel replay. -/

namespace Fixtures

def a2 : Fin 2 := ⟨0, by decide⟩
def y2 : Fin 2 := ⟨1, by decide⟩
def write2 : Gate 2 := ⟨y2, a2, by decide⟩
def feedback2 : Gate 2 := ⟨a2, y2, by decide⟩

/-- (y+=a; a+=y)^3 is a raw identity; projection retains three a+=y gates. -/
def feedbackWord : List (Gate 2) :=
  [write2, feedback2, write2, feedback2, write2, feedback2]

private theorem cons_congr {α : Type} {a b : α} {xs ys : List α}
    (ha : a = b) (ht : xs = ys) : a :: xs = b :: ys := by
  cases ha
  cases ht
  rfl

theorem feedback_restores : raw feedbackWord = identity 2 := by
  funext r c
  revert r c
  decide

theorem feedback_projection :
    projected y2 feedbackWord = applyGate feedback2 (identity 2) := by
  funext r c
  revert r c
  decide

theorem feedback_actual_donors :
    donors y2 feedbackWord =
      [(identity 2) a2, (identity 2) y2, rowXor ((identity 2) a2) ((identity 2) y2)] := by
  refine cons_congr ?_ (cons_congr ?_ (cons_congr ?_ rfl))
  all_goals
    funext c
    revert c
    decide

theorem feedback_computed_masks :
    (retainedDonors y2 feedbackWord).length = 2 ∧
    reducedCoefficients y2 feedbackWord a2 = [true, false] ∧
    reducedCoefficients y2 feedbackWord y2 = [false, false] := by
  decide

theorem feedback_certificate :
    ∀ r, (reducedCoefficients y2 feedbackWord r).length =
        (retainedDonors y2 feedbackWord).length ∧
      combination (retainedDonors y2 feedbackWord)
        (reducedCoefficients y2 feedbackWord r) =
        rowXor ((identity 2) r) (projected y2 feedbackWord r) := by
  exact (restored_row_certificate y2 feedbackWord feedback_restores (by decide)).2.2

/-- Total indexing only for these finite failure controls. -/
def rowAt : List (Row n) → Nat → Row n
  | [], _ => zeroRow
  | v :: _, 0 => v
  | _ :: vs, k + 1 => rowAt vs k

/-- Sampling the second donor from the FINAL raw state gives a wrong row. -/
theorem final_state_sampling_is_wrong :
    rowAt (donors y2 feedbackWord) 1 ≠ raw feedbackWord a2 := by
  intro h
  have hbad : (rowAt (donors y2 feedbackWord) 1) a2 ≠ raw feedbackWord a2 a2 := by
    decide
  exact hbad (congrFun h a2)

/-- Sampling from the PROJECTED prefix instead of the raw prefix is wrong. -/
theorem projected_state_sampling_is_wrong :
    rowAt (donors y2 feedbackWord) 1 ≠ projected y2 (feedbackWord.take 2) a2 := by
  intro h
  have hbad : (rowAt (donors y2 feedbackWord) 1) a2 ≠
      projected y2 (feedbackWord.take 2) a2 a2 := by
    decide
  exact hbad (congrFun h a2)

def a3 : Fin 3 := ⟨0, by decide⟩
def b3 : Fin 3 := ⟨1, by decide⟩
def y3 : Fin 3 := ⟨2, by decide⟩
def ya : Gate 3 := ⟨y3, a3, by decide⟩
def byGate : Gate 3 := ⟨b3, y3, by decide⟩
def ba : Gate 3 := ⟨b3, a3, by decide⟩
def ay : Gate 3 := ⟨a3, y3, by decide⟩
def yb : Gate 3 := ⟨y3, b3, by decide⟩

/-- Raw commutator identity, with nonidentity projected HELPER block. -/
def commutatorWord : List (Gate 3) := [ya, byGate, ya, byGate, ba]

theorem commutator_restores : raw commutatorWord = identity 3 := by
  funext r c
  revert r c
  decide

theorem commutator_projection :
    projected y3 commutatorWord = applyGate ba (identity 3) := by
  funext r c
  revert r c
  decide

/-- Concrete helper/helper entry: the projected endpoint is NOT the raw block. -/
theorem raw_helper_block_is_wrong :
    projected y3 commutatorWord b3 a3 ≠ raw commutatorWord b3 a3 := by
  decide

theorem commutator_certificate :
    (retainedDonors y3 commutatorWord).length = 1 ∧
    (∀ r, (reducedCoefficients y3 commutatorWord r).length =
        (retainedDonors y3 commutatorWord).length ∧
      combination (retainedDonors y3 commutatorWord)
        (reducedCoefficients y3 commutatorWord r) =
        rowXor ((identity 3) r) (projected y3 commutatorWord r)) := by
  constructor
  · decide
  · exact (restored_row_certificate y3 commutatorWord commutator_restores
      (by decide)).2.2

/-- The two retained gates do not commute; the interleaved target write is skipped. -/
def chronologyWord : List (Gate 3) := [ay, yb, ba]

theorem chronological_projection :
    projected y3 chronologyWord = raw [ay, ba] := by
  exact projected_eq_filter y3 chronologyWord

/-- Reversing retained gates fails at a specific full-matrix entry. -/
theorem reversed_projection_is_wrong :
    projected y3 chronologyWord b3 y3 ≠ raw [ba, ay] b3 y3 := by
  decide

/-- A nonempty zero-target word restores and is handled by the zero case. -/
theorem zero_target_fixture : projected y3 [ay, ay] = identity 3 := by
  apply zero_target_restored
  · funext r c
    revert r c
    decide
  · decide

end Fixtures

/- Exact-version replay must capture these commands' ACTUAL output.
   No expected axiom list is substituted for an observed receipt. -/

#print axioms rowXor_eq_zero
#print axioms combination_append
#print axioms combination_xorMasks
#print axioms combination_not
#print axioms eliminate_first_donor
#print axioms applyGate_donor_unchanged
#print axioms projectedFrom_eq_filter
#print axioms projected_eq_filter
#print axioms rawFrom_append
#print axioms projectedFrom_append
#print axioms donorsFrom_append
#print axioms donors_target_snoc
#print axioms donors_retained_snoc
#print axioms donorsFrom_length
#print axioms donors_length
#print axioms targetCount_eq_filter_length
#print axioms defect_retained
#print axioms defect_target_write
#print axioms scanFrom_append
#print axioms scanFrom_raw
#print axioms scanFrom_projected
#print axioms scanFrom_recorded
#print axioms scan_raw
#print axioms scan_projected
#print axioms scan_recorded
#print axioms initial_invariant
#print axioms scanStep_invariant
#print axioms scanFrom_invariant
#print axioms scan_invariant
#print axioms row_generation
#print axioms prefix_row_generation
#print axioms target_telescope
#print axioms restored_donor_sum_zero
#print axioms restored_row_certificate
#print axioms restored_at_most_certificate
#print axioms zero_target_projected_eq_raw
#print axioms zero_target_restored
#print axioms Fixtures.feedback_restores
#print axioms Fixtures.feedback_projection
#print axioms Fixtures.feedback_actual_donors
#print axioms Fixtures.feedback_computed_masks
#print axioms Fixtures.feedback_certificate
#print axioms Fixtures.final_state_sampling_is_wrong
#print axioms Fixtures.projected_state_sampling_is_wrong
#print axioms Fixtures.commutator_restores
#print axioms Fixtures.commutator_projection
#print axioms Fixtures.raw_helper_block_is_wrong
#print axioms Fixtures.commutator_certificate
#print axioms Fixtures.chronological_projection
#print axioms Fixtures.reversed_projection_is_wrong
#print axioms Fixtures.zero_target_fixture

end TargetWriteCertificate
