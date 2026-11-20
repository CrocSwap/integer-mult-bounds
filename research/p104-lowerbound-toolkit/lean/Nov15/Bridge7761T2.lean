/-
Bridge7761T2 (lane CHAINTIE, Nov 18).  Chain data of #7761 as kernel-checked facts (chains c < 8, steps j < clen c):
  clen/cpos/cid/cbeta : chain length, bank position, chart id (clamped), relay beta (D5);
  chainFacts          : cpos < 5746, bS/bT at cpos = cid j / cid (j+1), height drops, ids < 1099, beta ≠ 0;
  injChk              : positions pairwise distinct (as pairs (c,j));   digChk : chkDig at all 23 chain banks (T1);
  suppChk             : the relay fresh vector f_j = d_j - β_j d_(j-1) (from the packed digits D_k*d_k(xin p)) is supported in the chart of step j
                        (fresh j p ≠ 0 -> lq p ∈ chart j, by inSpanB on the chart tables).
  chart_desc, lq_mem_chart : helper lemmas.   Kernel only.
-/
import Nov15.Bridge7761T1
import Nov15.Bridge7761F3
import Nov15.Bridge7761O1
import Nov15.Bridge7761O2

namespace Bridge7761
open Finset Module BankNC0 BridgeP

def clen (c : ℕ) : ℕ := (chPos.getD c []).length
def cpos (c j : ℕ) : ℕ := (chPos.getD c []).getD j 0
def cid (c j : ℕ) : ℕ := (chIds.getD c []).getD (min j (clen c)) 0
def cbeta (c j : ℕ) : ℚ := if j < clen c then (chBeta.getD c []).getD j 1 else 1

def chainFactB (c j : ℕ) : Bool :=
  decide (cpos c j < 5746) && (srcId (cpos c j) == cid c j) && (dstId (cpos c j) == cid c (j + 1)) &&
  decide (hp (cid c (j + 1)) < hp (cid c j)) && decide (cid c j < 1099) && decide (cid c (j + 1) < 1099) &&
  decide (cbeta c j ≠ 0)

def chainFacts : Bool := (List.range 8).all fun c => (List.range (clen c)).all fun j => chainFactB c j

theorem chainFacts_ok : chainFacts = true := by decide +kernel

theorem chainFact (c j : ℕ) (hc : c < 8) (hj : j < clen c) :
    cpos c j < 5746 ∧ srcId (cpos c j) = cid c j ∧ dstId (cpos c j) = cid c (j + 1) ∧
    hp (cid c (j + 1)) < hp (cid c j) ∧ cid c j < 1099 ∧ cid c (j + 1) < 1099 ∧ cbeta c j ≠ 0 := by
  have h := List.all_eq_true.1 (List.all_eq_true.1 chainFacts_ok c (List.mem_range.2 hc)) j (List.mem_range.2 hj)
  simp only [chainFactB, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩ := h
  exact ⟨h1, h2, h3, h4, h5, h6, h7⟩

def injB (c j c' j' : ℕ) : Bool := !(cpos c j == cpos c' j') || (c == c' && j == j')
def injChk : Bool := (List.range 8).all fun c => (List.range (clen c)).all fun j =>
  (List.range 8).all fun c' => (List.range (clen c')).all fun j' => injB c j c' j'
theorem injChk_ok : injChk = true := by decide +kernel

theorem cpos_inj (c j c' j' : ℕ) (hc : c < 8) (hj : j < clen c) (hc' : c' < 8) (hj' : j' < clen c')
    (h : cpos c j = cpos c' j') : c = c' ∧ j = j' := by
  have := List.all_eq_true.1 (List.all_eq_true.1 (List.all_eq_true.1 (List.all_eq_true.1 injChk_ok c
    (List.mem_range.2 hc)) j (List.mem_range.2 hj)) c' (List.mem_range.2 hc')) j' (List.mem_range.2 hj')
  simp only [injB, h, beq_self_eq_true, Bool.not_true, Bool.false_or, Bool.and_eq_true, beq_iff_eq] at this
  exact this

theorem digAll : ((List.range 8).all fun c => (List.range (clen c)).all fun j => chkDig (cpos c j)) = true := by
  decide +kernel

theorem digOK (c j : ℕ) (hc : c < 8) (hj : j < clen c) : chkDig (cpos c j) = true :=
  List.all_eq_true.1 (List.all_eq_true.1 digAll c (List.mem_range.2 hc)) j (List.mem_range.2 hj)

noncomputable def dqN (c j p : ℕ) : ℚ := (bdig (QT0.get (cpos c j)) (xField.getD p 0) : ℚ) / (dk (cpos c j) : ℚ)
noncomputable def freshQN (c j p : ℕ) : ℚ :=
  if j = 0 then dqN c 0 p else dqN c j p - cbeta c j * dqN c (j - 1) p
noncomputable def suppB (c j p : ℕ) : Bool :=
  decide (freshQN c j p = 0) || inSpanB (ubL (cid c j)) (upL (cid c j)) (DW4.lab p)
noncomputable def suppChk : Bool := (List.range 8).all fun c => (List.range (clen c)).all fun j =>
  (List.range 104).all fun p => suppB c j p

theorem suppChk_ok : suppChk = true := by decide +kernel

theorem supp (c j p : ℕ) (hc : c < 8) (hj : j < clen c) (hp : p < 104) :
    freshQN c j p ≠ 0 → inSpanB (ubL (cid c j)) (upL (cid c j)) (DW4.lab p) = true := by
  intro hne
  have := List.all_eq_true.1 (List.all_eq_true.1 (List.all_eq_true.1 suppChk_ok c (List.mem_range.2 hc)) j
    (List.mem_range.2 hj)) p (List.mem_range.2 hp)
  simp only [suppB, Bool.or_eq_true, decide_eq_true_eq] at this
  exact this.resolve_left hne

theorem chart_desc (k : ℕ) (hk : k < 5746) (h : hp (dstId k) < hp (srcId k)) :
    chartOf (dstId k) ≤ chartOf (srcId k) := by
  have hs := srcId_lt k hk
  have hd := dstId_lt k hk
  rcases nest7761 k hk with h1 | h1
  · exfalso
    have h2 := Submodule.finrank_mono h1
    have e1 := finrank_chartOf _ hs
    have e2 := finrank_chartOf _ hd
    have : (finrank (ZMod 2) (chartOf (srcId k)) : ℤ) ≤ finrank (ZMod 2) (chartOf (dstId k)) := by exact_mod_cast h2
    rw [e1, e2] at this; linarith
  · exact h1

theorem lq_mem_chart (c : ℕ) (hc : c < 1099) (p : Fin 104)
    (h : inSpanB (ubL c) (upL c) (DW4.lab p) = true) : DF.lq p ∈ chartOf c := by
  have hmem := inSpanB_mem h
  rw [(ub_ok _ hc).1] at hmem
  unfold chartOf
  exact hmem

end Bridge7761
#print axioms Bridge7761.chainFacts_ok
#print axioms Bridge7761.injChk_ok
#print axioms Bridge7761.digAll
#print axioms Bridge7761.suppChk_ok
#print axioms Bridge7761.chart_desc
#print axioms Bridge7761.lq_mem_chart
