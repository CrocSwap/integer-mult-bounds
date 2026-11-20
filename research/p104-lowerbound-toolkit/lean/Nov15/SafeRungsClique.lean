/-
SafeRungsClique (lane LEAN-R12, Nov 18).  cards/WILD/UCEIL/MINPREM.md rows P2a/P2, AUDIT-MIN.md (B).
R2 target-disjointness: the 8-port clique Q = {11,37,134,168,268,290,385,431} (labels of F2^9, bit-vectors as Nat)
has odd weight and pairwise odd overlaps (decide-checked), so for p,q in Q:  p.q = 1 (dot over F2).  Hence no chart
that lies in q^perp (q in Q) contains an element of Q.  So the owned moves ENTERING a down-set (R1 type) and those
ENTERING U_Q (R2 type) are disjoint BY TARGET, and  #owned moves >= 8 + 8 = 16  (`owned_ge_16`).
R1 (>= 8 entering moves) and R2 (>= 8 entering moves) themselves are the paper-proved hypotheses hR1/hR2.
`Q subset port labels` is a data fact (independent.py / ladder.log "Q in port labels True"): not needed here.
Kernel only: no sorry, no native_decide, no axioms.
-/
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Fintype.Fin
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

namespace SafeRungsClique

/-- Hamming weight of a 9-bit label, written out so that `decide` evaluates it. -/
def wt (n : ℕ) : ℕ :=
  n % 2 + (n / 2) % 2 + (n / 4) % 2 + (n / 8) % 2 + (n / 16) % 2 + (n / 32) % 2 +
  (n / 64) % 2 + (n / 128) % 2 + (n / 256) % 2

/-- F2 dot product of two labels = parity of the weight of the bitwise AND. -/
def dot (p q : ℕ) : ℕ := wt (p &&& q) % 2

def Q : List ℕ := [11, 37, 134, 168, 268, 290, 385, 431]

theorem Q_lt : ∀ p ∈ Q, p < 512 := by decide
theorem Q_odd_weight : ∀ p ∈ Q, wt p % 2 = 1 := by decide
theorem Q_pairwise_odd : ∀ p ∈ Q, ∀ q ∈ Q, p ≠ q → dot p q = 1 := by decide
/-- p.p = wt p mod 2 for labels < 512 (a decide-checked finite fact on Q). -/
theorem Q_self : ∀ p ∈ Q, dot p p = 1 := by decide

/-- the clique fact: p.q = 1 for ALL p, q in Q (equal or distinct). -/
theorem Q_dot_one : ∀ p ∈ Q, ∀ q ∈ Q, dot p q = 1 := by
  intro p hp q hq
  by_cases h : p = q
  · subst h; exact Q_self p hp
  · exact Q_pairwise_odd p hp q hq h

/-- A chart = a set of labels (vectors).  R1 type: chart inside q^perp for some q in Q. -/
def InDown (C : Finset ℕ) : Prop := ∃ q ∈ Q, ∀ x ∈ C, dot x q = 0
/-- R2 type: chart meets Q (lies in U_Q). -/
def InUp (C : Finset ℕ) : Prop := ∃ p ∈ Q, p ∈ C

/-- DISJOINT BY TARGET. -/
theorem down_up_disjoint (C : Finset ℕ) : ¬ (InDown C ∧ InUp C) := by
  rintro ⟨⟨q, hq, hd⟩, ⟨p, hp, hpC⟩⟩
  have h0 := hd p hpC
  have h1 := Q_dot_one p hp q hq
  omega

open Classical in
/-- m >= 16: owned moves with targets `tgt i`, among them >= 8 entering a down-set and >= 8 entering U_Q. -/
theorem owned_ge_16 {n : ℕ} (tgt : Fin n → Finset ℕ)
    (hR1 : 8 ≤ (Finset.univ.filter (fun i => InDown (tgt i))).card)
    (hR2 : 8 ≤ (Finset.univ.filter (fun i => InUp (tgt i))).card) : 16 ≤ n := by
  classical
  have hd : Disjoint (Finset.univ.filter (fun i => InDown (tgt i)))
      (Finset.univ.filter (fun i => InUp (tgt i))) := by
    rw [Finset.disjoint_filter]
    intro i _ h1 h2
    exact down_up_disjoint (tgt i) ⟨h1, h2⟩
  have hu := Finset.card_union_of_disjoint hd
  have hle : ((Finset.univ.filter (fun i => InDown (tgt i))) ∪
      (Finset.univ.filter (fun i => InUp (tgt i)))).card ≤ n := by
    have := Finset.card_le_univ (α := Fin n) ((Finset.univ.filter (fun i => InDown (tgt i))) ∪
      (Finset.univ.filter (fun i => InUp (tgt i))))
    simpa using this
  omega

end SafeRungsClique
