/-
SPDX-License-Identifier: Apache-2.0

Finite-image successor to PR1598, Discussion1548.
STATUS: SOURCE ONLY / NOT YET KERNEL CHECKED by this producer.
Target: Lean 4.30.0, commit d024af099ca4bf2c86f649261ebf59565dc8c622.

Import the UNCHANGED TargetWriteCertificate.lean at PR1598 head
96ef13e9c0aada8730ace8624fde2de1e3ddb1b9, SHA256
5cb5cab0eb14cc53739d801963a50ad4ffeb8ca112ab994bfa856feeb81cd4b4.
No dependency source is copied or modified in this successor.

Written lemma and concrete execution certificate: Andrey Mas, with
substantial GPT-6 Pro assistance, PR1546 and PR1598. Codex supplied
coordination, source pins, and separate local verification, not the
mathematical or Lean proofs here. Precursor: Gareth Davidson / @bitplane,
PR1420, d19a944897714f2ecae72720b7dafc3e256f2f8d (mathematical commit
dc6ba012c92470ea830e3b0ff2dab28fbd8126d8); earlier @woklerx PR1105
feedback lineage. This successor credits substantial GPT-6 Pro formalization assistance
through ChatGPT at the user-requested setting. The requested Pro setting is not an independent
backend-attestation claim. No novelty is claimed for the written lemma.

M r c means coefficient of INPUT c in OUTPUT r. Action is M*x, NOT M^T*x.
All input coordinates, including the arbitrary dirty target, are retained.
The cardinality statement is an explicit injection of the actual image
subtype into Fin (2^(m-1)). No numeric rank/dimension API is introduced.
Classical.choose is used only to select an input witness for each actual
output; the donor measurements, decoder, and input bit code are executable.
-/

import Std
import Init.Data.List.FinRange
import TargetWriteCertificate

set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000

namespace TargetWriteFiniteImage

open TargetWriteCertificate

variable {n : Nat}

/- Small Boolean equalities, with ordinary constructor proofs. -/

theorem xor_false (a : Bool) : Bool.xor a false = a := by
  cases a <;> rfl

theorem false_xor (a : Bool) : Bool.xor false a = a := by
  cases a <;> rfl

