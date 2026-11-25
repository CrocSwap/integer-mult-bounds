import PackedParityReindex
import Mathlib.Tactic.FinCases

/-!
Exact strict-upper source quadratic phases under the packed/address map.
Only the nine coordinate positions are split; payload bits remain symbolic.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
-/
set_option Elab.async false
namespace CurrentMain.PackedQuadraticReindex
open Current535PackedCoordinates
open PackedParityReindex
open CliffordNineBitDecoder
open HyperplaneEnd.Clifford (par9 qv qvAux)
open scoped BigOperators

private theorem bit_and (a b : Bool) :
    boolBit (a && b) = boolBit a * boolBit b := by
  cases a <;> cases b <;> decide +kernel

private theorem upper_parity (row : Nat) (x : Packed) (i : Fin 9) :
    boolBit (par9 ((row >>> (i.val + 1)) &&& (x.val >>> (i.val + 1)))) =
      ∑ j : Fin 9, if i.val < j.val then mask row j * unpack x j else 0 := by
  have hs : x.val >>> (i.val + 1) < 512 :=
    lt_of_le_of_lt (by
      simpa only [Nat.shiftRight_eq_div_pow] using
        Nat.div_le_self x.val (2 ^ (i.val + 1))) x.isLt
  have hb : (row >>> (i.val + 1)) &&& (x.val >>> (i.val + 1)) < 512 :=
    lt_of_le_of_lt Nat.and_le_right hs
  have high (j : Nat) (hj : 9 ≤ j) : x.val.testBit j = false := by
    apply Nat.testBit_lt_two_pow
    have hp : (512 : Nat) ≤ 2 ^ j := Nat.pow_le_pow_right (n := 2) (by decide) hj
    exact lt_of_lt_of_le x.isLt hp
  rw [HyperplaneEnd.Clifford.par9_spec ⟨_, hb⟩, parity_sum]
  simp only [Nat.testBit_and, bit_and, Nat.testBit_shiftRight]
  fin_cases i <;> simp [Fin.sum_univ_succ, mask, unpack, boolBit, high]

/-- The source's shifted parity is precisely the strict-upper binary sum.
Its natural value is retained before multiplication by two in Z4 arithmetic. -/
theorem upper_parity_value (row : Nat) (x : Packed) (i : Fin 9) :
    (if par9 ((row >>> (i.val + 1)) &&& (x.val >>> (i.val + 1))) then 1 else 0) =
      ((∑ j : Fin 9, if i.val < j.val then mask row j * unpack x j else 0) : Bit).val := by
  rw [← upper_parity]
  cases h : par9 ((row >>> (i.val + 1)) &&& (x.val >>> (i.val + 1))) <;>
    simp [boolBit, h, ZMod.val_one_eq_one_mod]

private theorem qvAux_ofFn : ∀ n (Q alpha : Fin n → Nat) (x start : Nat),
    qvAux (List.ofFn Q) (List.ofFn alpha) x start =
      ∑ i : Fin n, if (x >>> (start + i.val)) % 2 = 1 then
        alpha i + 2 * (if par9 ((Q i >>> (start + i.val + 1)) &&&
          (x >>> (start + i.val + 1))) then 1 else 0) else 0 := by
  intro n
  induction n with
  | zero => intro Q alpha x start; simp [qvAux]
  | succ n ih =>
    intro Q alpha x start
    rw [List.ofFn_succ, List.ofFn_succ, qvAux, Fin.sum_univ_succ, ih]
    apply congrArg₂ (· + ·)
    · simp
    · apply Finset.sum_congr rfl
      intro i _
      simp only [Fin.val_succ, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem getD_ofFn {n : Nat} (f : Fin n → Nat) (i : Fin n) :
    (List.ofFn f).getD i.val 0 = f i := by
  simp [List.getD_eq_getElem?_getD, List.getElem?_ofFn, i.isLt]

private theorem qv_ofFn (Q alpha : Fin 9 → Nat) (x : Packed) :
    qv (List.ofFn Q) (List.ofFn alpha) x.val =
      qvalue (List.ofFn Q) (List.ofFn alpha) (unpack x) := by
  unfold qv qvalue
  rw [qvAux_ofFn]
  apply congrArg (fun n : Nat => n % 4)
  simp only [Nat.zero_add]
  rw [Finset.mul_sum, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  rw [getD_ofFn]
  have hq : (∑ j : Fin 9, if i.val < j.val then
      matrix (List.ofFn Q) i j * unpack x j else 0) =
      ∑ j : Fin 9, if i.val < j.val then mask (Q i) j * unpack x j else 0 := by
    simp only [matrix, getD_ofFn, mask]
  rw [hq, ← upper_parity_value]
  have hc : ((x.val >>> i.val) % 2 = 1) ↔ x.val.testBit i.val = true := by
    rw [Nat.mod_two_eq_one_iff_testBit_zero, Nat.testBit_shiftRight]
    simp
  simp only [hc]
  cases h : x.val.testBit i.val <;>
    simp [h, unpack, mask, ZMod.val_one_eq_one_mod]

private theorem list_ofFn_getD (xs : List Nat) (hl : xs.length = 9) :
    List.ofFn (fun i : Fin 9 => xs.getD i.val 0) = xs := by
  apply List.ext_getElem
  · simpa only [List.length_ofFn] using hl.symm
  · intro i hi hx
    rw [List.getElem_ofFn]
    simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hx,
      Option.getD_some]

/-- Both lists have exactly nine entries, retaining source paired-list stopping
behavior and the full modulo-four exponent rather than an equality up to phase. -/
theorem quadratic_value (Q alpha : List Nat) (hQ : Q.length = 9)
    (ha : alpha.length = 9) (x : Packed) :
    qv Q alpha x.val = qvalue Q alpha (unpack x) := by
  have hq := list_ofFn_getD Q hQ
  have hl := list_ofFn_getD alpha ha
  calc
    qv Q alpha x.val = qv (List.ofFn (fun i : Fin 9 => Q.getD i.val 0))
        (List.ofFn (fun i : Fin 9 => alpha.getD i.val 0)) x.val := by rw [hq, hl]
    _ = qvalue (List.ofFn (fun i : Fin 9 => Q.getD i.val 0))
        (List.ofFn (fun i : Fin 9 => alpha.getD i.val 0)) (unpack x) := qv_ofFn _ _ x
    _ = qvalue Q alpha (unpack x) := by rw [hq, hl]

noncomputable section
/-- Exact diagonal action for every payload, with no omitted global scalar. -/
theorem diagonal_reindex (Q alpha : List Nat) (hQ : Q.length = 9)
    (ha : alpha.length = 9) (v : Packed → ℂ) :
    payloadEquiv (HyperplaneEnd.Clifford.gC 512 (.dg Q alpha) v) =
      fun a => Complex.I ^ qvalue Q alpha a * payloadEquiv v a := by
  funext a
  obtain ⟨x, rfl⟩ := addressEquiv.surjective a
  rw [show addressEquiv x = unpack x from rfl]
  simp only [payload_apply, pack_unpack, HyperplaneEnd.Clifford.gC]
  rw [quadratic_value Q alpha hQ ha x]
end
end CurrentMain.PackedQuadraticReindex

#print axioms CurrentMain.PackedQuadraticReindex.upper_parity_value
#print axioms CurrentMain.PackedQuadraticReindex.quadratic_value
#print axioms CurrentMain.PackedQuadraticReindex.diagonal_reindex
