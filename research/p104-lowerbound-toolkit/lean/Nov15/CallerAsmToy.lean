/-
CallerAsmToy (lane CALLERASM, Nov 20).  Non-vacuity of the word-level hypotheses: a LEGAL 2-role, 1-stage caller word
with a genuine type-B J record (HOST(0,1,1,1), both coefficients /= 0, then IDLE 0 {0}, IDLE 1 {0}) and two thin QUERY events
(sigma = 3, 1):  odd targets (q^3, q), 4 frame columns = n + 2 (T = Q = 2).  It is SPEC-legal (`toyW_legal`, every ring with q^4 = 1).
[C exact, python] prod V = -I and the stage K-block has det 8 /= 0 (lambda /= -1); the Lean statement of that block is NOT proved here.
k = 1, so the pair statements are vacuous: this checks the schema / legality / count hypotheses, `word_count`, `word_mains`.
-/
import Nov15.CallerAsm
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
namespace CallerAsm
open Finset Matrix CallerSign CallerWord

def toyW : CWord 2 1 where
  evs := [.host 0 1 1 1, .idle 0 {0} 0, .idle 1 {0} 0, .swap 0 1, .scale 1 (-2), .query 0 1 3,
          .scale 1 (-1/2), .query 1 0 1, .scale 0 (-1)]
  ex := ![3, 1]
  mask := fun _ => {0}

set_option maxHeartbeats 8000000 in
theorem toyW_legal : Legal toyW := by
  refine ⟨?_, ?_⟩
  · intro e he s t a b h
    subst h
    simp [toyW] at he
    rcases he with ⟨rfl, rfl, -, -⟩
    decide
  · intro S _ _ q i D hq hi
    have h2 : (algebraMap ℚ S) (-1 / 2) * 2 = -1 := by
      rw [← map_ofNat (algebraMap ℚ S) 2, ← map_mul]; norm_num
    unfold LegalAt replay pre target toyW
    ext r r'
    fin_cases r <;> fin_cases r' <;>
      simp [evMat, E1, qp, Matrix.mul_apply, Fin.sum_univ_two, Matrix.diagonal, Equiv.swap_apply_left,
        Equiv.swap_apply_right, Matrix.one_apply, map_neg, map_one, map_ofNat]
    · ring
    · linear_combination (2 * D 0) * hq
    · linear_combination (-(D 0)) * hq + (-(D 0)) * h2
    · linear_combination (-2 * D 0 * q) * hq + (-(D 0) * q) * h2

def toyJ : JB toyW where
  pos := fun _ => 0
  mono := fun a b h => absurd h (by rw [Subsingleton.elim a b]; exact lt_irrefl _)
  lt := fun _ => by decide
  u := fun _ => 0
  v := fun _ => 1
  a := fun _ => 1
  b := fun _ => 1
  a0 := fun _ => by norm_num
  b0 := fun _ => by norm_num
  uv := fun _ => by decide
  h0 := fun _ => rfl
  h1 := fun s => by obtain rfl := Subsingleton.elim s 0; rfl
  h2 := fun s => by obtain rfl := Subsingleton.elim s 0; rfl

theorem toyW_odd : ∀ r, toyW.ex r % 2 = 1 := by
  intro r; fin_cases r <;> decide

theorem toyW_card : Fintype.card (Iota toyW) = 4 := by
  rw [Fintype.card_subtype]
  decide +kernel

/-- the event bookkeeping on the toy: roles at stage 0 = incidence events at stage 0 (= 2: the two contacts). -/
theorem toyW_count : (univ.filter fun r : Fin 2 => (0 : Fin 1) ∈ toyW.mask r).card =
    (univ.filter fun j => (0 : Fin 1) ∈ evS toyW j).card := word_count toyW_legal 0

theorem toyW_count_val : (univ.filter fun j => (0 : Fin 1) ∈ evS toyW j).card = 2 := by
  decide +kernel

theorem toyW_mains : 2 * 1 ≤ (univ.filter fun j => (evS toyW j).card = 1).card := word_mains toyJ

/-- the event data (kernel / biorthogonal vectors) of the legal toy exists, for the type-B schema. -/
noncomputable def toyEvData := wordEv toyW_legal toyJ.sch

theorem toyW_nonvac : Legal toyW ∧ (∀ r, toyW.ex r % 2 = 1) ∧ Fintype.card (Iota toyW) = 4 ∧ 2 + 2 = Fintype.card (Iota toyW) :=
  ⟨toyW_legal, toyW_odd, toyW_card, by rw [toyW_card]⟩

end CallerAsm

#print axioms CallerAsm.toyW_legal
#print axioms CallerAsm.toyW_nonvac
#print axioms CallerAsm.toyW_count
#print axioms CallerAsm.toyW_mains
