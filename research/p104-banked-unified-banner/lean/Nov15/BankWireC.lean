/-
BankWireC .  
CHART CONDITIONS (item 1), concrete: the witness flag [153,191,70,98,265,280,253,392,1] of BankFlagB as a flag of
subspaces FF j = span (first j flag vectors) of V = F_2^9 (bitmasks -> vectors, functional phi a = <a, .>).
  flag_step       : finrank FF (j+1) = finrank FF j + 1 for j < 9, FF 0 = bot, FF 9 = top
                    (witness functionals w_j: DATA, decide+kernel)
  pair_chart      : a (v,a) pair with v = comb m (m < 2^j), par a v = 1, par a (flag t) = 0 for t < j-1
                    has  vec v in FF j \ FF (j-1),  FF (j-1) <= ker phi_a,  FF j not <= ker phi_a
                    (exactly the hypotheses of BankWireB.out_cut / in_cut at cut c = j-1)
  out_ok / in_ok  : decide+kernel: every COUNTED pair of OUT / IN (BankFlagB.cnt) satisfies those hypotheses at
                    j = level v; counted rows per cut: 2 at j = 2..8, total 14 / 14.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.BankFlagB
import Nov15.BankWireA
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Field.ZMod
import Mathlib.LinearAlgebra.Dimension.Finrank
import Mathlib.LinearAlgebra.Dimension.Constructions

namespace BankWireC
open Finset Module Submodule BankFlagB

instance fact2 : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

abbrev V := Fin 9 → ZMod 2

def vec (m : ℕ) : V := fun i => if m.testBit i then 1 else 0
def fl (i : ℕ) : V := vec (flag.getD i 0)

def FF (j : ℕ) : Submodule (ZMod 2) V := span (ZMod 2) (fl '' {i | i < j})

def phi (a : ℕ) : V →ₗ[ZMod 2] ZMod 2 :=
  ∑ i : Fin 9, if a.testBit i then (LinearMap.proj i : V →ₗ[ZMod 2] ZMod 2) else 0

theorem phi_apply (a : ℕ) (x : V) : phi a x = ∑ i : Fin 9, if a.testBit i then x i else 0 := by
  unfold phi
  simp only [LinearMap.sum_apply]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  split_ifs <;> simp

theorem sum_range_list (g : ℕ → ZMod 2) (n : ℕ) :
    ∑ i ∈ Finset.range n, g i = ((List.range n).map g).sum := by
  induction n with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ, ih, List.range_succ, List.map_append, List.sum_append]; simp

theorem filter_len_sum (p : ℕ → Bool) (l : List ℕ) :
    (((l.filter p).length : ℕ) : ZMod 2) = (l.map (fun i => if p i = true then (1 : ZMod 2) else 0)).sum := by
  induction l with
  | nil => simp
  | cons x l ih =>
    by_cases h : p x = true
    · simp [List.filter_cons, h, ih, add_comm]
    · simp [List.filter_cons, h, ih]

