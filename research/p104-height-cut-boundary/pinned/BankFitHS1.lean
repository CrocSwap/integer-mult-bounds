/-
BankFitHS1 (lane LEAN-BANK, Nov 18).  HEIGHT-STOP cut machinery (UCEIL/bankport/BP.md §2, AUDIT-BP (a),(b)), combinatorial part.
A height cut = a set S of heights 0..9 (bitmask m); a chart c is "in" iff m.testBit (finrank c).
  HSContract  : main contract for height cuts: π injective, support {self, π f}; Ehi = 104 rows of heights (1→9) with a
                nonzero partner entry at a (0→8) field; Elo = 104 rows (0→8) with a nonzero partner entry at a (1→9) field
                (checked on #7761's final graph: LEANSWARM/bankfit/contract7761.py, 104 + 104).
  cut_hs      : banks crossing S (either direction) ≥ fields crossing S + 208·[S separates {1,9} | {0,8}]
                (BankFlagC2.cut_extras in both directions; no down-set needed).
  mol_hs      : for ANY nonnegative integer cut decomposition W of a height function M (Σ_S W_S [i∈S ⊕ j∈S] = M |i-j|),
                Σ_f M(climb) + 208·sep(W) ≤ Σ_k M(dh_k).
Kernel only.
-/
import Nov15.BankFitA
import Nov15.BankFlagC2

namespace BankFitHS
open Finset Module BankNC0 BankWireC BankFit

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

structure HSContract (N : Net K (Submodule (ZMod 2) V) Fld Bank) where
  π : Fld → Fld
  πinj : Function.Injective π
  hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f
  Ehi : Finset Fld
  Elo : Finset Fld
  hi_card : Ehi.card = 104
  lo_card : Elo.card = 104
  hi_h : ∀ e ∈ Ehi, finrank (ZMod 2) (N.A e) = 1 ∧ finrank (ZMod 2) (N.B e) = 9 ∧
    finrank (ZMod 2) (N.A (π e)) = 0 ∧ finrank (ZMod 2) (N.B (π e)) = 8
  lo_h : ∀ e ∈ Elo, finrank (ZMod 2) (N.A e) = 0 ∧ finrank (ZMod 2) (N.B e) = 8 ∧
    finrank (ZMod 2) (N.A (π e)) = 1 ∧ finrank (ZMod 2) (N.B (π e)) = 9
  nz_hi : ∀ e ∈ Ehi, N.O e (π e) ≠ 0
  nz_lo : ∀ e ∈ Elo, N.O e (π e) ≠ 0

def isSep (m : ℕ) : Bool :=
  (m.testBit 1 && m.testBit 9 && !m.testBit 0 && !m.testBit 8) ||
  (!m.testBit 1 && !m.testBit 9 && m.testBit 0 && m.testBit 8)

def xcut (m i j : ℕ) : ℕ := if m.testBit i = m.testBit j then 0 else 1

def decVal (W : List (ℕ × ℕ)) (i j : ℕ) : ℕ := (W.map fun p => p.2 * xcut p.1 i j).sum

def sepVal (W : List (ℕ × ℕ)) : ℕ := (W.map fun p => if isSep p.1 then p.2 else 0).sum

/-- height of a chart -/
noncomputable abbrev ht (c : Submodule (ZMod 2) V) : ℕ := finrank (ZMod 2) c

theorem ht_le (c : Submodule (ZMod 2) V) : ht c ≤ 9 := by
  have := Submodule.finrank_le c; simpa using this

/-- one direction with extras. -/
theorem dir_extras (N : Net K (Submodule (ZMod 2) V) Fld Bank)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (hc : HSContract N) (P : Submodule (ZMod 2) V → Prop) [DecidablePred P] (E : Finset Fld)
    (hE : ∀ e ∈ E, ¬ P (N.A e) ∧ ¬ P (N.B e)) (hπ : ∀ e ∈ E, P (N.A (hc.π e)) ∧ P (N.B (hc.π e)))
    (hnz : ∀ e ∈ E, N.O e (hc.π e) ≠ 0) :
    (univ.filter (fun f => P (N.A f) ∧ ¬ P (N.B f))).card + E.card ≤
      (univ.filter (fun k => P (N.src k) ∧ ¬ P (N.dst k))).card :=
  BankFlagC.cut_extras N P _ E hc.π (fun c hc' => (mem_filter.mp hc').2) (hminor _) hE hπ hnz hc.hsupp
    (fun e _ r _ h => hc.πinj h)