theorem and_xor_left (a b c : Bool) :
    (Bool.xor a b && c) = Bool.xor (a && c) (b && c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem and_xor_right (a b c : Bool) :
    (a && Bool.xor b c) = Bool.xor (a && b) (a && c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem xor_interchange (a b c d : Bool) :
    Bool.xor (Bool.xor a b) (Bool.xor c d) =
      Bool.xor (Bool.xor a c) (Bool.xor b d) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

/- Actual full-coordinate matrix-vector action. List.finRange n lists all
   Fin n coordinates once, in increasing order. No coordinates are omitted. -/

def dotOn (cols : List (Fin n)) (u x : Row n) : Bool :=
  match cols with
  | [] => false
  | c :: cs => Bool.xor (u c && x c) (dotOn cs u x)

def dot (u x : Row n) : Bool := dotOn (List.finRange n) u x

def matrixAction (M : Matrix n) (x : Row n) : Row n := fun r => dot (M r) x

def InImage (M : Matrix n) (z : Row n) : Prop :=
  ∃ x : Row n, matrixAction M x = z

/-- Values are actual full-register output vectors, with an input witness. -/
def ActualImage (M : Matrix n) := { z : Row n // InImage M z }

def projectedDefect (y : Fin n) (w : List (Gate n)) : Matrix n :=
  defect (identity n) (projected y w)

theorem dotOn_zero (cols : List (Fin n)) (x : Row n) :
    dotOn cols zeroRow x = false := by
  induction cols with
  | nil => rfl
  | cons c cs ih =>
      change Bool.xor false (dotOn cs zeroRow x) = false
      exact (congrArg (Bool.xor false) ih).trans rfl

theorem dot_zero (x : Row n) : dot zeroRow x = false :=
  dotOn_zero (List.finRange n) x

theorem dotOn_rowXor (cols : List (Fin n)) (u v x : Row n) :
    dotOn cols (rowXor u v) x = Bool.xor (dotOn cols u x) (dotOn cols v x) := by
  induction cols with
  | nil => rfl
  | cons c cs ih =>
      change Bool.xor (Bool.xor (u c) (v c) && x c)
          (dotOn cs (rowXor u v) x) =
        Bool.xor (Bool.xor (u c && x c) (dotOn cs u x))
          (Bool.xor (v c && x c) (dotOn cs v x))
      rw [and_xor_left, ih]
      exact xor_interchange (u c && x c) (v c && x c)
        (dotOn cs u x) (dotOn cs v x)

theorem dot_rowXor (u v x : Row n) :
    dot (rowXor u v) x = Bool.xor (dot u x) (dot v x) :=
  dotOn_rowXor (List.finRange n) u v x

theorem dot_bitScale (b : Bool) (v x : Row n) :
    dot (bitScale b v) x = (b && dot v x) := by
  cases b with
  | false => simpa only [bitScale_false] using dot_zero x
  | true =>
      rw [bitScale_true] <;> cases dot v x <;> rfl

theorem dotOn_inputXor (cols : List (Fin n)) (u x t : Row n) :
    dotOn cols u (rowXor x t) = Bool.xor (dotOn cols u x) (dotOn cols u t) := by
  induction cols with
  | nil => rfl
  | cons c cs ih =>
      change Bool.xor (u c && Bool.xor (x c) (t c))
          (dotOn cs u (rowXor x t)) =
        Bool.xor (Bool.xor (u c && x c) (dotOn cs u x))
          (Bool.xor (u c && t c) (dotOn cs u t))
      rw [and_xor_right, ih]
      exact xor_interchange (u c && x c) (u c && t c)
        (dotOn cs u x) (dotOn cs u t)

/-- Concrete XOR-additivity, not an assumed finite-field structure. -/
theorem matrixAction_inputXor (M : Matrix n) (x t : Row n) :
    matrixAction M (rowXor x t) =
      rowXor (matrixAction M x) (matrixAction M t) := by
  funext r
  exact dotOn_inputXor (List.finRange n) (M r) x t

theorem matrixAction_zero_input (M : Matrix n) :
    matrixAction M zeroRow = zeroRow := by
  have h := matrixAction_inputXor M (zeroRow : Row n) zeroRow
  simpa only [rowXor_self] using h

/- An identity/action bridge makes the full-register orientation explicit. -/

theorem dotOn_succ (cols : List (Fin n)) (u x : Row (n + 1)) :
    dotOn (cols.map Fin.succ) u x =
      dotOn cols (fun c => u c.succ) (fun c => x c.succ) := by
  induction cols with
  | nil => rfl
  | cons c cs ih =>
      change Bool.xor (u c.succ && x c.succ) (dotOn (cs.map Fin.succ) u x) =
        Bool.xor (u c.succ && x c.succ)
          (dotOn cs (fun j => u j.succ) (fun j => x j.succ))
      rw [ih]

theorem dot_succ (u x : Row (n + 1)) :
    dot u x = Bool.xor (u 0 && x 0)
      (dot (fun c : Fin n => u c.succ) (fun c : Fin n => x c.succ)) := by
  unfold dot
  rw [List.finRange_succ]
  change Bool.xor (u 0 && x 0) (dotOn ((List.finRange n).map Fin.succ) u x) = _
  rw [dotOn_succ]

theorem dot_identity (r : Fin n) (x : Row n) :
    dot ((identity n) r) x = x r := by
  induction n with
  | zero => exact Fin.elim0 r
  | succ k ih =>
      refine Fin.cases ?_ ?_ r
      · rw [dot_succ]
        have hh : identity (k + 1) (0 : Fin (k + 1)) 0 = true := by
          simp [identity]
        have ht : (fun c : Fin k => identity (k + 1) 0 c.succ) = zeroRow := by
          funext c
          have hne : (0 : Fin (k + 1)) ≠ c.succ :=
            fun h => Fin.succ_ne_zero c h.symm
          simp [identity, zeroRow, hne]
        simpa only [hh, ht, dot_zero] using xor_false (x 0)
      · intro i
        rw [dot_succ]
        have hh : identity (k + 1) i.succ 0 = false := by
          simp [identity, Fin.succ_ne_zero]
        have ht : (fun c : Fin k => identity (k + 1) i.succ c.succ) =
            (identity k) i := by
          funext c
          simp [identity, Fin.succ_inj]
        simpa only [hh, ht, ih] using false_xor (x i.succ)

theorem matrixAction_identity (x : Row n) : matrixAction (identity n) x = x := by
  funext r
  exact dot_identity r x

theorem matrixAction_defect (R P : Matrix n) (x : Row n) :
    matrixAction (defect R P) x =
      rowXor (matrixAction R x) (matrixAction P x) := by
  funext r
  exact dot_rowXor (R r) (P r) x

/-- The map whose image is bounded is literally x XOR (P*x). -/
theorem projectedDefect_action (y : Fin n) (w : List (Gate n)) (x : Row n) :
    matrixAction (projectedDefect y w) x =
      rowXor x (matrixAction (projected y w) x) := by
  change matrixAction (defect (identity n) (projected y w)) x = _
  rw [matrixAction_defect, matrixAction_identity]

/- Evaluate each actual donor row on the same arbitrary full input. -/

def measurements (G : List (Row n)) (x : Row n) : List Bool :=
  G.map (fun v => dot v x)

def scalarCombination : List Bool → List Bool → Bool
  | b :: bs, t :: ts => Bool.xor (b && t) (scalarCombination bs ts)
  | _, _ => false

def decode (C : Fin n → List Bool) (values : List Bool) : Row n :=
  fun r => scalarCombination (C r) values

theorem measurements_length (G : List (Row n)) (x : Row n) :
    (measurements G x).length = G.length := by
  simp only [measurements, List.length_map]

/-- This algebraic identity also respects the source's totalized truncation.
    The matrix-certificate applications BELOW require exact mask lengths. -/
theorem dot_combination (G : List (Row n)) (bs : List Bool) (x : Row n) :
    dot (combination G bs) x = scalarCombination bs (measurements G x) := by
  induction G generalizing bs with
  | nil =>
      cases bs <;> simpa only [combination, measurements, List.map_nil,
        scalarCombination] using dot_zero x
  | cons v vs ih =>
      cases bs with
      | nil => simpa only [combination, scalarCombination] using dot_zero x
      | cons b bs =>
          change dot (rowXor (bitScale b v) (combination vs bs)) x =
            Bool.xor (b && dot v x) (scalarCombination bs (measurements vs x))
          rw [dot_rowXor, dot_bitScale, ih bs]

/-- ROW generation produces a factorization of the correctly oriented M*x.
    No row/column rank equality, dimension, or cardinality fact is assumed. -/
theorem matrix_factorization (M : Matrix n) (G : List (Row n))
    (C : Fin n → List Bool)
    (hrows : ∀ r, (C r).length = G.length ∧ combination G (C r) = M r)
    (x : Row n) :
    matrixAction M x = decode C (measurements G x) := by
  funext r
  change dot (M r) x = scalarCombination (C r) (measurements G x)
  rw [← (hrows r).2]
  exact dot_combination G (C r) x

theorem equal_measurements_equal_outputs (M : Matrix n) (G : List (Row n))
    (C : Fin n → List Bool)
    (hrows : ∀ r, (C r).length = G.length ∧ combination G (C r) = M r)
    (x t : Row n) (h : measurements G x = measurements G t) :
    matrixAction M x = matrixAction M t := by
  rw [matrix_factorization M G C hrows x, matrix_factorization M G C hrows t, h]

/- Exact bounded binary coding. Leading list bit is least significant.
   Equal code only implies equal lists when their lengths agree. -/

def bitNumber : Bool → Nat
  | false => 0
  | true => 1

def bitsCode : List Bool → Nat
  | [] => 0
  | b :: bs => bitNumber b + 2 * bitsCode bs

theorem bitsCode_lt (bs : List Bool) : bitsCode bs < 2 ^ bs.length := by
  induction bs with
  | nil => decide
  | cons b bs ih =>
      change bitNumber b + 2 * bitsCode bs < 2 ^ (bs.length + 1)
      rw [Nat.pow_succ]
      cases b <;> simp only [bitNumber] <;> omega

theorem bitsCode_eq_at_length (as bs : List Bool)
    (hlen : as.length = bs.length) (hcode : bitsCode as = bitsCode bs) :
    as = bs := by
  induction as generalizing bs with
  | nil =>
      cases bs with
      | nil => rfl
      | cons b bs => simp at hlen
  | cons a as ih =>
      cases bs with
      | nil => simp at hlen
      | cons b bs =>
          have ht : as.length = bs.length := Nat.succ.inj hlen
          have hab : a = b := by
            cases a <;> cases b
            · rfl
            · simp only [bitsCode, bitNumber] at hcode
              omega
            · simp only [bitsCode, bitNumber] at hcode
              omega
            · rfl
          subst b
          have hc : bitsCode as = bitsCode bs := by
            change bitNumber a + 2 * bitsCode as = bitNumber a + 2 * bitsCode bs at hcode
            omega
          exact congrArg (List.cons a) (ih bs ht hc)

def inputCode (G : List (Row n)) (x : Row n) : Fin (2 ^ G.length) :=
  ⟨bitsCode (measurements G x), by
    simpa only [measurements_length] using bitsCode_lt (measurements G x)⟩

theorem measurements_eq_of_inputCode_eq (G : List (Row n)) (x t : Row n)
    (h : inputCode G x = inputCode G t) : measurements G x = measurements G t := by
  apply bitsCode_eq_at_length (measurements G x) (measurements G t)
  · simp only [measurements_length]
  · exact congrArg (fun j : Fin (2 ^ G.length) => j.val) h

/-- Only the witness selection is noncomputable. It selects a PREIMAGE of
    the actual output; it does not assume that measurements are canonical. -/
noncomputable def imageCode (M : Matrix n) (G : List (Row n))
    (z : ActualImage M) : Fin (2 ^ G.length) :=
  inputCode G (Classical.choose z.property)

/-- Different outputs have different chosen measurement codes. Different
    inputs producing the SAME output need not have the same measurements. -/
theorem imageCode_injective (M : Matrix n) (G : List (Row n))
    (C : Fin n → List Bool)
    (hrows : ∀ r, (C r).length = G.length ∧ combination G (C r) = M r) :
    ∀ a b : ActualImage M, imageCode M G a = imageCode M G b → a = b := by
  intro a b hab
  have hc : inputCode G (Classical.choose a.property) =
      inputCode G (Classical.choose b.property) := hab
  have hm := measurements_eq_of_inputCode_eq G
    (Classical.choose a.property) (Classical.choose b.property) hc
  have hout := equal_measurements_equal_outputs M G C hrows
    (Classical.choose a.property) (Classical.choose b.property) hm
  apply Subtype.ext
  exact (Classical.choose_spec a.property).symm.trans
    (hout.trans (Classical.choose_spec b.property))

/-- Explicit finite-image bound: an injection into a finite ordinal of the
    stated size, not a custom quantity misleadingly called rank. -/
theorem matrix_image_bound (M : Matrix n) (G : List (Row n))
    (C : Fin n → List Bool)
    (hrows : ∀ r, (C r).length = G.length ∧ combination G (C r) = M r) :
    ∃ code : ActualImage M → Fin (2 ^ G.length),
      ∀ a b, code a = code b → a = b := by
  exact ⟨imageCode M G, imageCode_injective M G C hrows⟩

/- Source-bound universal successor: actual words, donors, and row masks. -/

theorem restored_action_factorization (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hpos : 0 < targetCount y w) (x : Row n) :
    matrixAction (projectedDefect y w) x =
      decode (reducedCoefficients y w) (measurements (retainedDonors y w) x) := by
  have hrows := (restored_row_certificate y w hraw hpos).2.2
  exact matrix_factorization (projectedDefect y w) (retainedDonors y w)
    (reducedCoefficients y w) hrows x

theorem restored_measurement_length (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hpos : 0 < targetCount y w) (x : Row n) :
    (measurements (retainedDonors y w) x).length = targetCount y w - 1 := by
  rw [measurements_length]
  exact (restored_row_certificate y w hraw hpos).2.1

/-- MAIN POSITIVE CASE: at most 2^(m-1) DISTINCT ACTUAL OUTPUTS.
    The exact meaning of 'at most' is the displayed injective function. -/
theorem restored_positive_image_bound (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hpos : 0 < targetCount y w) :
    ∃ code : ActualImage (projectedDefect y w) → Fin (2 ^ (targetCount y w - 1)),
      ∀ a b, code a = code b → a = b := by
  rcases restored_row_certificate y w hraw hpos with ⟨_, hsize, hrows⟩
  have hb := matrix_image_bound (projectedDefect y w) (retainedDonors y w)
    (reducedCoefficients y w) hrows
  exact Eq.subst
    (motive := fun k : Nat =>
      ∃ code : ActualImage (projectedDefect y w) → Fin (2 ^ k),
        ∀ a b, code a = code b → a = b)
    hsize hb

/-- No target writes: the actual full-register defect map is zero. -/
theorem zero_target_defect_action (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hzero : targetCount y w = 0) (x : Row n) :
    matrixAction (projectedDefect y w) x = zeroRow := by
  funext r
  change dot (rowXor ((identity n) r) (projected y w r)) x = false
  rw [zero_target_restored y w hraw hzero, rowXor_self, dot_zero]

/-- The image is exactly the singleton containing the zero output. -/
theorem zero_target_image_exact (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hzero : targetCount y w = 0) (z : Row n) :
    InImage (projectedDefect y w) z ↔ z = zeroRow := by
  constructor
  · intro hz
    rcases hz with ⟨x, hx⟩
    exact hx.symm.trans (zero_target_defect_action y w hraw hzero x)
  · intro hz
    refine ⟨zeroRow, ?_⟩
    exact (zero_target_defect_action y w hraw hzero zeroRow).trans hz.symm

theorem zero_target_image_bound (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) (hzero : targetCount y w = 0) :
    ∃ code : ActualImage (projectedDefect y w) → Fin 1,
      ∀ a b, code a = code b → a = b := by
  refine ⟨fun _ => ⟨0, by decide⟩, ?_⟩
  intro a b _
  apply Subtype.ext
  have ha : a.val = zeroRow :=
    (zero_target_image_exact y w hraw hzero a.val).mp a.property
  have hb : b.val = zeroRow :=
    (zero_target_image_exact y w hraw hzero b.val).mp b.property
  exact ha.trans hb.symm

/-- Both cases, using truncated natural subtraction: for m=0 the bound is 1. -/
theorem restored_image_bound (y : Fin n) (w : List (Gate n))
    (hraw : raw w = identity n) :
    ∃ code : ActualImage (projectedDefect y w) → Fin (2 ^ (targetCount y w - 1)),
      ∀ a b, code a = code b → a = b := by
  by_cases hz : targetCount y w = 0
  · have hbound : 1 = 2 ^ (targetCount y w - 1) := by
      simp only [hz, Nat.zero_sub, Nat.pow_zero]
    exact Eq.subst
      (motive := fun k : Nat =>
        ∃ code : ActualImage (projectedDefect y w) → Fin k,
          ∀ a b, code a = code b → a = b)
      hbound (zero_target_image_bound y w hraw hz)
  · have hp : 0 < targetCount y w := by omega
    exact restored_positive_image_bound y w hraw hp

/- Small proof declarations. They become kernel-checked fixtures only when
   THIS file is accepted by the pinned compiler. No execution is claimed. -/

namespace Fixtures

open TargetWriteCertificate.Fixtures

/-- Nonsymmetric defect E_(b,a): M*e_a=e_b, with output index first. -/
theorem commutator_action_orientation :
    matrixAction (projectedDefect y3 commutatorWord) ((identity 3) a3) =
      (identity 3) b3 := by
  funext r
  revert r
  decide

/-- Transposing the matrix would change this observed output bit. -/
theorem transpose_action_is_wrong :
    matrixAction (projectedDefect y3 commutatorWord) ((identity 3) a3) b3 ≠
      matrixAction (fun r c => projectedDefect y3 commutatorWord c r)
        ((identity 3) a3) b3 := by
  decide

/-- This defect reads the arbitrary dirty TARGET input into the helper output. -/
theorem feedback_reads_dirty_target :
    matrixAction (projectedDefect y2 feedbackWord) ((identity 2) y2) =
      (identity 2) a2 := by
  funext r
  revert r
  decide

/-- Inputs agree on the only helper, but their defect outputs differ. -/
theorem cleaning_target_changes_answer :
    ((identity 2) y2) a2 = (zeroRow : Row 2) a2 ∧
      matrixAction (projectedDefect y2 feedbackWord) ((identity 2) y2) a2 ≠
        matrixAction (projectedDefect y2 feedbackWord) zeroRow a2 := by
  decide

/-- An actual two-target-write raw identity gets the Fin 2 bound. -/
theorem commutator_image_bound :
    ∃ code : ActualImage (projectedDefect y3 commutatorWord) → Fin 2,
      ∀ a b, code a = code b → a = b := by
  exact restored_positive_image_bound y3 commutatorWord commutator_restores (by decide)

/-- Nonempty zero-target word; universal zero-image theorem, not a new model. -/
theorem nonempty_zero_image (z : Row 3) :
    InImage (projectedDefect y3 [ay, ay]) z ↔ z = zeroRow := by
  apply zero_target_image_exact y3 [ay, ay]
  · funext r c
    revert r c
    decide
  · decide

/-- Measurement codes do NOT in general descend through equal-output inputs.
    The main image injection deliberately chooses one input witness instead. -/
theorem same_output_different_input_codes :
    matrixAction (projectedDefect y2 feedbackWord) zeroRow =
      matrixAction (projectedDefect y2 feedbackWord) ((identity 2) a2) ∧
    inputCode (retainedDonors y2 feedbackWord) zeroRow ≠
      inputCode (retainedDonors y2 feedbackWord) ((identity 2) a2) := by
  constructor
  · funext r
    revert r
    decide
  · decide

/-- Code injectivity needs the exact length premise: padded zeros collide. -/
theorem unequal_length_code_collision :
    bitsCode [] = bitsCode [false] ∧ ([] : List Bool) ≠ [false] := by
  decide

end Fixtures

/- An axiom report for EVERY theorem declared in this successor follows.
   These commands request reports; they are NOT a pre-recorded axiom receipt.
   No private declarations are hidden from the report list. -/

#print axioms xor_false
#print axioms false_xor
#print axioms and_xor_left
#print axioms and_xor_right
#print axioms xor_interchange
#print axioms dotOn_zero
#print axioms dot_zero
#print axioms dotOn_rowXor
#print axioms dot_rowXor
#print axioms dot_bitScale
#print axioms dotOn_inputXor
#print axioms matrixAction_inputXor
#print axioms matrixAction_zero_input
#print axioms dotOn_succ
#print axioms dot_succ
#print axioms dot_identity
#print axioms matrixAction_identity
#print axioms matrixAction_defect
#print axioms projectedDefect_action
#print axioms measurements_length
#print axioms dot_combination
#print axioms matrix_factorization
#print axioms equal_measurements_equal_outputs
#print axioms bitsCode_lt
#print axioms bitsCode_eq_at_length
#print axioms measurements_eq_of_inputCode_eq
#print axioms imageCode_injective
#print axioms matrix_image_bound
#print axioms restored_action_factorization
#print axioms restored_measurement_length
#print axioms restored_positive_image_bound
#print axioms zero_target_defect_action
#print axioms zero_target_image_exact
#print axioms zero_target_image_bound
#print axioms restored_image_bound
#print axioms Fixtures.commutator_action_orientation
#print axioms Fixtures.transpose_action_is_wrong
#print axioms Fixtures.feedback_reads_dirty_target
#print axioms Fixtures.cleaning_target_changes_answer
#print axioms Fixtures.commutator_image_bound
#print axioms Fixtures.nonempty_zero_image
#print axioms Fixtures.same_output_different_input_codes
#print axioms Fixtures.unequal_length_code_collision

#check @restored_positive_image_bound
#check @restored_image_bound
#check @zero_target_image_exact

end TargetWriteFiniteImage