theorem phi_vec (a b : ℕ) : phi a (vec b) = ((par a b : ℕ) : ZMod 2) := by
  rw [phi_apply]
  have h1 : ∀ i : Fin 9, (if a.testBit i then vec b i else 0) =
      (if (a &&& b).testBit (i : ℕ) = true then (1 : ZMod 2) else 0) := by
    intro i
    simp only [vec, Nat.testBit_and]
    cases a.testBit i <;> cases b.testBit i <;> simp
  simp_rw [h1]
  rw [Fin.sum_univ_eq_sum_range (fun i => if (a &&& b).testBit i = true then (1 : ZMod 2) else 0) 9,
    sum_range_list, ← filter_len_sum]
  unfold par
  exact (ZMod.natCast_eq_natCast_iff' _ _ 2).mpr (Nat.mod_mod _ _).symm

theorem FF_mono (j : ℕ) : FF j ≤ FF (j+1) :=
  Submodule.span_mono (Set.image_mono (fun i (hi : i < j) => by simp only [Set.mem_setOf_eq]; omega))

theorem FF_zero : FF 0 = ⊥ := by simp [FF]

theorem fl_mem {i j : ℕ} (h : i < j) : fl i ∈ FF j := Submodule.subset_span ⟨i, h, rfl⟩

theorem FF_succ (j : ℕ) : FF (j+1) = FF j ⊔ span (ZMod 2) {fl j} := by
  apply le_antisymm
  · refine Submodule.span_le.mpr ?_
    rintro _ ⟨i, hi, rfl⟩
    have : i < j ∨ i = j := by simp only [Set.mem_setOf_eq] at hi; omega
    rcases this with h | h
    · exact Submodule.mem_sup_left (fl_mem h)
    · subst h; exact Submodule.mem_sup_right (Submodule.mem_span_singleton_self _)
  · exact sup_le (FF_mono j) ((Submodule.span_singleton_le_iff_mem _ _).mpr (fl_mem (Nat.lt_succ_self j)))

/-- DATA: witness functionals separating flag j from the span of flags 0..j-1 (found by w.py) -/
def wit : List ℕ := [1, 2, 34, 6, 17, 9, 100, 273, 153]

theorem wit_ok : (List.range 9).all (fun j =>
    par (wit.getD j 0) (flag.getD j 0) == 1 &&
    (List.range j).all (fun i => par (wit.getD j 0) (flag.getD i 0) == 0)) = true := by decide +kernel

theorem FF_le_ker (a j : ℕ) (hz : ∀ t, t < j → par a (flag.getD t 0) = 0) :
    FF j ≤ LinearMap.ker (phi a) := by
  refine Submodule.span_le.mpr ?_
  rintro _ ⟨i, hi, rfl⟩
  simp only [Set.mem_setOf_eq] at hi
  rw [SetLike.mem_coe, LinearMap.mem_ker, fl, phi_vec, hz i hi]; rfl

theorem flag_step (j : ℕ) (hj : j < 9) : Module.finrank (ZMod 2) (FF (j+1)) = Module.finrank (ZMod 2) (FF j) + 1 := by
  have hw := wit_ok
  simp only [List.all_eq_true, List.mem_range, Bool.and_eq_true, beq_iff_eq] at hw
  obtain ⟨h1, h2⟩ := hw j hj
  have hnot : fl j ∉ FF j := by
    intro hm
    have := FF_le_ker (wit.getD j 0) j (fun t ht => h2 t (by simpa using ht)) hm
    rw [LinearMap.mem_ker, fl, phi_vec, h1] at this
    exact absurd this (by decide)
  have hv : fl j ≠ 0 := fun h => hnot (h ▸ Submodule.zero_mem _)
  have hdis : Disjoint (FF j) (span (ZMod 2) {fl j}) := by
    exact (Submodule.disjoint_span_singleton' hv).mpr hnot
  have := Submodule.finrank_sup_add_finrank_inf_eq (FF j) (span (ZMod 2) {fl j})
  rw [hdis.eq_bot, finrank_span_singleton hv, ← FF_succ] at this
  simp at this; omega

theorem FF_nine : FF 9 = ⊤ := by
  refine Submodule.eq_top_of_finrank_eq (S := FF 9) ?_
  have : ∀ j, j ≤ 9 → Module.finrank (ZMod 2) (FF j) = j := by
    intro j
    induction j with
    | zero => intro _; simp [FF_zero]
    | succ j ih => intro hj; rw [flag_step j (by omega), ih (by omega)]
  rw [this 9 le_rfl]; simp

theorem vec_xor (x y : ℕ) : vec (x ^^^ y) = vec x + vec y := by
  funext i
  simp only [vec, Nat.testBit_xor, Pi.add_apply]
  cases x.testBit i <;> cases y.testBit i <;> decide

theorem vec_zero : vec 0 = 0 := by funext i; simp [vec]

theorem foldl_mem (j m : ℕ) (hm : ∀ i, m.testBit i = true → i < j) :
    ∀ (l : List ℕ) (acc : ℕ), vec acc ∈ FF j →
      vec (l.foldl (fun acc i => if m.testBit i then acc ^^^ flag.getD i 0 else acc) acc) ∈ FF j := by
  intro l
  induction l with
  | nil => intro acc h; exact h
  | cons x l ih =>
    intro acc h
    simp only [List.foldl_cons]
    apply ih
    split_ifs with hb
    · rw [vec_xor]; exact Submodule.add_mem _ h (fl_mem (hm x hb))
    · exact h

theorem comb_mem (j m : ℕ) (hm : m < 2 ^ j) : vec (comb m) ∈ FF j := by
  unfold comb
  apply foldl_mem j m
  · intro i hi
    by_contra hij
    have : m < 2 ^ i := lt_of_lt_of_le hm (Nat.pow_le_pow_right (by norm_num) (by omega))
    rw [Nat.testBit_eq_false_of_lt this] at hi; exact absurd hi (by simp)
  · rw [vec_zero]; exact Submodule.zero_mem _

/-- the chart conditions of a counted pair at level j (cut c = j-1 of BankWireB). -/
theorem pair_chart (v a j : ℕ) (hj : 1 ≤ j) (hm : ∃ m, m < 2 ^ j ∧ comb m = v) (hodd : par a v = 1)
    (hz : ∀ t, t < j - 1 → par a (flag.getD t 0) = 0) :
    vec v ∈ FF (j - 1 + 1) ∧ vec v ∉ FF (j - 1) ∧ FF (j - 1) ≤ LinearMap.ker (phi a) ∧
      ¬ FF (j - 1 + 1) ≤ LinearMap.ker (phi a) := by
  have e : j - 1 + 1 = j := by omega
  have hle := FF_le_ker a (j - 1) hz
  have hmem : vec v ∈ FF j := by
    obtain ⟨m, hm1, rfl⟩ := hm; exact comb_mem j m hm1
  have hphi : phi a (vec v) = 1 := by rw [phi_vec, hodd]; rfl
  rw [e]
  refine ⟨hmem, fun h => ?_, hle, fun h => ?_⟩
  · have := hle h; rw [LinearMap.mem_ker, hphi] at this; exact absurd this (by decide)
  · have := h hmem; rw [LinearMap.mem_ker, hphi] at this; exact absurd this (by decide)

/-- DATA check: every counted pair of P satisfies the pair_chart hypotheses at j = level v. -/
def pairOk (P : List (ℕ × ℕ)) (i : ℕ) : Bool :=
  let v := (P.getD i (0, 0)).1
  let a := (P.getD i (0, 0)).2
  let j := level v
  decide (1 ≤ j) && decide (j ≤ 9) && (List.range (2 ^ j)).any (fun m => comb m == v) && (par a v == 1) &&
    (List.range (j - 1)).all (fun t => par a (flag.getD t 0) == 0)

theorem out_ok : (cnt OUT).all (pairOk OUT) = true := by decide +kernel
theorem in_ok : (cnt IN).all (pairOk IN) = true := by decide +kernel

/-- usable form: a counted row i of P has the chart conditions at cut c = level - 1 (so F(c+1) = level). -/
theorem counted_chart (P : List (ℕ × ℕ)) (hok : (cnt P).all (pairOk P) = true) (i : ℕ) (hi : i ∈ cnt P) :
    level (P.getD i (0, 0)).1 - 1 < 9 ∧
    vec (P.getD i (0, 0)).1 ∈ FF (level (P.getD i (0, 0)).1 - 1 + 1) ∧
    vec (P.getD i (0, 0)).1 ∉ FF (level (P.getD i (0, 0)).1 - 1) ∧
    FF (level (P.getD i (0, 0)).1 - 1) ≤ LinearMap.ker (phi (P.getD i (0, 0)).2) ∧
    ¬ FF (level (P.getD i (0, 0)).1 - 1 + 1) ≤ LinearMap.ker (phi (P.getD i (0, 0)).2) := by
  have h := (List.all_eq_true.mp hok) i hi
  unfold pairOk at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.any_eq_true, List.mem_range, beq_iff_eq,
    List.all_eq_true] at h
  obtain ⟨⟨⟨⟨h1, h9⟩, ⟨m, hm, hmv⟩⟩, hodd⟩, hz⟩ := h
  have := pair_chart (P.getD i (0, 0)).1 (P.getD i (0, 0)).2 (level (P.getD i (0, 0)).1) h1 ⟨m, hm, hmv⟩ hodd
    (fun t ht => by simpa using hz t ht)
  exact ⟨by omega, this⟩

end BankWireC
