/-
BankFlagB .  
R2-bank / R1-bank finite facts, decide+kernel-checked on the caller-fixed main contract (DATA, #7717
bank2/pairs.py: OUT = 104 hosted rows (v = own birth vector, a = functional of partner's final hyperplane H = ker a),
IN = 104 live Y rows (v = partner birth vector, a = functional of the row's final hyperplane); F_2^9 as 9-bit masks;
 N(i,l) = [v_i ∉ H_l] = par(a_l, v_i)).
Flag [153,191,70,98,265,280,253,392,1]: F_j = span(flag[0..j-1]).  Pair i is COUNTED at cut j = level v_i iff v_i ∉ H_i and
F_{j-1} ⊆ H_i.  Certified: 14 counted pairs OUT, 14 IN, two per cut j = 2..8, each cut an N-clique, no N between cuts.
Named premises (not formalised): P-BLOCK (cut-j rank extras ≥ size of a counted N-clique: block-triangular rows of the
nonzero-principal-minor matrix, BANK2 §2), P-CUTMASS (mass ≥ field crossings + Σ_j cut ranks: BankNC0b cut_lemma, both
directions), P-LOC, P-1S', P-HLOC, P-CALLER.  Kernel only: no sorry, no native_decide, no new axioms.
-/
import Mathlib.Data.Nat.Bitwise
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Order.Interval.Finset.Nat
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace BankFlagB
open Finset

def flag : List ℕ := [153, 191, 70, 98, 265, 280, 253, 392, 1]
def par (a b : ℕ) : ℕ := ((List.range 9).filter (fun i => (a &&& b).testBit i)).length % 2
def comb (m : ℕ) : ℕ := (List.range 9).foldl (fun acc i => if m.testBit i then acc ^^^ flag.getD i 0 else acc) 0
/-- the flag is a basis: no nontrivial combination vanishes -/
theorem flag_indep : ∀ m < 512, comb m = 0 → m = 0 := by decide +kernel
/-- cut index (1..9) of v: least j with v ∈ F_j -/
def level (v : ℕ) : ℕ := ((List.range 9).find? (fun j => (List.range (2^(j+1))).any (fun m => comb m == v))).getD 99 + 1

def OUT : List (ℕ × ℕ) := [(81, 81), (273, 273), (262, 262), (98, 98), (290, 290), (268, 268), (164, 164), (280, 280), (11, 11), (19, 19), (35, 35), (131, 131), (259, 259), (13, 13), (21, 21), (37, 37), (69, 69), (133, 133), (261, 261), (41, 41), (73, 73), (265, 265), (49, 49), (145, 145), (161, 161), (193, 193), (321, 321), (385, 385), (14, 14), (22, 22), (38, 38), (70, 70), (134, 134), (26, 26), (74, 74), (138, 138), (50, 50), (146, 146), (274, 274), (194, 194), (322, 322), (386, 386), (28, 28), (44, 44), (140, 140), (84, 84), (148, 148), (276, 276), (100, 100), (292, 292), (196, 196), (324, 324), (388, 388), (56, 56), (88, 88), (152, 152), (168, 168), (296, 296), (200, 200), (328, 328), (392, 392), (112, 112), (176, 176), (304, 304), (208, 208), (336, 336), (400, 400), (224, 224), (352, 352), (416, 416), (508, 508), (506, 506), (502, 502), (494, 494), (478, 478), (446, 446), (382, 382), (254, 254), (505, 505), (501, 501), (493, 493), (477, 477), (445, 445), (381, 381), (253, 253), (499, 499), (475, 475), (443, 443), (379, 379), (251, 251), (487, 487), (471, 471), (439, 439), (375, 375), (247, 247), (463, 463), (431, 431), (367, 367), (239, 239), (415, 415), (351, 351), (223, 223), (319, 319), (191, 191)]

def IN : List (ℕ × ℕ) := [(11, 11), (19, 19), (35, 35), (131, 131), (259, 259), (13, 13), (21, 21), (37, 37), (69, 69), (133, 133), (261, 261), (41, 41), (73, 73), (265, 265), (49, 49), (81, 81), (145, 145), (273, 273), (161, 161), (193, 193), (321, 321), (385, 385), (14, 14), (22, 22), (38, 38), (70, 70), (134, 134), (262, 262), (26, 26), (74, 74), (138, 138), (50, 50), (146, 146), (274, 274), (98, 98), (290, 290), (194, 194), (322, 322), (386, 386), (28, 28), (44, 44), (140, 140), (268, 268), (84, 84), (148, 148), (276, 276), (100, 100), (164, 164), (292, 292), (196, 196), (324, 324), (388, 388), (56, 56), (88, 88), (152, 152), (280, 280), (168, 168), (296, 296), (200, 200), (328, 328), (392, 392), (112, 112), (176, 176), (304, 304), (208, 208), (336, 336), (400, 400), (224, 224), (352, 352), (416, 416), (508, 508), (506, 506), (502, 502), (494, 494), (478, 478), (446, 446), (382, 382), (254, 254), (505, 505), (501, 501), (493, 493), (477, 477), (445, 445), (381, 381), (253, 253), (499, 499), (475, 475), (443, 443), (379, 379), (251, 251), (487, 487), (471, 471), (439, 439), (375, 375), (247, 247), (463, 463), (431, 431), (367, 367), (239, 239), (415, 415), (351, 351), (223, 223), (319, 319), (191, 191)]

def cliqueIN : List ℕ := [0, 7, 21, 26, 35, 42, 56, 96]

def cntOUT : List ℕ := [1, 3, 7, 21, 27, 30, 31, 48, 60, 66, 84, 89, 101, 103]

def cntIN : List ℕ := [13, 17, 21, 24, 25, 34, 46, 55, 60, 66, 84, 89, 101, 103]

def N (P : List (ℕ × ℕ)) (i l : ℕ) : ℕ := par (P.getD l (0,0)).2 (P.getD i (0,0)).1
def counted (P : List (ℕ × ℕ)) (i : ℕ) : Bool :=
  N P i i == 1 && (flag.take (level (P.getD i (0,0)).1 - 1)).all (fun f => par (P.getD i (0,0)).2 f == 0)
def cnt (P : List (ℕ × ℕ)) : List ℕ := (List.range P.length).filter (counted P)
def atLevel (P : List (ℕ × ℕ)) (j : ℕ) : ℕ := ((cnt P).filter (fun i => level (P.getD i (0,0)).1 == j)).length
/-- N-clique per cut, no N across cuts -/
def blocky (P : List (ℕ × ℕ)) : Bool :=
  (cnt P).all (fun i => (cnt P).all (fun l =>
    if level (P.getD i (0,0)).1 == level (P.getD l (0,0)).1 then N P i l == 1 && N P l i == 1
    else N P i l == 0 && N P l i == 0))

theorem out_len : OUT.length = 104 := by decide +kernel
theorem in_len : IN.length = 104 := by decide +kernel
theorem out_cnt : cnt OUT = cntOUT := by decide +kernel
theorem in_cnt : cnt IN = cntIN := by decide +kernel
theorem out_blocky : blocky OUT = true := by decide +kernel
theorem in_blocky : blocky IN = true := by decide +kernel
theorem out_levels : (List.range 10).map (atLevel OUT) = [0, 0, 2, 2, 2, 2, 2, 2, 2, 0] := by decide +kernel
theorem in_levels : (List.range 10).map (atLevel IN) = [0, 0, 2, 2, 2, 2, 2, 2, 2, 0] := by decide +kernel
theorem out_total : (cnt OUT).length = 14 := by decide +kernel
theorem in_total : (cnt IN).length = 14 := by decide +kernel

theorem sum_out : ∑ j ∈ Finset.Icc 1 9, atLevel OUT j = 14 := by decide +kernel
theorem sum_in : ∑ j ∈ Finset.Icc 1 9, atLevel IN j = 14 := by decide +kernel

/-- (2) R2-bank.  e j = rank extras at cut j; P-BLOCK: atLevel ≤ e j (counted N-clique at cut j, nonzero minors). -/
theorem R2_out (e : ℕ → ℕ) (hblock : ∀ j, atLevel OUT j ≤ e j) : 14 ≤ ∑ j ∈ Finset.Icc 1 9, e j := by
  rw [← sum_out]; exact Finset.sum_le_sum (fun j _ => hblock j)

theorem R2_in (e : ℕ → ℕ) (hblock : ∀ j, atLevel IN j ≤ e j) : 14 ≤ ∑ j ∈ Finset.Icc 1 9, e j := by
  rw [← sum_in]; exact Finset.sum_le_sum (fun j _ => hblock j)

/-- Mass wiring.  P-CUTMASS: ascent mass ≥ Σ_f c_f + Σ_j extrasOUT_j, descent mass ≥ Σ_j extrasIN_j. -/
theorem R2_bank (cf asc desc : ℕ) (eo ei : ℕ → ℕ)
    (hasc : cf + ∑ j ∈ Finset.Icc 1 9, eo j ≤ asc) (hdesc : ∑ j ∈ Finset.Icc 1 9, ei j ≤ desc)
    (bo : ∀ j, atLevel OUT j ≤ eo j) (bi : ∀ j, atLevel IN j ≤ ei j) :
    cf + 14 ≤ asc ∧ 14 ≤ desc := by
  have := R2_out eo bo; have := R2_in ei bi; omega

/-- (3) R1-bank: an 8-clique of live rows (self-odd, pairwise N both ways). -/
def clique8 : Bool :=
  cliqueIN.length == 8 && cliqueIN.all (fun i => cliqueIN.all (fun l => N IN i l == 1 && (i == l || N IN l i == 1)))
theorem clique8_ok : clique8 = true := by decide +kernel
/-- P-R1CUT: descent banks ≥ rank of the clique rows across the ⇓q^⊥ cut (BANK1 §3, needs P-NEST). -/
theorem R1_bank (desc : ℕ) (h : cliqueIN.length ≤ desc) : 8 ≤ desc := by
  have : cliqueIN.length = 8 := by decide +kernel
  omega

end BankFlagB
#print axioms BankFlagB.R2_bank
#print axioms BankFlagB.out_cnt
#print axioms BankFlagB.clique8_ok