theorem card_xor {α : Type} [Fintype α] [DecidableEq α] (p q : α → Prop) [DecidablePred p] [DecidablePred q] :
    (univ.filter (fun x => ¬ (p x ↔ q x))).card =
      (univ.filter (fun x => p x ∧ ¬ q x)).card + (univ.filter (fun x => ¬ p x ∧ q x)).card := by
  rw [← card_union_of_disjoint]
  · congr 1; ext x; simp only [mem_filter, mem_univ, true_and, mem_union]; tauto
  · rw [disjoint_left]; intro x h1 h2; simp only [mem_filter, mem_univ, true_and] at h1 h2; tauto

theorem sum_xcut {α : Type} [Fintype α] (m : ℕ) (a b : α → ℕ) :
    ∑ x, xcut m (a x) (b x) = (univ.filter (fun x => ¬ (m.testBit (a x) = true ↔ m.testBit (b x) = true))).card := by
  rw [card_filter]
  refine sum_congr rfl (fun x _ => ?_)
  unfold xcut
  by_cases h1 : m.testBit (a x) <;> by_cases h2 : m.testBit (b x) <;> simp [h1, h2]

/-- per height cut: crossing banks ≥ crossing fields + 208 on separating cuts. -/
theorem cut_hs (N : Net K (Submodule (ZMod 2) V) Fld Bank)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (hc : HSContract N) (m : ℕ) :
    ∑ f, xcut m (ht (N.A f)) (ht (N.B f)) + (if isSep m then 208 else 0) ≤
      ∑ k, xcut m (ht (N.src k)) (ht (N.dst k)) := by
  classical
  rw [sum_xcut, sum_xcut, card_xor, card_xor]
  set P : Submodule (ZMod 2) V → Prop := fun c => m.testBit (ht c) = true with hP
  set Q : Submodule (ZMod 2) V → Prop := fun c => ¬ m.testBit (ht c) = true with hQ
  have base : ∀ (R : Submodule (ZMod 2) V → Prop) [DecidablePred R],
      (univ.filter (fun f => R (N.A f) ∧ ¬ R (N.B f))).card ≤
        (univ.filter (fun k => R (N.src k) ∧ ¬ R (N.dst k))).card := by
    intro R _
    have := dir_extras N hminor hc R ∅ (by simp) (by simp) (by simp)
    simpa using this
  by_cases hs : isSep m
  · rw [if_pos hs]
    have hhi := hc.hi_h
    have hlo := hc.lo_h
    unfold isSep at hs
    simp only [Bool.or_eq_true, Bool.and_eq_true, Bool.not_eq_true'] at hs
    rcases hs with ⟨⟨⟨b1, b9⟩, b0⟩, b8⟩ | ⟨⟨⟨b1, b9⟩, b0⟩, b8⟩
    · -- S ∋ 1, 9; ∌ 0, 8: direction P carries Elo, direction Q carries Ehi
      have d1 := dir_extras N hminor hc P hc.Elo
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hlo e he; simp [hP, h1, h2, b0, b8])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hlo e he; simp [hP, h3, h4, b1, b9]) hc.nz_lo
      have d2 := dir_extras N hminor hc Q hc.Ehi
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hhi e he; simp [hQ, h1, h2, b1, b9])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hhi e he; simp [hQ, h3, h4, b0, b8]) hc.nz_hi
      rw [hc.lo_card] at d1; rw [hc.hi_card] at d2
      simp only [hP, hQ, not_not] at d1 d2
      omega
    · have d1 := dir_extras N hminor hc P hc.Ehi
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hhi e he; simp [hP, h1, h2, b1, b9])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hhi e he; simp [hP, h3, h4, b0, b8]) hc.nz_hi
      have d2 := dir_extras N hminor hc Q hc.Elo
        (fun e he => by obtain ⟨h1, h2, -, -⟩ := hlo e he; simp [hQ, h1, h2, b0, b8])
        (fun e he => by obtain ⟨-, -, h3, h4⟩ := hlo e he; simp [hQ, h3, h4, b1, b9]) hc.nz_lo
      rw [hc.hi_card] at d1; rw [hc.lo_card] at d2
      simp only [hP, hQ, not_not] at d1 d2
      omega
  · rw [if_neg hs]
    have a1 := base P
    have a2 := base Q
    simp only [hP, hQ, not_not] at a1 a2
    omega

theorem decVal_cons (p : ℕ × ℕ) (W : List (ℕ × ℕ)) (i j : ℕ) :
    decVal (p :: W) i j = p.2 * xcut p.1 i j + decVal W i j := by simp [decVal]

theorem sepVal_cons (p : ℕ × ℕ) (W : List (ℕ × ℕ)) :
    sepVal (p :: W) = (if isSep p.1 then p.2 else 0) + sepVal W := by simp [sepVal]

/-- any nonnegative integer height-cut decomposition W. -/
theorem dec_hs (N : Net K (Submodule (ZMod 2) V) Fld Bank)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (hc : HSContract N) (W : List (ℕ × ℕ)) :
    ∑ f, decVal W (ht (N.A f)) (ht (N.B f)) + 208 * sepVal W ≤
      ∑ k, decVal W (ht (N.src k)) (ht (N.dst k)) := by
  induction W with
  | nil => simp [decVal, sepVal]
  | cons p W ih =>
    simp only [decVal_cons, sepVal_cons, sum_add_distrib, ← mul_sum]
    have hcut := cut_hs N hminor hc p.1
    have h2 : p.2 * (∑ f, xcut p.1 (ht (N.A f)) (ht (N.B f)) + (if isSep p.1 then 208 else 0)) ≤
        p.2 * ∑ k, xcut p.1 (ht (N.src k)) (ht (N.dst k)) := Nat.mul_le_mul_left _ hcut
    have h3 : 208 * (if isSep p.1 then p.2 else 0) = p.2 * (if isSep p.1 then 208 else 0) := by
      split_ifs <;> ring
    rw [mul_add] at h2
    rw [mul_add, h3]
    omega

/-- molecule form: W decomposes the height function M on heights 0..9. -/
theorem mol_hs (N : Net K (Submodule (ZMod 2) V) Fld Bank)
    (hminor : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (hc : HSContract N) (W : List (ℕ × ℕ)) (M : ℕ → ℕ)
    (hdec : ∀ i, i < 10 → ∀ j, j < 10 → decVal W i j = M (dh i j)) :
    ∑ f, M (dh (ht (N.A f)) (ht (N.B f))) + 208 * sepVal W ≤
      ∑ k, M (dh (ht (N.src k)) (ht (N.dst k))) := by
  have h := dec_hs N hminor hc W
  have e1 : ∀ f, decVal W (ht (N.A f)) (ht (N.B f)) = M (dh (ht (N.A f)) (ht (N.B f))) := fun f =>
    hdec _ (by have := ht_le (N.A f); omega) _ (by have := ht_le (N.B f); omega)
  have e2 : ∀ k, decVal W (ht (N.src k)) (ht (N.dst k)) = M (dh (ht (N.src k)) (ht (N.dst k))) := fun k =>
    hdec _ (by have := ht_le (N.src k); omega) _ (by have := ht_le (N.dst k); omega)
  simp only [e1, e2] at h
  exact h

end BankFitHS
#print axioms BankFitHS.mol_hs
